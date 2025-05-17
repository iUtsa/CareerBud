from flask import Flask
from flask_login import current_user
from app.config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, DEBUG
from app.extensions import db, bcrypt, login_manager, socketio, csrf, migrate
import humanize
import os
from datetime import datetime
from app.routes.resume_bp import resume_bp
from app.routes.coursebud_bp import coursebud_bp
from app.routes.taskbud_bp import taskbud_bp

def timeago(dt):
    return humanize.naturaltime(datetime.utcnow() - dt)

def create_app(config_class=None):
    app = Flask(__name__)

    app.jinja_env.filters['timeago'] = timeago
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

    # Basic config
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Add this near your os.makedirs line for debugging
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    print(f"Upload directory: {upload_dir}")
    print(f"Directory exists: {os.path.exists(upload_dir)}")
    print(f"Directory is writable: {os.access(upload_dir, os.W_OK)}")

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.jobs import jobs_bp
    # Commenting out the old courses_bp
    # from app.routes.courses import courses_bp
    from app.routes.progress import progress_bp
    from app.routes.social_bp import social_bp
    from app.routes.subscription import subscription_bp
    from app.routes.admin_bp import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jobs_bp)
    # Commenting out registration of the old courses_bp
    # app.register_blueprint(courses_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(resume_bp)
    # Register the new coursebud_bp
    app.register_blueprint(coursebud_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(taskbud_bp)


    # Import models here to avoid circular imports
    from app import models
    from app.models import load_user
    login_manager.user_loader(load_user)

    # Auto-create database tables
    with app.app_context():
        from app.sockets import chat_events
        # Creates the tables in PostgreSQL
        db.create_all()

    # Add context processor for social notification counts
    @app.context_processor
    def inject_social_counts():
        if current_user.is_authenticated:
            try:
                # Import social models
                from app.models import Message, Connection
                
                # Count all messages instead of filtering by read status
                unread_messages_count = Message.query.filter_by(
                    recipient_id=current_user.id
                ).count()  # Remove the read=False filter
                
                # For now, set group messages to 0
                unread_group_messages = 0
                
                # Update filter to use recipient_id instead of friend_id
                pending_connections_count = Connection.query.filter_by(
                    recipient_id=current_user.id, 
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


def reset_course_sequence():
    """Reset the course ID sequence to the next available ID."""
    from sqlalchemy import text
    
    # Get the maximum ID currently in the courses table
    max_id_result = db.session.execute(text("SELECT MAX(id) FROM courses")).fetchone()
    max_id = max_id_result[0] or 0
    
    # Set the sequence to start from max_id + 1
    db.session.execute(text(f"ALTER SEQUENCE courses_id_seq RESTART WITH {max_id + 1}"))
    db.session.commit()