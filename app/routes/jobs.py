from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import get_jobs, add_job_application, add_todo, update_todo_status, delete_todo
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

jobs_bp = Blueprint('jobs', __name__)

# Forms
class JobApplicationForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Applied', 'Applied'),
        ('Interview', 'Interview Scheduled'),
        ('Offered', 'Offered'),
        ('Rejected', 'Rejected')
    ], validators=[DataRequired()])
    interview_date = DateField('Interview Date', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Add Application')

class TodoForm(FlaskForm):
    title = StringField('Task', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[Optional()], format='%Y-%m-%d')
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Task')

@jobs_bp.route('/jobs')
@login_required
def jobs():
    form = JobApplicationForm()

    try:
        # Get job listings (limit based on subscription tier)
        all_jobs = get_jobs()
        job_listings = all_jobs if current_user.is_premium else all_jobs[:5]

        # Get user's job applications
        job_applications = current_user.job_applications

        return render_template(
            'jobs.html',
            title='Jobs',
            job_listings=job_listings,
            job_applications=job_applications,
            form=form,
            is_premium=current_user.is_premium
        )

    except Exception as e:
        flash(f"Error loading jobs data: {e}", "danger")
        return redirect(url_for('dashboard.dashboard'))

@jobs_bp.route('/jobs/apply', methods=['POST'])
@login_required
def apply_job():
    form = JobApplicationForm()

    if form.validate_on_submit():
        company = form.company.data
        position = form.position.data
        status = form.status.data
        interview_date = form.interview_date.data

        if add_job_application(current_user.id, company, position, status, interview_date):
            flash('Job application added successfully!', 'success')
        else:
            flash('Failed to add job application', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('jobs.jobs'))

@jobs_bp.route('/todo')
@login_required
def todo():
    form = TodoForm()

    try:
        # Ensure current_user.todos is a list of objects (Todo)
        if not hasattr(current_user, 'todos'):
            flash("No todos found for the user.", "danger")
            return redirect(url_for('dashboard.dashboard'))

        # Get all todos, sort by completion status and due date
        todos = sorted(current_user.todos, key=lambda x: (x.completed, x.due_date or datetime.max))

        # Debug: Print todos to check if it's returning the expected data
        print(todos)

        return render_template(
            'todo.html',
            title='Todo List',
            todos=todos,
            form=form
        )

    except Exception as e:
        # Print out the error for debugging
        print(f"Error loading todo data: {e}")
        flash(f"Error loading todo data: {e}", "danger")
        return redirect(url_for('dashboard.dashboard'))



@jobs_bp.route('/todos/add', methods=['POST'])
@login_required
def add_todo_route():
    form = TodoForm()

    if form.validate_on_submit():
        title = form.title.data
        due_date = form.due_date.data
        priority = form.priority.data

        if add_todo(current_user.id, title, due_date, priority):
            flash('Task added successfully!', 'success')
        else:
            flash('Failed to add task', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('jobs.todo'))

@jobs_bp.route('/todos/update', methods=['POST'])
@login_required
def update_todo_route():
    todo_id = request.form.get('todo_id')
    completed = request.form.get('completed') == 'true'

    if update_todo_status(current_user.id, todo_id, completed):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to update task status'}), 400

@jobs_bp.route('/todos/delete', methods=['POST'])
@login_required
def delete_todo_route():
    todo_id = request.form.get('todo_id')

    if delete_todo(current_user.id, todo_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to delete task'}), 400

@jobs_bp.route('/passive-income')
@login_required
def passive_income():
    # Check if user has premium subscription
    if not current_user.is_premium:
        flash('Passive Income tools are only available for Premium subscribers', 'warning')
        return redirect(url_for('subscription.plans'))

    # This would typically include passive income ideas, tools, and analytics
    income_ideas = [
        {
            'title': 'Start a Blog',
            'description': 'Create content in your area of expertise and monetize through ads, affiliate marketing, or sponsored posts.',
            'difficulty': 'Medium',
            'startup_cost': 'Low',
            'time_commitment': 'High',
            'potential_income': '$500-$5000/month'
        },
        {
            'title': 'Create an Online Course',
            'description': 'Package your technical knowledge into a course and sell it on platforms like Udemy or Teachable.',
            'difficulty': 'Medium',
            'startup_cost': 'Low',
            'time_commitment': 'Medium',
            'potential_income': '$1000-$10000/month'
        },
        {
            'title': 'Develop Mobile Apps',
            'description': 'Use your programming skills to create useful apps that generate income through ads or purchases.',
            'difficulty': 'High',
            'startup_cost': 'Low',
            'time_commitment': 'High',
            'potential_income': 'Variable'
        },
        {
            'title': 'Freelance Development',
            'description': 'Take on part-time freelance work to build your portfolio and generate extra income.',
            'difficulty': 'Medium',
            'startup_cost': 'None',
            'time_commitment': 'Variable',
            'potential_income': '$1000-$10000/month'
        },
        {
            'title': 'Create Digital Products',
            'description': 'Develop templates, plugins, or other digital assets that can be sold repeatedly.',
            'difficulty': 'Medium',
            'startup_cost': 'Low',
            'time_commitment': 'Medium',
            'potential_income': '$500-$3000/month'
        }
    ]

    return render_template(
        'passive_income.html',
        title='Passive Income',
        income_ideas=income_ideas
    )
