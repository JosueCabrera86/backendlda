from flask import request, jsonify, current_app
import jwt
from functools import wraps
from models import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Buscar token en encabezado Authorization
        auth_header = request.headers.get("Authorization", "")
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

            # Obtener user_id del token (coincide con login)
            user_id = data.get("user_id")
            if not user_id:
                return jsonify({"error": "Token inválido: no contiene user_id"}), 401

            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({"error": "Usuario no encontrado"}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token ha expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        except Exception as e:
            print("Error en token_required:", e)
            return jsonify({"error": "Error interno de autenticación"}), 500

        # Pasar el usuario al endpoint protegido
        return f(current_user, *args, **kwargs)

    return decorated
