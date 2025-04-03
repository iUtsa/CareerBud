from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from app.config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, DEBUG

# Initialize extensions
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
db = SQLAlchemy()

def create_app(config_class=None):
    app = Flask(__name__)

    # Basic config
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.jobs import jobs_bp
    from app.routes.courses import courses_bp
    from app.routes.progress import progress_bp
    from app.routes.social_bp import social_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(social_bp)

    # Import models (so SQLAlchemy sees them)
    from app import models
    from app.models import load_user
    login_manager.user_loader(load_user)

    # Auto-create database tables
    with app.app_context():
        db.create_all()

    return app
