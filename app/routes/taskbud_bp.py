from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from app.models import Goal, Task, DailyPlan, TaskActivity, db
from app.models import get_user_goals, get_user_tasks, get_overdue_tasks, get_upcoming_tasks
from app.models import generate_daily_plan, get_goal_statistics
from datetime import datetime, timedelta
import re

taskbud_bp = Blueprint('taskbud', __name__)

@taskbud_bp.route('/taskbud')
@login_required
def index():
    """Main TaskBud dashboard."""
    # Get statistics
    stats = get_goal_statistics(current_user.id)
    
    # Get active goals
    active_goals = Goal.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).order_by(Goal.priority).all()
    
    # Get today's tasks
    today = datetime.utcnow().date()
    daily_plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not daily_plan:
        daily_plan = generate_daily_plan(current_user.id)
    
    # Get upcoming tasks
    upcoming_tasks = get_upcoming_tasks(current_user.id, days=7)
    
    return render_template(
        'taskbud/dashboard.html',
        stats=stats,
        active_goals=active_goals,
        daily_plan=daily_plan,
        upcoming_tasks=upcoming_tasks,
        today=today
    )

@taskbud_bp.route('/taskbud/goals')
@login_required
def goals():
    """View all goals."""
    goal_type = request.args.get('type')
    status = request.args.get('status')
    
    goals = get_user_goals(current_user.id, goal_type, status)
    
    # For parent goals selection
    parent_goals = Goal.query.filter_by(
        user_id=current_user.id,
        goal_type='long_term'
    ).all()
    
    return render_template(
        'taskbud/goals.html',
        goals=goals,
        parent_goals=parent_goals,
        goal_type=goal_type,
        status=status
    )

@taskbud_bp.route('/taskbud/goals/new', methods=['GET', 'POST'])
@login_required
def new_goal():
    """Create a new goal."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        goal_type = request.form.get('goal_type')
        priority = request.form.get('priority', 2, type=int)
        parent_goal_id = request.form.get('parent_goal_id')
        
        # Convert parent_goal_id to int or None
        if parent_goal_id and parent_goal_id != 'none':
            parent_goal_id = int(parent_goal_id)
        else:
            parent_goal_id = None
        
        # Parse target date
        target_date_str = request.form.get('target_date')
        target_date = None
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid target date format', 'error')
                return redirect(url_for('taskbud.new_goal'))
        
        goal = Goal(
            user_id=current_user.id,
            title=title,
            description=description,
            goal_type=goal_type,
            priority=priority,
            target_date=target_date,
            parent_goal_id=parent_goal_id
        )
        
        db.session.add(goal)
        db.session.commit()
        
        # Log activity
        activity = TaskActivity(
            user_id=current_user.id,
            goal_id=goal.id,
            activity_type='created',
            details=f"Created goal: {goal.title}"
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Goal created successfully', 'success')
        return redirect(url_for('taskbud.goals'))
    
    # Get parent goals for selection
    parent_goals = Goal.query.filter_by(
        user_id=current_user.id,
        goal_type='long_term'
    ).all()
    
    return render_template(
        'taskbud/goal_form.html',
        parent_goals=parent_goals,
        goal=None,
        csrf_token=generate_csrf()
    )

@taskbud_bp.route('/taskbud/goals/<int:goal_id>')
@login_required
def view_goal(goal_id):
    """View a specific goal and its tasks."""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    
    # Get tasks for this goal
    tasks = Task.query.filter_by(goal_id=goal.id).order_by(Task.priority, Task.due_date).all()
    
    # Get sub-goals if any
    sub_goals = Goal.query.filter_by(parent_goal_id=goal.id).all()
    
    return render_template(
        'taskbud/view_goals.html',
        goal=goal,
        tasks=tasks,
        sub_goals=sub_goals
    )

@taskbud_bp.route('/taskbud/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    """Edit an existing goal."""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        goal.title = request.form.get('title')
        goal.description = request.form.get('description')
        goal.goal_type = request.form.get('goal_type')
        goal.priority = request.form.get('priority', 2, type=int)
        
        parent_goal_id = request.form.get('parent_goal_id')
        if parent_goal_id and parent_goal_id != 'none':
            goal.parent_goal_id = int(parent_goal_id)
        else:
            goal.parent_goal_id = None
        
        # Parse target date
        target_date_str = request.form.get('target_date')
        if target_date_str:
            try:
                goal.target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid target date format', 'error')
                return redirect(url_for('taskbud.edit_goal', goal_id=goal.id))
        else:
            goal.target_date = None
        
        db.session.commit()
        
        # Log activity
        activity = TaskActivity(
            user_id=current_user.id,
            goal_id=goal.id,
            activity_type='updated',
            details=f"Updated goal: {goal.title}"
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Goal updated successfully', 'success')
        return redirect(url_for('taskbud.view_goal', goal_id=goal.id))
    
    # Get parent goals for selection
    parent_goals = Goal.query.filter_by(
        user_id=current_user.id,
        goal_type='long_term'
    ).all()
    
    return render_template(
        'taskbud/goal_form.html',
        goal=goal,
        parent_goals=parent_goals,
        csrf_token=generate_csrf()
    )

@taskbud_bp.route('/taskbud/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    """Delete a goal."""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    
    # Check if goal has sub-goals
    sub_goals = Goal.query.filter_by(parent_goal_id=goal.id).all()
    if sub_goals:
        flash('Cannot delete goal with sub-goals. Please delete sub-goals first.', 'error')
        return redirect(url_for('taskbud.view_goal', goal_id=goal.id))
    
    # Log activity before deleting
    activity = TaskActivity(
        user_id=current_user.id,
        activity_type='deleted',
        details=f"Deleted goal: {goal.title}"
    )
    db.session.add(activity)
    
    # Delete the goal (tasks will be deleted due to cascade)
    db.session.delete(goal)
    db.session.commit()
    
    flash('Goal deleted successfully', 'success')
    return redirect(url_for('taskbud.goals'))

@taskbud_bp.route('/taskbud/goals/<int:goal_id>/complete', methods=['POST'])
@login_required
def complete_goal(goal_id):
    """Mark a goal as complete."""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    
    goal.status = 'completed'
    goal.completed_at = datetime.utcnow()
    goal.progress = 100.0
    db.session.commit()
    
    # Log activity
    activity = TaskActivity(
        user_id=current_user.id,
        goal_id=goal.id,
        activity_type='completed',
        details=f"Completed goal: {goal.title}"
    )
    db.session.add(activity)
    db.session.commit()
    
    flash('Goal marked as complete', 'success')
    return redirect(url_for('taskbud.view_goal', goal_id=goal.id))

@taskbud_bp.route('/taskbud/tasks')
@login_required
def tasks():
    """View all tasks."""
    status = request.args.get('status')
    due_date_str = request.args.get('due_date')
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    tasks = get_user_tasks(current_user.id, status, due_date)
    
    return render_template(
        'taskbud/tasks.html',
        tasks=tasks,
        status=status,
        due_date=due_date
    )

@taskbud_bp.route('/taskbud/goals/<int:goal_id>/tasks/new', methods=['GET', 'POST'])
@login_required
def new_task(goal_id):
    """Create a new task for a goal."""
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 2, type=int)
        status = request.form.get('status', 'pending')
        
        # Parse due date
        due_date_str = request.form.get('due_date')
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format', 'error')
                return redirect(url_for('taskbud.new_task', goal_id=goal.id))
        
        # Parse additional fields
        difficulty = request.form.get('difficulty', 2, type=int)
        estimated_hours = request.form.get('estimated_hours', 1.0, type=float)
        tags = request.form.get('tags', '')
        
        task = Task(
            goal_id=goal.id,
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date,
            difficulty=difficulty,
            estimated_hours=estimated_hours,
            tags=tags
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Log activity
        activity = TaskActivity(
            user_id=current_user.id,
            task_id=task.id,
            goal_id=goal.id,
            activity_type='created',
            details=f"Created task: {task.title}"
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Task created successfully', 'success')
        return redirect(url_for('taskbud.view_goal', goal_id=goal.id))
    
    return render_template(
        'taskbud/task_form.html',
        goal=goal,
        task=None,
        csrf_token=generate_csrf()
    )

@taskbud_bp.route('/taskbud/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task."""
    task = Task.query.join(Goal).filter(
        Task.id == task_id,
        Goal.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = request.form.get('priority', 2, type=int)
        task.status = request.form.get('status')
        
        # Parse due date
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format', 'error')
                return redirect(url_for('taskbud.edit_task', task_id=task.id))
        else:
            task.due_date = None
        
        # Parse additional fields
        task.difficulty = request.form.get('difficulty', 2, type=int)
        task.estimated_hours = request.form.get('estimated_hours', 1.0, type=float)
        task.tags = request.form.get('tags', '')
        
        db.session.commit()
        
        # Log activity
        activity = TaskActivity(
            user_id=current_user.id,
            task_id=task.id,
            goal_id=task.goal_id,
            activity_type='updated',
            details=f"Updated task: {task.title}"
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Task updated successfully', 'success')
        return redirect(url_for('taskbud.view_goal', goal_id=task.goal_id))
    
    return render_template(
        'taskbud/task_form.html',
        task=task,
        goal=task.goal,
        csrf_token=generate_csrf()
    )

@taskbud_bp.route('/taskbud/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    task = Task.query.join(Goal).filter(
        Task.id == task_id,
        Goal.user_id == current_user.id
    ).first_or_404()
    
    goal_id = task.goal_id
    
    # Log activity before deleting
    activity = TaskActivity(
        user_id=current_user.id,
        goal_id=goal_id,
        activity_type='deleted',
        details=f"Deleted task: {task.title}"
    )
    db.session.add(activity)
    
    # Delete the task
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully', 'success')
    return redirect(url_for('taskbud.view_goal', goal_id=goal_id))

@taskbud_bp.route('/taskbud/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Mark a task as complete."""
    task = Task.query.join(Goal).filter(
        Task.id == task_id,
        Goal.user_id == current_user.id
    ).first_or_404()
    
    task.mark_complete()
    
    # Log activity
    activity = TaskActivity(
        user_id=current_user.id,
        task_id=task.id,
        goal_id=task.goal_id,
        activity_type='completed',
        details=f"Completed task: {task.title}"
    )
    db.session.add(activity)
    db.session.commit()
    
    # If from AJAX, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'goal_progress': task.goal.progress
        })
    
    # Otherwise redirect
    flash('Task marked as complete', 'success')
    return redirect(url_for('taskbud.view_goal', goal_id=task.goal_id))

@taskbud_bp.route('/taskbud/daily-plan')
@login_required
def daily_plan():
    """View today's daily plan."""
    date_str = request.args.get('date')
    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.utcnow().date()
    else:
        date = datetime.utcnow().date()
    
    # Get plan for this date
    plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=date
    ).first()
    
    if not plan:
        plan = generate_daily_plan(current_user.id, date)
    
    # Get previous and next dates for navigation
    prev_date = date - timedelta(days=1)
    next_date = date + timedelta(days=1)
    
    return render_template(
        'taskbud/daily_plan.html',
        plan=plan,
        date=date,
        prev_date=prev_date,
        next_date=next_date
    )

@taskbud_bp.route('/taskbud/daily-plan/regenerate', methods=['POST'])
@login_required
def regenerate_daily_plan():
    """Force regenerate today's plan."""
    date_str = request.form.get('date')
    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.utcnow().date()
    else:
        date = datetime.utcnow().date()
    
    # Delete existing plan if any
    existing_plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=date
    ).first()
    
    if existing_plan:
        db.session.delete(existing_plan)
        db.session.commit()
    
    # Generate new plan
    generate_daily_plan(current_user.id, date)
    
    flash('Daily plan regenerated successfully', 'success')
    return redirect(url_for('taskbud.daily_plan', date=date.strftime('%Y-%m-%d')))

@taskbud_bp.route('/taskbud/daily-plan/update-task', methods=['POST'])
@login_required
def update_daily_task():
    """Update a task in the daily plan."""
    plan_id = request.form.get('plan_id', type=int)
    task_index = request.form.get('task_index', type=int)
    completed = request.form.get('completed') == 'true'
    
    plan = DailyPlan.query.filter_by(
        id=plan_id,
        user_id=current_user.id
    ).first_or_404()
    
    tasks = plan.get_tasks()
    
    if 0 <= task_index < len(tasks):
        # Update the task
        tasks[task_index]['completed'] = completed
        
        # If task has a DB ID, update the actual task
        task_id = tasks[task_index].get('id')
        if task_id and completed:
            task = Task.query.get(task_id)
            if task:
                task.mark_complete()
        
        # Save the updated tasks
        plan.set_tasks(tasks)
        
        # Update completion rate
        plan.update_completion_rate()
        
        return jsonify({
            'success': True,
            'completion_rate': plan.completion_rate
        })
    
    return jsonify({'success': False, 'error': 'Invalid task index'})

@taskbud_bp.route('/taskbud/stats')
@login_required
def statistics():
    """View task and goal statistics."""
    stats = get_goal_statistics(current_user.id)
    
    # Get recent activities
    activities = TaskActivity.query.filter_by(
        user_id=current_user.id
    ).order_by(TaskActivity.created_at.desc()).limit(20).all()
    
    # Get completion history for the entire year
    today = datetime.utcnow().date()
    start_date = datetime(today.year, 1, 1).date()
    days = (today - start_date).days + 1
    history = []
    
    # Pre-populate history with all dates from Jan 1 to today
    for i in range(days):
        date = start_date + timedelta(days=i)
        history.append({'date': date.strftime('%Y-%m-%d'), 'count': 0})
    
    # Fetch completed tasks and update counts
    completed_tasks = Task.query.join(Goal).filter(
        Goal.user_id == current_user.id,
        Task.completed == True,
        Task.completed_at >= start_date,
        Task.completed_at <= today
    ).with_entities(Task.completed_at.cast(db.Date), db.func.count()).group_by(Task.completed_at.cast(db.Date)).all()
    
    # Update history with actual counts
    for date, count in completed_tasks:
        date_str = date.strftime('%Y-%m-%d')
        for entry in history:
            if entry['date'] == date_str:
                entry['count'] = count
                break
    
    return render_template(
        'taskbud/statistics.html',
        stats=stats,
        activities=activities,
        history=history
    )

@taskbud_bp.route('/taskbud/api/generate-tasks', methods=['POST'])
@login_required
def api_generate_tasks():
    """API endpoint to generate tasks for a goal using AI."""
    goal_id = request.json.get('goal_id')
    
    goal = Goal.query.filter_by(
        id=goal_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Extract keywords from goal title and description
    keywords = re.findall(r'\b\w{3,}\b', (goal.title + ' ' + (goal.description or '')).lower())
    
    # Generate tasks based on goal type and keywords
    suggested_tasks = []
    
    if 'learn' in keywords or 'study' in keywords:
        suggested_tasks = [
            {
                'title': f"Research resources for {goal.title}",
                'priority': 1,
                'estimated_hours': 2.0,
                'tags': 'research,planning'
            },
            {
                'title': f"Create study plan for {goal.title}",
                'priority': 1,
                'estimated_hours': 1.5,
                'tags': 'planning,organization'
            },
            {
                'title': f"Complete first module of {goal.title}",
                'priority': 2,
                'estimated_hours': 3.0,
                'tags': 'learning,progress'
            }
        ]
    elif 'project' in keywords:
        suggested_tasks = [
            {
                'title': f"Define requirements for {goal.title}",
                'priority': 1,
                'estimated_hours': 2.0,
                'tags': 'planning,requirements'
            },
            {
                'title': f"Create timeline for {goal.title}",
                'priority': 1,
                'estimated_hours': 1.0,
                'tags': 'planning,timeline'
            },
            {
                'title': f"Identify resources needed for {goal.title}",
                'priority': 2,
                'estimated_hours': 1.5,
                'tags': 'resources,planning'
            }
        ]
    elif 'fitness' in keywords or 'exercise' in keywords or 'workout' in keywords:
        suggested_tasks = [
            {
                'title': f"Research workout routines for {goal.title}",
                'priority': 1,
                'estimated_hours': 1.0,
                'tags': 'research,fitness'
            },
            {
                'title': f"Create workout schedule for {goal.title}",
                'priority': 1,
                'estimated_hours': 1.0,
                'tags': 'planning,fitness'
            },
            {
                'title': f"Complete first week of {goal.title} workouts",
                'priority': 2,
                'estimated_hours': 3.0,
                'tags': 'fitness,progress'
            }
        ]
    else:
        # Generic tasks if no specific category is detected
        suggested_tasks = [
            {
                'title': f"Research and planning for {goal.title}",
                'priority': 1,
                'estimated_hours': 2.0,
                'tags': 'research,planning'
            },
            {
                'title': f"Identify first steps for {goal.title}",
                'priority': 1,
                'estimated_hours': 1.0,
                'tags': 'planning,first steps'
            },
            {
                'title': f"Set milestones for {goal.title}",
                'priority': 2,
                'estimated_hours': 1.5,
                'tags': 'planning,milestones'
            }
        ]
    
    # Calculate due dates based on goal target date
    target_date = goal.target_date
    today = datetime.utcnow()
    
    for i, task in enumerate(suggested_tasks):
        if target_date:
            # Calculate days between today and target date
            days_range = (target_date - today).days
            
            if days_range > 0:
                # Distribute tasks across the available time
                # First tasks due sooner, later tasks due closer to the target date
                due_days = max(1, int(days_range * (i+1) / (len(suggested_tasks) + 1)))
                task['due_date'] = (today + timedelta(days=due_days)).strftime('%Y-%m-%d')
    
    return jsonify({
        'success': True,
        'tasks': suggested_tasks
    })

@taskbud_bp.route('/taskbud/api/create-suggested-tasks', methods=['POST'])
@login_required
def api_create_suggested_tasks():
    """API endpoint to create suggested tasks."""
    # Validate CSRF token for API endpoints
    if request.json.get('csrf_token') != generate_csrf():
        return jsonify({
            'success': False,
            'error': 'Invalid CSRF token'
        }), 403
        
    goal_id = request.json.get('goal_id')
    tasks = request.json.get('tasks', [])
    
    goal = Goal.query.filter_by(
        id=goal_id,
        user_id=current_user.id
    ).first_or_404()
    
    created_tasks = []
    
    for task_data in tasks:
        # Parse due date if provided
        due_date = None
        if 'due_date' in task_data and task_data['due_date']:
            try:
                due_date = datetime.strptime(task_data['due_date'], '%Y-%m-%d')
            except ValueError:
                pass
        
        task = Task(
            goal_id=goal.id,
            title=task_data['title'],
            description=task_data.get('description', ''),
            priority=task_data.get('priority', 2),
            status='pending',
            due_date=due_date,
            difficulty=task_data.get('difficulty', 2),
            estimated_hours=task_data.get('estimated_hours', 1.0),
            tags=task_data.get('tags', ''),
            is_ai_generated=True
        )
        
        db.session.add(task)
        created_tasks.append(task)
    
    if created_tasks:
        db.session.commit()
        
        # Log activity
        activity = TaskActivity(
            user_id=current_user.id,
            goal_id=goal.id,
            activity_type='generated',
            details=f"Generated {len(created_tasks)} tasks for goal: {goal.title}"
        )
        db.session.add(activity)
        db.session.commit()
    
    return jsonify({
        'success': True,
        'count': len(created_tasks),
        'redirect': url_for('taskbud.view_goal', goal_id=goal.id)
    })

# Initialize CSRF protection for the blueprint
def init_csrf(app):
    csrf = CSRFProtect(app)
    return csrf