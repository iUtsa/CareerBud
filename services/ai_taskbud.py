from datetime import datetime, timedelta
import re
import random
import math

class TaskBudAI:
    """AI service for TaskBud recommendations and task generation."""
    
    def __init__(self, user_data=None):
        self.user_data = user_data or {}
        self.task_patterns = {
            'learning': [
                "Research {topic} fundamentals",
                "Complete first module on {topic}",
                "Practice {topic} for 1 hour",
                "Take notes on {topic} key concepts",
                "Review {topic} materials",
                "Find a mentor for {topic}",
                "Join a community for {topic} learners",
                "Create a study schedule for {topic}",
                "Build a small project using {topic}",
                "Test your knowledge on {topic}"
            ],
            'project': [
                "Define requirements for {project}",
                "Create a timeline for {project}",
                "Identify resources needed for {project}",
                "Set up development environment for {project}",
                "Design architecture for {project}",
                "Implement core functionality of {project}",
                "Test {project} functionality",
                "Get feedback on {project}",
                "Refine {project} based on feedback",
                "Document {project} process and results"
            ],
            'fitness': [
                "Research workout routines for {goal}",
                "Create a weekly workout schedule for {goal}",
                "Prepare meal plan supporting {goal}",
                "Complete first week of {goal} training",
                "Track progress on {goal}",
                "Adjust routine based on {goal} progress",
                "Find accountability partner for {goal}",
                "Research supplements for {goal}",
                "Rest and recovery day for {goal}",
                "Evaluate {goal} progress and adjust plan"
            ],
            'career': [
                "Update resume for {career_goal}",
                "Research companies in {career_goal} field",
                "Network with professionals in {career_goal}",
                "Learn a new skill for {career_goal}",
                "Apply for {career_goal} positions",
                "Prepare for interviews in {career_goal}",
                "Set up job alerts for {career_goal}",
                "Attend event related to {career_goal}",
                "Find a mentor in {career_goal} field",
                "Update LinkedIn profile for {career_goal}"
            ],
            'financial': [
                "Create budget for {financial_goal}",
                "Research investment options for {financial_goal}",
                "Set up automatic savings for {financial_goal}",
                "Track expenses related to {financial_goal}",
                "Meet with financial advisor about {financial_goal}",
                "Reduce expenses to support {financial_goal}",
                "Increase income sources for {financial_goal}",
                "Review progress on {financial_goal}",
                "Adjust strategy for {financial_goal}",
                "Celebrate milestone for {financial_goal}"
            ],
            'generic': [
                "Research and planning for {goal}",
                "Identify first steps for {goal}",
                "Set milestones for {goal}",
                "Create a timeline for {goal}",
                "Find resources for {goal}",
                "Get feedback on {goal} progress",
                "Review and adjust {goal} plan",
                "Document progress on {goal}",
                "Share {goal} progress with stakeholders",
                "Celebrate {goal} milestone"
            ]
        }
    
    def categorize_goal(self, goal_title, goal_description=None):
        """Determine the category of a goal based on title and description."""
        combined_text = (goal_title + ' ' + (goal_description or '')).lower()
        
        # Define keywords for each category
        categories = {
            'learning': ['learn', 'study', 'course', 'education', 'knowledge', 'skill', 'training', 'language', 'certification'],
            'project': ['project', 'build', 'create', 'develop', 'launch', 'implement', 'design', 'app', 'website', 'software'],
            'fitness': ['fitness', 'exercise', 'workout', 'health', 'weight', 'diet', 'nutrition', 'gym', 'run', 'marathon', 'muscle'],
            'career': ['career', 'job', 'profession', 'work', 'promotion', 'salary', 'interview', 'resume', 'linkedin', 'networking'],
            'financial': ['finance', 'money', 'save', 'invest', 'budget', 'debt', 'expense', 'income', 'retirement', 'mortgage']
        }
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            category_scores[category] = score
        
        # Find the category with the highest score
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        # If no significant matches, return generic
        if best_category[1] == 0:
            return 'generic'
        
        return best_category[0]
    
    def generate_tasks_for_goal(self, goal, count=5):
        """Generate appropriate tasks for a goal."""
        # Determine goal category
        category = self.categorize_goal(goal.title, goal.description)
        
        # Get patterns for this category
        patterns = self.task_patterns.get(category, self.task_patterns['generic'])
        
        # Shuffle patterns and take requested count
        random.shuffle(patterns)
        selected_patterns = patterns[:min(count, len(patterns))]
        
        # Extract key terms from goal title
        key_terms = re.findall(r'\b[a-zA-Z]{3,}\b', goal.title)
        key_term = key_terms[0] if key_terms else "goal"
        
        # Generate tasks by filling in patterns
        tasks = []
        for pattern in selected_patterns:
            task_title = pattern.format(
                topic=key_term,
                project=goal.title,
                goal=goal.title,
                career_goal=key_term,
                financial_goal=key_term
            )
            
            # Generate appropriate task metadata
            priority = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
            difficulty = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
            estimated_hours = round(random.uniform(0.5, 4.0), 1)
            
            # Generate appropriate tags
            available_tags = [
                category, key_term, 'planning', 'progress', 'milestone', 
                'research', 'implementation', 'review', 'feedback'
            ]
            selected_tags = random.sample(available_tags, min(3, len(available_tags)))
            
            tasks.append({
                'title': task_title,
                'priority': priority,
                'difficulty': difficulty,
                'estimated_hours': estimated_hours,
                'tags': ','.join(selected_tags)
            })
        
        # Distribute tasks over time if goal has a target date
        self._schedule_tasks(tasks, goal)
        
        return tasks
    
    def _schedule_tasks(self, tasks, goal):
        """Schedule tasks across the goal timeline."""
        if not goal.target_date:
            return
        
        today = datetime.utcnow()
        days_range = (goal.target_date - today).days
        
        if days_range <= 0:
            return
        
        # Distribute tasks using different distribution patterns
        # based on task priorities
        for i, task in enumerate(tasks):
            priority = task['priority']
            
            if priority == 1:  # High priority: front-loaded
                due_factor = math.sqrt((i+1) / len(tasks))
            elif priority == 2:  # Medium priority: evenly distributed
                due_factor = (i+1) / len(tasks)
            else:  # Low priority: back-loaded
                due_factor = ((i+1) / len(tasks)) ** 2
            
            due_days = max(1, int(days_range * due_factor))
            task['due_date'] = (today + timedelta(days=due_days)).strftime('%Y-%m-%d')
    
    def suggest_daily_tasks(self, user_tasks, user_goals, max_tasks=5):
        """Suggest daily tasks based on user's goals and tasks."""
        # Find overdue and high priority tasks
        overdue_tasks = [task for task in user_tasks if task.is_overdue()]
        high_priority_tasks = [task for task in user_tasks if task.priority == 1 and not task.completed]
        
        # Find active goals with upcoming deadlines
        urgent_goals = sorted(
            [goal for goal in user_goals if goal.status == 'active' and goal.target_date], 
            key=lambda g: g.days_remaining() or 999
        )
        
        # Start with most critical tasks
        suggested_tasks = []
        
        # Add most overdue tasks
        for task in sorted(overdue_tasks, key=lambda t: t.due_date)[:2]:
            if len(suggested_tasks) < max_tasks:
                suggested_tasks.append(task)
        
        # Add highest priority tasks
        for task in high_priority_tasks[:2]:
            if len(suggested_tasks) < max_tasks and task not in suggested_tasks:
                suggested_tasks.append(task)
        
        # Add tasks from urgent goals
        for goal in urgent_goals[:2]:
            pending_tasks = [task for task in goal.tasks if not task.completed]
            if pending_tasks and len(suggested_tasks) < max_tasks:
                # Choose a task from this goal
                chosen_task = min(pending_tasks, key=lambda t: t.priority)
                if chosen_task not in suggested_tasks:
                    suggested_tasks.append(chosen_task)
        
        # Fill remaining slots with a mix of tasks
        remaining_tasks = [
            task for task in user_tasks 
            if not task.completed and task not in suggested_tasks
        ]
        
        # Sort by a weighted score of priority and due date
        def task_score(task):
            priority_score = task.priority * 10
            days_score = task.days_remaining() or 100
            return priority_score + days_score
        
        remaining_tasks.sort(key=task_score)
        
        for task in remaining_tasks:
            if len(suggested_tasks) < max_tasks:
                suggested_tasks.append(task)
            else:
                break
        
        return suggested_tasks
    
    def analyze_productivity_patterns(self, task_activities, completed_tasks):
        """Analyze user productivity patterns from task history."""
        if not task_activities or not completed_tasks:
            return {
                'peak_days': ['Monday', 'Wednesday'],  # Default suggestion
                'peak_hours': ['9 AM', '2 PM'],  # Default suggestion
                'task_preference': 'varied',
                'completion_rate': 0,
                'avg_completion_time': 0
            }
        
        # Extract completion timestamps
        completion_times = [task.completed_at for task in completed_tasks if task.completed_at]
        
        # Analyze peak days
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = [0] * 7
        
        for timestamp in completion_times:
            day_counts[timestamp.weekday()] += 1
        
        # Find the top 2 days
        day_indices = sorted(range(len(day_counts)), key=lambda i: day_counts[i], reverse=True)[:2]
        peak_days = [weekdays[i] for i in day_indices]
        
        # Analyze peak hours
        hour_counts = [0] * 24
        
        for timestamp in completion_times:
            hour_counts[timestamp.hour] += 1
        
        # Find the top 2 hours
        hour_indices = sorted(range(len(hour_counts)), key=lambda i: hour_counts[i], reverse=True)[:2]
        peak_hours = [f"{i if i <= 12 else i-12} {'AM' if i < 12 or i == 24 else 'PM'}" for i in hour_indices]
        
        # Analyze task preferences
        task_types = {}
        for task in completed_tasks:
            if task.tags:
                for tag in task.get_tags_list():
                    if tag not in task_types:
                        task_types[tag] = 0
                    task_types[tag] += 1
        
        # Find the most common tags
        preferred_tasks = []
        if task_types:
            preferred_tasks = sorted(task_types.items(), key=lambda x: x[1], reverse=True)[:2]
            preferred_tasks = [t[0] for t in preferred_tasks]
            task_preference = ', '.join(preferred_tasks)
        else:
            task_preference = 'varied'
        
        # Calculate completion rate
        total_tasks = len(completed_tasks) + len([t for t in task_activities if t.activity_type == 'created'])
        completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average time to complete tasks
        avg_completion_time = 0
        completion_times = []
        
        for task in completed_tasks:
            if task.created_at and task.completed_at:
                time_diff = (task.completed_at - task.created_at).total_seconds() / 3600  # In hours
                completion_times.append(time_diff)
        
        if completion_times:
            avg_completion_time = sum(completion_times) / len(completion_times)
        
        return {
            'peak_days': peak_days,
            'peak_hours': peak_hours,
            'task_preference': task_preference,
            'completion_rate': round(completion_rate, 1),
            'avg_completion_time': round(avg_completion_time, 1)
        }
    
    def suggest_goal_improvements(self, goal, tasks):
        """Suggest improvements for goal based on progress and tasks."""
        suggestions = []
        
        # Check if goal has a target date
        if not goal.target_date:
            suggestions.append({
                'type': 'missing_target_date',
                'message': 'Set a target date to better track progress and stay motivated',
                'importance': 'high'
            })
        
        # Check if goal has any tasks
        if not tasks:
            suggestions.append({
                'type': 'no_tasks',
                'message': 'Break down your goal into specific tasks to make progress more manageable',
                'importance': 'high'
            })
        
        # Check if goal description is detailed enough
        if not goal.description or len(goal.description) < 50:
            suggestions.append({
                'type': 'brief_description',
                'message': 'Add more details to your goal description to clarify what success looks like',
                'importance': 'medium'
            })
        
        # Check if long-term goal has sub-goals
        if goal.goal_type == 'long_term' and not goal.sub_goals:
            suggestions.append({
                'type': 'no_sub_goals',
                'message': 'Create shorter-term sub-goals to make this long-term goal more achievable',
                'importance': 'high'
            })
        
        # Check progress rate
        if goal.target_date and goal.progress < 20:
            days_passed = (datetime.utcnow() - goal.start_date).days
            total_days = (goal.target_date - goal.start_date).days
            
            if total_days > 0:
                expected_progress = (days_passed / total_days) * 100
                
                if expected_progress > goal.progress + 20:
                    suggestions.append({
                        'type': 'behind_schedule',
                        'message': 'Your goal is behind schedule. Consider adjusting the timeline or breaking it into smaller tasks',
                        'importance': 'high'
                    })
        
        return suggestions
    
    def recommend_resources(self, goal):
        """Recommend resources based on goal category."""
        category = self.categorize_goal(goal.title, goal.description)
        
        resources = {
            'learning': [
                {'type': 'app', 'name': 'Anki', 'url': 'https://apps.ankiweb.net/', 'description': 'Spaced repetition flashcard system'},
                {'type': 'website', 'name': 'Coursera', 'url': 'https://www.coursera.org/', 'description': 'Online courses from top universities'},
                {'type': 'book', 'name': 'How to Learn Anything Fast', 'description': 'Book by Josh Kaufman'}
            ],
            'project': [
                {'type': 'app', 'name': 'Trello', 'url': 'https://trello.com/', 'description': 'Project management tool'},
                {'type': 'website', 'name': 'GitHub', 'url': 'https://github.com/', 'description': 'Version control and collaboration'},
                {'type': 'method', 'name': 'Agile Methodology', 'description': 'Iterative approach to project management'}
            ],
            'fitness': [
                {'type': 'app', 'name': 'MyFitnessPal', 'url': 'https://www.myfitnesspal.com/', 'description': 'Nutrition and exercise tracking'},
                {'type': 'website', 'name': 'Fitness Blender', 'url': 'https://www.fitnessblender.com/', 'description': 'Free workout videos'},
                {'type': 'book', 'name': 'Atomic Habits', 'description': 'Book by James Clear on building fitness habits'}
            ],
            'career': [
                {'type': 'website', 'name': 'LinkedIn Learning', 'url': 'https://www.linkedin.com/learning/', 'description': 'Professional skills courses'},
                {'type': 'app', 'name': 'Glassdoor', 'url': 'https://www.glassdoor.com/', 'description': 'Company reviews and salary information'},
                {'type': 'book', 'name': 'What Color Is Your Parachute?', 'description': 'Job-hunting and career guidance book'}
            ],
            'financial': [
                {'type': 'app', 'name': 'YNAB (You Need A Budget)', 'url': 'https://www.youneedabudget.com/', 'description': 'Budgeting software'},
                {'type': 'website', 'name': 'Investopedia', 'url': 'https://www.investopedia.com/', 'description': 'Financial education website'},
                {'type': 'book', 'name': 'The Simple Path to Wealth', 'description': 'Investment guide by JL Collins'}
            ],
            'generic': [
                {'type': 'app', 'name': 'Notion', 'url': 'https://www.notion.so/', 'description': 'All-in-one workspace'},
                {'type': 'website', 'name': 'Mindtools', 'url': 'https://www.mindtools.com/', 'description': 'Skills development resources'},
                {'type': 'book', 'name': 'Atomic Habits', 'description': 'Book by James Clear on building good habits'}
            ]
        }
        
        return resources.get(category, resources['generic'])