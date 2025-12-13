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
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


# =========================
# AUTH MIDDLEWARE
# =========================
def token_required(required_rol=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"message": "Token no enviado"}), 403

            token = auth_header.split(" ")[1]

            # 1️⃣ Validar token
            auth_resp = requests.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {token}",
                },
            )

            if auth_resp.status_code != 200:
                return jsonify({"message": "Token inválido"}), 401

            auth_user = auth_resp.json()
            auth_id = auth_user["id"]  # UUID

            print("=== DEBUG TOKEN HEADER ===")
            print("auth_header:", auth_header)
            print("AUTH_ID:", auth_id)
            print("USER EMAIL:", auth_user.get("email"))

            # 2️⃣ Obtener rol REAL desde public.users (USAR auth_id)
            db_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/users?auth_id=eq.{auth_id}&select=rol",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                },
            )

            print("=== DEBUG DB RESPONSE ===")
            print("Status code:", db_resp.status_code)
            try:
                print("Response JSON:", db_resp.json())
            except Exception as e:
                print("No JSON response:", db_resp.text)

            if not db_resp.ok or not db_resp.json():
                return jsonify({"message": "Usuario no registrado en la base"}), 403

            rol = db_resp.json()[0]["rol"]

            if required_rol and rol != required_rol:
                return jsonify({"message": "Permiso denegado"}), 403

            kwargs["current_user"] = {
                "auth_id": auth_id,
                "rol": rol,
                "email": auth_user.get("email"),
            }

            return f(*args, **kwargs)

        return decorated
    return decorator



# =========================
# GET USERS (ADMIN)
# =========================
@app.route("/admin/users", methods=["GET"])
@token_required(required_rol="admin")
def get_users(current_user):
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?select=id,auth_id,name,email,rol,categoria,disciplina",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
        )
        if not resp.ok:
            return jsonify({"error": resp.json()}), resp.status_code
        return jsonify(resp.json()), 200
    except Exception as e:
        return jsonify({"error": "internal", "details": str(e)}), 500


# =========================
# CREATE USER
# =========================
@app.route("/users", methods=["POST"])
@token_required(required_rol="admin")
def create_user(current_user):
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        rol = data.get("rol", "user")
        name = data.get("name")
        categoria = data.get("categoria")
        disciplina = data.get("disciplina")

        if not email or not password:
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        if categoria in (None, ""):
            categoria = None
        else:
            categoria = int(categoria)

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
                "user_metadata": {
                    "rol": rol,
                    "name": name,
                    "categoria": categoria,
                    "disciplina": disciplina,
                },
            },
        )

        if resp.status_code not in (200, 201):
            return jsonify({"error": resp.json()}), resp.status_code

        return jsonify({"message": "Usuario creado correctamente"}), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "internal", "details": str(e)}), 500


# =========================
# CHANGE PASSWORD
# =========================
@app.route("/users/password", methods=["PATCH"])
@token_required()
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


# =========================
# EDIT USER (PATCH)
# =========================
@app.route("/users", methods=["PATCH"])
@token_required(required_rol="admin")
def edit_user(current_user):
    data = request.get_json()
    user_id = data.get("id")
    updates = {}

    for field in ["name", "rol", "categoria", "disciplina"]:
        if field in data:
            updates[field] = data[field]

    if not user_id or not updates:
        return jsonify({"error": "Faltan datos"}), 400

    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/users?auth_id=eq.{user_id}",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
        },
        json=updates,
    )

    if not resp.ok:
        return jsonify({"error": resp.json()}), resp.status_code

    return jsonify({"message": "Usuario actualizado"}), 200


# =========================
# EDIT MULTIPLE USERS
# =========================
@app.route("/users/multiple", methods=["PATCH"])
@token_required(required_rol="admin")
def edit_multiple_users(current_user):
    data = request.get_json()
    ids = data.get("ids", [])
    categoria = data.get("categoria")

    if not ids or categoria is None:
        return jsonify({"error": "Faltan datos"}), 400

    for uid in ids:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/users?auth_id=eq.{uid}",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
            },
            json={"categoria": int(categoria)},
        )

    return jsonify({"message": "Usuarios actualizados"}), 200


# =========================
# DELETE USER
# =========================
@app.route("/users/<user_id>", methods=["DELETE"])
@token_required(required_rol="admin")
def delete_user(current_user, user_id):
    # Eliminar de la tabla users
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/users?auth_id=eq.{user_id}",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        },
    )

    # Eliminar del auth
    delete_auth = requests.delete(
        f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        },
    )

    if delete_auth.status_code not in (200, 204):
        return jsonify({"error": delete_auth.json()}), delete_auth.status_code

    return jsonify({"message": "Usuario eliminado completamente"}), 200



