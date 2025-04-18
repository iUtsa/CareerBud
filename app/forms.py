# app/forms.py
# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SelectMultipleField, DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from flask_wtf.file import FileField
from wtforms import RadioField  # Add this import


class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=1000)])
    image = FileField('Image', validators=[Optional()])
    visibility = SelectField('Visibility', choices=[
        ('public', 'Public - Everyone can see'),
        ('connections', 'Connections Only'),
        ('private', 'Private - Only me')
    ], validators=[DataRequired()])
    submit = SubmitField('Post')

class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=3, max=50)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    members = SelectMultipleField('Add Members', choices=[], validators=[DataRequired()])
    submit = SubmitField('Create Group')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    university = StringField('University', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    gpa = FloatField('GPA', validators=[DataRequired()])
    credits = IntegerField('Credits', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class AchievementForm(FlaskForm):
    title = StringField('Achievement Title', validators=[DataRequired()])
    date = DateField('Date', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Add Achievement')

class MessageForm(FlaskForm):
    content = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class ResumeForm(FlaskForm):
    title = StringField('Resume Title', validators=[DataRequired(), Length(max=100)])
    template = RadioField('Template', choices=[
        ('modern', 'Modern'),
        ('professional', 'Professional'),
        ('creative', 'Creative'),
        ('minimal', 'Minimal'),
        ('tech', 'Tech')
    ], default='modern', validators=[DataRequired()]) # Added default value here
    objective = TextAreaField('Career Objective/Summary', validators=[Optional(), Length(max=500)])
    primary_color = StringField('Primary Color', validators=[Optional(), Length(max=20)], default='#4ade80')
    secondary_color = StringField('Secondary Color', validators=[Optional(), Length(max=20)], default='#60a5fa')
    font_family = SelectField('Font', choices=[
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Lato', 'Lato'),
        ('Montserrat', 'Montserrat'),
        ('Raleway', 'Raleway')
    ], default='Roboto') # Added default value here

class ResumeSectionForm(FlaskForm):
    """
    Form for adding or editing a resume section
    """
    section_type = SelectField('Section Type', choices=[
        ('education', 'Education'),
        ('experience', 'Work Experience'),
        ('project', 'Project'),
        ('volunteer', 'Volunteer Experience'),
        ('certification', 'Certification'),
        ('award', 'Award/Achievement'),
        ('custom', 'Custom Section')
    ])
    title = StringField('Title/Position', validators=[DataRequired(), Length(max=100)])
    organization = StringField('Organization/Institution', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    start_date = DateField('Start Date', validators=[Optional()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[Optional()], format='%Y-%m-%d')
    is_current = BooleanField('Currently Active', default=False)
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    bullets = TextAreaField('Bullet Points (One per line)', validators=[Optional()])

class ResumeSkillForm(FlaskForm):
    """
    Form for adding or editing a resume skill
    """
    skill_name = StringField('Skill', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('technical', 'Technical Skills'),
        ('soft', 'Soft Skills'),
        ('language', 'Languages'),
        ('certification', 'Certifications'),
        ('other', 'Other Skills')
    ])
    proficiency = IntegerField('Proficiency (1-5)', validators=[Optional(), NumberRange(min=1, max=5)], default=3)

class ResumeAnalysisForm(FlaskForm):
    """
    Form for analyzing a resume against a job description
    """
    job_description = TextAreaField('Job Description', validators=[DataRequired()])
    job_title = StringField('Job Title', validators=[Optional(), Length(max=100)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])