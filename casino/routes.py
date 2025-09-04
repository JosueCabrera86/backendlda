from flask import Blueprint, jsonify
from models import User
from utils.auth import token_required

casino_bp = Blueprint("casino_bp", __name__)

MATERIAL_CASINO = {
    0: ["Clase introductoria de Salsa"],
    1: ["Pasos básicos"],
    2: ["Vueltas simples"],
    3: ["Rueda de casino nivel 1"],
    # ...
}


@casino_bp.route("/material", methods=["GET"])
@token_required
def get_casino_material(current_user):
    if current_user.disciplina != "casino":
        return jsonify({"error": "No tienes acceso a Salsa Cubana"}), 403

    nivel = current_user.categoria or 0
    material = []
    for i in range(0, nivel+1):
        material.extend(MATERIAL_CASINO.get(i, []))

    return jsonify({"disciplina": "casino", "nivel": nivel, "material": material})
