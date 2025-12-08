from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models AFTER creating db (to avoid circular imports)
from .models import User, Post, Section  

__all__ = ["db", "User", "Post", "Section"]
