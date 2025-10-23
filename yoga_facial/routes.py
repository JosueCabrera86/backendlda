from flask import Blueprint, jsonify
from utils.auth import token_required


yoga_bp = Blueprint("yoga_bp", __name__)

MATERIAL_YOGAFACIAL = {
    0: [""],
    1: ["Clase introductoria -video,Clase introductoria -pdf,"],
    2: ["Masaje periférico"],
    3: ["Masaje de reseteo facial"],
    4: ["Masaje de preparación facial", "Clase 1"],
    5: ["1. Frente y ojos - pdf"],
    6: ["1. Frente y ojos - video"],
    7: ["2. Una rutina para ojos - pdf"],
    8: ["2. Una rutina para ojos - video"],
    9: ["Masaje guasha"],
    10: ["Clase 2"],
    11: ["3. Línea facial y cuello - pdf"],
    12: ["3. Línea facial y cuello - video"],
    13: ["Masaje relajante"],
    14: ["4. Nariz, labios y nasolabiales - pdf"],
    15: ["4. Nariz, labios y nasolabiales - video"],
    16: ["Clase 3"],
    17: ["5. Pómulos y sonrisa - pdf"],
    18: ["5. Pómulos y sonrisa - video"],
    19: ["Masaje acupresión - pdf"],
    20: ["7. Acupresión avanzados - video"],
    21: ["Clase especial de Kinesiotape-video"]
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
