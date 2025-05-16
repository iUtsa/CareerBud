from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import (
    # Import the models and functions we created
    Course, CourseCategory, CourseSection, CourseLesson, CourseEnrollment,
    CourseCertificate, CourseReview, LessonCompletion,
    get_course_categories, get_courses_by_category, search_courses,
    get_pending_courses, approve_course, reject_course, create_course,
    submit_course_for_review, enroll_in_course, mark_lesson_complete,
    get_user_courses, get_user_enrollments, get_user_completed_courses,
    get_course_statistics
)
from werkzeug.utils import secure_filename
import os
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField, FloatField, SelectField, BooleanField, FileField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime
import uuid
import time
from app.extensions import db

coursebud_bp = Blueprint('coursebud', __name__, url_prefix='/coursebud')

# Form classes
class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=5, max=255)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    level = SelectField('Level', choices=[
        ('beginner', 'Beginner'), 
        ('intermediate', 'Intermediate'), 
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    price = FloatField('Price', validators=[Optional(), NumberRange(min=0)])
    is_free = BooleanField('Free Course')
    is_premium = BooleanField('Premium (Subscription) Course')
    duration = StringField('Estimated Duration', validators=[Optional()])
    thumbnail = FileField('Course Thumbnail')
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in get_course_categories()]

class CourseSectionForm(FlaskForm):
    title = StringField('Section Title', validators=[DataRequired(), Length(min=3, max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Changes')

class CourseLessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired(), Length(min=3, max=255)])
    content_type = SelectField('Content Type', choices=[
        ('video', 'Video'), 
        ('text', 'Text Content'),
        ('quiz', 'Quiz'),
        ('resource', 'Downloadable Resource')
    ], validators=[DataRequired()])
    content = TextAreaField('Content/URL', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[Optional(), NumberRange(min=0)])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    is_free_preview = BooleanField('Free Preview Lesson')

class CourseReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (1, '1 - Poor'), 
        (2, '2 - Fair'), 
        (3, '3 - Good'), 
        (4, '4 - Very Good'), 
        (5, '5 - Excellent')
    ], coerce=int, validators=[DataRequired()])
    review_text = TextAreaField('Your Review', validators=[Optional(), Length(max=1000)])

class CourseSearchForm(FlaskForm):
    query = StringField('Search Courses', validators=[Optional()])
    # Change this line to make the coerce function handle empty strings
    category = SelectField('Category', validators=[Optional()], coerce=lambda x: int(x) if x else None)
    level = SelectField('Level', choices=[
        ('', 'All Levels'),
        ('beginner', 'Beginner'), 
        ('intermediate', 'Intermediate'), 
        ('advanced', 'Advanced')
    ], validators=[Optional()])
    price = SelectField('Price', choices=[
        ('', 'All Prices'),
        ('free', 'Free'), 
        ('paid', 'Paid')
    ], validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(CourseSearchForm, self).__init__(*args, **kwargs)
        categories = get_course_categories()
        self.category.choices = [('', 'All Categories')] + [(str(c.id), c.name) for c in categories]


class EditLessonForm(FlaskForm):
    lesson_id = HiddenField()
    title = StringField('Lesson Title', validators=[DataRequired()])
    content_type = SelectField('Content Type', choices=[
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('resource', 'Resource')
    ])
    content = TextAreaField('Content', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)')
    is_free_preview = BooleanField('Free Preview')

# Routes
@coursebud_bp.route('/')
def index():
    """CourseBud home page with featured courses"""
    search_form = CourseSearchForm()
    
    # Get some featured courses (newest approved courses)
    featured_courses = Course.query.filter_by(status='approved').order_by(Course.created_at.desc()).limit(6).all()
    
    # Get categories with course counts
    categories = get_course_categories()
    
    # Get trending (most enrolled) courses
    trending_courses = Course.query.filter_by(status='approved').join(
        CourseEnrollment
    ).group_by(Course.id).order_by(db.func.count(CourseEnrollment.id).desc()).limit(4).all()
    
    return render_template(
        'coursebud/index.html',
        title='CourseBud - Learn & Teach',
        featured_courses=featured_courses,
        trending_courses=trending_courses,
        categories=categories,
        search_form=search_form
    )

@coursebud_bp.route('/explore')
def explore():
    """Explore courses with search and filters"""
    search_form = CourseSearchForm(request.args)
    
    # Process search and filters
    query = request.args.get('query', '')
    category_id = request.args.get('category', '')
    level = request.args.get('level', '')
    price = request.args.get('price', '')
    
    filters = {}
    if category_id and category_id != '':
        filters['category'] = int(category_id)
    if level and level != '':
        filters['level'] = level
    if price and price != '':
        filters['price'] = price
    
    # Search courses
    if query:
        courses = search_courses(query, filters)
    elif filters:
        # Apply filters only
        courses = Course.query.filter_by(status='approved')
        
        if 'category' in filters:
            courses = courses.filter_by(category_id=filters['category'])
        if 'level' in filters:
            courses = courses.filter_by(level=filters['level'])
        if 'price' in filters:
            if filters['price'] == 'free':
                courses = courses.filter_by(is_free=True)
            elif filters['price'] == 'paid':
                courses = courses.filter_by(is_free=False)
                
        courses = courses.order_by(Course.created_at.desc()).all()
    else:
        # No search or filters, show recent courses
        courses = Course.query.filter_by(status='approved').order_by(Course.created_at.desc()).limit(20).all()
    
    # Get categories for filters
    categories = get_course_categories()
    
    return render_template(
        'coursebud/explore.html',
        title='Explore Courses',
        courses=courses,
        categories=categories,
        search_form=search_form
    )

@coursebud_bp.route('/course/<int:course_id>')
def view_course(course_id):
    """View a course details page"""
    course = Course.query.get_or_404(course_id)
    
    # Only show approved courses to regular users
    if course.status != 'approved' and (not current_user.is_authenticated or 
                                      (course.creator_id != current_user.id and not current_user.is_admin)):
        flash('This course is not available.', 'warning')
        return redirect(url_for('coursebud.index'))
    
    # Check if user is enrolled
    is_enrolled = False
    user_progress = 0
    enrollment = None
    
    if current_user.is_authenticated:
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()
        
        if enrollment:
            is_enrolled = True
            user_progress = enrollment.progress
    
    # Get course reviews
    reviews = CourseReview.query.filter_by(course_id=course_id).order_by(CourseReview.created_at.desc()).all()
    
    # Get course statistics
    stats = get_course_statistics(course_id)
    
    # Review form for enrolled users
    review_form = None
    if is_enrolled:
        # Check if user already left a review
        user_review = CourseReview.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        if not user_review:
            review_form = CourseReviewForm()
    
    return render_template(
        'coursebud/view_course.html',
        title=course.title,
        course=course,
        is_enrolled=is_enrolled,
        user_progress=user_progress,
        enrollment=enrollment,
        reviews=reviews,
        stats=stats,
        review_form=review_form
    )

@coursebud_bp.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def course_enroll(course_id):
    """Enroll in a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if course is approved
    if course.status != 'approved':
        flash('This course is not available for enrollment.', 'warning')
        return redirect(url_for('coursebud.view_course', course_id=course_id))
    
    # Check if user is already enrolled
    existing = CourseEnrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if existing:
        flash('You are already enrolled in this course!', 'info')
        return redirect(url_for('coursebud.learn', course_id=course_id))
    
    # Check if premium course and user has premium
    if course.is_premium and not current_user.is_premium():
        flash('This course requires a premium subscription.', 'warning')
        return redirect(url_for('subscription.plans'))
    
    # Check if paid course (handle payment)
    if not course.is_free and not course.is_premium:
        # Placeholder for payment processing
        # In a real implementation, redirect to payment page
        flash('This is a paid course. Payment functionality is not implemented yet.', 'warning')
        return redirect(url_for('coursebud.view_course', course_id=course_id))
    
    # Enroll user
    enrollment_id = enroll_in_course(current_user.id, course_id)
    
    if enrollment_id:
        flash(f'Successfully enrolled in {course.title}!', 'success')
        return redirect(url_for('coursebud.learn', course_id=course_id))
    else:
        flash('Failed to enroll in the course. Please try again.', 'danger')
        return redirect(url_for('coursebud.view_course', course_id=course_id))

@coursebud_bp.route('/learn/<int:course_id>')
@login_required
def learn(course_id):
    """Learning interface for an enrolled course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is enrolled
    enrollment = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        flash('You are not enrolled in this course.', 'warning')
        return redirect(url_for('coursebud.view_course', course_id=course_id))
    
    # Get sections and lessons
    sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.order).all()
    
    # Get completed lessons
    completed_lesson_ids = [
        completion.lesson_id for completion in LessonCompletion.query.filter_by(
            enrollment_id=enrollment.id
        ).all()
    ]
    
    # Find current lesson (first incomplete or last completed)
    current_lesson = None
    for section in sections:
        for lesson in section.lessons:
            if lesson.id not in completed_lesson_ids:
                current_lesson = lesson
                break
        if current_lesson:
            break
    
    # If all lessons completed, show the last lesson
    if not current_lesson and sections and sections[0].lessons:
        last_section = sections[-1]
        if last_section.lessons:
            current_lesson = last_section.lessons[-1]
    
    return render_template(
        'coursebud/learn.html',
        title=f'Learning: {course.title}',
        course=course,
        sections=sections,
        current_lesson=current_lesson,
        enrollment=enrollment,
        completed_lesson_ids=completed_lesson_ids
    )

@coursebud_bp.route('/learn/<int:course_id>/lesson/<int:lesson_id>')
@login_required
def view_lesson(course_id, lesson_id):
    """View a specific lesson"""
    course = Course.query.get_or_404(course_id)
    lesson = CourseLesson.query.get_or_404(lesson_id)
    
    # Verify lesson belongs to course
    section = lesson.section
    if section.course_id != course_id:
        flash('Lesson not found in this course.', 'danger')
        return redirect(url_for('coursebud.learn', course_id=course_id))
    
    # Check if user is enrolled
    enrollment = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        # Check if this is a free preview lesson
        if not lesson.is_free_preview:
            flash('You need to enroll in this course to access this lesson.', 'warning')
            return redirect(url_for('coursebud.view_course', course_id=course_id))
    
    # Get sections and lessons for navigation
    sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.order).all()
    
    # Get completed lessons
    completed_lesson_ids = []
    if enrollment:
        completed_lesson_ids = [
            completion.lesson_id for completion in LessonCompletion.query.filter_by(
                enrollment_id=enrollment.id
            ).all()
        ]
    
    # Find next and previous lessons
    next_lesson = None
    prev_lesson = None
    found_current = False
    
    for s in sections:
        for l in s.lessons:
            if found_current:
                next_lesson = l
                break
            elif l.id == lesson_id:
                found_current = True
            else:
                prev_lesson = l
        if found_current and next_lesson:
            break
    
    return render_template(
        'coursebud/lesson.html',
        title=lesson.title,
        course=course,
        lesson=lesson,
        sections=sections,
        enrollment=enrollment,
        completed_lesson_ids=completed_lesson_ids,
        next_lesson=next_lesson,
        prev_lesson=prev_lesson
    )

@coursebud_bp.route('/learn/<int:course_id>/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(course_id, lesson_id):
    """Mark a lesson as complete"""
    # Check if user is enrolled
    enrollment = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        return jsonify({'success': False, 'message': 'You are not enrolled in this course'})
    
    # Mark lesson as complete
    success = mark_lesson_complete(current_user.id, lesson_id)
    
    if success:
        # Check if course is now completed
        enrollment = CourseEnrollment.query.get(enrollment.id)  # Refresh
        
        if enrollment.is_completed:
            return jsonify({
                'success': True, 
                'progress': enrollment.progress,
                'completed': True,
                'message': 'Congratulations! You have completed the course.'
            })
        
        return jsonify({'success': True, 'progress': enrollment.progress})
    
    return jsonify({'success': False, 'message': 'Failed to mark lesson as complete'})

@coursebud_bp.route('/learn/<int:course_id>/certificate')
@login_required
def view_certificate(course_id):
    """View course completion certificate"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is enrolled and completed the course
    enrollment = CourseEnrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        is_completed=True
    ).first()
    
    if not enrollment:
        flash('You have not completed this course yet.', 'warning')
        return redirect(url_for('coursebud.learn', course_id=course_id))
    
    # Get certificate
    certificate = CourseCertificate.query.filter_by(enrollment_id=enrollment.id).first()
    
    if not certificate:
        flash('Certificate not found. Please contact support.', 'warning')
        return redirect(url_for('coursebud.learn', course_id=course_id))
    
    return render_template(
        'coursebud/certificate.html',
        title='Course Certificate',
        course=course,
        certificate=certificate,
        enrollment=enrollment
    )

@coursebud_bp.route('/my-learning')
@login_required
def my_learning():
    """Show user's enrolled courses"""
    # Get user enrollments
    enrollments = get_user_enrollments(current_user.id)
    
    # Separate in-progress and completed courses
    in_progress = []
    completed = []
    
    for enrollment in enrollments:
        if enrollment.is_completed:
            completed.append(enrollment)
        else:
            in_progress.append(enrollment)
    
    return render_template(
        'coursebud/my_learning.html',
        title='My Learning',
        in_progress=in_progress,
        completed=completed
    )

@coursebud_bp.route('/course/<int:course_id>/review', methods=['POST'])
@login_required
def add_review(course_id):
    """Add a review to a course"""
    form = CourseReviewForm(request.form)
    
    if form.validate_on_submit():
        # Check if user is enrolled and allowed to review
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            flash('You need to be enrolled in this course to review it.', 'warning')
            return redirect(url_for('coursebud.view_course', course_id=course_id))
        
        # Check if user already reviewed
        existing = CourseReview.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()
        
        if existing:
            # Update existing review
            existing.rating = form.rating.data
            existing.review_text = form.review_text.data
            db.session.commit()
            flash('Your review has been updated!', 'success')
        else:
            # Create new review
            review = CourseReview(
                user_id=current_user.id,
                course_id=course_id,
                rating=form.rating.data,
                review_text=form.review_text.data
            )
            db.session.add(review)
            db.session.commit()
            flash('Your review has been added!', 'success')
    
    return redirect(url_for('coursebud.view_course', course_id=course_id))

# Instructor routes for creating and managing courses
@coursebud_bp.route('/teach')
@login_required
def teach():
    """Dashboard for course creators"""
    # Get user's created courses
    courses = get_user_courses(current_user.id)
    
    # Separate courses by status
    draft_courses = [c for c in courses if c.status == 'draft']
    pending_courses = [c for c in courses if c.status == 'pending']
    approved_courses = [c for c in courses if c.status == 'approved']
    rejected_courses = [c for c in courses if c.status == 'rejected']
    
    return render_template(
        'coursebud/teach.html',
        title='Teach on CourseBud',
        draft_courses=draft_courses,
        pending_courses=pending_courses,
        approved_courses=approved_courses,
        rejected_courses=rejected_courses
    )

@coursebud_bp.route('/teach/course/new', methods=['GET', 'POST'])
@login_required
def create_new_course():
    """Create a new course"""
    form = CourseForm()
    
    if form.validate_on_submit():
        # Handle thumbnail upload
        thumbnail_filename = None
        if form.thumbnail.data:
            # Save thumbnail
            filename = secure_filename(form.thumbnail.data.filename)
            thumbnail_filename = f"{current_user.id}_{int(time.time())}_{filename}"
            upload_folder = current_app.config['UPLOAD_FOLDER']
            form.thumbnail.data.save(os.path.join(upload_folder, thumbnail_filename))
        
        # Create course
        course_data = {
            'title': form.title.data,
            'description': form.description.data,
            'category_id': form.category_id.data,
            'level': form.level.data,
            'price': form.price.data if not form.is_free.data else 0,
            'is_free': form.is_free.data,
            'is_premium': form.is_premium.data,
            'duration': form.duration.data,
            'thumbnail': thumbnail_filename
        }
        
        course_id = create_course(current_user.id, course_data)
        
        if course_id:
            flash('Course created successfully! Now add sections and lessons.', 'success')
            return redirect(url_for('coursebud.edit_course', course_id=course_id))
        else:
            flash('Failed to create course. Please try again.', 'danger')
    
    return render_template(
        'coursebud/create_course.html',
        title='Create New Course',
        form=form
    )

@coursebud_bp.route('/teach/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit course details"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the creator
    if course.creator_id != current_user.id:
        flash('You can only edit your own courses.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    # Check if course is in editable state
    if course.status not in ['draft', 'rejected']:
        flash('This course cannot be edited in its current state.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        # Handle thumbnail upload
        if form.thumbnail.data:
            # Save thumbnail
            filename = secure_filename(form.thumbnail.data.filename)
            thumbnail_filename = f"{current_user.id}_{int(time.time())}_{filename}"
            upload_folder = current_app.config['UPLOAD_FOLDER']
            form.thumbnail.data.save(os.path.join(upload_folder, thumbnail_filename))
            course.thumbnail = thumbnail_filename
        
        # Update course details
        course.title = form.title.data
        course.description = form.description.data
        course.category_id = form.category_id.data
        course.level = form.level.data
        course.is_free = form.is_free.data
        course.price = form.price.data if not form.is_free.data else 0
        course.is_premium = form.is_premium.data
        course.duration = form.duration.data
        
        db.session.commit()
        flash('Course details updated successfully!', 'success')
        return redirect(url_for('coursebud.manage_course_content', course_id=course_id))
    
    return render_template(
        'coursebud/edit_course.html',
        title='Edit Course',
        form=form,
        course=course
    )

@coursebud_bp.route('/teach/course/<int:course_id>/lesson/<int:lesson_id>/edit', methods=['POST'])
@login_required
def edit_lesson(course_id, lesson_id):
    lesson = CourseLesson.query.get_or_404(lesson_id)

    # Authorization: make sure the current user owns the course
    if lesson.section.course.creator_id != current_user.id:
        flash('You are not authorized to edit this lesson.', 'danger')
        return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

    # Update lesson fields from form data
    lesson.title = request.form.get('title')
    lesson.content_type = request.form.get('content_type')
    lesson.content = request.form.get('content')
    lesson.duration = int(request.form.get('duration') or 0)
    lesson.is_free_preview = 'is_free_preview' in request.form

    db.session.commit()
    form = EditLessonForm()
    flash('Lesson updated successfully.', 'success')
    return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

@coursebud_bp.route('/teach/course/<int:course_id>/edit/section/<int:section_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_section(course_id, section_id):
    """Edit course section details"""
    course = Course.query.get_or_404(course_id)
    section = CourseSection.query.get_or_404(section_id)  # Fix to refer to CourseSection model

    # Check if user is the creator of the course
    if course.creator_id != current_user.id:
        flash('You can only edit your own courses.', 'warning')
        return redirect(url_for('coursebud.manage_course_content'))
    
    # Check if course is in editable state
    if course.status not in ['draft', 'rejected']:
        flash('This course cannot be edited in its current state.', 'warning')
        return redirect(url_for('coursebud.manage_course_content'))

    # Ensure you're modifying the correct section
    if section.course_id != course_id:
        flash('This section does not belong to the specified course.', 'warning')
        return redirect(url_for('coursebud.manage_course_content'))

    # Create form for section edit (assuming you have a form for section)
    sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.order).all()
    
    # Forms for adding new section/lesson
    section_form = CourseSectionForm()
    lesson_form = CourseLessonForm()

    if section_form.validate_on_submit():
        # Update section details
        section.title = section_form.title.data
        section.description = section_form.description.data

        db.session.commit()
        flash('Section details updated successfully!', 'success')
        
        # Redirect to the manage course content page after saving the changes
        return redirect(url_for('coursebud.manage_course_content', course_id=course.id))

    return render_template(
        'coursebud/manage_content.html',
        title='Manage Course Content',
        course=course,
        sections=sections,
        section_form=section_form,
        lesson_form=lesson_form
    )

@coursebud_bp.route('/teach/course/<int:course_id>/content', methods=['GET', 'POST'])
@login_required
def manage_course_content(course_id):
    """Manage course sections and lessons"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the creator
    if course.creator_id != current_user.id:
        flash('You can only manage your own courses.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    # Check if course is in editable state
    if course.status not in ['draft', 'rejected']:
        flash('This course content cannot be edited in its current state.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    if request.method == 'POST':
        if 'edit_section_id' in request.form:
            # ----- Edit Section -----
            section_id = request.form.get('edit_section_id')    
            section = CourseSection.query.get_or_404(section_id)

            if section.course_id != course_id:
                flash('This section does not belong to the specified course.', 'warning')
                return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

            form = CourseSectionForm()
            if form.validate():
                section.title = form.title.data
                section.description = form.description.data
                db.session.commit()
                flash('Section updated successfully!', 'success')
            else:
                flash('Failed to update section. Please check the form.', 'danger')

        elif 'edit_lesson_id' in request.form:
            # ----- Edit Lesson -----
            lesson_id = request.form.get('edit_lesson_id')
            lesson = CourseLesson.query.get_or_404(lesson_id)

            if lesson.section.course_id != course_id:
                flash('This lesson does not belong to the specified course.', 'warning')
                return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

            lesson.title = request.form.get('title')
            lesson.content_type = request.form.get('content_type')
            lesson.content = request.form.get('content')
            lesson.duration = int(request.form.get('duration') or 0)
            lesson.is_free_preview = 'is_free_preview' in request.form
            db.session.commit()
            flash('Lesson updated successfully!', 'success')

        else:
            flash('No valid edit target specified.', 'danger')
    # Get sections and lessons
    sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.order).all()
    
    # Forms for adding new section/lesson
    section_form = CourseSectionForm()
    lesson_form = CourseLessonForm()

    return render_template(
        'coursebud/manage_content.html',
        title='Manage Course Content',
        course=course,
        sections=sections,
        section_form=section_form,
        lesson_form=lesson_form
    )

@coursebud_bp.route('/teach/course/<int:course_id>/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(course_id, lesson_id):
    lesson = CourseLesson.query.get_or_404(lesson_id)

    # Authorization: Only course creator can delete
    if lesson.section.course.creator_id != current_user.id:
        flash('You are not authorized to delete this lesson.', 'danger')
        return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully.', 'success')
    return redirect(url_for('coursebud.manage_course_content', course_id=course_id))


@coursebud_bp.route('/teach/course/<int:course_id>/section/<int:section_id>/delete', methods=['POST'])
@login_required
def delete_section(course_id, section_id):
    section = CourseSection.query.get_or_404(section_id)

    if section.course.creator_id != current_user.id:
        flash('You are not authorized to delete this section.', 'danger')
        return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

    # Delete lessons first
    for lesson in section.lessons:
        db.session.delete(lesson)

    db.session.delete(section)
    db.session.commit()
    flash('Section and all its lessons were deleted.', 'success')
    return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

@coursebud_bp.route('/teach/course/<int:course_id>/section/add', methods=['POST'])
@login_required
def add_section(course_id):
    """Add a new section to a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the creator
    if course.creator_id != current_user.id:
        flash('You can only manage your own courses.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    # Check if course is in editable state
    if course.status not in ['draft', 'rejected']:
        flash('This course content cannot be edited in its current state.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    form = CourseSectionForm(request.form)
    
    if form.validate_on_submit():
        # Get max order if not provided
        order = form.order.data
        if order is None:
            max_order = db.session.query(db.func.max(CourseSection.order)).filter_by(course_id=course_id).scalar() or 0
            order = max_order + 1
        
        # Create section
        section = CourseSection(
            course_id=course_id,
            title=form.title.data,
            description=form.description.data,
            order=order
        )
        
        db.session.add(section)
        db.session.commit()
        flash('Section added successfully!', 'success')
    else:
        flash('Failed to add section. Please check the form.', 'danger')
    
    return redirect(url_for('coursebud.manage_course_content', course_id=course_id))

@coursebud_bp.route('/teach/section/<int:section_id>/lesson/add', methods=['POST'])
@login_required
def add_lesson(section_id):
    """Add a new lesson to a section"""
    section = CourseSection.query.get_or_404(section_id)
    course = Course.query.get(section.course_id)
    
    # Check if user is the creator
    if course.creator_id != current_user.id:
        flash('You can only manage your own courses.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    # Check if course is in editable state
    if course.status not in ['draft', 'rejected']:
        flash('This course content cannot be edited in its current state.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    form = CourseLessonForm(request.form)
    
    if form.validate_on_submit():
        # Get max order if not provided
        order = form.order.data
        if order is None:
            max_order = db.session.query(db.func.max(CourseLesson.order)).filter_by(section_id=section_id).scalar() or 0
            order = max_order + 1
        
        # Create lesson
        lesson = CourseLesson(
            section_id=section_id,
            title=form.title.data,
            content_type=form.content_type.data,
            content=form.content.data,
            duration=form.duration.data,
            order=order,
            is_free_preview=form.is_free_preview.data
        )
        
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson added successfully!', 'success')
    else:
        flash('Failed to add lesson. Please check the form.', 'danger')
    
    return redirect(url_for('coursebud.manage_course_content', course_id=course.id))

@coursebud_bp.route('/teach/course/<int:course_id>/submit', methods=['POST'])
@login_required
def submit_for_review(course_id):
    """Submit course for admin review"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the creator
    if course.creator_id != current_user.id:
        flash('You can only submit your own courses.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    # Check if course is in draft or rejected state
    if course.status not in ['draft', 'rejected']:
        flash('This course is already submitted or approved.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    # Check if course has content
    sections = CourseSection.query.filter_by(course_id=course_id).all()
    if not sections:
        flash('Your course needs at least one section with content before submission.', 'warning')
        return redirect(url_for('coursebud.manage_course_content', course_id=course_id))
    
    has_lessons = False
    for section in sections:
        if section.lessons:
            has_lessons = True
            break
    
    if not has_lessons:
        flash('Your course needs at least one lesson before submission.', 'warning')
        return redirect(url_for('coursebud.manage_course_content', course_id=course_id))
    
    # Submit course
    if submit_course_for_review(course_id):
        flash('Your course has been submitted for review! You will be notified once it is approved.', 'success')
    else:
        flash('Failed to submit course for review. Please try again.', 'danger')
    
    return redirect(url_for('coursebud.teach'))

@coursebud_bp.route('/teach/course/<int:course_id>/stats')
@login_required
def course_stats(course_id):
    """View course statistics"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the creator
    if course.creator_id != current_user.id:
        flash('You can only view statistics for your own courses.', 'warning')
        return redirect(url_for('coursebud.teach'))
    
    # Get statistics
    stats = get_course_statistics(course_id)
    
    # Get enrollments
    enrollments = CourseEnrollment.query.filter_by(course_id=course_id).order_by(CourseEnrollment.enrolled_at.desc()).all()
    
    # Get reviews
    reviews = CourseReview.query.filter_by(course_id=course_id).order_by(CourseReview.created_at.desc()).all()
    
    return render_template(
        'coursebud/course_stats.html',
        title='Course Statistics',
        course=course,
        stats=stats,
        enrollments=enrollments,
        reviews=reviews
    )

# Admin routes for course management
@coursebud_bp.route('/admin/pending-courses')
@login_required
def admin_pending_courses():
    """Admin view of courses pending approval"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('coursebud.index'))
    
    # Get pending courses
    pending_courses = get_pending_courses()
    
    return render_template(
        'coursebud/admin/pending_courses.html',
        title='Pending Courses',
        pending_courses=pending_courses
    )

@coursebud_bp.route('/admin/course/<int:course_id>/review', methods=['GET', 'POST'])
@login_required
def admin_review_course(course_id):
    """Admin review of a course"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('coursebud.index'))
    
    course = Course.query.get_or_404(course_id)
    
    # Check if course is pending
    if course.status != 'pending':
        flash('This course is not pending review.', 'info')
        return redirect(url_for('coursebud.admin_pending_courses'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        notes = request.form.get('notes', '')
        
        if action == 'approve':
            if approve_course(course_id, notes):
                flash('Course has been approved!', 'success')
            else:
                flash('Failed to approve course.', 'danger')
        elif action == 'reject':
            if reject_course(course_id, notes):
                flash('Course has been rejected.', 'success')
            else:
                flash('Failed to reject course.', 'danger')
        
        return redirect(url_for('coursebud.admin_pending_courses'))
    
    # Get sections and lessons for review
    sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.order).all()
    
    return render_template(
        'coursebud/admin/review_course.html',
        title='Review Course',
        course=course,
        sections=sections
    )

# Categories management
@coursebud_bp.route('/category/<int:category_id>')
def category_courses(category_id):
    """Show courses in a category"""
    category = CourseCategory.query.get_or_404(category_id)
    courses = get_courses_by_category(category_id)
    
    return render_template(
        'coursebud/category.html',
        title=category.name,
        category=category,
        courses=courses
    )