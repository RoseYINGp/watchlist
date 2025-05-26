# models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from watchlist import db
from sqlalchemy import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))
    comments = db.relationship('Comment', backref='movie', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=func.now())
    #
    comment_text = db.Column(db.Text, nullable=False)  # 保持原字段名
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))