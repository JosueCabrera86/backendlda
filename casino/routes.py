# from flask import Blueprint, jsonify
# from utils.auth import token_required

# casino_bp = Blueprint("casino_bp", __name__)

# MATERIAL_CASINO = {
#     0: [""],
#     1: ["Nivel Básico"],
#     2: ["Nivel Principiante"],
#     3: ["Nivel Intermedio"],
#     4: ["Nivel Avanzado"]
# }


# @casino_bp.route("/material", methods=["GET"])
# @token_required
# def get_casino_material(current_user):
#     user_disciplina = (current_user.disciplina or "").strip().lower()

#     print(
#         f"[Casino] Usuario {current_user.email} accediendo al material. "
#         f"Rol: {current_user.rol}, Categoria: {current_user.categoria}, Disciplina: {user_disciplina}"
#     )

#     if user_disciplina != "casino":
#         return jsonify({"error": "No tienes acceso a Casino"}), 403

#     # Admin ve todo, usuario normal según su categoría
#     nivel = max(MATERIAL_CASINO.keys()) if current_user.rol == "admin" else int(
#         current_user.categoria or 0)

#     material = []
#     for i in range(nivel + 1):
#         material.extend(MATERIAL_CASINO.get(i, []))

#     print(f"[Casino] Material enviado a {current_user.email}: {material}")

#     return jsonify({
#         "disciplina": "casino",
#         "nivel": nivel,
#         "material": material
#     })
