# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length

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