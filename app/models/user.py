from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    contact = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    business_type = db.Column(db.String(50), nullable=True)
    date_created = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=True, default=True)
    is_admin = db.Column(db.Boolean, nullable=True, default=False)

    def __repr__(self):
        return f'<User {self.name}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        """Save user to database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete user from database"""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'contact': self.contact,
            'business_type': self.business_type,
            'date_created': self.date_created,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }