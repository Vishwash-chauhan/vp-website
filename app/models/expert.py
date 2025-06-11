from flask_sqlalchemy import SQLAlchemy
from app import db
from datetime import datetime

class Expert(db.Model):
    __tablename__ = 'experts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # Keeping this field but not linking to users
    name = db.Column(db.String(100), nullable=False)
    expertise = db.Column(db.String(500), nullable=False)
    profile_picture = db.Column(db.LargeBinary, nullable=True)  # longblob in MySQL
    contact = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    about = db.Column(db.Text, nullable=True)
    portfolio_link = db.Column(db.String(255), nullable=True)
    instagram_profile = db.Column(db.String(255), nullable=True)
    linkedin_profile = db.Column(db.String(255), nullable=True)
    twitter_profile = db.Column(db.String(255), nullable=True)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    rating = db.Column(db.Numeric(3, 2), nullable=True, default=5.00)
    reviews_count = db.Column(db.Integer, nullable=True, default=0)
    is_available = db.Column(db.Boolean, nullable=True, default=True)
    is_verified = db.Column(db.Boolean, nullable=True, default=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Expert {self.name}>'

    def to_dict(self):
        """Convert expert object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'expertise': self.expertise,
            'contact': self.contact,
            'phone_number': self.phone_number,
            'bio': self.bio,
            'about': self.about,
            'portfolio_link': self.portfolio_link,
            'instagram_profile': self.instagram_profile,
            'linkedin_profile': self.linkedin_profile,
            'twitter_profile': self.twitter_profile,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else 0.0,
            'rating': float(self.rating) if self.rating else 5.0,
            'reviews_count': self.reviews_count,
            'is_available': self.is_available,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        """Save expert to database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete expert from database"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_available(cls):
        """Get all available experts"""
        return cls.query.filter_by(is_available=True).all()

    @classmethod
    def get_verified(cls):
        """Get verified experts"""
        return cls.query.filter_by(is_available=True, is_verified=True).all()

    @classmethod
    def search_experts(cls, search_term):
        """Search experts by name, expertise, or bio"""
        return cls.query.filter(
            cls.is_available == True,
            (cls.name.contains(search_term) | 
             cls.expertise.contains(search_term) | 
             cls.bio.contains(search_term))
        ).all()

    @classmethod
    def get_by_expertise(cls, expertise_term):
        """Get experts by expertise area"""
        return cls.query.filter(
            cls.is_available == True,
            cls.expertise.contains(expertise_term)
        ).all()
