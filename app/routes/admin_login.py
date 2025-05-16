from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email
from app.models import User
from app.extensions import db
from functools import wraps

# Create a dedicated blueprint for admin authentication
admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# Form for admin login
class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Admin login route
@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # If user is already logged in and is an admin, redirect to admin dashboard
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    
    # If user is logged in but not an admin, show access denied
    if current_user.is_authenticated and not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('coursebud.index'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and is an admin
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_admin:
                login_user(user, remember=form.remember_me.data)
                session['is_admin_session'] = True
                
                # Redirect to the requested page or admin dashboard
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('admin.admin_dashboard')
                
                flash('Welcome to the admin dashboard!', 'success')
                return redirect(next_page)
            else:
                flash('You do not have permission to access the admin area.', 'danger')
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('admin/login.html', title='Admin Login', form=form)

# Admin logout route
@admin_auth_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    session.pop('is_admin_session', None)
    flash('You have been logged out from the admin area.', 'info')
    return redirect(url_for('admin_auth.admin_login'))

# Admin session check middleware
def admin_session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin_session'):
            flash('Admin session required. Please login again.', 'warning')
            return redirect(url_for('admin_auth.admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Enhanced admin_required decorator that checks both admin status and admin session
def enhanced_admin_required(f):
    @wraps(f)
    @login_required
    @admin_session_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('coursebud.index'))
        return f(*args, **kwargs)
    return decorated_function