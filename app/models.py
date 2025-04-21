from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy import Column, Integer, String, Text, Boolean
from app import db  # Ensure this is at the top of your models.py
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db, bcrypt
from typing import Optional, Dict, Union
import re










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

class PostLike(db.Model):
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship('Post', backref='likes')
    user = db.relationship('User', backref='post_likes')


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

# Add these models to your models.py file

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    template = db.Column(db.String(50), default='modern')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_primary = db.Column(db.Boolean, default=False)
    
    # Resume metadata
    objective = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    
    # Color and style preferences
    primary_color = db.Column(db.String(20), default='#4ade80')
    secondary_color = db.Column(db.String(20), default='#60a5fa')
    font_family = db.Column(db.String(50), default='Roboto')
    
    # Score and analytics
    ats_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='resumes')
    resume_sections = db.relationship('ResumeSection', back_populates='resume', cascade='all, delete-orphan')
    resume_skills = db.relationship('ResumeSkill', back_populates='resume', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Resume {self.title}>'


class ResumeSection(db.Model):
    __tablename__ = 'resume_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'education', 'experience', 'project', etc.
    title = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    
    # Relationships
    resume = db.relationship('Resume', back_populates='resume_sections')
    bullets = db.relationship('ResumeBullet', back_populates='section', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ResumeSection {self.type}: {self.title}>'


class ResumeBullet(db.Model):
    __tablename__ = 'resume_bullets'
    
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('resume_sections.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    impact_score = db.Column(db.Float, default=0.0)  # AI score for impact
    
    # Relationships
    section = db.relationship('ResumeSection', back_populates='bullets')
    
    def __repr__(self):
        return f'<ResumeBullet {self.id}>'


class ResumeSkill(db.Model):
    __tablename__ = 'resume_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)  # 'Technical', 'Soft Skills', etc.
    proficiency = db.Column(db.Integer, default=0)  # 1-5 scale
    order = db.Column(db.Integer, default=0)
    
    # Relationships
    resume = db.relationship('Resume', back_populates='resume_skills')
    
    def __repr__(self):
        return f'<ResumeSkill {self.skill_name}>'


# Add these functions to work with resume data

def create_resume(user_id, title, template='modern'):
    try:
        # Check if this is the first resume for the user
        is_first = not Resume.query.filter_by(user_id=user_id).first()
        
        resume = Resume(
            user_id=user_id,
            title=title,
            template=template,
            is_primary=is_first  # First resume is primary by default
        )
        db.session.add(resume)
        db.session.commit()
        return resume.id
    except Exception as e:
        print(f"Error creating resume: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return None


def get_user_resumes(user_id):
    try:
        return Resume.query.filter_by(user_id=user_id).order_by(Resume.updated_at.desc()).all()
    except Exception as e:
        print(f"Error retrieving resumes: {type(e).__name__} - {str(e)}")
        return []


def get_resume(resume_id, user_id=None):
    """
    Get a resume by ID. If user_id is provided, ensure the resume belongs to that user.
    """
    query = Resume.query.filter_by(id=resume_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    return query.first()


def update_resume(resume_id, user_id, resume_data):
    """
    Update a resume with the provided data
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return False
            
        # Update basic resume fields
        for key, value in resume_data.items():
            if hasattr(resume, key):
                setattr(resume, key, value)
        
        resume.updated_at = datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating resume: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return False


def delete_resume(resume_id, user_id):
    """
    Delete a resume
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return False
            
        db.session.delete(resume)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error deleting resume: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return False


def add_resume_section(resume_id, user_id, section_data):
    """
    Add a section to a resume
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return None
            
        # Get the highest order and add 1
        max_order = db.session.query(db.func.max(ResumeSection.order)).filter_by(resume_id=resume_id).scalar() or 0
        
        section = ResumeSection(
            resume_id=resume_id,
            type=section_data.get('type'),
            title=section_data.get('title'),
            organization=section_data.get('organization'),
            location=section_data.get('location'),
            start_date=section_data.get('start_date'),
            end_date=section_data.get('end_date'),
            is_current=section_data.get('is_current', False),
            description=section_data.get('description'),
            order=max_order + 1
        )
        db.session.add(section)
        db.session.commit()
        
        # Add bullets if provided
        bullets = section_data.get('bullets', [])
        for idx, bullet_content in enumerate(bullets):
            bullet = ResumeBullet(
                section_id=section.id,
                content=bullet_content,
                order=idx
            )
            db.session.add(bullet)
        
        db.session.commit()
        return section.id
    except Exception as e:
        print(f"Error adding resume section: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return None


def add_resume_skill(resume_id, user_id, skill_data):
    """
    Add a skill to a resume
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return None
            
        # Get the highest order and add 1
        max_order = db.session.query(db.func.max(ResumeSkill.order)).filter_by(resume_id=resume_id).scalar() or 0
        
        skill = ResumeSkill(
            resume_id=resume_id,
            skill_name=skill_data.get('skill_name'),
            category=skill_data.get('category'),
            proficiency=skill_data.get('proficiency', 3),
            order=max_order + 1
        )
        db.session.add(skill)
        db.session.commit()
        return skill.id
    except Exception as e:
        print(f"Error adding resume skill: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return None


def generate_resume_summary(resume_id, user_id):
    """
    Generate an AI-powered summary for a resume
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return False
            
        # Get user data
        user = User.query.get(user_id)
        
        # Get sections for this resume
        experience_sections = ResumeSection.query.filter_by(
            resume_id=resume_id, 
            type='experience'
        ).order_by(ResumeSection.order).all()
        
        education_sections = ResumeSection.query.filter_by(
            resume_id=resume_id, 
            type='education'
        ).order_by(ResumeSection.order).all()
        
        skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()
        
        # Build context for summary generation
        context = {
            'name': f"{user.first_name} {user.last_name}",
            'major': user.major,
            'university': user.university,
            'experience': [
                {
                    'title': section.title,
                    'organization': section.organization,
                    'bullets': [bullet.content for bullet in section.bullets]
                } for section in experience_sections
            ],
            'education': [
                {
                    'degree': section.title,
                    'school': section.organization,
                } for section in education_sections
            ],
            'skills': [skill.skill_name for skill in skills]
        }
        
        # This is where you would integrate with an AI service to generate the summary
        # For now, we'll create a simple placeholder summary based on the context
        summary = f"Dedicated {context['major']} student at {context['university']} with experience in "
        
        if context['experience']:
            summary += f"{context['experience'][0]['title']} at {context['experience'][0]['organization']}. "
        else:
            summary += "various projects and coursework. "
            
        if context['skills']:
            skills_str = ", ".join(context['skills'][:3])
            summary += f"Skilled in {skills_str} and more."
        
        resume.summary = summary
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Error generating resume summary: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return False




def analyze_resume_ats(resume_id: int, user_id: int, job_description: Optional[str] = None) -> Optional[Dict[str, Union[int, str]]]:
    """
    Analyze a resume against ATS criteria with optional job description for keyword matching.
    
    Parameters:
    - resume_id: Resume ID to analyze
    - user_id: ID of the user who owns the resume
    - job_description: Optional job description to compare against resume skills
    
    Returns:
    - dict with score and feedback, or None if error
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return None

        # Fetch associated resume data
        sections = ResumeSection.query.filter_by(resume_id=resume_id).all()
        skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()

        # Criteria checks
        has_experience = any(section.type == 'experience' for section in sections)
        has_education = any(section.type == 'education' for section in sections)
        has_skills = len(skills) > 0
        bullet_count = sum(len(section.bullets) for section in sections)
        has_enough_bullets = bullet_count >= 5

        # Basic scoring breakdown (max 70)
        base_score = 0
        if has_experience:
            base_score += 25
        if has_education:
            base_score += 20
        if has_skills:
            base_score += 15
        if has_enough_bullets:
            base_score += 10  # slightly lower to make room for advanced scoring

        feedback = []

        # Job match scoring (max 25)
        job_match_score = 0
        if job_description:
            job_description = job_description.lower()
            matched_skills = sum(1 for skill in skills if skill.skill_name.lower() in job_description)

            if skills:
                match_ratio = matched_skills / len(skills)
                job_match_score = min(25, match_ratio * 25)

                if match_ratio < 0.3:
                    feedback.append("Your skills don't strongly match the job description. Add more relevant keywords.")
            else:
                feedback.append("Your resume is missing technical or soft skills.")

        # General feedback
        if not has_experience:
            feedback.append("Add work experience to make your resume stronger.")
        if not has_education:
            feedback.append("Include your educational qualifications.")
        if not has_skills:
            feedback.append("Add technical and soft skills to strengthen your resume.")
        if bullet_count < 5:
            feedback.append("Use bullet points to describe your responsibilities and achievements.")

        # Final score (max 95%)
        total_score = base_score + job_match_score
        final_score = round(min(95, total_score * 0.97))  # Apply slight deduction for realism

        resume.ats_score = final_score
        resume.feedback = "\n".join(feedback) if feedback else "Your resume is well-balanced and ATS-friendly."
        db.session.commit()

        return {
            'score': final_score,
            'feedback': resume.feedback
        }

    except Exception as e:
        print(f"[ATS Analyzer Error] {type(e).__name__}: {e}")
        db.session.rollback()
        return None



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

    existing_like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    if not existing_like:
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


# Add this function to your models.py file

def delete_post(post_id, user_id):
    """
    Delete a post if the user is the owner
    
    Args:
        post_id: The ID of the post to delete
        user_id: The ID of the user trying to delete the post
        
    Returns:
        bool: True if post was deleted, False otherwise
    """
    try:
        post = Post.query.get(post_id)
        
        # Check if post exists and user is the owner
        if not post or post.user_id != user_id:
            return False
            
        # Delete all likes associated with the post
        PostLike.query.filter_by(post_id=post_id).delete()
        
        # Delete all comments associated with the post
        Comment.query.filter_by(post_id=post_id).delete()
        
        # Delete the post itself
        db.session.delete(post)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error deleting post: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return False
    
def advanced_ats_analyzer(resume_id, user_id, job_description=None, industry=None, company_size=None):
    print("[DEBUG] Advanced analyzer called with:")
    print("resume_id:", resume_id)
    print("user_id:", user_id)
    print("job_description:", job_description)
    print("industry:", industry)
    print("company_size:", company_size)

    """
    Advanced ATS Resume Analysis Algorithm
    
    Analyzes resumes using sophisticated techniques similar to those used by modern ATS systems 
    in enterprise hiring processes.
    
    Parameters:
    - resume_id: ID of the resume to analyze
    - user_id: ID of the user who owns the resume
    - job_description: Optional job description text for targeted analysis
    - industry: Optional industry context (e.g., "tech", "finance", "healthcare")
    - company_size: Optional company size context ("startup", "mid-size", "enterprise")
    
    Returns:
    - Dictionary with analysis results and recommendations
    """
    try:
        # Get resume and its components
        resume = get_resume(resume_id, user_id)
        if not resume:
            return None
            
        sections = ResumeSection.query.filter_by(resume_id=resume_id).all()
        skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()
        user = User.query.get(user_id)
        
        # Initialize analysis metrics
        metrics = {
            # Core metrics
            'format_score': 0,
            'content_score': 0,
            'keyword_score': 0,
            'impact_score': 0,
            'readability_score': 0,
            
            # Section-specific metrics
            'contact_score': 0,
            'summary_score': 0,
            'experience_score': 0,
            'education_score': 0,
            'skills_score': 0,
            'projects_score': 0,
            
            # Additional metrics
            'relevance_score': 0 if job_description else None,
            'achievement_focus': 0,
            'action_verb_usage': 0,
            'quantification_score': 0,
            'technical_match': 0,
            'soft_skills_match': 0,
            
            # Completeness metrics
            'section_completeness': 0,
            'detail_level': 0,
            
            # Red flags
            'red_flags': [],
            
            # Keywords
            'extracted_keywords': [],
            'found_keywords': [],
            'missing_keywords': [],
            'industry_keywords': [],
            
            # Feedback
            'overall_feedback': [],
            'section_feedback': {},
            'improvement_suggestions': [],
            'ats_optimization_tips': []
        }
        
        # 1. FORMAT ANALYSIS
        formats = analyze_resume_format(resume, sections)
        metrics['format_score'] = formats['score']
        metrics['section_completeness'] = formats['completeness']
        metrics['red_flags'].extend(formats['red_flags'])
        
        # 2. CONTACT INFORMATION ANALYSIS
        contact_analysis = analyze_contact_info(user, resume)
        metrics['contact_score'] = contact_analysis['score']
        metrics['section_feedback']['contact'] = contact_analysis['feedback']
        
        # 3. SKILLS ANALYSIS
        skills_analysis = analyze_skills(skills, job_description, industry)
        metrics['skills_score'] = skills_analysis['score']
        metrics['technical_match'] = skills_analysis['technical_match']
        metrics['soft_skills_match'] = skills_analysis['soft_skills_match']
        metrics['section_feedback']['skills'] = skills_analysis['feedback']
        
        # 4. EXPERIENCE ANALYSIS
        experience_sections = [s for s in sections if s.type == 'experience']
        exp_analysis = analyze_experience(experience_sections, job_description)
        metrics['experience_score'] = exp_analysis['score']
        metrics['action_verb_usage'] = exp_analysis['action_verb_usage']
        metrics['quantification_score'] = exp_analysis['quantification']
        metrics['achievement_focus'] = exp_analysis['achievement_focus']
        metrics['section_feedback']['experience'] = exp_analysis['feedback']
        
        # 5. EDUCATION ANALYSIS
        education_sections = [s for s in sections if s.type == 'education']
        edu_analysis = analyze_education(education_sections, job_description)
        metrics['education_score'] = edu_analysis['score']
        metrics['section_feedback']['education'] = edu_analysis['feedback']
        
        # 6. KEYWORD ANALYSIS
        if job_description:
            keyword_analysis = analyze_keywords(resume, sections, skills, job_description, industry)
            metrics['keyword_score'] = keyword_analysis['score']
            metrics['extracted_keywords'] = keyword_analysis['extracted_keywords']
            metrics['found_keywords'] = keyword_analysis['found_keywords']
            metrics['missing_keywords'] = keyword_analysis['missing_keywords']
            metrics['industry_keywords'] = keyword_analysis['industry_keywords']
            metrics['relevance_score'] = keyword_analysis['relevance']
        
        # 7. CONTENT & IMPACT ANALYSIS
        content_analysis = analyze_content_quality(resume, sections)
        metrics['content_score'] = content_analysis['score']
        metrics['impact_score'] = content_analysis['impact']
        metrics['readability_score'] = content_analysis['readability']
        metrics['detail_level'] = content_analysis['detail_level']
        
        # 8. PROJECTS ANALYSIS
        project_sections = [s for s in sections if s.type == 'project']
        if project_sections:
            proj_analysis = analyze_projects(project_sections, job_description)
            metrics['projects_score'] = proj_analysis['score']
            metrics['section_feedback']['projects'] = proj_analysis['feedback']
        
        # 9. SUMMARY/OBJECTIVE ANALYSIS
        if resume.objective:
            summary_analysis = analyze_summary(resume.objective, job_description)
            metrics['summary_score'] = summary_analysis['score']
            metrics['section_feedback']['summary'] = summary_analysis['feedback']
        
        # 10. CALCULATE OVERALL SCORE
        weights = calculate_industry_weights(industry, company_size, job_description is not None)
        overall_score = calculate_weighted_score(metrics, weights)
        
        # 11. GENERATE FEEDBACK & RECOMMENDATIONS
        feedback = generate_comprehensive_feedback(metrics, overall_score)
        metrics['overall_feedback'] = feedback['overall']
        metrics['improvement_suggestions'] = feedback['improvements']
        metrics['ats_optimization_tips'] = feedback['ats_tips']
        
        # 12. UPDATE RESUME WITH ANALYSIS RESULTS
        resume.ats_score = overall_score
        resume.feedback = "\n".join(metrics['overall_feedback'])
        db.session.commit()
        
        # 13. RETURN COMPLETE ANALYSIS
        return {
            'score': overall_score,
            'metrics': metrics,
            'feedback': resume.feedback
        }
        
    except Exception as e:
        print(f"Error in advanced ATS analysis: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return None
    
def analyze_resume_format(resume, sections):
    """Analyzes resume format and structure"""
    score = 75  # Base score
    red_flags = []
    completeness = 0
    
    # Check for essential sections
    required_sections = {
        'contact': False,  # Assumed to be in user profile
        'experience': False,
        'education': False,
        'skills': False
    }
    
    # Verify section presence
    for section in sections:
        if section.type in required_sections:
            required_sections[section.type] = True
    
    # Calculate completeness
    completeness = sum(1 for present in required_sections.values() if present) / len(required_sections) * 100
    
    # Check for red flags
    if not required_sections['experience']:
        red_flags.append("Missing experience section")
        score -= 15
    
    if not required_sections['education']:
        red_flags.append("Missing education section")
        score -= 10
    
    if not required_sections['skills']:
        red_flags.append("Missing skills section")
        score -= 10
        
    # Check section order (preferred order)
    current_order = [s.type for s in sorted(sections, key=lambda x: x.order)]
    preferred_order = ['experience', 'education', 'skills', 'project']
    
    # Calculate order correctness (partial match algorithm)
    order_score = 0
    if current_order:
        for i, section_type in enumerate(preferred_order):
            if section_type in current_order:
                position_diff = abs(i - current_order.index(section_type))
                order_score += max(0, 5 - position_diff)
        order_score = min(20, order_score)
        score += order_score
    
    return {
        'score': min(100, max(0, score)),
        'completeness': completeness,
        'red_flags': red_flags
    }

def analyze_contact_info(user, resume):
    """Analyzes contact information completeness"""
    score = 0
    feedback = []
    
    # Check for essential contact fields
    if user.first_name and user.last_name:
        score += 25
    else:
        feedback.append("Add your full name to your profile")
    
    if user.email:
        score += 25
    else:
        feedback.append("Add your email address to your profile")
    
    # Check for phone number (assumed to be in user profile)
    # This would need to be adjusted based on your actual user model
    has_phone = True  # Placeholder - replace with actual check
    if has_phone:
        score += 20
    else:
        feedback.append("Add your phone number to improve contact information")
    
    # Check for LinkedIn or other professional profiles
    # This would need to be adjusted based on your actual user model
    has_linkedin = False  # Placeholder - replace with actual check
    if has_linkedin:
        score += 15
    else:
        feedback.append("Add your LinkedIn profile URL for better networking opportunities")
    
    # Check for location information
    has_location = True  # Placeholder - replace with actual check
    if has_location:
        score += 15
    else:
        feedback.append("Add your location to your profile")
    
    if not feedback:
        feedback.append("Contact information is complete and well-structured")
        
    return {
        'score': score,
        'feedback': feedback
    }

def analyze_skills(skills, job_description=None, industry=None):
    """Analyzes skills relevance and presentation"""
    score = 70  # Base score
    feedback = []
    
    # Category distribution analysis
    categories = {}
    for skill in skills:
        category = skill.category or "Other"
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    # Check skill count
    skill_count = len(skills)
    if skill_count < 5:
        score -= 20
        feedback.append("Add more skills to your resume (aim for 10-15 relevant skills)")
    elif skill_count > 20:
        score -= 10
        feedback.append("Consider focusing on your most relevant skills (10-15 is ideal)")
    
    # Calculate technical vs soft skills ratio
    technical_count = sum(1 for skill in skills if skill.category in ['technical', 'tools', 'programming'])
    soft_count = sum(1 for skill in skills if skill.category in ['soft', 'interpersonal'])
    
    technical_percentage = (technical_count / skill_count * 100) if skill_count > 0 else 0
    soft_percentage = (soft_count / skill_count * 100) if skill_count > 0 else 0
    
    # Job description matching (if provided)
    matching_score = 0
    if job_description:
        matches = 0
        for skill in skills:
            if skill.skill_name.lower() in job_description.lower():
                matches += 1
        
        matching_percentage = (matches / skill_count * 100) if skill_count > 0 else 0
        matching_score = min(30, matching_percentage * 0.3)
        
        if matching_percentage < 30:
            feedback.append("Your skills don't strongly match the job description requirements")
        elif matching_percentage > 70:
            feedback.append("Excellent skills match with the job description")
    
    # Industry-specific skill analysis
    industry_match = 0
    if industry:
        industry_skills = get_industry_skills(industry)
        industry_matches = sum(1 for skill in skills if skill.skill_name.lower() in industry_skills)
        
        if industry_matches > 0:
            industry_match = min(20, (industry_matches / len(industry_skills)) * 100 * 0.2)
            
            if industry_match < 10:
                feedback.append(f"Add more {industry}-specific skills to your resume")
            else:
                feedback.append(f"Good inclusion of {industry}-specific skills")
    
    # Calculate final score
    score += matching_score + industry_match
    
    # Balance feedback
    if not feedback:
        if technical_percentage > 80:
            feedback.append("Consider adding more soft skills to balance your technical expertise")
        elif soft_percentage > 80:
            feedback.append("Consider adding more technical skills to balance your soft skills")
        else:
            feedback.append("Well-balanced mix of skills presented")
    
    return {
        'score': min(100, max(0, score)),
        'technical_match': technical_percentage,
        'soft_skills_match': soft_percentage,
        'feedback': feedback
    }

def analyze_experience(experience_sections, job_description=None):
    """Analyzes work experience sections"""
    if not experience_sections:
        return {
            'score': 0,
            'action_verb_usage': 0,
            'quantification': 0,
            'achievement_focus': 0,
            'feedback': ["Add work experience to your resume"]
        }
    
    score = 70  # Base score
    feedback = []
    action_verb_count = 0
    quantified_count = 0
    achievement_count = 0
    bullet_count = 0
    
    # Action verbs dictionary
    action_verbs = [
        'achieved', 'improved', 'trained', 'managed', 'created', 'resolved',
        'developed', 'designed', 'implemented', 'launched', 'increased',
        'decreased', 'reduced', 'negotiated', 'coordinated', 'led', 
        'supervised', 'directed', 'established', 'streamlined', 'generated',
        'delivered', 'produced', 'researched', 'analyzed', 'evaluated',
        'organized', 'maintained', 'prepared', 'provided', 'presented'
    ]
    
    # Analyze each section and its bullets
    for section in experience_sections:
        # Check for date completeness
        if not section.start_date:
            feedback.append(f"Add start date to your {section.title} position")
            score -= 5
        
        if not section.is_current and not section.end_date:
            feedback.append(f"Add end date to your {section.title} position")
            score -= 5
            
        # Check bullet quality
        if not section.bullets:
            feedback.append(f"Add bullet points to your {section.title} position")
            score -= 10
            continue
            
        for bullet in section.bullets:
            bullet_count += 1
            content = bullet.content.lower()
            
            # Check for action verbs
            has_action_verb = any(verb in content.split() for verb in action_verbs)
            if has_action_verb:
                action_verb_count += 1
            
            # Check for quantification
            has_quantification = any(char.isdigit() for char in content) or \
                                any(word in content for word in ['percent', '%', 'million', 'thousand', 'hundred'])
            if has_quantification:
                quantified_count += 1
                
            # Check for achievement focus (vs responsibility focus)
            achievement_indicators = ['improved', 'increased', 'reduced', 'saved', 'achieved', 
                                     'awarded', 'recognized', 'exceeded', 'generated']
            has_achievement = any(indicator in content for indicator in achievement_indicators)
            if has_achievement:
                achievement_count += 1
    
    # Calculate metrics
    if bullet_count > 0:
        action_verb_usage = (action_verb_count / bullet_count) * 100
        quantification = (quantified_count / bullet_count) * 100
        achievement_focus = (achievement_count / bullet_count) * 100
        
        # Score adjustments based on metrics
        if action_verb_usage < 50:
            score -= 10
            feedback.append("Use more action verbs to start your bullet points")
        
        if quantification < 30:
            score -= 10
            feedback.append("Add more measurable achievements with numbers and percentages")
            
        if achievement_focus < 40:
            score -= 5
            feedback.append("Focus more on achievements rather than responsibilities")
    else:
        action_verb_usage = 0
        quantification = 0
        achievement_focus = 0
    
    # Experience chronology check
    if len(experience_sections) > 1:
        is_chronological = is_experience_chronological(experience_sections)
        if not is_chronological:
            feedback.append("Ensure your experience is in reverse chronological order (most recent first)")
            score -= 5
    
    # Job description matching (if provided)
    if job_description:
        relevance_score = calculate_experience_relevance(experience_sections, job_description)
        score += relevance_score
        
        if relevance_score < 10:
            feedback.append("Your experience doesn't strongly align with the job requirements")
        elif relevance_score > 25:
            feedback.append("Your experience aligns well with the job requirements")
    
    # Final feedback
    if not feedback:
        feedback.append("Strong experience section with good bullet points")
    
    return {
        'score': min(100, max(0, score)),
        'action_verb_usage': action_verb_usage,
        'quantification': quantification,
        'achievement_focus': achievement_focus,
        'feedback': feedback
    }

def analyze_education(education_sections, job_description=None):
    """Analyzes education sections"""
    if not education_sections:
        return {
            'score': 0,
            'feedback': ["Add education to your resume"]
        }
        
    score = 80  # Base score
    feedback = []
    
    # Analyze each education section
    for section in education_sections:
        # Check for degree title
        if not section.title or len(section.title.strip()) < 5:
            feedback.append(f"Add your degree title/major for {section.organization}")
            score -= 10
            
        # Check for institution name
        if not section.organization or len(section.organization.strip()) < 2:
            feedback.append("Add the name of your educational institution")
            score -= 10
            
        # Check for dates
        if not section.start_date:
            feedback.append(f"Add start date to your education at {section.organization}")
            score -= 5
            
        if not section.is_current and not section.end_date:
            feedback.append(f"Add graduation/end date for {section.organization}")
            score -= 5
            
        # Check for location
        if not section.location:
            feedback.append(f"Add location for {section.organization}")
            score -= 3
            
        # Check for GPA or honors (in description or bullets)
        has_gpa = False
        has_honors = False
        
        if section.description:
            has_gpa = 'gpa' in section.description.lower() or 'grade point average' in section.description.lower()
            has_honors = any(term in section.description.lower() for term in 
                           ['honors', 'distinction', 'cum laude', 'magna cum laude', 'summa cum laude'])
        
        for bullet in section.bullets:
            if 'gpa' in bullet.content.lower() or 'grade point average' in bullet.content.lower():
                has_gpa = True
            if any(term in bullet.content.lower() for term in 
                 ['honors', 'distinction', 'cum laude', 'magna cum laude', 'summa cum laude']):
                has_honors = True
                
        if not has_gpa:
            feedback.append(f"Consider adding your GPA for {section.organization} if it's 3.0 or higher")
            
        if not has_honors and not has_gpa:
            feedback.append(f"Consider adding academic achievements or honors for {section.organization}")
    
    # Job description matching (if provided)
    if job_description:
        # Check if education level matches job requirements
        degree_levels = {
            'bachelor': 0,
            'master': 0,
            'phd': 0,
            'doctorate': 0,
            'mba': 0
        }
        
        for section in education_sections:
            for level in degree_levels:
                if level in section.title.lower():
                    degree_levels[level] += 1
                    
        required_levels = []
        for level in degree_levels:
            if level in job_description.lower():
                required_levels.append(level)
                
        if required_levels:
            has_required = any(degree_levels[level] > 0 for level in required_levels)
            if not has_required:
                required_str = ', '.join(required_levels)
                feedback.append(f"Job requires {required_str.title()} degree which doesn't appear in your education")
                score -= 15
    
    # Final feedback
    if not feedback:
        feedback.append("Strong education section with good details")
    
    return {
        'score': min(100, max(0, score)),
        'feedback': feedback
    }

def analyze_summary(summary_text, job_description=None):
    """Analyzes resume summary/objective section"""
    score = 75  # Base score
    feedback = []
    
    # Check length
    word_count = len(summary_text.split())
    if word_count < 30:
        score -= 10
        feedback.append("Your summary is too brief. Aim for 3-5 sentences that highlight your value proposition")
    elif word_count > 100:
        score -= 5
        feedback.append("Your summary is too lengthy. Keep it concise at 3-5 sentences")
        
    # Check for clichés
    cliches = ["results-driven", "team player", "detail-oriented", "self-starter",
               "think outside the box", "go-getter", "hard worker", "win-win",
               "proactive", "synergy", "goal-oriented"]
    
    cliche_count = sum(1 for cliche in cliches if cliche in summary_text.lower())
    if cliche_count > 2:
        score -= 10
        feedback.append("Replace generic phrases with specific achievements and skills")
        
    # Check for first-person pronouns
    first_person = ["i", "me", "my", "mine"]
    uses_first_person = any(pronoun in summary_text.lower().split() for pronoun in first_person)
    
    if uses_first_person:
        score -= 5
        feedback.append("Avoid using first-person pronouns (I, me, my) in your professional summary")
        
    # Check job description alignment
    if job_description:
        summary_lower = summary_text.lower()
        job_lower = job_description.lower()
        
        # Extract potential job title
        job_titles = extract_job_titles(job_description)
        has_job_title = any(title in summary_lower for title in job_titles)
        
        # Calculate keyword matching
        keywords = extract_keywords_from_job_description(job_description, 10)
        matches = sum(1 for keyword in keywords if keyword in summary_lower)
        
        relevance_score = min(25, matches * 5)
        if not has_job_title:
            relevance_score = max(0, relevance_score - 10)
            
        score += relevance_score
        
        if relevance_score < 10:
            feedback.append("Your summary doesn't align well with the target position")
        elif relevance_score > 20:
            feedback.append("Excellent alignment between your summary and the job requirements")
    
    # Final feedback
    if not feedback:
        feedback.append("Effective summary that highlights your value proposition")
        
    return {
        'score': min(100, max(0, score)),
        'feedback': feedback
    }

def analyze_keywords(resume, sections, skills, job_description, industry=None):
    """Analyzes keyword presence and relevance"""
    # Extract keywords from job description
    extracted_keywords = extract_keywords_from_job_description(job_description, 20)
    
    # Get industry-specific keywords
    industry_keywords = []
    if industry:
        industry_keywords = get_industry_keywords(industry)
        
    # Combine with industry keywords but keep track separately
    all_keywords = list(set(extracted_keywords + industry_keywords))
    
    # Search for keywords in resume
    found_keywords = []
    skill_keywords = [skill.skill_name.lower() for skill in skills]
    
    # Create a single text corpus from resume sections
    resume_text = ''
    if resume.objective:
        resume_text += resume.objective + ' '
        
    for section in sections:
        if section.title:
            resume_text += section.title + ' '
        if section.organization:
            resume_text += section.organization + ' '
        if section.description:
            resume_text += section.description + ' '
            
        for bullet in section.bullets:
            resume_text += bullet.content + ' '
            
    resume_text = resume_text.lower()
    
    # Check for keyword matches
    for keyword in all_keywords:
        # Check exact match
        if keyword.lower() in resume_text or keyword.lower() in skill_keywords:
            found_keywords.append(keyword)
            continue
            
        # Check for variations (plurals, verb forms)
        variations = get_keyword_variations(keyword)
        for variation in variations:
            if variation in resume_text or variation in skill_keywords:
                found_keywords.append(keyword)
                break
    
    # Calculate metrics
    found_count = len(found_keywords)
    missing_keywords = [k for k in extracted_keywords if k not in found_keywords]
    
    keyword_score = min(100, (found_count / len(all_keywords) * 100)) if all_keywords else 0
    relevance_score = min(100, (len([k for k in found_keywords if k in extracted_keywords]) / 
                        len(extracted_keywords) * 100)) if extracted_keywords else 0
    
    return {
        'score': keyword_score,
        'relevance': relevance_score,
        'extracted_keywords': extracted_keywords,
        'found_keywords': found_keywords,
        'missing_keywords': missing_keywords,
        'industry_keywords': industry_keywords
    }

def analyze_content_quality(resume, sections):
    """Analyzes overall content quality, impact and readability"""
    score = 70  # Base score
    bullet_texts = []
    
    # Get all bullet points
    for section in sections:
        for bullet in section.bullets:
            bullet_texts.append(bullet.content)
    
    # No bullets, no detailed analysis
    if not bullet_texts:
        return {
            'score': 50,
            'impact': 30,
            'readability': 60,
            'detail_level': 20
        }
    
    # Impact analysis
    impact_words = ['increased', 'decreased', 'improved', 'reduced', 'generated',
                   'achieved', 'delivered', 'led', 'managed', 'created',
                   'developed', 'designed', 'implemented', 'launched']
    
    impact_count = 0
    for bullet in bullet_texts:
        if any(word in bullet.lower() for word in impact_words):
            impact_count += 1
            
    impact_score = (impact_count / len(bullet_texts)) * 100
    
    # Readability analysis
    avg_words_per_bullet = sum(len(bullet.split()) for bullet in bullet_texts) / len(bullet_texts)
    
    readability_score = 100
    if avg_words_per_bullet < 6:
        readability_score -= 30  # Too short
    elif avg_words_per_bullet > 20:
        readability_score -= 20  # Too long
        
    # Detail level analysis
    detail_score = 0
    quantified_bullets = 0
    specificity_words = 0
    
    for bullet in bullet_texts:
        words = bullet.split()
        
        # Check for numbers (quantification)
        if any(bool(re.search(r'\d', word)) for word in words):
            quantified_bullets += 1
            
        # Check for specific technical terms
        specificity_words += sum(1 for word in words if len(word) > 8)
    
    if bullet_texts:
        quantified_ratio = quantified_bullets / len(bullet_texts)
        specificity_ratio = specificity_words / len(bullet_texts)
        
        detail_score = (quantified_ratio * 50) + (specificity_ratio * 10)
        detail_score = min(100, detail_score)
    
    # Final score adjustments
    content_score = score + (impact_score * 0.3) - abs(readability_score - 80) * 0.1
    
    return {
        'score': min(100, max(0, content_score)),
        'impact': impact_score,
        'readability': readability_score,
        'detail_level': detail_score
    }

def analyze_projects(project_sections, job_description=None):
    """Analyzes project sections (continued)"""
    if not project_sections:
        return {
            'score': 0,
            'feedback': ["Consider adding relevant projects to showcase your skills"]
        }
        
    score = 75  # Base score
    feedback = []
    
    # Job description relevance (if provided)
    if job_description:
        # Check if projects align with job requirements
        relevance_count = 0
        for section in project_sections:
            project_text = section.title + ' ' + (section.description or '')
            for bullet in section.bullets:
                project_text += ' ' + bullet.content
                
            project_text = project_text.lower()
            job_desc_lower = job_description.lower()
            
            # Extract key requirements from job description
            requirements = extract_requirements_from_job(job_description)
            matches = sum(1 for req in requirements if req in project_text)
            
            if matches >= 2:  # If at least 2 requirements match
                relevance_count += 1
                
        # Calculate relevance percentage
        relevance_percentage = (relevance_count / len(project_sections)) * 100 if project_sections else 0
        
        if relevance_percentage < 50:
            feedback.append("Your projects don't strongly align with the job requirements")
            score -= 10
        elif relevance_percentage > 80:
            feedback.append("Excellent alignment between your projects and the job requirements")
            score += 10
    
    # Final feedback
    if not feedback:
        feedback.append("Strong project section that effectively showcases your skills")
        
    return {
        'score': min(100, max(0, score)),
        'feedback': feedback
    }
def is_experience_chronological(experience_sections):
    """Checks if experience is in reverse chronological order"""
    dated_sections = []
    
    for section in experience_sections:
        if section.start_date:
            dated_sections.append((section, section.start_date))
            
    if len(dated_sections) <= 1:
        return True
        
    dated_sections.sort(key=lambda x: x[1], reverse=True)
    original_order = [section for section, _ in dated_sections]
    sorted_order = [section for section, _ in sorted(dated_sections, key=lambda x: x[1], reverse=True)]
    
    return original_order == sorted_order

def calculate_experience_relevance(experience_sections, job_description):
    """Calculates how relevant the experience is to the job description"""
    if not experience_sections or not job_description:
        return 0
        
    # Extract key requirements from job description
    requirements = extract_requirements_from_job(job_description)
    if not requirements:
        return 0
        
    # Create a text corpus from all experience sections
    experience_text = ""
    for section in experience_sections:
        if section.title:
            experience_text += section.title + " "
        if section.organization:
            experience_text += section.organization + " "
        if section.description:
            experience_text += section.description + " "
            
        for bullet in section.bullets:
            experience_text += bullet.content + " "
            
    experience_text = experience_text.lower()
    
    # Enhanced relevance analysis with semantic matching
    matches = 0
    weighted_matches = 0
    
    # Identify critical requirements vs. nice-to-have
    critical_requirements = []
    preferred_requirements = []
    
    for req in requirements:
        req_lower = req.lower()
        if any(term in req_lower for term in ["must", "required", "essential", "necessary"]):
            critical_requirements.append(req_lower)
        else:
            preferred_requirements.append(req_lower)
    
    # If no explicit categorization, treat all as critical
    if not critical_requirements:
        critical_requirements = requirements
    
    # Check for exact matches in critical requirements (higher weight)
    for req in critical_requirements:
        req_lower = req.lower()
        if req_lower in experience_text:
            matches += 2
            weighted_matches += 3  # Higher weight for critical requirements
        else:
            # Check for partial matches using key phrases
            key_phrases = [phrase for phrase in req_lower.split() if len(phrase) > 4]
            phrase_matches = sum(1 for phrase in key_phrases if phrase in experience_text)
            if phrase_matches > len(key_phrases) * 0.5:  # If more than half of key phrases match
                matches += 1
                weighted_matches += 1.5
    
    # Check for matches in preferred requirements (lower weight)
    for req in preferred_requirements:
        req_lower = req.lower()
        if req_lower in experience_text:
            matches += 1
            weighted_matches += 1  # Standard weight for preferred requirements
        else:
            # Check for partial matches
            key_phrases = [phrase for phrase in req_lower.split() if len(phrase) > 4]
            phrase_matches = sum(1 for phrase in key_phrases if phrase in experience_text)
            if phrase_matches > len(key_phrases) * 0.5:
                matches += 0.5
                weighted_matches += 0.5
    
    # Check for years of experience requirements
    years_of_experience_pattern = re.compile(r'(\d+)[\+]?\s*(?:years|yrs)')
    years_matches = years_of_experience_pattern.findall(job_description.lower())
    
    if years_matches:
        required_years = max([int(years) for years in years_matches])
        actual_years = calculate_total_experience_years(experience_sections)
        
        if actual_years >= required_years:
            weighted_matches += 5  # Significant bonus for meeting years requirement
        elif actual_years >= required_years * 0.8:
            weighted_matches += 2  # Partial bonus for being close
    
    # Calculate final relevance score (30 points max)
    total_requirements = len(critical_requirements) + len(preferred_requirements)
    if total_requirements > 0:
        base_relevance = (matches / total_requirements) * 20
        weighted_relevance = (weighted_matches / (total_requirements * 2)) * 30  # Normalized to account for weights
        
        # Combine both metrics with emphasis on weighted relevance
        relevance_score = min(30, (base_relevance * 0.3) + (weighted_relevance * 0.7))
    else:
        relevance_score = 0
    
    return relevance_score

def calculate_total_experience_years(experience_sections):
    """Calculates total years of experience from all positions"""
    total_years = 0
    
    for section in experience_sections:
        if section.start_date:
            end_date = datetime.now() if section.is_current else (section.end_date or datetime.now())
            duration = (end_date - section.start_date).days / 365
            total_years += duration
            
    return total_years

def extract_requirements_from_job(job_description):
    """Extracts key requirements from a job description with enhanced semantic understanding"""
    requirements = []
    
    # Look for common requirement indicators
    requirement_sections = []
    lines = job_description.split('\n')
    
    # Track if we're in a requirements section
    in_requirements = False
    for line in lines:
        line_lower = line.lower()
        
        # Check for section headers that indicate requirements
        if any(header in line_lower for term in ['requirements', 'qualifications', 'what you need', 'skills required', 
                                               'must have', 'required skills', 'job requirements']
              for header in [f"{term}:", f"{term}", f"{term.title()}", f"{term.upper()}"]):
            in_requirements = True
            requirement_sections.append([])
        # Check for section headers that indicate end of requirements
        elif in_requirements and any(header in line_lower for term in ['benefits', 'about us', 'what we offer', 
                                                                      'compensation', 'perks', 'why join us']
                                   for header in [f"{term}:", f"{term}", f"{term.title()}", f"{term.upper()}"]):
            in_requirements = False
        
        # Add line to current requirement section if we're in one
        if in_requirements and line.strip():
            requirement_sections[-1].append(line)
    
    # If no structured requirements found, use enhanced extraction techniques
    if not requirement_sections:
        # Look for bullet points or numbered lists
        bullet_patterns = [
            r'[•\-\*]\s+(.*?)(?=(?:[•\-\*])|$)',  # Bullet points
            r'^\d+\.\s+(.*?)(?=(?:^\d+\.)|$)',     # Numbered lists
            r'[\n■►◆●]\s+(.*?)(?=(?:[\n■►◆●])|$)'  # Special bullets
        ]
        
        for pattern in bullet_patterns:
            bullets = re.findall(pattern, job_description, re.MULTILINE | re.DOTALL)
            if bullets:
                requirement_sections.append(bullets)
                break
                
        # If still no requirements found, try sentence-based extraction
        if not requirement_sections:
            sentences = re.split(r'[.!?]\s+', job_description)
            
            # Look for requirement indicators in sentences
            requirement_indicators = [
                'experience', 'skill', 'knowledge', 'ability', 'proficient', 
                'familiar', 'degree', 'education', 'qualified', 'proficiency',
                'expertise', 'understanding', 'background', 'capable',
                'competent', 'required', 'must have', 'should have'
            ]
            
            requirement_sentences = [s for s in sentences if any(indicator in s.lower() for indicator in requirement_indicators)]
            
            if requirement_sentences:
                requirement_sections.append(requirement_sentences)
    
    # Process requirement sections with enhanced parsing
    for section in requirement_sections:
        for item in section:
            # Clean up the item
            item = item.strip()
            if not item or len(item) < 5:
                continue
                
            # Remove bullets, numbers, and other prefixes
            item = re.sub(r'^[•\-\*\d.]+\s*', '', item)
            
            # Check if the item contains multiple requirements
            if any(conjunction in item.lower() for conjunction in [' and ', '; ', ', ']):
                # Split by various conjunctions
                parts = re.split(r' and |; |, ', item)
                
                # Filter out very short parts (likely not complete requirements)
                valid_parts = [part.strip() for part in parts if len(part.strip()) > 10]
                
                # Add valid parts to requirements
                requirements.extend(valid_parts)
            else:
                requirements.append(item)
    
    # Enhanced filtering for meaningful requirements
    filtered_requirements = []
    for req in requirements:
        # Skip very short items
        if len(req) < 10:
            continue
            
        # Skip items that don't contain any informative words
        if not any(word in req.lower() for word in ['experience', 'skill', 'knowledge', 'degree', 'ability', 
                                                   'proficient', 'familiar', 'education', 'qualified']):
            continue
            
        filtered_requirements.append(req)
    
    # If we have too few requirements, try a more lenient approach
    if len(filtered_requirements) < 3:
        filtered_requirements = [req for req in requirements if len(req) >= 10]
    
    # Remove duplicates and near-duplicates
    unique_requirements = []
    for req in filtered_requirements:
        req_lower = req.lower()
        # Check if this requirement is similar to any we've already included
        if not any(similarity(req_lower, existing.lower()) > 0.7 for existing in unique_requirements):
            unique_requirements.append(req)
    
    return unique_requirements

def similarity(text1, text2):
    """Calculates a simple similarity score between two texts"""
    # Convert texts to sets of words
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0

def extract_job_titles(job_description):
    """Extracts potential job titles from job description with enhanced accuracy"""
    # Common job titles dictionary - expanded for better coverage
    common_titles = [
        # Technology
        'software engineer', 'software developer', 'frontend developer', 'backend developer',
        'full stack developer', 'data scientist', 'data analyst', 'machine learning engineer',
        'devops engineer', 'systems administrator', 'network engineer', 'security engineer',
        'cloud architect', 'database administrator', 'qa engineer', 'quality assurance',
        'site reliability engineer', 'infrastructure engineer', 'mobile developer',
        'solutions architect', 'technical lead', 'data engineer', 'ai researcher',
        'blockchain developer', 'game developer', 'web developer', 'ui developer',
        
        # Management
        'product manager', 'project manager', 'program manager', 'technical project manager',
        'engineering manager', 'director of engineering', 'cto', 'vp of engineering',
        'it manager', 'chief information officer', 'chief technology officer',
        'development manager', 'scrum master', 'product owner', 'delivery manager',
        
        # Business
        'business analyst', 'systems analyst', 'marketing manager', 'sales manager', 
        'account executive', 'customer success manager', 'operations manager',
        'finance manager', 'financial analyst', 'accountant', 'business development',
        'human resources', 'hr manager', 'talent acquisition', 'recruiter',
        
        # Design
        'ux designer', 'ui designer', 'graphic designer', 'product designer',
        'visual designer', 'interaction designer', 'user researcher', 'ux researcher',
        
        # Content/Marketing
        'content writer', 'content strategist', 'technical writer', 'copywriter',
        'content marketing', 'seo specialist', 'social media manager', 'digital marketer',
        'marketing specialist', 'brand manager'
    ]
    
    # Enhanced title patterns to look for in job description
    title_patterns = [
        # Job title as the first line or heading
        r'^[^\n]{0,30}?([A-Z][a-z]+(?:[\s\-]+[A-Z]?[a-z]+){1,5})[^\n]{0,30}?$',
        
        # Job title after "Title:", "Position:", "Role:", etc.
        r'(?:job title|position|role|job|title)[\s\:]{1,3}([A-Za-z]+(?:[\s\-]+[A-Za-z]+){1,5})',
        
        # "We are looking for a [Title]", "... seeking a [Title]", etc.
        r'(?:looking|seeking|hiring|searching|recruiting)(?:\s\w+){0,3}\s(?:for|a|an)\s([A-Za-z]+(?:[\s\-]+[A-Za-z]+){1,5})',
        
        # Title in all caps or title case at the beginning of the document
        r'(?:^|\n)([A-Z][A-Za-z]*(?:[\s\-]+[A-Za-z]+){1,4})'
    ]
    
    found_titles = []
    
    # First try to extract title using patterns
    for pattern in title_patterns:
        matches = re.findall(pattern, job_description, re.MULTILINE)
        if matches:
            for match in matches:
                match = match.strip()
                # Filter out very short or very long matches
                if 5 <= len(match) <= 50:
                    found_titles.append(match.lower())
    
    # If pattern matching found titles, clean them
    if found_titles:
        cleaned_titles = []
        for title in found_titles:
            # Remove common prefixes/suffixes
            for prefix in ['position:', 'title:', 'job:', 'role:']:
                if title.startswith(prefix):
                    title = title[len(prefix):].strip()
            
            # Remove location information
            title = re.sub(r'\s+\-\s+[A-Za-z\s,]+$', '', title)
            
            # Remove employment type
            title = re.sub(r'\s+\(?(full[\-\s]time|part[\-\s]time|contract|temporary|permanent)\)?$', '', title, flags=re.IGNORECASE)
            
            cleaned_titles.append(title)
            
        found_titles = cleaned_titles
    
    # If no titles found with patterns, try dictionary matching
    if not found_titles:
        # Check first few lines for common job titles
        first_lines = ' '.join(job_description.split('\n')[:5]).lower()
        
        for title in common_titles:
            if title in first_lines:
                found_titles.append(title)
                
        # If still nothing, check entire text
        if not found_titles:
            job_desc_lower = job_description.lower()
            for title in common_titles:
                if title in job_desc_lower:
                    found_titles.append(title)
    
    # If we found titles, sort by specificity (prefer longer titles)
    if found_titles:
        found_titles.sort(key=len, reverse=True)
        
        # Remove near-duplicates
        unique_titles = []
        for title in found_titles:
            # Only add if not already a substring of a longer title we've added
            if not any(title in existing for existing in unique_titles):
                unique_titles.append(title)
                
        # Limit to top 3 most specific titles
        found_titles = unique_titles[:3]
    
    return found_titles

def extract_keywords_from_job_description(job_description, max_keywords=15):
    """Extracts important keywords from job description with industry intelligence"""
    # Define enhanced keyword categories for more comprehensive extraction
    keyword_categories = {
        # Technical skills - expanded with trending technologies
        'technical_skills': [
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'php', 'swift', 'kotlin', 'scala', 'perl', 'r', 'matlab', 'bash', 'powershell',
            
            # Frontend
            'react', 'angular', 'vue', 'svelte', 'jquery', 'bootstrap', 'tailwind', 
            'css', 'html', 'sass', 'less', 'webpack', 'nextjs', 'gatsby', 'html5',
            
            # Backend
            'node', 'express', 'django', 'flask', 'spring', 'rails', 'laravel', 'aspnet',
            'fastapi', 'graphql', 'rest', 'api', 'microservices', 'serverless',
            
            # Database
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle', 'dynamodb', 'redis',
            'elasticsearch', 'neo4j', 'cassandra', 'mariadb', 'sqlite', 'couchdb',
            
            # Cloud
            'aws', 'azure', 'gcp', 'cloud', 'ec2', 's3', 'lambda', 'kubernetes', 'docker',
            'terraform', 'cloudformation', 'pulumi', 'ansible', 'chef', 'puppet',
            
            # DevOps
            'ci/cd', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket', 'azure devops',
            'travis', 'circleci', 'github actions', 'teamcity', 'bamboo',
            
            # AI/ML
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
            'nlp', 'computer vision', 'neural networks', 'ai', 'artificial intelligence',
            'transformers', 'llm', 'reinforcement learning', 'generative ai',
            
            # Data
            'data science', 'big data', 'data analytics', 'data engineering', 'etl',
            'hadoop', 'spark', 'tableau', 'power bi', 'looker', 'dbt', 'airflow',
            
            # Other tech
            'blockchain', 'ios', 'android', 'mobile', 'responsive', 'architecture',
            'ui/ux', 'design', 'figma', 'sketch', 'photoshop', 'illustrator',
            'security', 'agile', 'scrum', 'kanban', 'lean', 'devops'
        ],
        
        # Soft skills - expanded
        'soft_skills': [
            'communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking',
            'creativity', 'time management', 'organization', 'adaptability', 'flexibility',
            'interpersonal', 'presentation', 'writing', 'negotiation', 'conflict resolution',
            'decision making', 'analytical', 'attention to detail', 'self-motivated', 'initiative',
            'collaboration', 'mentoring', 'coaching', 'customer service', 'client management',
            'stakeholder management', 'strategic thinking', 'prioritization', 'emotional intelligence',
            'cross-functional', 'public speaking', 'active listening', 'empathy', 'resilience'
        ],
        
        # Experience levels - expanded
        'experience_levels': [
            'entry level', 'junior', 'mid-level', 'senior', 'principal', 'lead', 'manager',
            'director', 'vp', 'chief', 'head of', 'executive', 'c-level', 'ceo', 'cto', 'cio',
            'cfo', 'coo', 'years of experience', 'background in', 'expertise in', 'proficiency',
            'mastery', 'specialist', 'subject matter expert', 'architect', 'consultant',
            'intern', 'associate', 'staff', 'individual contributor', 'technical lead'
        ],
        
        # Industry domains - expanded
        'industry_domains': [
            'finance', 'banking', 'healthcare', 'medical', 'retail', 'e-commerce',
            'manufacturing', 'logistics', 'transportation', 'education', 'government',
            'non-profit', 'media', 'entertainment', 'gaming', 'sports', 'technology',
            'telecom', 'energy', 'utilities', 'real estate', 'construction', 'legal',
            'consulting', 'marketing', 'advertising', 'hospitality', 'travel', 'automotive',
            'aerospace', 'defense', 'pharma', 'biotech', 'insurance', 'agriculture',
            'food & beverage', 'consumer goods', 'fashion', 'luxury', 'environmental',
            'renewable energy', 'oil & gas', 'mining', 'chemicals', 'pharmaceuticals'
        ],
        
        # Domain-specific skills
        'domain_specific': [
            # Finance
            'financial analysis', 'accounting', 'investment', 'trading', 'portfolio management',
            'risk assessment', 'compliance', 'auditing', 'tax', 'budgeting', 'forecasting',
            
            # Healthcare
            'patient care', 'clinical', 'medical records', 'hipaa', 'ehr', 'telemedicine',
            'healthcare compliance', 'medical coding', 'patient management', 'clinical trials',
            
            # Marketing
            'seo', 'sem', 'ppc', 'social media', 'content marketing', 'email marketing',
            'growth hacking', 'conversion optimization', 'google analytics', 'ab testing',
            
            # Business
            'business intelligence', 'strategy', 'operations', 'supply chain', 'procurement',
            'vendor management', 'contract negotiation', 'business development', 'sales',
            'customer success', 'product management', 'project management', 'scrum'
        ],
        
        # Certifications - expanded
        'certifications': [
            'certification', 'certified', 'license', 'licensed', 'pmp', 'cpa', 'cfa',
            'aws certified', 'azure certified', 'google certified', 'scrum', 'agile',
            'itil', 'six sigma', 'cissp', 'ceh', 'comptia', 'ccna', 'mcsa', 'mcse',
            'cism', 'cisa', 'capm', 'prince2', 'cma', 'shrm', 'phr', 'sphr',
            'csm', 'safe', 'ccnp', 'ccie', 'rhce', 'lpic', 'gcp', 'oracle certified',
            'salesforce certified', 'pmi', 'cka', 'ckad', 'security+', 'network+',
            'a+', 'cloud+', 'linux+', 'project+', 'server+', 'ccsp', 'oscp'
        ]
    }
    
    # Flatten the categories for easier searching
    all_keywords = []
    for category, keywords in keyword_categories.items():
        all_keywords.extend([(keyword, category) for keyword in keywords])
    
    # Find matches in job description
    job_desc_lower = job_description.lower()
    matches = []
    
    # First pass: exact matches
    for keyword, category in all_keywords:
        if keyword in job_desc_lower:
            count = job_desc_lower.count(keyword)
            importance = 1
            
            # Apply importance weighting based on location in the document
            if keyword in job_desc_lower[:int(len(job_desc_lower)/3)]:  # Appears in first third
                importance += 1
                
            # Apply importance weighting based on emphasis
            if re.search(r'required|must\s+have|essential', job_desc_lower[max(0, job_desc_lower.find(keyword)-30):job_desc_lower.find(keyword)]):
                importance += 2
                
            matches.append((keyword, category, count, importance))
    
    # Extract job title for priority weighting
    job_title = extract_job_titles(job_description)
    
    # Prioritize keywords in different ways:
    # 1. First by importance score
    # 2. Then by frequency
    # 3. Then by length (prefer longer, more specific terms)
    sorted_matches = sorted(matches, key=lambda x: (x[3], x[2], len(x[0])), reverse=True)
    
    # Balance keywords across categories for diversity
    final_keywords = []
    used_categories = set()
    
    # First, add job title keywords if found
    if job_title:
        for title in job_title:
            final_keywords.append(title)
            
    # Then, add one from each category to ensure diversity
    for keyword, category, _, _ in sorted_matches:
        if category not in used_categories and keyword not in final_keywords:
            final_keywords.append(keyword)
            used_categories.add(category)
            
            if len(final_keywords) >= max_keywords * 0.5:
                break
    
    # Finally, add remaining top keywords up to max_keywords
    for keyword, _, _, _ in sorted_matches:
        if keyword not in final_keywords:
            final_keywords.append(keyword)
            
            if len(final_keywords) >= max_keywords:
                break
    
    return final_keywords

def get_keyword_variations(keyword):
    """Generates variations of a keyword for more flexible matching"""
    variations = [keyword]
    
    # Simple singular/plural variations
    if keyword.endswith('s') and not keyword.endswith('ss'):
        variations.append(keyword[:-1])  # Remove trailing 's'
    else:
        variations.append(keyword + 's')  # Add trailing 's'
        
    # Common verb forms
    if keyword.endswith('ing'):
        variations.append(keyword[:-3])  # develop from developing
        variations.append(keyword[:-3] + 'e')  # manage from managing
        variations.append(keyword[:-3] + 'ed')  # develop from developing -> developed
        
    if keyword.endswith('ed'):
        variations.append(keyword[:-2])  # develop from developed
        variations.append(keyword[:-1])  # manage from managed
        variations.append(keyword[:-2] + 'ing')  # develop from developed -> developing
        
    # Adjective variations
    if keyword.endswith('ability'):
        variations.append(keyword[:-5] + 'le')  # scalable from scalability
        
    if keyword.endswith('able'):
        variations.append(keyword[:-4] + 'ability')  # scalable -> scalability
        
    # Handle common prefixes
    if keyword.startswith('pre'):
        variations.append(keyword[3:])  # pre-process -> process
    
    if keyword.startswith('re'):
        variations.append(keyword[2:])  # redesign -> design
        
    # Hyphenated variations
    if '-' in keyword:
        variations.append(keyword.replace('-', ' '))  # user-friendly -> user friendly
        variations.append(keyword.replace('-', ''))  # user-friendly -> userfriendly
    elif ' ' in keyword:
        variations.append(keyword.replace(' ', '-'))  # user friendly -> user-friendly
        variations.append(keyword.replace(' ', ''))  # user friendly -> userfriendly
        
    # Common abbreviations and full forms
    abbreviations = {
        'ui': 'user interface',
        'ux': 'user experience',
        'db': 'database',
        'admin': 'administrator',
        'dev': 'development',
        'ops': 'operations',
        'app': 'application',
        'tech': 'technology',
        'mgmt': 'management',
        'sr': 'senior',
        'jr': 'junior',
        'qa': 'quality assurance',
        'ai': 'artificial intelligence',
        'ml': 'machine learning'
    }
    
    # Add abbreviation variations
    if keyword in abbreviations:
        variations.append(abbreviations[keyword])
    else:
        # Check if it's a full form that has an abbreviation
        for abbr, full in abbreviations.items():
            if keyword == full:
                variations.append(abbr)
                
    # Remove duplicates and empty strings
    variations = [v for v in variations if v]
    variations = list(set(variations))
    
    return variations

def get_industry_skills(industry):
    """Returns common skills for a specific industry with enhanced comprehensiveness"""
    industry_skills = {
        'tech': [
            # Software Development
            'programming', 'software development', 'web development', 'mobile development',
            'full stack', 'frontend', 'backend', 'microservices', 'api development',
            'debugging', 'code review', 'version control', 'git', 'continuous integration',
            
            # Methodologies
            'agile', 'scrum', 'kanban', 'waterfall', 'extreme programming', 'tdd',
            'bdd', 'devops', 'cicd', 'continuous deployment', 'continuous delivery',
            
            # Infrastructure
            'cloud', 'architecture', 'aws', 'azure', 'gcp', 'infrastructure as code',
            'containerization', 'docker', 'kubernetes', 'virtualization', 'vmware',
            
            # Security
            'cybersecurity', 'application security', 'penetration testing', 'vulnerability assessment',
            'security architecture', 'security compliance', 'identity management',
            
            # Data
            'data analysis', 'data science', 'machine learning', 'artificial intelligence',
            'business intelligence', 'data visualization', 'data modeling', 'etl',
            'data warehousing', 'big data', 'data engineering'
        ],
        
        'finance': [
            # Core Finance
            'financial analysis', 'financial modeling', 'financial reporting', 'forecasting',
            'budgeting', 'variance analysis', 'cash flow management', 'capital planning',
            
            # Banking/Investment
            'banking', 'investment', 'portfolio management', 'asset management',
            'wealth management', 'securities', 'trading', 'derivatives', 'fixed income',
            'equity research', 'market analysis', 'fund management',
            
            # Risk/Compliance
            'risk assessment', 'risk management', 'compliance', 'regulatory reporting',
            'aml', 'kyc', 'fraud detection', 'internal controls', 'audit', 'sox compliance',
            
            # Accounting
            'accounting', 'financial accounting', 'managerial accounting', 'tax',
            'general ledger', 'accounts payable', 'accounts receivable', 'reconciliation',
            'cost accounting', 'revenue recognition', 'gaap', 'ifrs',
            
            # Analysis Tools
            'excel', 'vba', 'bloomberg', 'capital iq', 'factset', 'morningstar',
            'tableau', 'power bi', 'hyperion', 'fico', 'sas', 'stata', 'eviews',
            
            # FinTech
            'fintech', 'blockchain', 'cryptocurrency', 'digital payments', 'robotic process automation',
            'algorithmic trading', 'payment processing', 'digital banking'
        ],
        
        'healthcare': [
            # Clinical
            'patient care', 'medical terminology', 'clinical documentation', 'treatment planning',
            'diagnosis', 'patient assessment', 'medical procedures', 'clinical workflow',
            'care coordination', 'telehealth', 'clinical trials', 'medical protocols',
            
            # Administration
            'healthcare administration', 'medical billing', 'coding', 'revenue cycle management',
            'hipaa', 'healthcare compliance', 'utilization review', 'case management',
            'quality improvement', 'patient safety', 'risk management', 'credentialing',
            
            # Technical
            'electronic health records', 'emr systems', 'healthcare informatics', 'medical devices',
            'health information exchange', 'clinical decision support', 'healthcare interoperability',
            'medical imaging', 'telemedicine platforms', 'patient portals', 'healthcare analytics',
            
            # Specialized
            'pharmacy operations', 'laboratory services', 'radiology', 'nursing informatics',
            'population health management', 'value-based care', 'patient engagement',
            'disease management', 'preventative care', 'health insurance'
        ],
        
        'marketing': [
            # Digital Marketing
            'digital marketing', 'social media', 'content strategy', 'seo',
            'sem', 'ppc', 'email marketing', 'marketing automation', 'inbound marketing',
            'conversion optimization', 'landing page optimization', 'a/b testing',
            
            # Analytics
            'marketing analytics', 'google analytics', 'customer segmentation', 'attribution modeling',
            'campaign tracking', 'funnel analysis', 'cohort analysis', 'kpi reporting',
            'engagement metrics', 'customer lifetime value', 'marketing roi',
            
            # Strategy
            'brand development', 'positioning', 'market research', 'competitive analysis',
            'customer journey mapping', 'target audience definition', 'value proposition',
            'pricing strategy', 'go-to-market strategy', 'product marketing',
            
            # Technical
            'crm systems', 'marketing platforms', 'content management systems', 'adobe creative suite',
            'marketing technology stack', 'data visualization', 'web analytics', 'tag management',
            
            # Content
            'content creation', 'copywriting', 'content marketing', 'storytelling',
            'video production', 'social media content', 'blog management', 'editorial planning'
        ],
        
        'retail': [
            # Operations
            'merchandising', 'inventory management', 'supply chain', 'pos systems', 'retail operations',
            'loss prevention', 'store management', 'visual merchandising', 'category management',
            'planogram development', 'stock replenishment', 'warehouse management',
            
            # Sales & Customer Experience
            'sales techniques', 'customer service', 'clienteling', 'customer relationship management',
            'upselling', 'cross-selling', 'customer loyalty programs', 'customer experience design',
            'customer feedback systems', 'consumer behavior analysis', 'mystery shopping',
            
            # Digital Retail
            'e-commerce', 'omnichannel retail', 'online merchandising', 'digital storefronts',
            'online catalog management', 'mobile commerce', 'click and collect', 'dropshipping',
            'marketplace management', 'digital payments', 'online customer experience',
            
            # Analytics
            'retail analytics', 'sales forecasting', 'basket analysis', 'customer segmentation',
            'price elasticity', 'inventory optimization', 'demand planning', 'markdown optimization',
            'store traffic analysis', 'conversion rate optimization', 'retail kpis'
        ],
        
        'manufacturing': [
            # Operations
            'production planning', 'quality control', 'quality assurance', 'process improvement',
            'manufacturing operations', 'production scheduling', 'capacity planning', 'material requirements planning',
            'inventory control', 'bill of materials', 'work order management', 'kitting',
            
            # Methodologies
            'lean manufacturing', 'six sigma', 'kaizen', '5s', 'total productive maintenance',
            'just-in-time', 'kanban', 'continuous improvement', 'value stream mapping',
            'poka-yoke', 'statistical process control', 'design for manufacturability',
            
            # Technical
            'cnc programming', 'plc programming', 'cad/cam', 'manufacturing automation',
            'robotics', 'industrial controls', 'machine operation', 'tooling design',
            'production line design', 'equipment maintenance', 'industrial engineering',
            
            # Supply Chain
            'supply chain management', 'procurement', 'sourcing', 'vendor management',
            'materials management', 'logistics coordination', 'distribution', 'warehousing',
            'transportation management', 'demand planning', 'inventory optimization'
        ],
        
        'consulting': [
            # Project Management
            'client management', 'project delivery', 'requirements gathering', 'scope management',
            'project planning', 'resource allocation', 'timeline management', 'milestone tracking',
            'risk management', 'issue resolution', 'project governance', 'agile methodologies',
            
            # Analysis
            'business analysis', 'process analysis', 'financial modeling', 'market analysis',
            'data analysis', 'competitive analysis', 'stakeholder analysis', 'gap analysis',
            'cost-benefit analysis', 'root cause analysis', 'scenario planning', 'benchmarking',
            
            # Strategy
            'strategic planning', 'change management', 'organizational design', 'business transformation',
            'digital transformation', 'operational excellence', 'performance improvement',
            'business process reengineering', 'growth strategy', 'mergers & acquisitions',
            
            # Communication
            'stakeholder management', 'executive presentations', 'client communications',
            'requirements documentation', 'workshop facilitation', 'executive reporting',
            'proposal development', 'deliverable creation', 'status reporting'
        ]
    }
    
    return industry_skills.get(industry.lower(), [])

def get_industry_keywords(industry):
    """Returns common keywords for a specific industry with enhanced relevance"""
    industry_keywords = {
        'tech': [
            # Core Concepts
            'innovation', 'digital transformation', 'cutting-edge', 'technical excellence',
            'startup', 'scale', 'disruptive', 'platform', 'saas', 'api-first',
            'user experience', 'product-led growth', 'agile', 'continuous integration',
            
            # Technical
            'architecture', 'scalability', 'reliability', 'performance', 'security',
            'infrastructure', 'cloud native', 'containerization', 'microservices',
            'full-stack', 'frontend', 'backend', 'mobile', 'responsive', 'reactive',
            
            # Business
            'product-market fit', 'user acquisition', 'customer retention', 'monetization',
            'business model', 'go-to-market', 'technology stack', 'technical debt',
            'minimum viable product', 'feature development', 'product roadmap'
        ],
        
        'finance': [
            # Core Concepts
            'revenue', 'profit', 'budget', 'forecasting', 'compliance', 'risk management',
            'investment', 'assets', 'portfolio', 'regulatory', 'capital markets',
            'financial performance', 'liquidity', 'solvency', 'profitability',
            
            # Analysis
            'financial analysis', 'variance analysis', 'ratio analysis', 'trend analysis',
            'cash flow analysis', 'balance sheet analysis', 'income statement',
            'statement of cash flows', 'financial modeling', 'scenario planning',
            
            # Compliance & Governance
            'audit', 'internal controls', 'sox compliance', 'regulatory reporting',
            'governance', 'risk assessment', 'compliance framework', 'policy implementation',
            'financial controls', 'disclosure requirements', 'financial integrity'
        ],
        
        'healthcare': [
            # Core Concepts
            'patient', 'care', 'medical', 'clinical', 'treatment', 'diagnosis',
            'health', 'wellness', 'outcomes', 'protocol', 'therapy', 'intervention',
            'prevention', 'recovery', 'continuity of care', 'evidence-based practice',
            
            # Administration
            'healthcare delivery', 'patient management', 'clinical workflow', 'care coordination',
            'utilization', 'reimbursement', 'billing', 'coding', 'revenue cycle',
            'quality measures', 'healthcare operations', 'regulatory compliance',
            
            # Technical
            'electronic health record', 'health information exchange', 'interoperability',
            'clinical decision support', 'telehealth', 'remote monitoring', 'digital health',
            'health informatics', 'medical devices', 'health data', 'population health'
        ],
        
        'marketing': [
            # Core Concepts
            'campaign', 'audience', 'engagement', 'conversion', 'brand', 'positioning',
            'messaging', 'channel', 'segment', 'funnel', 'acquisition', 'retention',
            'loyalty', 'awareness', 'consideration', 'purchase', 'advocacy',
            
            # Strategy
            'marketing strategy', 'campaign planning', 'target market', 'value proposition',
            'competitive advantage', 'market penetration', 'brand identity', 'differentiation',
            'customer journey', 'touchpoints', 'customer experience', 'persona development',
            
            # Analytics
            'marketing roi', 'attribution', 'engagement metrics', 'conversion rate',
            'customer acquisition cost', 'lifetime value', 'bounce rate', 'click-through rate',
            'impressions', 'reach', 'analytics', 'dashboard', 'performance indicators'
        ],
        
        'retail': [
            # Core Concepts
            'customer', 'sales', 'merchandise', 'inventory', 'e-commerce', 'omnichannel',
            'store', 'shopper', 'consumer', 'pricing', 'promotion', 'loyalty',
            'assortment', 'fulfillment', 'pos', 'retail experience', 'storefront',
            
            # Operations
            'retail operations', 'store management', 'inventory management', 'stock levels',
            'replenishment', 'markdown', 'shrinkage', 'loss prevention', 'visual merchandising',
            'planogram', 'category management', 'space planning', 'fixture design',
            
            # Customer Experience
            'customer experience', 'shopping journey', 'in-store experience', 'digital experience',
            'clienteling', 'personalization', 'customer service', 'satisfaction',
            'loyalty program', 'customer feedback', 'voice of customer', 'nps'
        ],
        
        'manufacturing': [
            # Core Concepts
            'production', 'efficiency', 'quality', 'process improvement', 'operations',
            'lean', 'six sigma', 'supply chain', 'materials', 'assembly', 'inventory',
            'throughput', 'productivity', 'automation', 'manufacturing excellence',
            
            # Operations
            'production planning', 'scheduling', 'capacity utilization', 'work orders',
            'bill of materials', 'routing', 'machine utilization', 'setup reduction',
            'cycle time', 'lead time', 'takt time', 'bottleneck analysis', 'constraint management',
            
            # Quality & Improvement
            'quality control', 'quality assurance', 'inspection', 'testing', 'root cause analysis',
            'corrective action', 'preventive action', 'statistical process control',
            'variance reduction', 'continuous improvement', 'kaizen', 'value stream mapping'
        ],
        
        'consulting': [
            # Core Concepts
            'client', 'solution', 'strategy', 'deliverable', 'engagement', 'implementation',
            'stakeholder', 'analysis', 'recommendation', 'transformation', 'framework',
            'methodology', 'best practice', 'roadmap', 'assessment', 'advisory',
            
            # Project Management
            'project management', 'scope', 'timeline', 'milestones', 'deliverables',
            'requirements', 'constraints', 'dependencies', 'critical path',
            'resource allocation', 'project governance', 'status reporting',
            
            # Client Management
            'client relationship', 'expectation management', 'executive sponsorship',
            'change management', 'stakeholder alignment', 'communication planning',
            'resistance management', 'adoption strategy', 'training', 'knowledge transfer'
        ]
    }
    
    return industry_keywords.get(industry.lower(), [])

def calculate_industry_weights(industry, company_size, has_job_description):
    """Calculates scoring weights based on industry and company size with enhanced precision"""
    # Base weights applicable to all scenarios
    weights = {
        'format_score': 10,
        'content_score': 25,
        'keyword_score': 15 if has_job_description else 5,
        'impact_score': 15,
        'readability_score': 5,
        'contact_score': 5,
        'summary_score': 5,
        'experience_score': 30,
        'education_score': 15,
        'skills_score': 20,
        'projects_score': 10,
        'relevance_score': 20 if has_job_description else 0
    }
    
    # Industry-specific weight adjustments
    if industry:
        industry = industry.lower()
        
        if industry == 'tech':
            weights.update({
                'skills_score': weights['skills_score'] + 5,  # Technical skills highly valued
                'projects_score': weights['projects_score'] + 5,  # Project work demonstrates practical skills
                'impact_score': weights['impact_score'] + 3,  # Results matter in tech
                'experience_score': weights['experience_score'] - 3,  # Skills often valued over years
                'education_score': weights['education_score'] - 5,  # Less emphasis on formal education
                'format_score': weights['format_score'] - 5  # Less formality in tech resumes
            })
            
        elif industry == 'finance':
            weights.update({
                'education_score': weights['education_score'] + 5,  # Credentials matter more
                'format_score': weights['format_score'] + 5,  # Formality and precision valued
                'content_score': weights['content_score'] + 3,  # Detail and accuracy important
                'readability_score': weights['readability_score'] + 2,  # Clear communication essential
                'projects_score': weights['projects_score'] - 5,  # Less emphasis on project work
                'impact_score': weights['impact_score'] - 5  # Individual contribution sometimes less visible
            })
            
        elif industry == 'healthcare':
            weights.update({
                'education_score': weights['education_score'] + 10,  # Credentials critical
                'skills_score': weights['skills_score'] + 5,  # Specific skills/certifications valued
                'format_score': weights['format_score'] + 5,  # Professionalism important
                'contact_score': weights['contact_score'] + 3,  # Complete contact info for credentialing
                'projects_score': weights['projects_score'] - 10,  # Less emphasis on projects
                'relevance_score': weights['relevance_score'] + 5 if has_job_description else 0  # Specific role fit important
            })
            
        elif industry == 'marketing':
            weights.update({
                'impact_score': weights['impact_score'] + 10,  # Results and metrics crucial
                'content_score': weights['content_score'] + 5,  # Communication quality matters
                'readability_score': weights['readability_score'] + 5,  # Clear expression valued
                'summary_score': weights['summary_score'] + 5,  # Personal branding important
                'education_score': weights['education_score'] - 10,  # Less emphasis on formal education
                'format_score': weights['format_score'] - 5  # Creativity sometimes valued over strict format
            })
            
        elif industry == 'retail':
            weights.update({
                'experience_score': weights['experience_score'] + 5,  # Hands-on experience valued
                'impact_score': weights['impact_score'] + 5,  # Results focus important
                'skills_score': weights['skills_score'] + 3,  # Specific retail skills valued
                'content_score': weights['content_score'] + 2,  # Clear communication of responsibilities
                'education_score': weights['education_score'] - 10,  # Less emphasis on degrees
                'projects_score': weights['projects_score'] - 5  # Fewer formal projects
            })
            
        elif industry == 'manufacturing':
            weights.update({
                'skills_score': weights['skills_score'] + 5,  # Technical skills crucial
                'experience_score': weights['experience_score'] + 5,  # Experience highly valued
                'impact_score': weights['impact_score'] + 5,  # Efficiency and results focus
                'projects_score': weights['projects_score'] + 3,  # Process improvement projects relevant
                'summary_score': weights['summary_score'] - 3,  # Less emphasis on personal branding
                'education_score': weights['education_score'] - 10  # Technical skills often valued over degrees
            })
            
        elif industry == 'consulting':
            weights.update({
                'impact_score': weights['impact_score'] + 10,  # Results and client impact crucial
                'content_score': weights['content_score'] + 5,  # Clear articulation of value
                'education_score': weights['education_score'] + 5,  # Credentials often valued
                'format_score': weights['format_score'] + 5,  # Professional presentation important
                'experience_score': weights['experience_score'] + 5,  # Client experience valued
                'projects_score': weights['projects_score'] - 5  # Client work often replaces separate projects
            })
    
    # Company size adjustments        
    if company_size:
        company_size = company_size.lower()
        
        if company_size == 'startup':
            weights.update({
                'skills_score': weights['skills_score'] + 5,  # Versatility valued
                'impact_score': weights['impact_score'] + 5,  # Direct contribution to business
                'projects_score': weights['projects_score'] + 3,  # Initiative and self-direction
                'relevance_score': weights['relevance_score'] + 3 if has_job_description else 0,  # Role fit important
                'format_score': weights['format_score'] - 5,  # Less formal expectations
                'education_score': weights['education_score'] - 5  # Skills over credentials
            })
            
        elif company_size == 'mid-size':
            weights.update({
                'experience_score': weights['experience_score'] + 3,  # Relevant experience valued
                'skills_score': weights['skills_score'] + 3,  # Specific skills important
                'impact_score': weights['impact_score'] + 3,  # Results focus
                'summary_score': weights['summary_score'] + 2,  # Clear articulation of fit
                'format_score': weights['format_score'] - 1,  # Moderate formality
                'education_score': weights['education_score'] - 5  # Balanced view of credentials
            })
            
        elif company_size == 'enterprise':
            weights.update({
                'format_score': weights['format_score'] + 5,  # ATS compatibility crucial
                'education_score': weights['education_score'] + 5,  # Credentials for screening
                'keyword_score': weights['keyword_score'] + 5 if has_job_description else 0,  # ATS optimization
                'relevance_score': weights['relevance_score'] + 5 if has_job_description else 0,  # Role alignment
                'skills_score': weights['skills_score'] - 5,  # Broader skill categories
                'projects_score': weights['projects_score'] - 5  # Formal work experience often favored
            })
    
    # Normalize weights to sum to 100
    total = sum(weights.values())
    weights = {k: (v / total) * 100 for k, v in weights.items()}
    
    return weights

def calculate_weighted_score(metrics, weights):
    """Calculates overall score based on metrics and weights with enhanced reliability"""
    score = 0
    counted_metrics = 0
    
    for metric, weight in weights.items():
        # Only consider metrics that exist and have valid values
        if metric in metrics and metrics[metric] is not None:
            if isinstance(metrics[metric], (int, float)) and not isinstance(metrics[metric], bool):
                score += (metrics[metric] * weight / 100)
                counted_metrics += 1
    
    # If we couldn't calculate based on enough metrics, use a more conservative score
    if counted_metrics < len(weights) * 0.7:
        # Apply a penalty for incomplete metrics
        completion_factor = counted_metrics / len(weights)
        score = score * completion_factor
    
    # Ensure score is within valid range
    return min(100, max(0, score))

def generate_comprehensive_feedback(metrics, overall_score):
    """Generates comprehensive feedback based on metrics and score with enhanced actionability"""
    # Initialize feedback categories
    overall = []
    improvements = []
    ats_tips = []
    
    # OVERALL ASSESSMENT - Tailored to score range
    if overall_score >= 90:
        overall.append("Exceptional resume that should perform very well with ATS systems and hiring managers. You've effectively showcased your qualifications in a well-structured format.")
    elif overall_score >= 80:
        overall.append("Strong resume that meets most ATS requirements and presents your qualifications effectively. Minor optimizations could further enhance your application.")
    elif overall_score >= 70:
        overall.append("Good resume with specific areas for improvement to enhance ATS performance. You have solid content but need strategic adjustments to maximize impact.")
    elif overall_score >= 60:
        overall.append("Average resume that may pass some ATS systems but needs improvements to be competitive. Several key areas need attention to strengthen your application.")
    else:
        overall.append("Below average resume that needs significant improvements to pass ATS screening. A targeted revision focusing on structure, content, and keywords will substantially improve your results.")
    
    # FORMAT FEEDBACK - Focus on ATS compatibility
    if 'format_score' in metrics and metrics['format_score'] < 70:
        improvements.append("Improve your resume structure and formatting for better ATS compatibility.")
        
        if 'red_flags' in metrics and metrics['red_flags']:
            for flag in metrics['red_flags'][:2]:  # Limit to top 2 flags
                improvements.append(f"Address this format issue: {flag}")
                
        ats_tips.append("Use standard section headings (Experience, Education, Skills) that ATS systems recognize.")
        ats_tips.append("Maintain a clean, single-column layout with standard formatting to ensure proper parsing.")
    
    # KEYWORD OPTIMIZATION - Critical for ATS
    if 'keyword_score' in metrics and metrics['keyword_score'] < 70 and 'relevance_score' in metrics and metrics['relevance_score'] is not None:
        improvements.append("Add more relevant keywords that match the job description requirements.")
        
        if 'missing_keywords' in metrics and metrics['missing_keywords'] and len(metrics['missing_keywords']) > 0:
            keyword_list = ', '.join(metrics['missing_keywords'][:5])  # Limit to top 5
            improvements.append(f"Include these key terms from the job description: {keyword_list}")
            
        ats_tips.append("Most ATS systems rank resumes based on keyword matching. Include exact phrases from the job posting.")
        ats_tips.append("Incorporate keywords naturally throughout your resume, especially in your Experience and Skills sections.")
    
    # SKILLS SECTION - Showcase capabilities
    if 'skills_score' in metrics and metrics['skills_score'] < 70:
        improvements.append("Enhance your skills section with more relevant and organized skills.")
        
        if 'technical_match' in metrics and 'soft_skills_match' in metrics:
            if metrics['technical_match'] < 60:
                improvements.append("Add more technical or hard skills related to your field.")
            if metrics['soft_skills_match'] < 40:
                improvements.append("Include more soft skills to demonstrate workplace effectiveness.")
                
        ats_tips.append("Organize skills by category (Technical, Soft, Domain-Specific) for better readability and scanning.")
        ats_tips.append("Prioritize skills mentioned in the job description near the top of each category.")
    
    # EXPERIENCE SECTION - Demonstrate impact
    if 'experience_score' in metrics and metrics['experience_score'] < 70:
        improvements.append("Strengthen your experience section with more accomplishments and results.")
        
        if 'action_verb_usage' in metrics and metrics['action_verb_usage'] < 60:
            improvements.append("Start each bullet point with strong action verbs (Developed, Implemented, Managed).")
            
        if 'quantification_score' in metrics and metrics['quantification_score'] < 50:
            improvements.append("Quantify your achievements with specific numbers, percentages, and metrics.")
            
        if 'achievement_focus' in metrics and metrics['achievement_focus'] < 40:
            improvements.append("Focus more on achievements and results rather than just listing responsibilities.")
            
        ats_tips.append("Use industry-standard job titles that ATS systems will recognize.")
        ats_tips.append("Include relevant keywords from the job description in your bullet points.")
    
    # EDUCATION SECTION - Credentials matter
    if 'education_score' in metrics and metrics['education_score'] < 70:
        improvements.append("Enhance your education section with more complete information.")
        
        # Check section feedback for specific education issues
        if 'section_feedback' in metrics and 'education' in metrics['section_feedback']:
            edu_feedback = metrics['section_feedback']['education']
            if edu_feedback and len(edu_feedback) > 0:
                # Get the most important education feedback
                improvements.append(edu_feedback[0])
    
    # SUMMARY/OBJECTIVE - Personal branding
    if 'summary_score' in metrics and metrics['summary_score'] < 70 and metrics['summary_score'] > 0:
        improvements.append("Improve your professional summary to create a stronger first impression.")
        
        # Check section feedback for specific summary issues
        if 'section_feedback' in metrics and 'summary' in metrics['section_feedback']:
            summary_feedback = metrics['section_feedback']['summary']
            if summary_feedback and len(summary_feedback) > 0:
                # Get the most important summary feedback
                improvements.append(summary_feedback[0])
                
        ats_tips.append("Include relevant keywords in your summary that match the job title and key requirements.")
    elif 'summary_score' in metrics and metrics['summary_score'] == 0:
        improvements.append("Add a powerful professional summary that highlights your value proposition.")
        ats_tips.append("A strong summary improves both ATS performance and human readability.")
    
    # CONTENT QUALITY - Clarity and impact
    if 'content_score' in metrics and metrics['content_score'] < 70:
        improvements.append("Enhance overall content quality with clearer, more impactful descriptions.")
        
        if 'impact_score' in metrics and metrics['impact_score'] < 60:
            improvements.append("Add more accomplishment-focused language that demonstrates your value.")
            
        if 'readability_score' in metrics and metrics['readability_score'] < 70:
            improvements.append("Improve readability with concise, clear language and appropriate bullet length.")
            
        ats_tips.append("Use industry-standard terminology that both ATS systems and hiring managers will recognize.")
    
    # PROJECTS - Practical application
    if 'projects_score' in metrics and metrics['projects_score'] < 70 and metrics['projects_score'] > 0:
        improvements.append("Strengthen your projects section to better showcase your practical skills.")
        
        # Check section feedback for specific project issues
        if 'section_feedback' in metrics and 'projects' in metrics['section_feedback']:
            project_feedback = metrics['section_feedback']['projects']
            if project_feedback and len(project_feedback) > 0:
                # Get the most important project feedback
                improvements.append(project_feedback[0])
    
    # General ATS optimization tips
    ats_tips.extend([
        "Save your resume as a standard PDF or .docx file to ensure proper parsing by ATS systems.",
        "Avoid using text boxes, images, icons, or multiple columns that can confuse ATS software.",
        "Use a clean, professional font such as Arial, Calibri, or Times New Roman.",
        "Spell out acronyms at least once to ensure both the ATS and human reviewers understand them."
    ])
    
    return {
        'overall': overall,
        'improvements': improvements,
        'ats_tips': ats_tips
    }