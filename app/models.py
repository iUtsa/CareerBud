from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy import Column, Integer, String, Text, Boolean
from app import db  # Ensure this is at the top of your models.py
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db, bcrypt









# Association table for many-to-many relationship between users and courses
user_courses = db.Table('user_courses',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

# User model with existing attributes and relationship to courses
# User model with existing attributes and relationship to courses
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    university = db.Column(db.String(128))
    major = db.Column(db.String(128))
    subscription_tier = db.Column(db.String(32), default='free')
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    gpa = db.Column(db.Float, default=0.0)
    credits = db.Column(db.Integer, default=0)
    total_credits = db.Column(db.Integer, default=128)

    job_applications = db.relationship('JobApplication', backref='user', lazy=True)
    todos = db.relationship('Todo', backref='user', lazy=True)
    skills = db.relationship('Skill', backref='user', lazy=True)
    achievements = db.relationship('Achievement', back_populates='user', lazy=True)  # Change to back_populates
    current_courses = db.relationship('Course', secondary='user_courses', backref='users')
    internships = db.relationship('Internship', back_populates='user', lazy=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_premium(self):
        if not self.subscription_end_date:
            return False
        return self.subscription_tier == 'premium' and datetime.utcnow() < self.subscription_end_date




class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications', lazy=True)

    def __repr__(self):
        return f'<Notification {self.id} - {self.message}>'



# Internship model with the updated backref



class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    job_type = db.Column(db.String(50))

class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(64), default='Applied')
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    interview_date = db.Column(db.DateTime, nullable=True)

class Internship(db.Model):
    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    description = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='internships')  # Link with back_populates



class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(50), default='medium')

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    skill_type = db.Column(db.String(50))
    level = db.Column(db.String(50))
    percentage = db.Column(db.Float)

class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='achievements')  # Change to back_populates





class Connection(db.Model):
    __tablename__ = 'connections'
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_connections')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_connections')


class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, nullable=False)
    user2_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visibility = db.Column(db.String(20), default='public')  # Add this field
    image_filename = db.Column(db.String(255))


    user = db.relationship('User', backref='posts')

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    level = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    premium_only = db.Column(db.Boolean, default=False)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
    post = db.relationship('Post', backref='comments')

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='likes')
    post = db.relationship('Post', backref='likes')


class Group(db.Model):
    __tablename__ = 'groups'
    __table_args__ = {'extend_existing': True}  # Add this to avoid conflicts in case of redefinition

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Individual message
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)  # For group messages
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)  # For group messages
    read = db.Column(db.Boolean, default=False)  # Add this line

    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    group = db.relationship('Group', foreign_keys=[group_id], backref='messages')  # For group messages
    conversation = db.relationship('Conversation', foreign_keys=[conversation_id])  # For group messages


def send_message(sender_id, recipient_id, content):
    try:
        message = Message(sender_id=sender_id, recipient_id=recipient_id, content=content)
        db.session.add(message)
        db.session.commit()
        return message
    except Exception as e:
        db.session.rollback()
        print(f"Error sending message: {e}")
        return None

def send_group_message(sender_id, group_id, content):
    try:
        # Create a new group message
        group_message = Message(sender_id=sender_id, group_id=group_id, content=content)
        db.session.add(group_message)
        db.session.commit()
        return group_message
    except Exception as e:
        db.session.rollback()
        print(f"Error sending group message: {e}")
        return None

def get_db():
    return current_app.extensions['sqlalchemy'].db

def get_group_messages(group_id):
    try:
        # Retrieve messages for a specific group
        return Message.query.filter_by(group_id=group_id).order_by(Message.created_at).all()
    except Exception as e:
        print(f"Error retrieving group messages: {type(e).__name__} - {str(e)}")
        return []


def get_user_groups(user_id):
    try:
        return Group.query.filter_by(created_by=user_id).order_by(Group.created_at.desc()).all()
    except Exception as e:
        print(f"Error retrieving user groups: {type(e).__name__} - {str(e)}")
        return []


def create_group(name, description, created_by):
    try:
        group = Group(name=name, description=description, created_by=created_by)
        db.session.add(group)
        db.session.commit()
        return group.id
    except Exception as e:
        print(f"Error creating group: {type(e).__name__} - {str(e)}")
        return None

# Add a get_post function to fetch a specific post
def get_post(post_id, user_id=None):
    try:
        post = Post.query.get(post_id)
        if not post:
            return None
            
        # Check visibility permissions
        if post.visibility == 'public':
            return post
        elif post.visibility == 'connections':
            connections = get_connections(user_id)
            friend_ids = [friend.id for friend in connections]
            if post.user_id in friend_ids or post.user_id == user_id:
                return post
        elif post.visibility == 'private':
            if post.user_id == user_id:
                return post
        return None
    except Exception as e:
        print(f"Error retrieving post: {type(e).__name__} - {str(e)}")
        return None

def like_post(post_id, user_id):
    post = Post.query.get(post_id)
    if not post:
        return False
    if not any(like.user_id == user_id for like in post.likes):
        new_like = PostLike(post_id=post_id, user_id=user_id)
        db.session.add(new_like)
        db.session.commit()
        return True
    return False

def unlike_post(post_id, user_id):
    post = Post.query.get(post_id)
    if not post:
        return False
    like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return True
    return False



def add_comment(post_id, user_id, content):
    try:
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return comment.id
    except Exception as e:
        print(f"Error adding comment: {type(e).__name__} - {str(e)}")
        return None


# Updated create_post function with image support while preserving existing functionality
def create_post(user_id, content, visibility='public', image_filename=None):
    try:
        # Validate visibility value
        if visibility not in ['public', 'connections', 'private']:
            visibility = 'public'  # Default to public if invalid
            
        post = Post(user_id=user_id, content=content, visibility=visibility, image_filename=image_filename)
        db.session.add(post)
        db.session.commit()
        return post.id  # Return the ID of the created post
    except Exception as e:
        print(f"Error creating post: {e}")
        db.session.rollback()
        return None


def get_messages(conversation_id):
    try:
        return Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
    except Exception as e:
        print(f"Error retrieving messages: {type(e).__name__} - {str(e)}")
        return []

def add_connection(user_id, friend_id):
    try:
        connection = Connection(user_id=user_id, friend_id=friend_id)
        db.session.add(connection)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding connection: {type(e).__name__} - {str(e)}")
        return False
    
def accept_connection(user_id, friend_id):
    try:
        connection = Connection.query.filter_by(user_id=friend_id, friend_id=user_id, status='pending').first()
        if connection:
            connection.status = 'accepted'
            connection.accepted_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error accepting connection: {type(e).__name__} - {str(e)}")
        return False
    


def get_connection(user_id, target_user_id):
    try:
        connection = Connection.query.filter(
            ((Connection.requester_id == user_id) & (Connection.recipient_id == target_user_id)) |
            ((Connection.requester_id == target_user_id) & (Connection.recipient_id == user_id))
        ).first()
        return connection
    except Exception as e:
        print(f"Error fetching connection: {type(e).__name__} - {str(e)}")
        return None



def get_connection_status(user_id, target_user_id):
    """
    Check the connection status between two users (user_id and target_user_id).
    Returns one of the following: 'not_connected', 'pending', 'request_received', 'connected'
    """
    try:
        connection = Connection.query.filter(
            ((Connection.requester_id == user_id) & (Connection.recipient_id == target_user_id)) |
            ((Connection.requester_id == target_user_id) & (Connection.recipient_id == user_id))
        ).first()

        if not connection:
            return 'not_connected'

        if connection.status == 'pending':
            if connection.requester_id == user_id:
                return 'pending'
            else:
                return 'request_received'
        
        if connection.status == 'accepted':
            return 'connected'

        return 'not_connected'  # Default if no status matches

    except Exception as e:
        print(f"Error checking connection status: {type(e).__name__} - {str(e)}")
        return 'not_connected'
    
def get_conversations(user_id):
    try:
        return Conversation.query.filter(
            (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
        ).order_by(Conversation.created_at.desc()).all()
    except Exception as e:
        print(f"Error retrieving conversations: {type(e).__name__} - {str(e)}")
        return []


def create_user(email, password, first_name, last_name, university, major):
    try:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists")
            return None

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            university=university,
            major=major
        )
        db.session.add(user)
        db.session.commit()
        print(f"User created successfully with ID: {user.id}")
        return user.id

    except Exception as e:
        print(f"Error creating user: {type(e).__name__} - {str(e)}")
        return None

def authenticate_user(email, password):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user found with email: {email}")
            return None
        if bcrypt.check_password_hash(user.password, password):
            return user
        else:
            print(f"Password verification failed for user: {email}")
            return None
    except Exception as e:
        print(f"Error authenticating user: {type(e).__name__} - {str(e)}")
        return None

def load_user(user_id):
    return User.query.get(int(user_id))

def update_user_profile(user_id, profile_data):
    user = User.query.get(int(user_id))
    if not user:
        return False
    for key, value in profile_data.items():
        setattr(user, key, value)
    db.session.commit()
    return True

def update_subscription(user_id, subscription_tier, end_date=None):
    user = User.query.get(int(user_id))
    if not user:
        return False
    user.subscription_tier = subscription_tier
    user.subscription_end_date = end_date
    db.session.commit()
    return True

def update_academic_progress(user_id, gpa, credits, current_courses):
    user = User.query.get(int(user_id))
    if not user:
        return False
    
    # Update GPA and credits
    user.gpa = gpa
    user.credits = credits
    
    # Update current courses (if needed)
    user.current_courses = current_courses
    
    db.session.commit()
    return True


def get_courses():
    return Course.query.all()

def get_jobs():
    return Job.query.all()

def add_job_application(user_id, company, position, status='Applied', interview_date=None):
    try:
        application = JobApplication(
            user_id=user_id,
            company=company,
            position=position,
            status=status,
            interview_date=interview_date
        )
        db.session.add(application)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding job application: {type(e).__name__} - {str(e)}")
        return False

def add_todo(user_id, title, due_date=None, priority='medium'):
    try:
        todo = Todo(
            user_id=user_id,
            title=title,
            due_date=due_date,
            priority=priority
        )
        db.session.add(todo)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding todo: {type(e).__name__} - {str(e)}")
        return False

def update_todo_status(user_id, todo_id, completed):
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return False
    todo.completed = completed
    db.session.commit()
    return True

def delete_todo(user_id, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return False
    db.session.delete(todo)
    db.session.commit()
    return True

def update_skill(user_id, skill_name, skill_type, level, percentage):
    skill = Skill.query.filter_by(user_id=user_id, name=skill_name, skill_type=skill_type).first()
    if not skill:
        skill = Skill(
            user_id=user_id,
            name=skill_name,
            skill_type=skill_type,
            level=level,
            percentage=percentage
        )
        db.session.add(skill)
    else:
        skill.level = level
        skill.percentage = percentage
    db.session.commit()
    return True

def create_conversation(user1_id, user2_id):
    try:
        existing = Conversation.query.filter(
            ((Conversation.user1_id == user1_id) & (Conversation.user2_id == user2_id)) |
            ((Conversation.user1_id == user2_id) & (Conversation.user2_id == user1_id))
        ).first()
        if not existing:
            convo = Conversation(user1_id=user1_id, user2_id=user2_id)
            db.session.add(convo)
            db.session.commit()
            return convo.id
        return existing.id
    except Exception as e:
        print(f"Error creating conversation: {type(e).__name__} - {str(e)}")
        return None

def get_connections(user_id):
    try:
        accepted = Connection.query.filter(
            ((Connection.requester_id == user_id) | (Connection.recipient_id == user_id)) &
            (Connection.status == 'accepted')
        ).all()

        connected_users = []
        for conn in accepted:
            if conn.requester_id == user_id:
                connected_users.append(User.query.get(conn.recipient_id))
            else:
                connected_users.append(User.query.get(conn.requester_id))
        return connected_users
    except Exception as e:
        print(f"Error fetching connections: {type(e).__name__} - {str(e)}")
        return []
    
# Fix the get_feed function to return posts, not achievements
def get_feed(user_id):
    try:
        # Get user's connections
        connections = get_connections(user_id)
        friend_ids = [friend.id for friend in connections]
        
        # Include user's own posts
        friend_ids.append(user_id)
        
        # Return posts from connections and the user's own posts
        # Filter by visibility (public or connections)
        return Post.query.filter(
            (Post.user_id.in_(friend_ids)) & 
            ((Post.visibility == 'public') | 
             (Post.visibility == 'connections') |
             ((Post.visibility == 'private') & (Post.user_id == user_id)))
        ).order_by(Post.created_at.desc())
    except Exception as e:
        print(f"Error retrieving feed: {type(e).__name__} - {str(e)}")
        return Post.query.filter(False)  # empty query fallback






def add_achievement(user_id, title, date):
    try:
        achievement = Achievement(
            user_id=user_id,
            title=title,
            date=date
        )
        db.session.add(achievement)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding achievement: {type(e).__name__} - {str(e)}")
        return False

def search_users(query):
    return User.query.filter(
        or_(
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
            User.university.ilike(f"%{query}%"),
            User.major.ilike(f"%{query}%")
        )
    ).limit(20).all()