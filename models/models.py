from . import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    categoria = db.Column(db.Integer)
    disciplina = db.Column(db.String(50))
    password = db.Column(db.String(300))
    rol = db.Column(db.String(20), default="usuario")


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    secciones = db.relationship(
        "Section", backref="post", cascade="all, delete-orphan"
    )


class Section(db.Model):
    __tablename__ = "sections"

    id = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.String(300))
    subtitulo = db.Column(db.String(200))
    texto = db.Column(db.Text, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
