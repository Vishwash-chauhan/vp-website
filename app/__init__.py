from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import base64
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Initialize Firebase
    from app.utils.firebase_auth import init_firebase_app
    init_firebase_app()

    # Add template context processor for current year
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.now().year}
    
    # Add base64 filter for template
    @app.template_filter('b64encode')
    def b64encode_filter(data):
        if data:
            return base64.b64encode(data).decode('utf-8')
        return ''

    # Add Firebase config to all templates
    @app.context_processor
    def inject_firebase_config():
        from app.utils.firebase_auth import firebaseConfig
        return {'firebase_config': firebaseConfig}

    # Add datetime filter for formatting timestamps
    @app.template_filter('datetime')
    def datetime_filter(timestamp, format='%Y-%m-%d %H:%M:%S'):
        from datetime import datetime
        if timestamp:
            return datetime.fromtimestamp(timestamp / 1000).strftime(format)
        return ''

    # Register blueprints
    from app.routes.main import main
    from app.routes.auth import auth  # Import the auth blueprint
    
    app.register_blueprint(main)
    app.register_blueprint(auth)  # Register the auth blueprint
    
    return app

# Import models to ensure they're registered with SQLAlchemy
from app.models import user, expert, category