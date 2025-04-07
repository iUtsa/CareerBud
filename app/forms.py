# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SelectMultipleField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=1000)])
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