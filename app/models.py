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


def analyze_resume_ats(resume_id, user_id, job_description=None):
    """
    Analyze a resume against ATS systems and potentially a job description
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return False
            
        # Get resume sections and skills
        sections = ResumeSection.query.filter_by(resume_id=resume_id).all()
        skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()
        
        # Basic checks - these would be more sophisticated in a real implementation
        has_contact = True  # Assume user profile has contact info
        has_experience = any(section.type == 'experience' for section in sections)
        has_education = any(section.type == 'education' for section in sections)
        has_skills = len(skills) > 0
        bullet_count = sum(len(section.bullets) for section in sections)
        has_enough_bullets = bullet_count >= 5
        
        # Calculate basic ATS score - this would be more sophisticated in reality
        base_score = 0
        if has_contact: base_score += 20
        if has_experience: base_score += 25
        if has_education: base_score += 20
        if has_skills: base_score += 15
        if has_enough_bullets: base_score += 20
        
        # Calculate more sophisticated score if job description is provided
        job_match_score = 0
        feedback = []
        
        if job_description:
            # This simulates keyword matching - in a real implementation, 
            # you'd use more sophisticated NLP
            job_description = job_description.lower()
            skill_matches = 0
            
            for skill in skills:
                if skill.skill_name.lower() in job_description:
                    skill_matches += 1
            
            # Calculate match percentage
            if skills:
                match_percentage = (skill_matches / len(skills)) * 100
                job_match_score = min(30, match_percentage * 0.3)  # Max 30 points from keyword matching
            
            # Add feedback based on analysis
            if skill_matches < len(skills) * 0.3:
                feedback.append("Your skills don't strongly match the job description. Consider adding more relevant skills.")
            
            if not has_experience:
                feedback.append("Add professional experience to improve your resume's strength.")
            
            if bullet_count < 10:
                feedback.append("Add more bullet points to detail your experiences.")
        else:
            # General feedback without job description
            if not has_experience:
                feedback.append("Add professional experience to improve your resume's strength.")
            
            if not has_education:
                feedback.append("Add your educational background.")
                
            if not has_skills:
                feedback.append("Add your technical and soft skills.")
                
            if bullet_count < 5:
                feedback.append("Add more details to your experiences with bullet points.")
        
        # Calculate final score
        final_score = min(100, base_score + job_match_score)
        
        # Update resume with score and feedback
        resume.ats_score = final_score
        resume.feedback = "\n".join(feedback) if feedback else "Your resume meets basic ATS requirements."
        db.session.commit()
        
        return {
            'score': final_score,
            'feedback': resume.feedback
        }
    except Exception as e:
        print(f"Error analyzing resume: {type(e).__name__} - {str(e)}")
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