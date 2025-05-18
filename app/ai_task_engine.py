import json
import re
from datetime import datetime, timedelta
from collections import Counter
import numpy as np
from sqlalchemy import func
from app.models import Goal, Task, DailyPlan, db

class AITaskEngine:
    """Enhanced AI engine for intelligent task generation and planning."""
    
    # Task categories with associated keywords and suggested tasks
    TASK_CATEGORIES = {
        'learning': {
            'keywords': ['learn', 'study', 'education', 'course', 'book', 'read', 'knowledge', 'skill'],
            'tasks': [
                {'title': "Research resources and learning materials", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'research,planning', 'difficulty': 1},
                {'title': "Create detailed study plan", 'priority': 1, 'estimated_hours': 1.5, 'tags': 'planning,organization', 'difficulty': 2},
                {'title': "Set up learning environment", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'setup,preparation', 'difficulty': 1},
                {'title': "Complete first module/chapter", 'priority': 2, 'estimated_hours': 3.0, 'tags': 'learning,progress', 'difficulty': 2},
                {'title': "Schedule regular practice sessions", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'practice,consistency', 'difficulty': 1},
                {'title': "Find accountability partner or community", 'priority': 3, 'estimated_hours': 1.0, 'tags': 'community,support', 'difficulty': 1},
                {'title': "Create assessment method to track progress", 'priority': 2, 'estimated_hours': 1.5, 'tags': 'tracking,assessment', 'difficulty': 2},
                {'title': "Schedule mid-point review", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'review,assessment', 'difficulty': 2}
            ]
        },
        'project': {
            'keywords': ['project', 'develop', 'build', 'create', 'launch', 'implement', 'design'],
            'tasks': [
                {'title': "Define project scope and requirements", 'priority': 1, 'estimated_hours': 2.5, 'tags': 'planning,requirements', 'difficulty': 2},
                {'title': "Create detailed project timeline", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'planning,timeline', 'difficulty': 2},
                {'title': "Identify and secure required resources", 'priority': 1, 'estimated_hours': 1.5, 'tags': 'resources,planning', 'difficulty': 2},
                {'title': "Develop risk management plan", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'risk,planning', 'difficulty': 3},
                {'title': "Set up project tracking system", 'priority': 2, 'estimated_hours': 1.5, 'tags': 'tracking,organization', 'difficulty': 2},
                {'title': "Create communication plan for stakeholders", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'communication,stakeholders', 'difficulty': 2},
                {'title': "Develop prototype/initial version", 'priority': 1, 'estimated_hours': 4.0, 'tags': 'development,milestone', 'difficulty': 3},
                {'title': "Schedule regular progress reviews", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'review,tracking', 'difficulty': 1}
            ]
        },
        'fitness': {
            'keywords': ['fitness', 'exercise', 'workout', 'health', 'training', 'gym', 'run', 'strength', 'cardio'],
            'tasks': [
                {'title': "Research effective workout routines", 'priority': 1, 'estimated_hours': 1.5, 'tags': 'research,fitness', 'difficulty': 1},
                {'title': "Create weekly workout schedule", 'priority': 1, 'estimated_hours': 1.0, 'tags': 'planning,fitness', 'difficulty': 2},
                {'title': "Set up tracking method for progress", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'tracking,measurement', 'difficulty': 1},
                {'title': "Prepare workout environment/equipment", 'priority': 2, 'estimated_hours': 1.5, 'tags': 'preparation,equipment', 'difficulty': 1},
                {'title': "Plan nutrition strategy to support goals", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'nutrition,planning', 'difficulty': 2},
                {'title': "Complete first week of workouts", 'priority': 1, 'estimated_hours': 3.0, 'tags': 'fitness,milestone', 'difficulty': 2},
                {'title': "Schedule rest and recovery days", 'priority': 2, 'estimated_hours': 0.5, 'tags': 'recovery,health', 'difficulty': 1},
                {'title': "Find workout partner or community", 'priority': 3, 'estimated_hours': 1.0, 'tags': 'community,motivation', 'difficulty': 1}
            ]
        },
        'career': {
            'keywords': ['career', 'job', 'professional', 'work', 'business', 'promotion', 'skills', 'resume', 'interview'],
            'tasks': [
                {'title': "Update resume and professional profiles", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'resume,preparation', 'difficulty': 2},
                {'title': "Research industry trends and opportunities", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'research,industry', 'difficulty': 2},
                {'title': "Identify skill gaps and learning needs", 'priority': 1, 'estimated_hours': 1.5, 'tags': 'skills,assessment', 'difficulty': 2},
                {'title': "Create personal brand development plan", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'branding,strategy', 'difficulty': 3},
                {'title': "Schedule informational interviews", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'networking,research', 'difficulty': 2},
                {'title': "Join professional organizations or communities", 'priority': 3, 'estimated_hours': 1.0, 'tags': 'networking,community', 'difficulty': 1},
                {'title': "Create portfolio of work examples", 'priority': 2, 'estimated_hours': 3.0, 'tags': 'portfolio,examples', 'difficulty': 3},
                {'title': "Set up tracking for job applications", 'priority': 1, 'estimated_hours': 1.0, 'tags': 'tracking,organization', 'difficulty': 1}
            ]
        },
        'finance': {
            'keywords': ['finance', 'money', 'budget', 'save', 'invest', 'financial', 'debt', 'income', 'expense'],
            'tasks': [
                {'title': "Track expenses for one month", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'tracking,expenses', 'difficulty': 2},
                {'title': "Create detailed budget plan", 'priority': 1, 'estimated_hours': 2.5, 'tags': 'budget,planning', 'difficulty': 2},
                {'title': "Research investment options", 'priority': 2, 'estimated_hours': 3.0, 'tags': 'research,investments', 'difficulty': 3},
                {'title': "Set up automatic savings system", 'priority': 1, 'estimated_hours': 1.0, 'tags': 'savings,automation', 'difficulty': 1},
                {'title': "Create debt reduction strategy", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'debt,strategy', 'difficulty': 2},
                {'title': "Research tax optimization strategies", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'tax,optimization', 'difficulty': 3},
                {'title': "Set up emergency fund", 'priority': 1, 'estimated_hours': 1.0, 'tags': 'emergency,planning', 'difficulty': 1},
                {'title': "Schedule quarterly financial reviews", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'review,planning', 'difficulty': 2}
            ]
        },
        'creativity': {
            'keywords': ['creative', 'art', 'write', 'music', 'draw', 'paint', 'design', 'craft', 'novel', 'blog', 'podcast'],
            'tasks': [
                {'title': "Create project outline or concept", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'concept,planning', 'difficulty': 2},
                {'title': "Research techniques and inspiration", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'research,inspiration', 'difficulty': 1},
                {'title': "Set up dedicated creative workspace", 'priority': 2, 'estimated_hours': 1.5, 'tags': 'workspace,preparation', 'difficulty': 1},
                {'title': "Create schedule for regular practice", 'priority': 1, 'estimated_hours': 1.0, 'tags': 'schedule,practice', 'difficulty': 1},
                {'title': "Complete first draft/prototype", 'priority': 1, 'estimated_hours': 4.0, 'tags': 'creation,draft', 'difficulty': 3},
                {'title': "Find community for feedback and support", 'priority': 2, 'estimated_hours': 1.5, 'tags': 'community,feedback', 'difficulty': 2},
                {'title': "Develop revision and editing process", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'revision,process', 'difficulty': 2},
                {'title': "Plan sharing/publishing strategy", 'priority': 3, 'estimated_hours': 2.0, 'tags': 'publishing,strategy', 'difficulty': 2}
            ]
        },
        'technology': {
            'keywords': ['technology', 'tech', 'software', 'code', 'program', 'app', 'website', 'development', 'computer'],
            'tasks': [
                {'title': "Define technical requirements and scope", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'requirements,planning', 'difficulty': 2},
                {'title': "Set up development environment", 'priority': 1, 'estimated_hours': 2.0, 'tags': 'setup,environment', 'difficulty': 2},
                {'title': "Create architecture or design plan", 'priority': 1, 'estimated_hours': 3.0, 'tags': 'architecture,design', 'difficulty': 3},
                {'title': "Implement core functionality/features", 'priority': 1, 'estimated_hours': 4.0, 'tags': 'development,core', 'difficulty': 3},
                {'title': "Create testing plan and procedures", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'testing,quality', 'difficulty': 2},
                {'title': "Set up version control and backup system", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'version-control,backup', 'difficulty': 2},
                {'title': "Research and implement security measures", 'priority': 2, 'estimated_hours': 2.5, 'tags': 'security,implementation', 'difficulty': 3},
                {'title': "Create documentation for maintenance", 'priority': 3, 'estimated_hours': 2.0, 'tags': 'documentation,maintenance', 'difficulty': 2}
            ]
        },
        'personal': {
            'keywords': ['personal', 'self', 'habit', 'routine', 'wellbeing', 'development', 'growth', 'mindfulness'],
            'tasks': [
                {'title': "Define personal growth objectives", 'priority': 1, 'estimated_hours': 1.5, 'tags': 'objectives,planning', 'difficulty': 2},
                {'title': "Research methods and best practices", 'priority': 2, 'estimated_hours': 2.0, 'tags': 'research,methods', 'difficulty': 1},
                {'title': "Create daily/weekly routine", 'priority': 1, 'estimated_hours': 1.5, 'tags': 'routine,planning', 'difficulty': 2},
                {'title': "Set up tracking system for habits", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'tracking,habits', 'difficulty': 1},
                {'title': "Schedule regular reflection time", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'reflection,mindfulness', 'difficulty': 1},
                {'title': "Find accountability partner or mentor", 'priority': 3, 'estimated_hours': 1.0, 'tags': 'accountability,support', 'difficulty': 2},
                {'title': "Create reward system for milestones", 'priority': 3, 'estimated_hours': 1.0, 'tags': 'rewards,motivation', 'difficulty': 1},
                {'title': "Schedule monthly progress review", 'priority': 2, 'estimated_hours': 1.0, 'tags': 'review,assessment', 'difficulty': 1}
            ]
        }
    }
    
    @staticmethod
    def analyze_goal(goal):
        """Deeply analyze a goal to extract relevant contexts and keywords."""
        # Combine title and description
        text = (goal.title + " " + (goal.description or "")).lower()
        
        # Extract all meaningful words (3+ characters)
        words = re.findall(r'\b\w{3,}\b', text)
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Return word frequency dictionary
        return word_counts
    
    @staticmethod
    def detect_goal_category(goal):
        """Intelligently determine the most relevant category for a goal."""
        word_counts = AITaskEngine.analyze_goal(goal)
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, data in AITaskEngine.TASK_CATEGORIES.items():
            score = sum(word_counts.get(keyword, 0) * 2 for keyword in data['keywords'])
            
            # Check for direct keyword presence
            for keyword in data['keywords']:
                if keyword in (goal.title + " " + (goal.description or "")).lower():
                    score += 5  # Significant boost for direct keyword match
            
            category_scores[category] = score
        
        # If no strong matches, determine from goal type
        if max(category_scores.values(), default=0) == 0:
            if goal.goal_type == 'long_term':
                # For long-term goals with no clear category, default to project
                return 'project'
            else:
                # For short-term goals with no clear category, default to personal
                return 'personal'
        
        # Return category with highest score
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    @staticmethod
    def get_user_task_history(user_id):
        """Analyze user's task history to personalize recommendations."""
        # Get completed tasks for analysis
        completed_tasks = Task.query.join(Goal).filter(
            Goal.user_id == user_id,
            Task.completed == True
        ).order_by(Task.completed_at.desc()).limit(50).all()
        
        if not completed_tasks:
            return {
                'avg_completion_time': 7,  # days (default)
                'preferred_difficulty': 2,  # medium (default)
                'most_productive_tags': [],
                'task_completion_rate': 0.8  # 80% (default)
            }
        
        # Analyze completion times
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.completed_at:
                days = (task.completed_at - task.created_at).days
                if 0 <= days <= 30:  # Ignore outliers
                    completion_times.append(days)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 7
        
        # Analyze task difficulty preferences
        difficulties = [task.difficulty for task in completed_tasks if task.difficulty]
        preferred_difficulty = round(sum(difficulties) / len(difficulties)) if difficulties else 2
        
        # Analyze productive tags
        all_tags = []
        for task in completed_tasks:
            if task.tags:
                all_tags.extend([tag.strip() for tag in task.tags.split(',')])
        
        tag_counts = Counter(all_tags)
        most_productive_tags = [tag for tag, count in tag_counts.most_common(5)]
        
        # Calculate task completion rate
        all_user_tasks = Task.query.join(Goal).filter(
            Goal.user_id == user_id
        ).count()
        
        all_completed_tasks = Task.query.join(Goal).filter(
            Goal.user_id == user_id,
            Task.completed == True
        ).count()
        
        task_completion_rate = all_completed_tasks / all_user_tasks if all_user_tasks > 0 else 0.8
        
        return {
            'avg_completion_time': avg_completion_time,
            'preferred_difficulty': preferred_difficulty,
            'most_productive_tags': most_productive_tags,
            'task_completion_rate': task_completion_rate
        }
    
    @staticmethod
    def customize_tasks_for_user(tasks, user_profile):
        """Customize tasks based on user's historical performance."""
        customized_tasks = []
        
        for task in tasks:
            # Adjust task difficulty based on user preference
            if abs(task['difficulty'] - user_profile['preferred_difficulty']) > 1:
                task['difficulty'] = user_profile['preferred_difficulty']
            
            # Add user's productive tags where relevant
            task_tags = set(task['tags'].split(','))
            for tag in user_profile['most_productive_tags'][:2]:  # Add up to 2 productive tags
                if len(task_tags) < 5:  # Limit to 5 tags max
                    task_tags.add(tag)
            
            task['tags'] = ','.join(task_tags)
            
            # Adjust estimated hours based on completion rate
            if user_profile['task_completion_rate'] < 0.5:
                # User tends to complete fewer tasks, reduce estimates to be more achievable
                task['estimated_hours'] = max(0.5, task['estimated_hours'] * 0.8)
            elif user_profile['task_completion_rate'] > 0.9:
                # User completes tasks efficiently, can handle more
                task['estimated_hours'] = task['estimated_hours'] * 1.1
            
            customized_tasks.append(task)
        
        return customized_tasks
    
    @staticmethod
    def distribute_due_dates(tasks, target_date, start_date=None):
        """Intelligently distribute due dates for tasks."""
        if not start_date:
            start_date = datetime.utcnow()
        
        if not target_date:
            # If no target date, assign reasonable due dates based on priority
            for i, task in enumerate(tasks):
                if task['priority'] == 1:  # High priority
                    days_to_add = i + 2  # Start with soon due dates
                elif task['priority'] == 2:  # Medium priority
                    days_to_add = i + 5  # Medium timeframe
                else:  # Low priority
                    days_to_add = i + 8  # Longer timeframe
                
                task['due_date'] = (start_date + timedelta(days=days_to_add)).strftime('%Y-%m-%d')
            
            return tasks
        
        # Calculate total days between start and target
        days_range = (target_date - start_date).days
        
        if days_range <= 0:
            # If target date is in the past, assign all to tomorrow
            for task in tasks:
                task['due_date'] = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')
            return tasks
        
        # Distribute by priority and estimated time
        # First, calculate total estimated hours
        total_hours = sum(task.get('estimated_hours', 1.0) for task in tasks)
        
        # Sort tasks by priority (most important first)
        sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 2))
        
        # Distribute tasks
        for i, task in enumerate(sorted_tasks):
            # Calculate position in timeline based on priority and effort
            task_weight = (3 - task.get('priority', 2)) * 0.2 + task.get('estimated_hours', 1.0) / total_hours
            position = i / len(tasks) + task_weight
            
            # Normalize position to be between 0.1 and 0.9
            position = min(0.9, max(0.1, position))
            
            # Calculate days to add
            days_to_add = int(days_range * position)
            
            # Ensure high priority tasks come first
            if task.get('priority', 2) == 1:  # High priority
                days_to_add = min(days_to_add, days_range // 3)  # First third of the timeline
            elif task.get('priority', 2) == 3:  # Low priority
                days_to_add = max(days_to_add, days_range // 2)  # Second half of the timeline
            
            task['due_date'] = (start_date + timedelta(days=days_to_add)).strftime('%Y-%m-%d')
        
        return sorted_tasks
    
    @staticmethod
    def generate_tasks_for_goal(goal, num_tasks=None):
        """Generate intelligent, personalized tasks for a goal."""
        # Determine the most relevant category
        category = AITaskEngine.detect_goal_category(goal)
        
        # Get user profile for customization
        user_profile = AITaskEngine.get_user_task_history(goal.user_id)
        
        # Get base tasks from category
        base_tasks = AITaskEngine.TASK_CATEGORIES[category]['tasks']
        
        # Determine how many tasks to generate
        if not num_tasks:
            # Calculate appropriate number of tasks based on goal type and timeframe
            if goal.goal_type == 'long_term':
                num_tasks = min(8, len(base_tasks))
            else:
                num_tasks = min(5, len(base_tasks))
            
            # Adjust based on target date if available
            if goal.target_date:
                days_to_target = (goal.target_date - datetime.utcnow()).days
                if days_to_target <= 7:  # Short timeframe
                    num_tasks = min(3, num_tasks)
                elif days_to_target >= 30:  # Long timeframe
                    num_tasks = min(10, len(base_tasks))
        
        # Select most appropriate tasks
        selected_tasks = base_tasks[:num_tasks]
        
        # Personalize task titles with goal title
        for task in selected_tasks:
            task['title'] = task['title'].replace("project", goal.title).replace("workout", goal.title)
            
            # Ensure titles don't get too long
            if len(task['title']) > 70:
                task['title'] = task['title'][:67] + "..."
        
        # Customize tasks based on user profile
        customized_tasks = AITaskEngine.customize_tasks_for_user(selected_tasks, user_profile)
        
        # Distribute due dates intelligently
        final_tasks = AITaskEngine.distribute_due_dates(customized_tasks, goal.target_date)
        
        return final_tasks


# Enhanced functions that override/extend the functionality in models.py
def enhanced_generate_tasks(goal_id, user_id):
    """Enhanced AI function to generate tasks for a goal."""
    # Get the goal
    goal = Goal.query.filter_by(
        id=goal_id,
        user_id=user_id
    ).first()
    
    if not goal:
        return {
            'success': False,
            'error': 'Goal not found'
        }
    
    # Generate tasks using the AI engine
    suggested_tasks = AITaskEngine.generate_tasks_for_goal(goal)
    
    return {
        'success': True,
        'tasks': suggested_tasks
    }

def enhanced_generate_daily_plan(user_id, date=None):
    """Generate an enhanced daily plan based on goals, tasks, and user patterns."""
    if not date:
        date = datetime.utcnow().date()
    
    # Check if plan already exists
    existing_plan = DailyPlan.query.filter_by(
        user_id=user_id,
        date=date
    ).first()
    
    if existing_plan:
        return existing_plan
    
    # Get all active tasks for this user
    active_tasks = Task.query.join(Goal).filter(
        Goal.user_id == user_id,
        Task.completed == False
    ).all()
    
    if not active_tasks:
        # Create empty plan
        plan = DailyPlan(
            user_id=user_id,
            date=date,
            notes="No active tasks available for planning."
        )
        plan.set_tasks([])
        db.session.add(plan)
        db.session.commit()
        return plan
    
    # Score each task based on multiple factors
    task_scores = []
    
    for task in active_tasks:
        score = 0
        
        # Priority factor (1-3, higher priority = higher score)
        score += (4 - task.priority) * 10
        
        # Due date factor
        if task.due_date:
            days_until_due = (task.due_date.date() - date).days
            if days_until_due < 0:  # Overdue
                score += 15
            elif days_until_due == 0:  # Due today
                score += 12
            elif days_until_due <= 2:  # Due soon
                score += 8
            elif days_until_due <= 5:  # Due this week
                score += 5
        
        # Goal progress factor - prioritize tasks from goals with less progress
        if task.goal:
            score += max(0, (100 - task.goal.progress) / 10)
        
        # Goal priority factor
        if task.goal and task.goal.priority:
            score += (4 - task.goal.priority) * 5
        
        # Balance task difficulty
        if task.difficulty:
            # Distribute different difficulty levels throughout the day
            score += (task.difficulty - 2) * 2  # Slight preference for medium difficulty
        
        # Estimated time factor - include some quick wins
        if task.estimated_hours:
            if task.estimated_hours <= 1.0:
                score += 3  # Bonus for quick tasks
            elif task.estimated_hours >= 4.0:
                score -= 2  # Penalty for very long tasks
        
        task_scores.append((task, score))
    
    # Sort by score (highest first)
    task_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Get user profile to optimize plan
    user_profile = AITaskEngine.get_user_task_history(user_id)
    
    # Determine optimal number of tasks based on user's completion rate
    avg_tasks_per_day = min(10, max(3, int(5 / user_profile['task_completion_rate'])))
    
    # Balance workload based on estimated hours
    planned_tasks = []
    total_hours = 0
    target_hours = 6  # Target productive hours per day
    
    for task, score in task_scores:
        # Check if we've reached our task limit
        if len(planned_tasks) >= avg_tasks_per_day:
            break
            
        # Check if we've reached our hours limit
        task_hours = task.estimated_hours or 1.0
        if total_hours + task_hours > target_hours * 1.2:  # Allow slight overflow
            # Only add if high priority or due soon
            if task.priority == 1 or (task.due_date and (task.due_date.date() - date).days <= 1):
                pass  # Continue to add despite hour limit
            else:
                continue  # Skip this task
        
        # Add task to plan
        planned_tasks.append({
            'id': task.id,
            'title': task.title,
            'priority': task.priority,
            'goal_id': task.goal_id,
            'goal_title': task.goal.title if task.goal else None,
            'completed': False,
            'source': 'ai_optimized',
            'estimated_hours': task.estimated_hours,
            'difficulty': task.difficulty,
            'tags': task.tags
        })
        
        total_hours += task_hours
    
    # Create the daily plan
    plan = DailyPlan(
        user_id=user_id,
        date=date,
        notes=f"AI-optimized plan with {len(planned_tasks)} tasks totaling {total_hours:.1f} hours"
    )
    plan.set_tasks(planned_tasks)
    
    db.session.add(plan)
    db.session.commit()
    
    return plan