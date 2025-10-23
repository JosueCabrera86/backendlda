from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, Post, Section
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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)
CORS(app, resources={
     r"/*": {"origins": ["https://losdealla.com", "http://localhost:5173"]}}, supports_credentials=True)

app.register_blueprint(yoga_bp, url_prefix="/api/yoga-facial")
app.register_blueprint(casino_bp, url_prefix="/api/casino")
# ------------------ TOKEN & AUTH ------------------ #


def token_required(required_rol=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'message': 'Formato de token inválido'}), 403
            token = auth_header.split(' ')[1]

            try:
                data = jwt.decode(
                    token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_id = data.get('user_id') or data.get('id')
                if not user_id:
                    return jsonify({'message': 'Token inválido: no contiene ID de usuario'}), 401

                current_user = User.query.get(user_id)
                if not current_user:
                    return jsonify({'message': 'Usuario no encontrado'}), 401

                if required_rol and current_user.rol != required_rol:
                    return jsonify({'message': 'Permiso denegado'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'El token ha expirado'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token inválido'}), 401
            except Exception as e:
                print("Error en token_required:", e)
                return jsonify({'message': 'Error interno de autenticación'}), 500

            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

# ------------------ LOGIN ------------------ #


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Correo y contraseña son obligatorios'}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({
            'user_id': user.id,
            'exp': expiration,
            'rol': user.rol,
            'disciplina': user.disciplina,
            'categoria': user.categoria
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"message": "Login exitoso", "token": token}), 200
    else:
        return jsonify({"error": "Email o contraseña no válida"}), 401

# ------------------ USUARIOS ------------------ #


@app.route("/users", methods=['GET'])
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


@app.route("/users", methods=['POST'])
@token_required(required_rol='admin')
def create_user(current_user):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    categoria = data.get('categoria')
    disciplina = data.get('disciplina', '').lower().replace(
        " ", "_") if data.get('disciplina') else None
    password = data.get('password')
    rol = data.get('rol', 'user').lower()

    # Validación: siempre requerimos name, email, password y rol
    if not all([name, email, password, rol]):
        return jsonify({'error': 'Faltan datos obligatorios: name, email, rol o password'}), 400

    # Validación adicional: solo usuarios normales requieren categoría y disciplina
    if rol != 'admin' and (categoria is None or disciplina is None or disciplina == ''):
        return jsonify({'error': 'Faltan datos obligatorios para usuarios: categoria o disciplina'}), 400

    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'El correo ya está registrado'}), 400

    new_user = User(
        name=name,
        email=email,
        rol=rol,
        password=generate_password_hash(password),
        categoria=categoria if rol != 'admin' else None,
        disciplina=disciplina if rol != 'admin' else None
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Usuario creado con éxito",
        "user": {
            "name": new_user.name,
            "email": new_user.email,
            "categoria": new_user.categoria,
            "disciplina": new_user.disciplina,
            "rol": new_user.rol
        }
    }), 201


@app.route("/users/<email>", methods=['PUT'])
@token_required(required_rol='admin')
def update_user(current_user, email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json()
    if "name" in data:
        user.name = data["name"]
    if "categoria" in data:
        user.categoria = data["categoria"] if (
            data.get("rol", user.rol) != 'admin') else None
    if "disciplina" in data:
        user.disciplina = data["disciplina"].lower().replace(
            " ", "_") if (data.get("rol", user.rol) != 'admin') else None
    if "rol" in data:
        user.rol = data["rol"].lower()

    db.session.commit()
    return jsonify({
        "message": "Usuario actualizado",
        "user": {
            "name": user.name,
            "email": user.email,
            "categoria": user.categoria,
            "disciplina": user.disciplina,
            "rol": user.rol
        }
    }), 200


@app.route("/users/<email>", methods=['DELETE'])
@token_required(required_rol='admin')
def delete_user(current_user, email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado'}), 200


@app.route("/users/update-multiple", methods=['PUT'])
@token_required(required_rol='admin')
def update_multiple_users(current_user):
    data = request.get_json()
    usuarios = data.get("usuarios", [])

    updated = []
    errors = []

    for u in usuarios:
        user = User.query.filter_by(email=u.get("email")).first()
        if user:
            if "categoria" in u:
                user.categoria = u["categoria"]
            if "disciplina" in u:
                user.disciplina = u["disciplina"].lower().replace(" ", "_")
            if "rol" in u:
                user.rol = u["rol"].lower()
            updated.append(user.email)
        else:
            errors.append(u.get("email"))

    db.session.commit()

    return jsonify({
        "actualizados": updated,
        "no_encontrados": errors
    }), 200
