from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    categoria = db.Column(db.Integer, nullable=True)
    disciplina = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(300), nullable=True)
    rol = db.Column(db.String(20), default='usuario')

    def __repr__(self):
        return f"<User {self.name}>"


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación uno a muchos: un post tiene muchas secciones
    secciones = db.relationship(
        'Section', backref='post', cascade='all, delete-orphan')


class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.String(300), nullable=True)
    subtitulo = db.Column(db.String(200), nullable=True)
    texto = db.Column(db.Text, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
