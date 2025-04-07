# app/__init__.py

from flask import Flask
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from app.config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, DEBUG
from flask_migrate import Migrate

# Initialize extensions
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()

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
    csrf.init_app(app)  # Initialize CSRF protection here
    migrate.init_app(app, db)

    # Register blueprints inside the function to avoid circular imports
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.jobs import jobs_bp
    from app.routes.courses import courses_bp
    from app.routes.progress import progress_bp
    from app.routes.social_bp import social_bp
    from app.routes.subscription import subscription_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(subscription_bp)

    # Import models here to avoid circular imports
    from app import models
    from app.models import load_user
    login_manager.user_loader(load_user)

    # Auto-create database tables
    with app.app_context():
        db.create_all()
    
    # Add context processor for social notification counts
    @app.context_processor
    def inject_social_counts():
        if current_user.is_authenticated:
            try:
                # Import social models
                from app.models import Message, Connection, GroupMessage, GroupMember
                
                # Count unread direct messages
                unread_messages_count = Message.query.filter_by(
                    recipient_id=current_user.id, 
                    read=False
                ).count()
                
                # Count unread group messages
                unread_group_messages = db.session.query(GroupMessage).\
                    join(GroupMember, GroupMember.group_id == GroupMessage.group_id).\
                    filter(
                        GroupMember.user_id == current_user.id,
                        ~GroupMessage.read_by.any(id=current_user.id),
                        GroupMessage.sender_id != current_user.id
                    ).count()
                
                # Count pending connection requests
                pending_connections_count = Connection.query.filter_by(
                    friend_id=current_user.id, 
                    status='pending'
                ).count()
                
                # Total unread notifications
                total_unread = unread_messages_count + unread_group_messages + pending_connections_count
                
                return {
                    'unread_messages_count': unread_messages_count,
                    'unread_group_messages': unread_group_messages,
                    'pending_connections_count': pending_connections_count,
                    'total_unread_messages': unread_messages_count + unread_group_messages,
                    'total_notifications': total_unread
                }
            except Exception as e:
                app.logger.error(f"Error calculating social counts: {e}")
                # Return empty counts if there's an error
                return {
                    'unread_messages_count': 0,
                    'unread_group_messages': 0,
                    'pending_connections_count': 0,
                    'total_unread_messages': 0,
                    'total_notifications': 0
                }
        return {
            'unread_messages_count': 0,
            'unread_group_messages': 0, 
            'pending_connections_count': 0,
            'total_unread_messages': 0,
            'total_notifications': 0
        }
        
    # Register Flask-SocketIO event handlers
    with app.app_context():
        from app.sockets import chat_events

    return app
