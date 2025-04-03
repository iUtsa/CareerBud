from flask_login import UserMixin
from app import db, bcrypt
from datetime import datetime
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.email = user_data.get('email')
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.university = user_data.get('university')
        self.major = user_data.get('major')
        self.subscription_tier = user_data.get('subscription_tier', 'free')
        self.subscription_end_date = user_data.get('subscription_end_date')
        self.created_at = user_data.get('created_at')
        self.gpa = user_data.get('gpa', 0.0)
        self.credits = user_data.get('credits', 0)
        self.total_credits = user_data.get('total_credits', 120)
        self.skills = user_data.get('skills', {})
        self.achievements = user_data.get('achievements', [])
        self.internships = user_data.get('internships', [])
        self.job_applications = user_data.get('job_applications', [])
        self.current_courses = user_data.get('current_courses', [])
        self.todos = user_data.get('todos', [])
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_premium(self):
        if self.subscription_tier == 'premium':
            if self.subscription_end_date:
                return datetime.now() < self.subscription_end_date
        return False

# User registration
def create_user(email, password, first_name, last_name, university, major):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_data = {
        'email': email,
        'password': hashed_password,
        'first_name': first_name,
        'last_name': last_name,
        'university': university,
        'major': major,
        'subscription_tier': 'free',
        'created_at': datetime.now(),
        'gpa': 0.0,
        'credits': 0,
        'total_credits': 120,
        'skills': {
            'technical': {},
            'soft': {}
        },
        'achievements': [],
        'internships': [],
        'job_applications': [],
        'current_courses': [],
        'todos': []
    }
    
    result = db.users.insert_one(user_data)
    return str(result.inserted_id)

# User authentication
def authenticate_user(email, password):
    user_data = db.users.find_one({'email': email})
    if user_data and bcrypt.check_password_hash(user_data['password'], password):
        return User(user_data)
    return None

# User loader for Flask-Login
def load_user(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Update user profile
def update_user_profile(user_id, profile_data):
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': profile_data}
    )
    return result.modified_count > 0

# Update subscription tier
def update_subscription(user_id, subscription_tier, end_date=None):
    update_data = {'subscription_tier': subscription_tier}
    if end_date:
        update_data['subscription_end_date'] = end_date
        
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': update_data}
    )
    return result.modified_count > 0

# Get courses
def get_courses():
    return list(db.courses.find())

# Get jobs
def get_jobs():
    return list(db.jobs.find())

# Add job application
def add_job_application(user_id, company, position, status='Applied', interview_date=None):
    application = {
        'company': company,
        'position': position,
        'status': status,
        'applied_date': datetime.now()
    }
    
    if interview_date:
        application['interview_date'] = interview_date
        
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'job_applications': application}}
    )
    return result.modified_count > 0

# Update academic progress
def update_academic_progress(user_id, gpa, credits, courses):
    update_data = {
        'gpa': gpa,
        'credits': credits,
        'current_courses': courses
    }
    
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': update_data}
    )
    return result.modified_count > 0

# Add achievement
def add_achievement(user_id, title, date):
    achievement = {
        'title': title,
        'date': date
    }
    
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'achievements': achievement}}
    )
    return result.modified_count > 0

# Add or update skill
def update_skill(user_id, skill_name, skill_type, level, percentage):
    skill_path = f'skills.{skill_type}.{skill_name}'
    skill_data = {
        'level': level,
        'percentage': percentage
    }
    
    update_path = {skill_path: skill_data}
    
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': update_path}
    )
    return result.modified_count > 0

# Manage todo items
def add_todo(user_id, title, due_date=None, priority='medium'):
    todo = {
        'id': str(ObjectId()),
        'title': title,
        'completed': False,
        'created_at': datetime.now(),
        'priority': priority
    }
    
    if due_date:
        todo['due_date'] = due_date
        
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'todos': todo}}
    )
    return result.modified_count > 0

def update_todo_status(user_id, todo_id, completed):
    result = db.users.update_one(
        {'_id': ObjectId(user_id), 'todos.id': todo_id},
        {'$set': {'todos.$.completed': completed}}
    )
    return result.modified_count > 0

def delete_todo(user_id, todo_id):
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'todos': {'id': todo_id}}}
    )
    return result.modified_count > 0