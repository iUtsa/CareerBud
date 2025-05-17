from app import db
from datetime import datetime, timedelta
import json
from sqlalchemy import func

class Goal(db.Model):
    """Model for long-term and short-term goals."""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    goal_type = db.Column(db.String(50), default='long_term')  # long_term, short_term
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    priority = db.Column(db.Integer, default=2)  # 1=high, 2=medium, 3=low
    progress = db.Column(db.Float, default=0.0)  # percentage 0-100
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('goals', lazy=True))
    tasks = db.relationship('Task', backref='goal', lazy=True, cascade='all, delete-orphan')
    sub_goals = db.relationship('Goal', backref=db.backref('parent_goal', remote_side=[id]), lazy=True)
    
    # AI-related fields
    ai_suggestions = db.Column(db.Text)  # JSON string to store AI suggestions
    
    def __repr__(self):
        return f'<Goal {self.title}>'
    
    def calculate_progress(self):
        """Calculate progress based on completed tasks."""
        if not self.tasks:
            # If a goal has sub-goals, calculate progress from them
            if self.sub_goals:
                total_progress = sum(sub_goal.progress for sub_goal in self.sub_goals)
                total_goals = len(self.sub_goals)
                self.progress = total_progress / total_goals if total_goals > 0 else 0
            return self.progress
            
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task.completed)
        
        self.progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Check if goal is completed
        if self.progress >= 100 and not self.completed_at:
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            
        db.session.commit()
        return self.progress
    
    def get_ai_suggestions(self):
        """Get AI suggestions as Python object."""
        if self.ai_suggestions:
            return json.loads(self.ai_suggestions)
        return {}
    
    def set_ai_suggestions(self, suggestions_dict):
        """Save AI suggestions as JSON string."""
        self.ai_suggestions = json.dumps(suggestions_dict)
        db.session.commit()
    
    def days_remaining(self):
        """Calculate days remaining until target date."""
        if not self.target_date:
            return None
        return (self.target_date - datetime.utcnow()).days
    
    def is_overdue(self):
        """Check if goal is overdue."""
        if not self.target_date:
            return False
        return datetime.utcnow() > self.target_date and self.status != 'completed'


class Task(db.Model):
    """Model for tasks related to goals."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Integer, default=2)  # 1=high, 2=medium, 3=low
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI-related fields
    is_ai_generated = db.Column(db.Boolean, default=False)
    difficulty = db.Column(db.Integer, default=2)  # 1=easy, 2=medium, 3=hard
    estimated_hours = db.Column(db.Float, default=1.0)  # Estimated hours to complete
    tags = db.Column(db.String(255))  # Comma-separated tags
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def mark_complete(self):
        """Mark task as complete and update goal progress."""
        self.completed = True
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Update goal progress
        self.goal.calculate_progress()
    
    def is_overdue(self):
        """Check if task is overdue."""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and not self.completed
    
    def days_remaining(self):
        """Calculate days remaining until due date."""
        if not self.due_date:
            return None
        return (self.due_date - datetime.utcnow()).days
    
    def get_tags_list(self):
        """Return tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def set_tags_list(self, tags_list):
        """Set tags from a list."""
        if not tags_list:
            self.tags = ''
        else:
            self.tags = ','.join(tags_list)
        db.session.commit()


class DailyPlan(db.Model):
    """Model for daily task plans generated by AI."""
    __tablename__ = 'daily_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    tasks_json = db.Column(db.Text)  # JSON string of daily tasks
    completion_rate = db.Column(db.Float, default=0.0)  # percentage of completed tasks
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('daily_plans', lazy=True))
    
    def __repr__(self):
        return f'<DailyPlan for {self.date}>'
    
    def get_tasks(self):
        """Get tasks as Python object."""
        if self.tasks_json:
            return json.loads(self.tasks_json)
        return []
    
    def set_tasks(self, tasks_list):
        """Save tasks as JSON string."""
        self.tasks_json = json.dumps(tasks_list)
        db.session.commit()
    
    def update_completion_rate(self):
        """Update completion rate based on completed tasks."""
        tasks = self.get_tasks()
        if not tasks:
            self.completion_rate = 0.0
            return
            
        completed = sum(1 for task in tasks if task.get('completed', False))
        self.completion_rate = (completed / len(tasks)) * 100
        db.session.commit()


class TaskActivity(db.Model):
    """Model for logging task activity for analytics."""
    __tablename__ = 'task_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=True)
    activity_type = db.Column(db.String(50))  # created, completed, updated, etc.
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('task_activities', lazy=True))
    task = db.relationship('Task', backref=db.backref('activities', lazy=True))
    goal = db.relationship('Goal', backref=db.backref('activities', lazy=True))
    
    def __repr__(self):
        return f'<TaskActivity {self.activity_type}>'


# Helper functions for TaskBud
def get_user_goals(user_id, goal_type=None, status=None):
    """Get goals for a user with optional filters."""
    query = Goal.query.filter_by(user_id=user_id)
    
    if goal_type:
        query = query.filter_by(goal_type=goal_type)
    
    if status:
        query = query.filter_by(status=status)
    
    return query.order_by(Goal.priority, Goal.created_at.desc()).all()

def get_user_tasks(user_id, status=None, due_date=None):
    """Get tasks for a user with optional filters."""
    query = Task.query.join(Goal).filter(Goal.user_id == user_id)
    
    if status:
        query = query.filter(Task.status == status)
    
    if due_date:
        query = query.filter(func.date(Task.due_date) == due_date)
    
    return query.order_by(Task.priority, Task.due_date).all()

def get_overdue_tasks(user_id):
    """Get overdue tasks for a user."""
    return Task.query.join(Goal).filter(
        Goal.user_id == user_id,
        Task.due_date < datetime.utcnow(),
        Task.completed == False
    ).order_by(Task.due_date).all()

def get_upcoming_tasks(user_id, days=7):
    """Get upcoming tasks for the next X days."""
    end_date = datetime.utcnow() + timedelta(days=days)
    return Task.query.join(Goal).filter(
        Goal.user_id == user_id,
        Task.due_date >= datetime.utcnow(),
        Task.due_date <= end_date,
        Task.completed == False
    ).order_by(Task.due_date).all()

def get_today_tasks(user_id):
    """Get tasks due today."""
    today = datetime.utcnow().date()
    return get_user_tasks(user_id, due_date=today)

def generate_daily_plan(user_id, date=None):
    """Generate a daily plan based on goals and tasks."""
    if not date:
        date = datetime.utcnow().date()
    
    # Check if plan already exists
    existing_plan = DailyPlan.query.filter_by(
        user_id=user_id,
        date=date
    ).first()
    
    if existing_plan:
        return existing_plan
    
    # Get tasks due today
    today_tasks = get_today_tasks(user_id)
    
    # Get overdue tasks (limited to 3)
    overdue_tasks = get_overdue_tasks(user_id)[:3]
    
    # Get high priority tasks from goals (limited to 5)
    high_priority_tasks = Task.query.join(Goal).filter(
        Goal.user_id == user_id,
        Task.priority == 1,
        Task.completed == False
    ).limit(5).all()
    
    # Combine tasks and create a plan
    all_tasks = []
    task_ids_added = set()
    
    # Add today's tasks
    for task in today_tasks:
        if task.id not in task_ids_added:
            all_tasks.append({
                'id': task.id,
                'title': task.title,
                'priority': task.priority,
                'goal_id': task.goal_id,
                'goal_title': task.goal.title,
                'completed': False,
                'source': 'due_today',
                'estimated_hours': task.estimated_hours
            })
            task_ids_added.add(task.id)
    
    # Add overdue tasks
    for task in overdue_tasks:
        if task.id not in task_ids_added:
            all_tasks.append({
                'id': task.id,
                'title': task.title,
                'priority': task.priority,
                'goal_id': task.goal_id,
                'goal_title': task.goal.title,
                'completed': False,
                'source': 'overdue',
                'estimated_hours': task.estimated_hours
            })
            task_ids_added.add(task.id)
    
    # Add high priority tasks
    for task in high_priority_tasks:
        if task.id not in task_ids_added:
            all_tasks.append({
                'id': task.id,
                'title': task.title,
                'priority': task.priority,
                'goal_id': task.goal_id,
                'goal_title': task.goal.title,
                'completed': False,
                'source': 'high_priority',
                'estimated_hours': task.estimated_hours
            })
            task_ids_added.add(task.id)
    
    # Create the daily plan
    plan = DailyPlan(
        user_id=user_id,
        date=date,
        notes=f"Plan generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    )
    plan.set_tasks(all_tasks)
    
    db.session.add(plan)
    db.session.commit()
    
    return plan

def get_goal_statistics(user_id):
    """Get goal statistics for a user."""
    # Count of goals by type
    long_term_count = Goal.query.filter_by(
        user_id=user_id, 
        goal_type='long_term'
    ).count()
    
    short_term_count = Goal.query.filter_by(
        user_id=user_id, 
        goal_type='short_term'
    ).count()
    
    # Count by status
    active_count = Goal.query.filter_by(
        user_id=user_id, 
        status='active'
    ).count()
    
    completed_count = Goal.query.filter_by(
        user_id=user_id, 
        status='completed'
    ).count()
    
    # Task completion rates
    all_tasks = Task.query.join(Goal).filter(Goal.user_id == user_id).count()
    completed_tasks = Task.query.join(Goal).filter(
        Goal.user_id == user_id,
        Task.completed == True
    ).count()
    
    completion_rate = (completed_tasks / all_tasks * 100) if all_tasks > 0 else 0
    
    # Average progress of active goals
    active_goals = Goal.query.filter_by(
        user_id=user_id, 
        status='active'
    ).all()
    
    if active_goals:
        avg_progress = sum(goal.progress for goal in active_goals) / len(active_goals)
    else:
        avg_progress = 0
    
    return {
        'long_term_count': long_term_count,
        'short_term_count': short_term_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'all_tasks': all_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate,
        'avg_progress': avg_progress
    }