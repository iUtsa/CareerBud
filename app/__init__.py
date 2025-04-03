from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/studenthub')
client = MongoClient(mongo_uri)
db = client.get_database('studenthub')

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_object(config_class)
    
    # Initialize extensions with app
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.jobs import jobs_bp
    from app.routes.courses import courses_bp
    from app.routes.progress import progress_bp
    from app.routes.subscription import subscription_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(subscription_bp)
    
    # User loader for Flask-Login
    from app.models import load_user
    login_manager.user_loader(load_user)
    
    return app