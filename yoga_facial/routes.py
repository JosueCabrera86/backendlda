from flask import Blueprint, jsonify
from utils.auth import token_required

yoga_bp = Blueprint("yoga_bp", __name__)

MATERIAL_YOGAFACIAL = {
    0: ["Clase introductoria"],
    1: ["Masaje periférico"],
    2: ["Masaje de reseteo facial"],
    3: ["Masaje de preparación facial", "Clase 1"],
    4: ["1. Frente y ojos - pdf"],
    5: ["1. Frente y ojos - video"],
    6: ["2. Una rutina para ojos - pdf"],
    7: ["2. Una rutina para ojos - video"],
    8: ["Masaje guasha"],
    9: ["Clase 2"],
    10: ["3. Línea facial y cuello - pdf"],
    11: ["3. Línea facial y cuello - video"],
    12: ["Masaje relajante"],
    13: ["4. Nariz, labios y nasolabiales - pdf"],
    14: ["4. Nariz, labios y nasolabiales - video"],
    15: ["Clase 3"],
    16: ["5. Pómulos y sonrisa - pdf"],
    17: ["5. Pómulos y sonrisa - video"],
    18: ["Masaje acupresión - pdf"],
    19: ["7. Acupresión avanzados - video"],
    20: ["Clase especial de Kinesiotape-video"]
}


@yoga_bp.route("/material", methods=["GET"])
@token_required
def get_yoga_material(current_user):
    user_disciplina = (current_user.disciplina or "").strip().lower()

    print(
        f"[Yoga Facial] Usuario {current_user.email} accediendo al material. "
        f"Rol: {current_user.rol}, Categoria: {current_user.categoria}, Disciplina: {user_disciplina}"
    )

    if user_disciplina != "yoga_facial":
        return jsonify({"error": "No tienes acceso a Yoga Facial"}), 403

    # Admin ve todo, usuario normal según su categoría
    nivel = max(MATERIAL_YOGAFACIAL.keys()
                ) if current_user.rol == "admin" else current_user.categoria or 0

    material = []
    for i in range(nivel + 1):
        material.extend(MATERIAL_YOGAFACIAL.get(i, []))

    print(f"[Yoga Facial] Material enviado a {current_user.email}: {material}")

    return jsonify({
        "disciplina": "yoga_facial",
        "nivel": nivel,
        "material": material
    })
