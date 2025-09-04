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
from flask import Blueprint
from blog.routes import blog_bp
from yoga_facial.routes import yoga_bp
from casino.routes import casino_bp


load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

app.register_blueprint(blog_bp, url_prefix='/api')
app.register_blueprint(yoga_bp, url_prefix="/api/yoga-facial")
app.register_blueprint(casino_bp, url_prefix="/api/casino")


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validación de campos vacíos
    if not email or not password:
        return jsonify({'error': 'Correo y contraseña son obligatorios'}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        token = generate_token(user.id, user.rol)
        return jsonify({
            "message": "Login exitoso",
            "token": token
        }), 200
    else:
        return jsonify({"error": "Email o contraseña no válida"}), 401

# Función para generar el token JWT


def generate_token(user_id, rol):
    expiration = datetime.utcnow() + timedelta(hours=1)  # El token expirará en 1 hora
    token = jwt.encode({
        'user_id': user_id,
        'exp': expiration,
        'rol': rol
    }, app.config['SECRET_KEY'], algorithm='HS256')  # Usa la clave secreta
    return token


# Función para proteger rutas con JWT y verificar el rol (opcional)
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
                current_user = User.query.get(data['user_id'])

                if not current_user:
                    return jsonify({'message': 'Usuario no encontrado'}), 401

                if required_rol and current_user.rol != required_rol:
                    return jsonify({'message': 'Permiso denegado'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'El token ha expirado'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token inválido'}), 401

            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator


@app.route("/users", methods=['GET'])
@token_required()  # Solo requiere un token válido
def get_users(current_user):  # Recibimos el usuario actual decodificado
    users = User.query.all()
    return jsonify({
        "users": [
            {"id": user.id, "name": user.name,
             "email": user.email, "categoria": user.categoria}
            for user in users
        ]
    })


@app.route("/users", methods=['POST'])
@token_required(required_rol='admin')
def create_user(current_user):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    categoria = data.get('categoria')
    disciplina = data.get('disciplina')
    password = data.get('password')
    rol = data.get('rol', 'usuario')

    if not name or not email or not password:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'El correo ya está registrado'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, categoria=categoria,
                    password=hashed_password, rol=rol)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario creado con éxito'}), 201


@app.route("/users/<email>", methods=['PUT'])
# Solo los administradores pueden modificar usuarios
@token_required(required_rol='admin')
def update_user(current_user, email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    user.categoria = data.get('categoria', user.categoria)

    db.session.commit()
    return jsonify({'message': 'Usuario actualizado'}), 200


@app.route("/users/<email>", methods=['DELETE'])
# Solo los administradores pueden borrar usuarios
@token_required(required_rol='admin')
def delete_user(current_user, email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado'}), 200
