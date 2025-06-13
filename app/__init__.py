from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import base64

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

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

    from app.routes.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app