from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import update_academic_progress, update_skill, add_achievement
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import datetime

progress_bp = Blueprint('progress', __name__)

# Forms
class AcademicProgressForm(FlaskForm):
    gpa = FloatField('GPA', validators=[DataRequired(), NumberRange(min=0, max=4.0)])
    credits = IntegerField('Credits', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Progress')

class AchievementForm(FlaskForm):
    title = StringField('Achievement Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Add Achievement')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired()])
    skill_type = StringField('Skill Type', validators=[DataRequired()])
    level = StringField('Level', validators=[DataRequired()])
    percentage = IntegerField('Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Add/Update Skill')

@progress_bp.route('/progress')
@login_required
def progress():
    academic_form = AcademicProgressForm()
    achievement_form = AchievementForm()
    skill_form = SkillForm()
    
    # Set current values for academic form
    academic_form.gpa.data = current_user.gpa
    academic_form.credits.data = current_user.credits
    
    # Prepare the data for the template
    academic_progress = {
        'gpa': current_user.gpa,
        'credits': current_user.credits,
        'total_credits': current_user.total_credits,
        'progress_percentage': (current_user.credits / current_user.total_credits) * 100 if current_user.total_credits > 0 else 0
    }
    
    # Get academic progress details
    current_courses = current_user.current_courses
    
    # Get professional journey
    internships = current_user.internships
    job_applications = current_user.job_applications
    
    # Get skills
    technical_skills = current_user.skills.get('technical', {})
    soft_skills = current_user.skills.get('soft', {})
    
    # Get achievements
    achievements = sorted(current_user.achievements, 
                       key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d') if isinstance(x['date'], str) else x['date'],
                       reverse=True)
    
    # Get certificates (from skills or a separate field)
    certificates = [] # This would be populated from the database
    
    return render_template(
        'progress.html',
        title='Progress Tracker',
        academic_progress=academic_progress,
        current_courses=current_courses,
        internships=internships,
        job_applications=job_applications,
        technical_skills=technical_skills,
        soft_skills=soft_skills,
        achievements=achievements,
        certificates=certificates,
        academic_form=academic_form,
        achievement_form=achievement_form,
        skill_form=skill_form
    )

@progress_bp.route('/progress/update_academic', methods=['POST'])
@login_required
def update_academic():
    form = AcademicProgressForm()
    
    if form.validate_on_submit():
        gpa = form.gpa.data
        credits = form.credits.data
        
        # This would typically include current courses data as well
        current_courses = current_user.current_courses
        
        if update_academic_progress(current_user.id, gpa, credits, current_courses):
            flash('Academic progress updated successfully!', 'success')
        else:
            flash('Failed to update academic progress', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('progress.progress'))

@progress_bp.route('/progress/add_achievement', methods=['POST'])
@login_required
def add_achievement_route():
    form = AchievementForm()
    
    if form.validate_on_submit():
        title = form.title.data
        date = form.date.data.strftime('%Y-%m-%d')
        
        if add_achievement(current_user.id, title, date):
            flash('Achievement added successfully!', 'success')
        else:
            flash('Failed to add achievement', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('progress.progress'))

@progress_bp.route('/progress/update_skill', methods=['POST'])
@login_required
def update_skill_route():
    form = SkillForm()
    
    if form.validate_on_submit():
        name = form.name.data
        skill_type = form.skill_type.data
        level = form.level.data
        percentage = form.percentage.data
        
        if update_skill(current_user.id, name, skill_type, level, percentage):
            flash('Skill updated successfully!', 'success')
        else:
            flash('Failed to update skill', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('progress.progress'))