from flask import Blueprint, request, jsonify
from models import db, Post, Section
from datetime import datetime

blog_bp = Blueprint('blog', __name__)

# Obtener todos los posts


@blog_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    result = []
    for post in posts:
        result.append({
            'id': post.id,
            'title': post.title,
            'author': post.author,
            'created_at': post.created_at,
            'sections': [{
                'id': s.id,
                'imagen': s.imagen,
                'subtitulo': s.subtitulo,
                'texto': s.texto
            } for s in post.secciones]
        })
    return jsonify(result)


# Crear un nuevo post
@blog_bp.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    sections_data = data.get('sections', [])

    if not title or not author:
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    new_post = Post(title=title, author=author)
    for sec in sections_data:
        section = Section(
            imagen=sec.get('imagen'),
            subtitulo=sec.get('subtitulo'),
            texto=sec.get('texto'),
        )
        new_post.secciones.append(section)

    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post creado', 'id': new_post.id}), 201


# Obtener un solo post
@blog_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify({
        'id': post.id,
        'title': post.title,
        'author': post.author,
        'created_at': post.created_at,
        'sections': [{
            'id': s.id,
            'imagen': s.imagen,
            'subtitulo': s.subtitulo,
            'texto': s.texto
        } for s in post.secciones]
    })


# Actualizar un post
@blog_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.json

    post.title = data.get('title', post.title)
    post.author = data.get('author', post.author)

    # Opcional: actualizar secciones si se proveen
    # Aquí podrías eliminar y volver a crear, o hacer una lógica más fina
    if 'sections' in data:
        post.secciones.clear()
        for sec in data['sections']:
            section = Section(
                imagen=sec.get('imagen'),
                subtitulo=sec.get('subtitulo'),
                texto=sec.get('texto'),
            )
            post.secciones.append(section)

    db.session.commit()
    return jsonify({'message': 'Post actualizado'})


# Eliminar un post
@blog_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post eliminado'})
