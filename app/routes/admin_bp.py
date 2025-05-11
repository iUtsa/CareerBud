# Add these routes to your coursebud_bp.py or create a separate admin_bp.py

# Import the necessary models and functions
from app.models import (
    Course, CourseCategory, User, CourseEnrollment, Payment, Subscription,
    Quiz, QuizAttempt, CourseReview, CourseCertificate, CourseSection, CourseLesson,
    approve_course, reject_course, get_pending_courses
)
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from sqlalchemy import func, desc, asc
from datetime import datetime, timedelta
import json
import os
from werkzeug.utils import secure_filename

# If creating a separate blueprint, uncomment these lines
# admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Helper function to check if user is admin
def is_admin():
    return current_user.is_authenticated and current_user.is_admin

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('coursebud.index'))
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard
@coursebud_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with key metrics"""
    
    # Get basic counts
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = CourseEnrollment.query.count()
    pending_courses = Course.query.filter_by(status='pending').count()
    
    # Get courses created in the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_courses = Course.query.filter(Course.created_at >= thirty_days_ago).count()
    
    # Get users registered in the last 30 days
    new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    # Get enrollments in the last 30 days
    new_enrollments = CourseEnrollment.query.filter(CourseEnrollment.enrolled_at >= thirty_days_ago).count()
    
    # Get revenue statistics
    revenue_stats = get_revenue_statistics()
    
    # Get top courses by enrollment
    top_courses = Course.query.join(CourseEnrollment).group_by(Course.id).order_by(
        func.count(CourseEnrollment.id).desc()
    ).limit(5).all()
    
    # Get top courses by revenue
    top_revenue_courses = Course.query.join(CourseEnrollment).join(Payment).filter(
        Payment.status == 'succeeded',
        Payment.payment_type == 'course_purchase'
    ).group_by(Course.id).order_by(
        func.sum(Payment.amount).desc()
    ).limit(5).all()
    
    # Get top instructors by students
    top_instructors = User.query.join(
        Course, Course.creator_id == User.id
    ).join(
        CourseEnrollment, CourseEnrollment.course_id == Course.id
    ).group_by(User.id).order_by(
        func.count(CourseEnrollment.id).desc()
    ).limit(5).all()
    
    return render_template(
        'coursebud/admin/dashboard.html',
        title='Admin Dashboard',
        total_users=total_users,
        total_courses=total_courses,
        total_enrollments=total_enrollments,
        pending_courses=pending_courses,
        new_courses=new_courses,
        new_users=new_users,
        new_enrollments=new_enrollments,
        revenue_stats=revenue_stats,
        top_courses=top_courses,
        top_revenue_courses=top_revenue_courses,
        top_instructors=top_instructors
    )

# Helper function to get revenue statistics
def get_revenue_statistics():
    """Get revenue statistics for admin dashboard"""
    # Get total revenue
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'succeeded'
    ).scalar() or 0
    
    # Get revenue today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'succeeded',
        Payment.created_at >= today_start
    ).scalar() or 0
    
    # Get revenue this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'succeeded',
        Payment.created_at >= month_start
    ).scalar() or 0
    
    # Get revenue by course purchases vs subscriptions
    course_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'succeeded',
        Payment.payment_type == 'course_purchase'
    ).scalar() or 0
    
    subscription_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'succeeded',
        Payment.payment_type == 'subscription'
    ).scalar() or 0
    
    # Get subscriber count
    subscriber_count = Subscription.query.filter_by(status='active').count()
    
    return {
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'course_revenue': course_revenue,
        'subscription_revenue': subscription_revenue,
        'subscriber_count': subscriber_count
    }

# Course approvals page
@coursebud_bp.route('/admin/courses/pending')
@login_required
@admin_required
def admin_pending_courses():
    """Admin view of courses pending approval"""
    pending_courses = get_pending_courses()
    
    return render_template(
        'coursebud/admin/pending_courses.html',
        title='Pending Courses',
        pending_courses=pending_courses
    )

# Course review page
@coursebud_bp.route('/admin/course/<int:course_id>/review', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_review_course(course_id):
    """Admin review of a course"""
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
    
    # Get creator info
    creator = User.query.get(course.creator_id)
    
    # Get sections and lessons for review
    sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.order).all()
    
    # Count total lessons
    lesson_count = 0
    for section in sections:
        lesson_count += len(section.lessons)
    
    return render_template(
        'coursebud/admin/review_course.html',
        title='Review Course',
        course=course,
        creator=creator,
        sections=sections,
        lesson_count=lesson_count
    )

# Course management
@coursebud_bp.route('/admin/courses')
@login_required
@admin_required
def admin_courses():
    """Admin view of all courses"""
    # Get filter parameters
    status = request.args.get('status', 'all')
    category_id = request.args.get('category_id')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    
    # Base query
    query = Course.query
    
    # Apply filters
    if status != 'all':
        query = query.filter(Course.status == status)
        
    if category_id:
        query = query.filter(Course.category_id == category_id)
        
    if search:
        query = query.filter(
            (Course.title.ilike(f'%{search}%')) | 
            (Course.description.ilike(f'%{search}%'))
        )
    
    # Apply sorting
    if sort == 'newest':
        query = query.order_by(Course.created_at.desc())
    elif sort == 'oldest':
        query = query.order_by(Course.created_at.asc())
    elif sort == 'title_asc':
        query = query.order_by(Course.title.asc())
    elif sort == 'title_desc':
        query = query.order_by(Course.title.desc())
    elif sort == 'most_enrolled':
        query = query.outerjoin(CourseEnrollment).group_by(Course.id).order_by(
            func.count(CourseEnrollment.id).desc()
        )
    
    # Paginate results
    page = request.args.get('page', 1, type=int)
    per_page = 20
    courses = query.paginate(page=page, per_page=per_page)
    
    # Get categories for filter
    categories = CourseCategory.query.order_by(CourseCategory.name).all()
    
    return render_template(
        'coursebud/admin/courses.html',
        title='Manage Courses',
        courses=courses,
        categories=categories,
        status=status,
        category_id=category_id,
        search=search,
        sort=sort
    )

# User management
@coursebud_bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin view of all users"""
    # Get filter parameters
    role = request.args.get('role', 'all')
    subscription = request.args.get('subscription', 'all')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    
    # Base query
    query = User.query
    
    # Apply filters    
    if role == 'instructors':
        # Users who have created at least one course
        query = query.join(Course, Course.creator_id == User.id).group_by(User.id)
    elif role == 'students':
        # Users who have at least one enrollment but no courses
        query = query.join(CourseEnrollment, CourseEnrollment.user_id == User.id).filter(
            ~User.id.in_(
                db.session.query(Course.creator_id).distinct()
            )
        ).group_by(User.id)
    elif role == 'admins':
        query = query.filter(User.is_admin == True)
        
    if subscription == 'premium':
        query = query.filter(User.subscription_tier == 'premium')
    elif subscription == 'free':
        query = query.filter(User.subscription_tier == 'free')
    
    if search:
        query = query.filter(
            (User.first_name.ilike(f'%{search}%')) | 
            (User.last_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    # Apply sorting
    if sort == 'newest':
        query = query.order_by(User.created_at.desc())
    elif sort == 'oldest':
        query = query.order_by(User.created_at.asc())
    elif sort == 'name_asc':
        query = query.order_by(User.first_name.asc())
    elif sort == 'name_desc':
        query = query.order_by(User.first_name.desc())
    elif sort == 'most_courses':
        # Users with most created courses
        query = query.outerjoin(Course, Course.creator_id == User.id).group_by(User.id).order_by(
            func.count(Course.id).desc()
        )
    elif sort == 'most_enrolled':
        # Users with most enrollments
        query = query.outerjoin(CourseEnrollment, CourseEnrollment.user_id == User.id).group_by(User.id).order_by(
            func.count(CourseEnrollment.id).desc()
        )
    
    # Paginate results
    page = request.args.get('page', 1, type=int)
    per_page = 20
    users = query.paginate(page=page, per_page=per_page)
    
    return render_template(
        'coursebud/admin/users.html',
        title='Manage Users',
        users=users,
        role=role,
        subscription=subscription,
        search=search,
        sort=sort
    )

# View user details
@coursebud_bp.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_view_user(user_id):
    """Admin view of a user's details"""
    user = User.query.get_or_404(user_id)
    
    # Get user's created courses
    created_courses = Course.query.filter_by(creator_id=user_id).all()
    
    # Get user's enrollments
    enrollments = CourseEnrollment.query.filter_by(user_id=user_id).all()
    
    # Get user's payments
    payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
    
    # Get user's subscription
    subscription = Subscription.query.filter_by(user_id=user_id).first()
    
    # Get user's quiz attempts
    quiz_attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.completed_at.desc()).limit(10).all()
    
    # Get user's reviews
    reviews = CourseReview.query.filter_by(user_id=user_id).order_by(CourseReview.created_at.desc()).all()
    
    return render_template(
        'coursebud/admin/view_user.html',
        title=f'User: {user.full_name()}',
        user=user,
        created_courses=created_courses,
        enrollments=enrollments,
        payments=payments,
        subscription=subscription,
        quiz_attempts=quiz_attempts,
        reviews=reviews
    )

# Edit user
@coursebud_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    """Admin edit of a user"""
    user = User.query.get_or_404(user_id)
    
    class UserEditForm(FlaskForm):
        first_name = StringField('First Name', validators=[DataRequired()])
        last_name = StringField('Last Name', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired()])
        university = StringField('University', validators=[Optional()])
        major = StringField('Major', validators=[Optional()])
        subscription_tier = SelectField('Subscription Tier', choices=[
            ('free', 'Free'),
            ('premium', 'Premium')
        ])
        is_admin = SelectField('Admin Status', choices=[
            ('0', 'Regular User'),
            ('1', 'Administrator')
        ], coerce=int)
        submit = SubmitField('Save Changes')
    
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.university = form.university.data
        user.major = form.major.data
        user.subscription_tier = form.subscription_tier.data
        user.is_admin = bool(form.is_admin.data)
        
        # If switched to premium, update subscription end date
        if form.subscription_tier.data == 'premium' and user.subscription_tier != 'premium':
            user.subscription_end_date = datetime.utcnow() + timedelta(days=365)  # 1 year subscription
        
        # If switched to free, remove subscription end date
        if form.subscription_tier.data == 'free' and user.subscription_tier != 'free':
            user.subscription_end_date = None
        
        db.session.commit()
        flash(f'User {user.full_name()} has been updated.', 'success')
        return redirect(url_for('coursebud.admin_view_user', user_id=user_id))
    
    return render_template(
        'coursebud/admin/edit_user.html',
        title=f'Edit User: {user.full_name()}',
        form=form,
        user=user
    )

# Category management
@coursebud_bp.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_categories():
    """Admin management of course categories"""
    # Form for adding/editing categories
    class CategoryForm(FlaskForm):
        name = StringField('Category Name', validators=[DataRequired()])
        description = TextAreaField('Description', validators=[Optional()])
        parent_id = SelectField('Parent Category', coerce=int, validators=[Optional()])
        submit = SubmitField('Save Category')
    
    # Get all categories
    categories = CourseCategory.query.order_by(CourseCategory.name).all()
    
    # Set up form for adding new category
    form = CategoryForm()
    form.parent_id.choices = [(0, 'None')] + [(c.id, c.name) for c in categories]
    
    # Handle form submission
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        
        # Check if we're editing or creating
        category_id = request.form.get('category_id')
        
        if category_id:
            # Editing existing category
            category = CourseCategory.query.get_or_404(category_id)
            category.name = form.name.data
            category.description = form.description.data
            category.parent_id = parent_id
            flash(f'Category "{category.name}" has been updated.', 'success')
        else:
            # Creating new category
            category = CourseCategory(
                name=form.name.data,
                description=form.description.data,
                parent_id=parent_id
            )
            db.session.add(category)
            flash(f'Category "{form.name.data}" has been created.', 'success')
        
        db.session.commit()
        return redirect(url_for('coursebud.admin_categories'))
    
    return render_template(
        'coursebud/admin/categories.html',
        title='Manage Categories',
        categories=categories,
        form=form
    )

# Delete category
@coursebud_bp.route('/admin/category/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_category(category_id):
    """Delete a category"""
    category = CourseCategory.query.get_or_404(category_id)
    
    # Check if category has courses
    course_count = Course.query.filter_by(category_id=category_id).count()
    if course_count > 0:
        flash(f'Cannot delete category "{category.name}" because it has {course_count} courses.', 'danger')
        return redirect(url_for('coursebud.admin_categories'))
    
    # Check if category has subcategories
    subcategory_count = CourseCategory.query.filter_by(parent_id=category_id).count()
    if subcategory_count > 0:
        flash(f'Cannot delete category "{category.name}" because it has {subcategory_count} subcategories.', 'danger')
        return redirect(url_for('coursebud.admin_categories'))
    
    # Delete the category
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Category "{category.name}" has been deleted.', 'success')
    return redirect(url_for('coursebud.admin_categories'))

# Sales and revenue reports
@coursebud_bp.route('/admin/reports/revenue')
@login_required
@admin_required
def admin_revenue_report():
    """Admin revenue report"""
    # Get filter parameters
    period = request.args.get('period', 'month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Set default date range based on period
    today = datetime.utcnow()
    if period == 'day':
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'week':
        # Start of current week (Monday)
        start = today - timedelta(days=today.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = today
    elif period == 'month':
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today
    elif period == 'year':
        start = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today
    elif period == 'custom':
        # Parse custom date range
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        except (ValueError, TypeError):
            flash('Invalid date range. Showing current month.', 'warning')
            start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = today
            period = 'month'
    else:
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today
        period = 'month'
    
    # Get payments in date range
    payments = Payment.query.filter(
        Payment.created_at >= start,
        Payment.created_at <= end,
        Payment.status == 'succeeded'
    ).order_by(Payment.created_at.desc()).all()
    
    # Calculate revenue metrics
    total_revenue = sum(payment.amount for payment in payments)
    course_revenue = sum(payment.amount for payment in payments if payment.payment_type == 'course_purchase')
    subscription_revenue = sum(payment.amount for payment in payments if payment.payment_type == 'subscription')
    
    # Group revenue by day for chart
    daily_revenue = {}
    current_date = start
    while current_date <= end:
        day_str = current_date.strftime('%Y-%m-%d')
        daily_revenue[day_str] = 0
        current_date += timedelta(days=1)
    
    for payment in payments:
        day_str = payment.created_at.strftime('%Y-%m-%d')
        daily_revenue[day_str] += payment.amount
    
    # Convert to list for chart
    revenue_chart_data = [
        {'date': date, 'amount': amount} 
        for date, amount in daily_revenue.items()
    ]
    
    # Get top selling courses
    course_sales = {}
    for payment in payments:
        if payment.payment_type == 'course_purchase' and payment.course_id:
            if payment.course_id not in course_sales:
                course_sales[payment.course_id] = {
                    'course': Course.query.get(payment.course_id),
                    'count': 0,
                    'revenue': 0
                }
            course_sales[payment.course_id]['count'] += 1
            course_sales[payment.course_id]['revenue'] += payment.amount
    
    # Sort by revenue
    top_courses = sorted(
        course_sales.values(), 
        key=lambda x: x['revenue'], 
        reverse=True
    )[:10]
    
    return render_template(
        'coursebud/admin/revenue_report.html',
        title='Revenue Report',
        period=period,
        start_date=start.strftime('%Y-%m-%d'),
        end_date=end.strftime('%Y-%m-%d'),
        payments=payments,
        total_revenue=total_revenue,
        course_revenue=course_revenue,
        subscription_revenue=subscription_revenue,
        revenue_chart_data=json.dumps(revenue_chart_data),
        top_courses=top_courses
    )

# Platform settings
@coursebud_bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    """Admin platform settings"""
    class SettingsForm(FlaskForm):
        site_name = StringField('Site Name', validators=[DataRequired()])
        admin_email = StringField('Admin Email', validators=[DataRequired()])
        premium_price = FloatField('Premium Subscription Price', validators=[DataRequired()])
        platform_fee_percentage = FloatField('Platform Fee Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
        enable_public_profiles = SelectField('Enable Public Profiles', choices=[
            ('yes', 'Yes'),
            ('no', 'No')
        ])
        enable_course_reviews = SelectField('Enable Course Reviews', choices=[
            ('yes', 'Yes'),
            ('no', 'No')
        ])
        enable_certificate_sharing = SelectField('Enable Certificate Sharing', choices=[
            ('yes', 'Yes'),
            ('no', 'No')
        ])
        submit = SubmitField('Save Settings')
    
    # Load current settings from config
    current_settings = {
        'site_name': current_app.config.get('SITE_NAME', 'CourseBud'),
        'admin_email': current_app.config.get('ADMIN_EMAIL', 'admin@example.com'),
        'premium_price': current_app.config.get('PREMIUM_PRICE', 9.99),
        'platform_fee_percentage': current_app.config.get('PLATFORM_FEE_PERCENTAGE', 30),
        'enable_public_profiles': 'yes' if current_app.config.get('ENABLE_PUBLIC_PROFILES', True) else 'no',
        'enable_course_reviews': 'yes' if current_app.config.get('ENABLE_COURSE_REVIEWS', True) else 'no',
        'enable_certificate_sharing': 'yes' if current_app.config.get('ENABLE_CERTIFICATE_SHARING', True) else 'no'
    }
    
    form = SettingsForm(**current_settings)
    
    if form.validate_on_submit():
        # In a real application, you would save these to a database or config file
        # For this example, we'll just show a success message
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('coursebud.admin_settings'))
    
    return render_template(
        'coursebud/admin/settings.html',
        title='Platform Settings',
        form=form
    )

# System logs
@coursebud_bp.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    """View system logs"""
    # In a real application, you would load logs from a file or database
    # This is just a placeholder
    
    # Mock logs for demonstration
    logs = [
        {'timestamp': datetime.utcnow() - timedelta(minutes=5), 'level': 'INFO', 'message': 'User John Doe logged in'},
        {'timestamp': datetime.utcnow() - timedelta(minutes=10), 'level': 'WARNING', 'message': 'Failed login attempt for user jane@example.com'},
        {'timestamp': datetime.utcnow() - timedelta(minutes=15), 'level': 'ERROR', 'message': 'Payment processing failed for order #12345'},
        {'timestamp': datetime.utcnow() - timedelta(minutes=20), 'level': 'INFO', 'message': 'Course "Python for Beginners" was approved'},
        {'timestamp': datetime.utcnow() - timedelta(minutes=25), 'level': 'INFO', 'message': 'New user registered: alice@example.com'},
    ]
    
    return render_template(
        'coursebud/admin/logs.html',
        title='System Logs',
        logs=logs
    )