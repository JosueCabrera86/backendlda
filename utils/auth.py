from flask import request, jsonify, current_app
import jwt
from functools import wraps
from models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Buscar token en encabezado Authorization
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token faltante"}), 401

        try:
            # Decodificar token usando la SECRET_KEY de la app
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            current_user = User.query.get(data["id"])
            if not current_user:
                return jsonify({"error": "Usuario no encontrado"}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token ha expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        # Pasar el usuario al endpoint protegido
        return f(current_user, *args, **kwargs)

    return decorated
