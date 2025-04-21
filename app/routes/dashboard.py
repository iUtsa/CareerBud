from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import get_jobs, get_courses
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('social.feed'))
    return render_template('index.html', title='Welcome to CareersBud')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Get upcoming events (job interviews, deadlines)
    upcoming_events = []
    
    # Get recent achievements
    achievements = sorted(current_user.achievements,
                 key=lambda x: datetime.strptime(x.date.strftime('%Y-%m-%d'), '%Y-%m-%d') if isinstance(x.date, str) else x.date,
                 reverse=True)

    
    # Get job opportunities (limited for free tier)
    job_opportunities = get_jobs()
    if current_user.subscription_tier == 'free':
        job_opportunities = job_opportunities[:3]  # Limit for free tier
    
    # Get academic progress
    academic_progress = {
        'gpa': current_user.gpa,
        'credits': current_user.credits,
        'total_credits': current_user.total_credits,
        'progress_percentage': (current_user.credits / current_user.total_credits) * 100 if current_user.total_credits > 0 else 0
    }
    
    # Get current courses - added fallback if not defined
    current_courses = getattr(current_user, 'current_courses', [])
    
    # Check for upcoming job interviews (fixed to use attribute access)
    upcoming_interviews = []
    for app in current_user.job_applications:
        try:
            # Try attribute access first (for objects)
            if hasattr(app, 'interview_date') and app.interview_date is not None and app.interview_date > datetime.now():
                upcoming_interviews.append(app)
        except (AttributeError, TypeError):
            # Fall back to dictionary access if needed
            if isinstance(app, dict) and 'interview_date' in app and app['interview_date'] is not None and app['interview_date'] > datetime.now():
                upcoming_interviews.append(app)
    
    # Get todos (sorted by completion status and due date)
    todos = sorted([todo for todo in current_user.todos if not todo.completed], 
                   key=lambda x: x.due_date or datetime.max)[:5]
    
    return render_template(
        'dashboard.html',
        title='Dashboard',
        upcoming_events=upcoming_events,
        achievements=achievements,
        job_opportunities=job_opportunities,
        academic_progress=academic_progress,
        current_courses=current_courses,
        upcoming_interviews=upcoming_interviews,
        todos=todos
    )
