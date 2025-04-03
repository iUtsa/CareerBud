from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import get_courses, update_academic_progress
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired

courses_bp = Blueprint('courses', __name__)

class EnrollCourseForm(FlaskForm):
    course_id = StringField('Course ID', validators=[DataRequired()])
    submit = SubmitField('Enroll')

@courses_bp.route('/courses')
@login_required
def courses():
    form = EnrollCourseForm()
    
    # Get all available courses
    all_courses = get_courses()
    
    # Filter courses based on subscription tier
    if current_user.is_premium:
        available_courses = all_courses
    else:
        # For free tier, filter out premium courses or limit the number
        available_courses = [course for course in all_courses if not course.get('premium_only', False)]
    
    # Get user's current courses
    current_courses = current_user.current_courses
    current_course_ids = [course.get('id') for course in current_courses]
    
    return render_template(
        'courses.html',
        title='Courses',
        available_courses=available_courses,
        current_courses=current_courses,
        current_course_ids=current_course_ids,
        form=form,
        is_premium=current_user.is_premium
    )

@courses_bp.route('/courses/enroll', methods=['POST'])
@login_required
def enroll():
    form = EnrollCourseForm()
    
    if form.validate_on_submit():
        course_id = form.course_id.data
        
        # Get course details
        all_courses = get_courses()
        course = next((c for c in all_courses if c.get('id') == course_id), None)
        
        if not course:
            flash('Course not found', 'danger')
            return redirect(url_for('courses.courses'))
        
        # Check if premium course and user has premium subscription
        if course.get('premium_only', False) and not current_user.is_premium:
            flash('This course requires a premium subscription', 'warning')
            return redirect(url_for('subscription.plans'))
        
        # Check if already enrolled
        current_course_ids = [c.get('id') for c in current_user.current_courses]
        if course_id in current_course_ids:
            flash('You are already enrolled in this course', 'info')
            return redirect(url_for('courses.courses'))
        
        # Add course to user's current courses
        current_courses = current_user.current_courses
        current_courses.append({
            'id': course_id,
            'name': course.get('name'),
            'progress': 0,
            'grade': None
        })
        
        # Update user's courses in database
        if update_academic_progress(
            current_user.id, 
            current_user.gpa, 
            current_user.credits, 
            current_courses
        ):
            flash(f'Successfully enrolled in {course.get("name")}!', 'success')
        else:
            flash('Failed to enroll in course', 'danger')
    
    return redirect(url_for('courses.courses'))

@courses_bp.route('/courses/unenroll', methods=['POST'])
@login_required
def unenroll():
    course_id = request.form.get('course_id')
    
    if not course_id:
        flash('Course ID is required', 'danger')
        return redirect(url_for('courses.courses'))
    
    # Remove course from user's current courses
    current_courses = [c for c in current_user.current_courses if c.get('id') != course_id]
    
    # Get course name for flash message
    removed_course = next((c for c in current_user.current_courses if c.get('id') == course_id), None)
    course_name = removed_course.get('name', 'the course') if removed_course else 'the course'
    
    # Update user's courses in database
    if update_academic_progress(
        current_user.id, 
        current_user.gpa, 
        current_user.credits, 
        current_courses
    ):
        flash(f'Successfully unenrolled from {course_name}', 'success')
    else:
        flash('Failed to unenroll from course', 'danger')
    
    return redirect(url_for('courses.courses'))