from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
import requests
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

CORS(app, resources={r"/*": {"origins": ["https://losdealla.com", "http://localhost:5173"]}}, supports_credentials=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


# ---------------------------
# TOKEN DECORATOR
# ---------------------------
def token_required(required_rol=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"message": "Formato de token inválido"}), 403
            token = auth_header.split(" ")[1]
            try:
                data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                if required_rol and data.get("rol") != required_rol:
                    return jsonify({"message": "Permiso denegado"}), 403
                kwargs["current_user"] = data
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Token inválido"}), 401
            return f(*args, **kwargs)
        return decorated
    return decorator


# ---------------------------
# CREAR USUARIO
# ---------------------------
@app.route("/users", methods=["POST"])
@token_required(required_rol="admin")
def create_user(current_user):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    rol = data.get("rol", "user")

    if not all([email, password, rol]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    # Crear usuario en Supabase
    resp = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "email": email,
            "password": password,
            "role": rol  # solo info básica
        }
    )

    if resp.status_code not in (200, 201):
        return jsonify({"error": resp.json()}), 400

    return jsonify({"message": "Usuario creado en Supabase", "user": {"email": email, "rol": rol}}), 201


# ---------------------------
# CAMBIAR CONTRASEÑA
# ---------------------------
@app.route("/users/password", methods=["PATCH"])
@token_required()
def change_password(current_user):
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("password")

    if not email or not new_password:
        return jsonify({"error": "Faltan datos"}), 400

    resp = requests.put(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "email": email,
            "password": new_password
        }
    )

    if resp.status_code not in (200, 201):
        return jsonify({"error": resp.json()}), 400

    return jsonify({"message": "Contraseña actualizada"}), 200
