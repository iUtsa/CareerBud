from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models import authenticate_user, create_user, update_user_profile
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

auth_bp = Blueprint('auth', __name__)

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    university = StringField('University', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    university = StringField('University', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    gpa = StringField('GPA')
    credits = StringField('Credits')
    submit = SubmitField('Update Profile')

# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(form.email.data, form.password.data)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard.dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user_id = create_user(
                form.email.data,
                form.password.data,
                form.first_name.data,
                form.last_name.data,
                form.university.data,
                form.major.data
            )
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form, title='Register')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.university.data = current_user.university
        form.major.data = current_user.major
        form.gpa.data = current_user.gpa
        form.credits.data = current_user.credits
    
    if form.validate_on_submit():
        profile_data = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'university': form.university.data,
            'major': form.major.data
        }
        
        # Only update numeric fields if they're provided
        if form.gpa.data:
            try:
                profile_data['gpa'] = float(form.gpa.data)
            except ValueError:
                flash('GPA must be a number', 'danger')
                return render_template('auth/profile.html', form=form, title='Profile')
        
        if form.credits.data:
            try:
                profile_data['credits'] = int(form.credits.data)
            except ValueError:
                flash('Credits must be a number', 'danger')
                return render_template('auth/profile.html', form=form, title='Profile')
        
        if update_user_profile(current_user.id, profile_data):
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Failed to update profile', 'danger')
    
    return render_template('auth/profile.html', form=form, title='Profile')