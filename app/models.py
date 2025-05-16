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


#################
# Profile picture
#################
DEFAULT_PROFILE_PICTURE = "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"


def full_name(obj):
    return f"{obj.first_name} {obj.last_name}"

def short_name(obj):
    return f"{obj.first_name} {obj.last_name[0]}." if obj.last_name else obj.first_name

def has_profile_picture(obj, default_picture):
    return bool(getattr(obj, 'profile_picture', None)) and getattr(obj, 'profile_picture') != default_picture

def masked_email(obj):
    email = getattr(obj, 'email', '')
    parts = email.split("@")
    if len(parts) != 2:
        return email  # fallback
    name, domain = parts
    if len(name) <= 1:
        masked_name = "*"
    else:
        masked_name = name[0] + "*" * (len(name) - 1)
    return masked_name + "@" + domain

# Association table for many-to-many relationship between users and courses
'''
user_courses = db.Table('user_courses',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)
'''

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

    profile_picture = db.Column(db.Text, nullable=True, default=DEFAULT_PROFILE_PICTURE) 
    
    # Relationships - non-course related
    job_applications = db.relationship('JobApplication', backref='user', lazy=True)
    todos = db.relationship('Todo', backref='user', lazy=True)
    skills = db.relationship('Skill', backref='user', lazy=True)
    achievements = db.relationship('Achievement', back_populates='user', lazy=True)
    internships = db.relationship('Internship', back_populates='user', lazy=True)
    
    # Note: No course-related relationships defined here
    # They are all defined in the respective course models with backref
    
    def is_premium(self):
        if not self.subscription_end_date:
            return False
        return self.subscription_tier == 'premium' and datetime.utcnow() < self.subscription_end_date
    
    # Course-related helper methods
    def get_enrolled_courses(self):
        """Get all courses the user is enrolled in"""
        return [enrollment.course for enrollment in self.enrollments]
    
    def get_completed_courses(self):
        """Get all courses the user has completed"""
        return [enrollment.course for enrollment in self.enrollments if enrollment.is_completed]
    
    def is_enrolled_in(self, course_id):
        """Check if user is enrolled in a specific course"""
        return any(enrollment.course_id == course_id for enrollment in self.enrollments)
    
    def get_course_progress(self, course_id):
        """Get user's progress in a specific course"""
        enrollment = next((e for e in self.enrollments if e.course_id == course_id), None)
        return enrollment.progress if enrollment else 0


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
        ((Post.user_id.in_(friend_ids)) & (Post.visibility == 'connections'))
        | (Post.visibility == 'public')
        | ((Post.visibility == 'private') & (Post.user_id == user_id))
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






#coursebud
# Course Models and Functions

class Course(db.Model):
   __tablename__ = 'courses'
   __table_args__ = {'extend_existing': True}
   
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(255), nullable=False)
   description = db.Column(db.Text)
   creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   category_id = db.Column(db.Integer, db.ForeignKey('course_categories.id'))
   level = db.Column(db.String(50))  # beginner, intermediate, advanced
   price = db.Column(db.Float, default=0.0)
   is_free = db.Column(db.Boolean, default=True)
   is_premium = db.Column(db.Boolean, default=False)  # For subscription-based access
   thumbnail = db.Column(db.String(255))  # Path to course thumbnail image
   duration = db.Column(db.String(50))  # Estimated duration
   status = db.Column(db.String(20), default='draft')  # draft, pending, approved, rejected
   approval_notes = db.Column(db.Text)  # Admin notes for approval/rejection
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   
   # Relationships
   creator = db.relationship('User', backref='created_courses', foreign_keys=[creator_id])
   category = db.relationship('CourseCategory', backref='courses')
   sections = db.relationship('CourseSection', back_populates='course', cascade='all, delete-orphan')
   enrollments = db.relationship('CourseEnrollment', back_populates='course', cascade='all, delete-orphan')
   reviews = db.relationship('CourseReview', back_populates='course', cascade='all, delete-orphan')
   
   def average_rating(self):
       if not self.reviews:
           return 0
       return sum(review.rating for review in self.reviews) / len(self.reviews)
   
   def total_students(self):
       return len(self.enrollments)
   
   def total_lessons(self):
       count = 0
       for section in self.sections:
           count += len(section.lessons)
       return count
   
   def __repr__(self):
       return f'<Course {self.title}>'


class CourseCategory(db.Model):
   __tablename__ = 'course_categories'
   __table_args__ = {'extend_existing': True}
   
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(100), nullable=False)
   description = db.Column(db.Text)
   parent_id = db.Column(db.Integer, db.ForeignKey('course_categories.id'), nullable=True)
   
   # Relationship for hierarchical categories
   parent = db.relationship('CourseCategory', remote_side=[id], backref='subcategories')
   
   def __repr__(self):
       return f'<CourseCategory {self.name}>'


class CourseSection(db.Model):
   __tablename__ = 'course_sections'
   __table_args__ = {'extend_existing': True}
   
   id = db.Column(db.Integer, primary_key=True)
   course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
   title = db.Column(db.String(255), nullable=False)
   description = db.Column(db.Text)
   order = db.Column(db.Integer, default=0)
   
   # Relationships
   course = db.relationship('Course', back_populates='sections')
   lessons = db.relationship('CourseLesson', back_populates='section', cascade='all, delete-orphan', order_by='CourseLesson.order')
   
   def __repr__(self):
       return f'<CourseSection {self.title}>'


class CourseLesson(db.Model):
   __tablename__ = 'course_lessons'
   __table_args__ = {'extend_existing': True}
   
   id = db.Column(db.Integer, primary_key=True)
   section_id = db.Column(db.Integer, db.ForeignKey('course_sections.id'), nullable=False)
   title = db.Column(db.String(255), nullable=False)
   content_type = db.Column(db.String(50))  # video, text, quiz, etc.
   content = db.Column(db.Text)  # Text content or URL to video/resource
   duration = db.Column(db.Integer, default=0)  # Duration in minutes
   order = db.Column(db.Integer, default=0)
   is_free_preview = db.Column(db.Boolean, default=False)  # If this lesson is available as a free preview
   
   # Relationships
   section = db.relationship('CourseSection', back_populates='lessons')
   completions = db.relationship('LessonCompletion', back_populates='lesson', cascade='all, delete-orphan')
   
   def __repr__(self):
       return f'<CourseLesson {self.title}>'


class CourseEnrollment(db.Model):
   __tablename__ = 'course_enrollments'
   __table_args__ = (
       db.UniqueConstraint('user_id', 'course_id', name='unique_enrollment'),
       {'extend_existing': True}
   )
   
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
   enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
   progress = db.Column(db.Float, default=0.0)  # Progress percentage
   is_completed = db.Column(db.Boolean, default=False)
   completion_date = db.Column(db.DateTime)
   paid_amount = db.Column(db.Float, default=0.0)
   payment_status = db.Column(db.String(20), default='free')  # free, paid, subscription
   
   # Relationships
   user = db.relationship('User', backref='enrollments', foreign_keys=[user_id])
   course = db.relationship('Course', back_populates='enrollments')
   lesson_completions = db.relationship('LessonCompletion', back_populates='enrollment', cascade='all, delete-orphan')
   certificate = db.relationship('CourseCertificate', backref='enrollment', uselist=False, cascade='all, delete-orphan')
   
   def calculate_progress(self):
       if not self.course.total_lessons():
           return 0
       
       completed_lessons = len(self.lesson_completions)
       total_lessons = self.course.total_lessons()
       
       progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
       self.progress = progress
       
       # Check if course is completed
       if progress >= 100 and not self.is_completed:
           self.is_completed = True
           self.completion_date = datetime.utcnow()
       
       return progress
   
   def __repr__(self):
       return f'<CourseEnrollment {self.user_id}-{self.course_id}>'


class LessonCompletion(db.Model):
   __tablename__ = 'lesson_completions'
   __table_args__ = (
       db.UniqueConstraint('enrollment_id', 'lesson_id', name='unique_lesson_completion'),
       {'extend_existing': True}
   )
   
   id = db.Column(db.Integer, primary_key=True)
   enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollments.id'), nullable=False)
   lesson_id = db.Column(db.Integer, db.ForeignKey('course_lessons.id'), nullable=False)
   completed_at = db.Column(db.DateTime, default=datetime.utcnow)
   
   # Relationships
   enrollment = db.relationship('CourseEnrollment', back_populates='lesson_completions')
   lesson = db.relationship('CourseLesson', back_populates='completions')
   
   def __repr__(self):
       return f'<LessonCompletion {self.enrollment_id}-{self.lesson_id}>'


class CourseCertificate(db.Model):
   __tablename__ = 'course_certificates'
   __table_args__ = {'extend_existing': True}
   
   id = db.Column(db.Integer, primary_key=True)
   enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollments.id'), nullable=False, unique=True)
   certificate_number = db.Column(db.String(100), unique=True)
   issued_at = db.Column(db.DateTime, default=datetime.utcnow)
   
   def __repr__(self):
       return f'<CourseCertificate {self.certificate_number}>'


class CourseReview(db.Model):
   __tablename__ = 'course_reviews'
   __table_args__ = (
       db.UniqueConstraint('user_id', 'course_id', name='unique_review'),
       {'extend_existing': True}
   )
   
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
   rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
   review_text = db.Column(db.Text)
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
   # Relationships
   user = db.relationship('User', backref='course_reviews', foreign_keys=[user_id])
   course = db.relationship('Course', back_populates='reviews')
   
   def __repr__(self):
       return f'<CourseReview {self.user_id}-{self.course_id}>'


# Helper functions for courses
def get_course_categories():
   """Get all course categories"""
   return CourseCategory.query.order_by(CourseCategory.name).all()

def get_courses_by_category(category_id, include_pending=False, limit=None):
   """Get courses by category"""
   query = Course.query.filter_by(category_id=category_id)
   
   if not include_pending:
       query = query.filter_by(status='approved')
   
   query = query.order_by(Course.created_at.desc())
   
   if limit:
       query = query.limit(limit)
   
   return query.all()

def search_courses(query_text, filters=None, limit=None):
   """Search for courses by text and filters"""
   search_query = Course.query.filter(
       (Course.title.ilike(f"%{query_text}%")) | 
       (Course.description.ilike(f"%{query_text}%"))
   )
   
   if filters:
       if 'category' in filters:
           search_query = search_query.filter_by(category_id=filters['category'])
       
       if 'level' in filters:
           search_query = search_query.filter_by(level=filters['level'])
       
       if 'price' in filters:
           if filters['price'] == 'free':
               search_query = search_query.filter_by(is_free=True)
           elif filters['price'] == 'paid':
               search_query = search_query.filter_by(is_free=False)
   
   # Only show approved courses in search
   search_query = search_query.filter_by(status='approved')
   
   search_query = search_query.order_by(Course.created_at.desc())
   
   if limit:
       search_query = search_query.limit(limit)
   
   return search_query.all()

def get_pending_courses():
   """Get courses pending approval"""
   return Course.query.filter_by(status='pending').order_by(Course.created_at).all()

def approve_course(course_id, admin_notes=None):
   """Approve a course"""
   course = Course.query.get(course_id)
   if course:
       course.status = 'approved'
       if admin_notes:
           course.approval_notes = admin_notes
       db.session.commit()
       
       # Create notification for course creator
       notification = Notification(
           user_id=course.creator_id,
           message=f"Your course '{course.title}' has been approved!",
           is_read=False
       )
       db.session.add(notification)
       db.session.commit()
       return True
   return False

def reject_course(course_id, admin_notes):
   """Reject a course"""
   course = Course.query.get(course_id)
   if course:
       course.status = 'rejected'
       course.approval_notes = admin_notes
       db.session.commit()
       
       # Create notification for course creator
       notification = Notification(
           user_id=course.creator_id,
           message=f"Your course '{course.title}' was not approved. Please check the feedback.",
           is_read=False
       )
       db.session.add(notification)
       db.session.commit()
       return True
   return False

def create_course(user_id, course_data):
   """Create a new course"""
   try:
       course = Course(
           title=course_data.get('title'),
           description=course_data.get('description'),
           creator_id=user_id,
           category_id=course_data.get('category_id'),
           level=course_data.get('level'),
           price=course_data.get('price', 0.0),
           is_free=course_data.get('is_free', True),
           is_premium=course_data.get('is_premium', False),
           thumbnail=course_data.get('thumbnail'),
           duration=course_data.get('duration'),
           status='draft'  # Always start as draft
       )
       db.session.add(course)
       db.session.commit()
       return course.id
   except Exception as e:
       print(f"Error creating course: {str(e)}")
       db.session.rollback()
       return None

def submit_course_for_review(course_id):
   """Submit a course for admin review"""
   course = Course.query.get(course_id)
   if course and course.status == 'draft':
       course.status = 'pending'
       db.session.commit()
       
       # Notify admins (you might want to implement this differently)
       # This is just a placeholder for the concept
       admins = User.query.filter_by(is_admin=True).all()
       for admin in admins:
           notification = Notification(
               user_id=admin.id,
               message=f"New course '{course.title}' is pending review",
               is_read=False
           )
           db.session.add(notification)
       
       db.session.commit()
       return True
   return False

def enroll_in_course(user_id, course_id):
   """Enroll a user in a course"""
   # Check if already enrolled
   existing = CourseEnrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
   if existing:
       return existing.id
   
   course = Course.query.get(course_id)
   if not course or course.status != 'approved':
       return None
   
   # Check if it's a premium course and user has premium
   user = User.query.get(user_id)
   if course.is_premium and not user.is_premium():
       return None
   
   # Check if it's a paid course (handle payment separately)
   payment_status = 'free' if course.is_free else 'paid'
   
   enrollment = CourseEnrollment(
       user_id=user_id,
       course_id=course_id,
       payment_status=payment_status
   )
   
   db.session.add(enrollment)
   db.session.commit()
   return enrollment.id

def mark_lesson_complete(user_id, lesson_id):
   """Mark a lesson as complete for a user"""
   import time
   
   lesson = CourseLesson.query.get(lesson_id)
   if not lesson:
       return False
   
   # Find the enrollment
   enrollment = CourseEnrollment.query.filter_by(
       user_id=user_id, 
       course_id=lesson.section.course_id
   ).first()
   
   if not enrollment:
       return False
   
   # Check if already completed
   existing = LessonCompletion.query.filter_by(
       enrollment_id=enrollment.id,
       lesson_id=lesson_id
   ).first()
   
   if not existing:
       # Create new completion
       completion = LessonCompletion(
           enrollment_id=enrollment.id,
           lesson_id=lesson_id
       )
       db.session.add(completion)
       db.session.commit()
       
       # Update progress
       enrollment.calculate_progress()
       db.session.commit()
       
       # If course is now completed, generate certificate
       if enrollment.is_completed and not enrollment.certificate:
           # Generate unique certificate number
           certificate_number = f"CERT-{user_id}-{lesson.section.course_id}-{int(time.time())}"
           
           certificate = CourseCertificate(
               enrollment_id=enrollment.id,
               certificate_number=certificate_number
           )
           db.session.add(certificate)
           db.session.commit()
       
       return True
   
   return False

def get_user_courses(user_id):
   """Get courses created by a user"""
   return Course.query.filter_by(creator_id=user_id).order_by(Course.created_at.desc()).all()

def get_user_enrollments(user_id):
   """Get courses a user is enrolled in"""
   return CourseEnrollment.query.filter_by(user_id=user_id).join(Course).filter(
       Course.status == 'approved'
   ).order_by(CourseEnrollment.enrolled_at.desc()).all()

def get_user_completed_courses(user_id):
   """Get courses a user has completed"""
   return CourseEnrollment.query.filter_by(
       user_id=user_id,
       is_completed=True
   ).join(Course).order_by(CourseEnrollment.completion_date.desc()).all()

def get_course_statistics(course_id):
   """Get statistics for a course"""
   course = Course.query.get(course_id)
   if not course:
       return None
   
   stats = {
       'total_students': course.total_students(),
       'total_lessons': course.total_lessons(),
       'average_rating': course.average_rating(),
       'review_count': len(course.reviews),
       'completion_rate': 0
   }
   
   # Calculate completion rate
   completed_count = CourseEnrollment.query.filter_by(
       course_id=course_id,
       is_completed=True
   ).count()
   
   if stats['total_students'] > 0:
       stats['completion_rate'] = (completed_count / stats['total_students']) * 100
   
   return stats





# Employee-related tables
class Employee(db.Model):
    __tablename__ = 'employees'

    bud_id = db.Column(db.Integer, primary_key=True)  # Unique ID
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    passcode = db.Column(db.String(64), nullable=False)
    profile_picture = db.Column(db.Text, nullable=True, default=DEFAULT_PROFILE_PICTURE) 
