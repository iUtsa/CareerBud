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
    
def advanced_ats_analyzer(resume_id, user_id, job_description=None, industry=None, company_size=None):
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
    
    # Count matching requirements
    matches = sum(1 for req in requirements if req.lower() in experience_text)
    
    # Calculate score (30 points max)
    relevance_score = min(30, (matches / len(requirements)) * 30)
    
    return relevance_score

def extract_requirements_from_job(job_description):
    """Extracts key requirements from a job description"""
    requirements = []
    
    # Look for common requirement indicators
    requirement_sections = []
    lines = job_description.split('\n')
    
    in_requirements = False
    for line in lines:
        line_lower = line.lower()
        
        # Check for section headers
        if any(header in line_lower for header in ['requirements', 'qualifications', 'what you need', 'skills required']):
            in_requirements = True
            requirement_sections.append([])
        elif in_requirements and any(header in line_lower for header in ['benefits', 'about us', 'what we offer', 'compensation']):
            in_requirements = False
        
        if in_requirements and line.strip():
            requirement_sections[-1].append(line)
    
    # If no structured requirements found, use NLP techniques to extract them
    if not requirement_sections:
        # Look for bullet points
        bullets = re.findall(r'[•\-\*]\s+(.*?)(?=(?:[•\-\*])|$)', job_description, re.DOTALL)
        if bullets:
            requirement_sections.append(bullets)
        else:
            # Fall back to sentence-based extraction
            sentences = re.split(r'[.!?]\s+', job_description)
            requirement_sentences = [s for s in sentences if any(req in s.lower() for req in 
                                   ['experience', 'skill', 'knowledge', 'ability', 'proficient', 
                                    'familiar', 'degree', 'education', 'qualified'])]
            if requirement_sentences:
                requirement_sections.append(requirement_sentences)
    
    # Process requirement sections
    for section in requirement_sections:
        for item in section:
            # Clean up the item
            item = item.strip()
            if not item:
                continue
                
            # Remove bullets and numbers
            item = re.sub(r'^[•\-\*\d.]+\s*', '', item)
            
            # Split compound requirements
            if ' and ' in item:
                parts = item.split(' and ')
                requirements.extend(parts)
            else:
                requirements.append(item)
    
    # Remove duplicates and short entries
    requirements = [req for req in requirements if len(req) > 5]
    requirements = list(set(requirements))
    
    return requirements

def extract_keywords_from_job_description(job_description, max_keywords=15):
    """Extracts important keywords from job description"""
    # In a production system, this would use NLP or ML techniques
    # For this example, we'll use a simpler approach
    
    # Define common keyword categories
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'express',
        'django', 'flask', 'spring', 'hibernate', 'sql', 'nosql', 'mongodb', 'postgresql',
        'mysql', 'oracle', 'aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes',
        'ci/cd', 'jenkins', 'git', 'agile', 'scrum', 'devops', 'machine learning',
        'deep learning', 'tensorflow', 'pytorch', 'nlp', 'data science', 'analytics',
        'blockchain', 'ios', 'android', 'mobile', 'responsive', 'frontend', 'backend',
        'fullstack', 'ui/ux', 'design', 'photoshop', 'illustrator', 'figma', 'sketch'
    ]
    
    experience_keywords = [
        'manager', 'senior', 'junior', 'lead', 'architect', 'supervisor', 'director',
        'coordinator', 'specialist', 'analyst', 'consultant', 'administrator', 'developer',
        'engineer', 'designer', 'product', 'project', 'program', 'researcher', 'scientist',
        'head', 'chief', 'vp', 'president', 'executive', 'associate', 'assistant'
    ]
    
    domain_keywords = [
        'finance', 'healthcare', 'banking', 'insurance', 'retail', 'e-commerce',
        'manufacturing', 'logistics', 'transportation', 'education', 'government',
        'non-profit', 'media', 'entertainment', 'gaming', 'sports', 'technology',
        'telecom', 'energy', 'utilities', 'real estate', 'construction', 'legal',
        'consulting', 'marketing', 'advertising', 'hospitality', 'travel', 'automotive'
    ]
    
    soft_skill_keywords = [
        'communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking',
        'creativity', 'time management', 'organization', 'adaptability', 'flexibility',
        'interpersonal', 'presentation', 'writing', 'negotiation', 'conflict resolution',
        'decision making', 'analytical', 'attention to detail', 'self-motivated', 'initiative'
    ]
    
    # Combine all keywords
    all_keywords = skill_keywords + experience_keywords + domain_keywords + soft_skill_keywords
    
    # Find matches in job description
    matches = []
    job_desc_lower = job_description.lower()
    
    for keyword in all_keywords:
        if keyword in job_desc_lower:
            matches.append(keyword)
    
    # Extract job title (usually at the beginning)
    job_title = extract_job_titles(job_description)
    if job_title:
        matches = job_title + [m for m in matches if m not in job_title]
    
    # Prioritize keywords that appear multiple times
    keyword_counts = {}
    for keyword in matches:
        count = job_desc_lower.count(keyword)
        keyword_counts[keyword] = count
    
    # Sort by count and limit to max_keywords
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [k for k, v in sorted_keywords[:max_keywords]]
    
    return top_keywords

def extract_job_titles(job_description):
    """Extracts potential job titles from job description"""
    common_titles = [
        'software engineer', 'software developer', 'frontend developer', 'backend developer',
        'full stack developer', 'data scientist', 'data analyst', 'machine learning engineer',
        'devops engineer', 'systems administrator', 'network engineer', 'security engineer',
        'product manager', 'project manager', 'program manager', 'business analyst',
        'marketing manager', 'sales manager', 'account executive', 'customer success manager',
        'ux designer', 'ui designer', 'graphic designer', 'content writer', 'content strategist'
    ]
    
    # Check first few lines for job title
    first_lines = job_description.split('\n')[:3]
    first_paragraph = ' '.join(first_lines).lower()
    
    found_titles = []
    for title in common_titles:
        if title in first_paragraph:
            found_titles.append(title)
            
    # If nothing found in first paragraph, check entire text
    if not found_titles:
        job_desc_lower = job_description.lower()
        for title in common_titles:
            if title in job_desc_lower:
                found_titles.append(title)
    
    return found_titles

def get_keyword_variations(keyword):
    """Generates variations of a keyword for more flexible matching"""
    variations = [keyword]
    
    # Simple singular/plural variations
    if keyword.endswith('s'):
        variations.append(keyword[:-1])  # Remove trailing 's'
    else:
        variations.append(keyword + 's')  # Add trailing 's'
        
    # Common verb forms
    if keyword.endswith('ing'):
        variations.append(keyword[:-3])  # develop from developing
        variations.append(keyword[:-3] + 'e')  # manage from managing
        
    if keyword.endswith('ed'):
        variations.append(keyword[:-2])  # develop from developed
        variations.append(keyword[:-1])  # manage from managed
        
    # Adjective variations
    if keyword.endswith('ability'):
        variations.append(keyword[:-5] + 'le')  # scalable from scalability
        
    # Remove duplicates and empty strings
    variations = [v for v in variations if v]
    variations = list(set(variations))
    
    return variations

def get_industry_skills(industry):
    """Returns common skills for a specific industry"""
    industry_skills = {
        'tech': ['programming', 'software development', 'agile', 'scrum', 'cloud', 'architecture'],
        'finance': ['financial analysis', 'banking', 'investment', 'portfolio management', 'risk assessment'],
        'healthcare': ['patient care', 'medical terminology', 'clinical', 'hipaa', 'electronic health records'],
        'marketing': ['digital marketing', 'social media', 'content strategy', 'seo', 'analytics'],
        'retail': ['merchandising', 'inventory management', 'pos', 'sales', 'customer service'],
        'manufacturing': ['quality control', 'lean', 'six sigma', 'supply chain', 'production planning'],
        'consulting': ['client management', 'business analysis', 'requirements gathering', 'stakeholder management']
    }
    
    return industry_skills.get(industry.lower(), [])

def get_industry_keywords(industry):
    """Returns common keywords for a specific industry"""
    industry_keywords = {
        'tech': ['innovation', 'digital transformation', 'cutting-edge', 'technical', 'startup'],
        'finance': ['revenue', 'profit', 'budget', 'forecasting', 'compliance'],
        'healthcare': ['patient', 'care', 'medical', 'clinical', 'treatment'],
        'marketing': ['campaign', 'audience', 'engagement', 'conversion', 'brand'],
        'retail': ['customer', 'sales', 'merchandise', 'inventory', 'ecommerce'],
        'manufacturing': ['production', 'efficiency', 'quality', 'process improvement', 'operations'],
        'consulting': ['client', 'solution', 'strategy', 'deliverable', 'engagement']
    }
    
    return industry_keywords.get(industry.lower(), [])

def calculate_industry_weights(industry, company_size, has_job_description):
    """Calculates scoring weights based on industry and company size"""
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
    
    # Adjust weights based on industry
    if industry:
        industry = industry.lower()
        if industry == 'tech':
            weights['skills_score'] += 5
            weights['projects_score'] += 5
            weights['experience_score'] -= 5
            weights['education_score'] -= 5
        elif industry == 'finance':
            weights['education_score'] += 5
            weights['format_score'] += 5
            weights['projects_score'] -= 5
            weights['impact_score'] -= 5
        elif industry == 'creative':
            weights['projects_score'] += 10
            weights['impact_score'] += 5
            weights['format_score'] -= 5
            weights['education_score'] -= 10
            
    # Adjust weights based on company size
    if company_size:
        company_size = company_size.lower()
        if company_size == 'startup':
            weights['skills_score'] += 5
            weights['impact_score'] += 5
            weights['format_score'] -= 5
            weights['education_score'] -= 5
        elif company_size == 'enterprise':
            weights['format_score'] += 5
            weights['education_score'] += 5
            weights['skills_score'] -= 5
            weights['projects_score'] -= 5
            
    # Normalize weights to sum to 100
    total = sum(weights.values())
    weights = {k: (v / total) * 100 for k, v in weights.items()}
    
    return weights

def calculate_weighted_score(metrics, weights):
    """Calculates overall score based on metrics and weights"""
    score = 0
    
    for metric, weight in weights.items():
        if metric in metrics and metrics[metric] is not None:
            score += (metrics[metric] * weight / 100)
            
    return min(100, max(0, score))

def generate_comprehensive_feedback(metrics, overall_score):
    """Generates comprehensive feedback based on metrics and score"""
    overall = []
    improvements = []
    ats_tips = []
    
    # Overall assessment
    if overall_score >= 90:
        overall.append("Excellent resume that should perform very well with ATS systems and hiring managers.")
    elif overall_score >= 80:
        overall.append("Strong resume that meets most ATS requirements and should pass automated screening.")
    elif overall_score >= 70:
        overall.append("Good resume with some areas for improvement to enhance ATS performance.")
    elif overall_score >= 60:
        overall.append("Average resume that may pass some ATS systems but needs improvements to be competitive.")
    else:
        overall.append("Below average resume that needs significant improvements to pass ATS screening.")
    
    # Add section-specific feedback
    if metrics['format_score'] < 70:
        improvements.append("Improve resume structure and formatting for better ATS compatibility.")
        ats_tips.append("Use standard section headings (Experience, Education, Skills) that ATS systems recognize.")
    
    if metrics['keyword_score'] < 70 and metrics['relevance_score'] is not None:
        improvements.append("Add more relevant keywords that match the job description requirements.")
        ats_tips.append("Most ATS systems rank resumes based on keyword matching. Include exact phrases from the job posting.")
    
    if metrics['skills_score'] < 70:
        improvements.append("Enhance your skills section with more industry-relevant skills.")
        ats_tips.append("List both technical skills and soft skills, and organize them by category for better readability.")
    
    if metrics['experience_score'] < 70:
        improvements.append("Strengthen your experience section with more accomplishments and results.")
        ats_tips.append("Begin each bullet point with a strong action verb and include measurable achievements.")
    
    if metrics['education_score'] < 70:
        improvements.append("Provide more details in your education section, including relevant coursework.")
    
    if metrics['impact_score'] < 60:
        improvements.append("Add more measurable achievements to demonstrate your impact.")
        ats_tips.append("Quantify your achievements with numbers, percentages, and metrics wherever possible.")
    
    if metrics['action_verb_usage'] < 60:
        improvements.append("Use more action verbs at the beginning of your bullet points.")
    
    if metrics['quantification_score'] < 50:
        improvements.append("Include more numbers and metrics to quantify your achievements.")
    
    if metrics['readability_score'] < 70:
        improvements.append("Improve the readability of your bullet points with clearer, more concise language.")
        ats_tips.append("Use clean, simple formatting and avoid tables, headers, footers, and graphics that ATS may not process correctly.")
    
    # Add missing keywords suggestion if applicable
    if metrics['missing_keywords'] and len(metrics['missing_keywords']) > 0:
        keyword_list = ', '.join(metrics['missing_keywords'][:5])
        improvements.append(f"Add these missing keywords from the job description: {keyword_list}.")
    
    # General ATS tips
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