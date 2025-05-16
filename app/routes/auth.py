from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import AchievementForm
from app.models import Achievement, authenticate_user, create_user, update_user_profile
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app import db, bcrypt

auth_bp = Blueprint('auth', __name__)
achievement_bp = Blueprint('achievement', __name__)

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
        return redirect(url_for('social.feed'))  # ✅ Redirect to social feed if already logged in

    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(form.email.data, form.password.data)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('social.feed'))  # ✅ Redirect to social.feed
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

    # In your app/routes/auth.py
@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    # Check if new password and confirm password match
    if new_password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('auth.profile'))

    # You can add more checks like ensuring the current password is correct
    if change_password_logic(current_user.id, current_password, new_password):
        flash('Password changed successfully!', 'success')
    else:
        flash('Failed to change password. Please try again.', 'danger')

    return redirect(url_for('auth.profile'))


@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # Ensure the CSRF token is validated
    if request.form['confirm_email'] == current_user.email:
        # Perform account deletion logic here
        try:
            # Remove user from database
            db.session.delete(current_user)
            db.session.commit()

            flash("Your account has been deleted successfully.", 'success')
            return redirect(url_for('auth.logout'))  # Redirect to logout after account deletion
        except Exception as e:
            flash(f"Error deleting account: {e}", 'danger')
            return redirect(url_for('auth.profile'))  # Redirect back to the profile page in case of error

    flash("Email confirmation does not match.", 'danger')
    return redirect(url_for('auth.profile'))  # Redirect back if email doesn't match

@auth_bp.route('/add_achievement', methods=['GET', 'POST'])
@login_required
def add_achievement():
    form = AchievementForm()

    if form.validate_on_submit():
        # Create a new Achievement instance
        achievement = Achievement(
            title=form.title.data,
            description=form.description.data,  # Add description to the achievement
            date=form.date.data,  # Ensure date is also passed
            user_id=current_user.id
        )

        # Add to the session and commit to the database
        db.session.add(achievement)
        db.session.commit()

        flash('Achievement added successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/add_achievement.html', form=form)

