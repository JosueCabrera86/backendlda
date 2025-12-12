from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

CORS(
    app,
    resources={r"/*": {"origins": ["https://losdealla.com", "http://localhost:5173"]}},
    supports_credentials=True
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


# ===========================================================
# TOKEN REQUIRED
# ===========================================================
def token_required(required_rol=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):

            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"message": "Token no enviado"}), 403

            token = auth_header.split(" ")[1]

            resp = requests.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {token}",
                },
            )

            if resp.status_code != 200:
                return jsonify({"message": "Token inválido"}), 401

            user_data = resp.json()
            rol = user_data.get("user_metadata", {}).get("rol")

            if required_rol and rol != required_rol:
                return jsonify({"message": "Permiso denegado"}), 403

            kwargs["current_user"] = user_data
            return f(*args, **kwargs)

        return decorated
    return decorator


# ===========================================================
# CREAR USUARIO
# ===========================================================
@app.route("/users", methods=["POST"])
@token_required(required_rol="admin")
def create_user(current_user):
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    rol = data.get("rol", "user")
    name = data.get("name")
    categoria = data.get("categoria")
    disciplina = data.get("disciplina")

    if not email or not password:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    metadata = {
        "rol": rol,
        "name": name,
        "categoria": categoria,
        "disciplina": disciplina
    }

    # Crear en Auth
    resp = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "email": email,
            "password": password,
            "user_metadata": metadata
        },
    )

    if resp.status_code not in (200, 201):
        return jsonify({"error": resp.json()}), resp.status_code

    auth_user = resp.json()
    auth_id = auth_user.get("id")

    if not auth_id:
        return jsonify({"error": "Supabase no devolvió un id"}), 400

    # Insertar en tabla pública
    insert_resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/users",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json={
            "id": auth_id,
            "email": email,
            "name": name,
            "rol": rol,
            "categoria": categoria,
            "disciplina": disciplina
        },
    )

    if insert_resp.status_code not in (200, 201):
        return jsonify({"error": insert_resp.json()}), insert_resp.status_code

    return jsonify({
        "message": "Usuario creado",
        "user": insert_resp.json()
    }), 201


# ===========================================================
# CAMBIAR CONTRASEÑA
# ===========================================================
@app.route("/users/password", methods=["PATCH"])
@token_required()  # user o admin
def change_password(current_user):
    data = request.get_json()
    user_id = data.get("id")
    new_password = data.get("password")

    if not user_id or not new_password:
        return jsonify({"error": "Faltan datos"}), 400

    resp = requests.put(
        f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
        },
        json={"password": new_password},
    )

    if resp.status_code not in (200, 201):
        return jsonify({"error": resp.json()}), resp.status_code

    return jsonify({"message": "Contraseña actualizada"}), 200


# ===========================================================
# ELIMINAR USUARIO COMPLETO (AUTH + TABLA PUBLICA)
# ===========================================================
@app.route("/users/<user_id>", methods=["DELETE"])
@token_required(required_rol="admin")
def delete_user(current_user, user_id):

    # 1) Eliminar en tabla pública
    delete_public = requests.delete(
        f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Prefer": "return=representation",
        }
    )

    # 2) Eliminar en Auth
    delete_auth = requests.delete(
        f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
        }
    )

    if delete_auth.status_code not in (200, 204):
        return jsonify({"error": delete_auth.json()}), delete_auth.status_code

    return jsonify({"message": "Usuario eliminado completamente"}), 200


if __name__ == "__main__":
    app.run(debug=True)
