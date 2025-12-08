from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User,Post, Section
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from yoga_facial.routes import yoga_bp
from casino.routes import casino_bp


load_dotenv()
app = Flask(__name__)

# ---------------------------------------------
#              DATABASE CONFIG (SUPABASE)
# ---------------------------------------------
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI")

# 🔥 IMPORTANTE: SQLAlchemy + psycopg3 usan “postgresql+psycopg”
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Pool de conexión recomendado para Supabase Pooler
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 5,
    "connect_args": {
        "sslmode": "require"
    }
}

db.init_app(app)
migrate = Migrate(app, db)

# ---------------------------------------------
#              CORS CONFIG
# ---------------------------------------------
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://losdealla.com",
            "https://www.losdealla.com",
            "http://localhost:5173"
        ]
    }
}, supports_credentials=True)

# ---------------------------------------------
#                BLUEPRINTS
# ---------------------------------------------
app.register_blueprint(yoga_bp, url_prefix="/api/yoga-facial")
app.register_blueprint(casino_bp, url_prefix="/api/casino")


# ---------------------------------------------
#               TOKEN & AUTH
# ---------------------------------------------
def token_required(required_rol=None):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"message": "Formato de token inválido"}), 403

            token = auth_header.split(" ")[1]

            try:
                data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                user_id = data.get("user_id") or data.get("id")

                if not user_id:
                    return jsonify({"message": "Token inválido"}), 401

                current_user = User.query.get(user_id)
                if not current_user:
                    return jsonify({"message": "Usuario no encontrado"}), 401

                if required_rol and current_user.rol != required_rol:
                    return jsonify({"message": "Permiso denegado"}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({"message": "El token ha expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Token inválido"}), 401
            except Exception:
                return jsonify({"message": "Error interno"}), 500

            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


# ---------------------------------------------
#                 LOGIN
# ---------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Correo y contraseña obligatorios"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        token = jwt.encode({
            "user_id": user.id,
            "rol": user.rol,
            "disciplina": user.disciplina,
            "categoria": user.categoria,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({"message": "Login exitoso", "token": token})

    return jsonify({"error": "Credenciales inválidas"}), 401


# ---------------------------------------------
#                 USERS CRUD
# ---------------------------------------------
@app.route("/users", methods=["GET"])
@token_required()
def get_users(current_user):
    users = User.query.all()
    return jsonify({
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "categoria": u.categoria,
                "disciplina": u.disciplina,
                "rol": u.rol
            } for u in users
        ]
    })


@app.route("/users", methods=["POST"])
@token_required(required_rol="admin")
def create_user(current_user):
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    categoria = data.get("categoria")
    disciplina = data.get("disciplina", "").lower().replace(" ", "_")
    password = data.get("password")
    rol = data.get("rol", "user").lower()

    if not all([name, email, password, rol]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    if rol != "admin" and (not categoria or not disciplina):
        return jsonify({"error": "Faltan datos para usuarios no admin"}), 400

    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener mínimo 6 caracteres"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Correo ya registrado"}), 400

    new_user = User(
        name=name,
        email=email,
        rol=rol,
        password=generate_password_hash(password),
        categoria=categoria if rol != "admin" else None,
        disciplina=disciplina if rol != "admin" else None
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Usuario creado",
        "user": {
            "name": new_user.name,
            "email": new_user.email,
            "categoria": new_user.categoria,
            "disciplina": new_user.disciplina,
            "rol": new_user.rol
        }
    }), 201
