/**
 * TaskBud main JavaScript functionality
 */

// Initialize module
const TaskBud = (function() {
    
    // DOM elements cache
    const DOM = {};
    
    // App state
    const state = {
        selectedGoal: null,
        currentView: 'dashboard',
        taskFilters: {
            status: 'all',
            priority: 'all',
            dueDate: 'all'
        }
    };
    
    /**
     * Initialize the TaskBud application
     */
    function init() {
        // Cache DOM elements
        cacheDOM();
        
        // Setup event listeners
        bindEvents();
        
        // Initialize components
        initComponents();
        
        console.log('TaskBud initialized');
    }
    
    /**
     * Cache frequently used DOM elements
     */
    function cacheDOM() {
        // Task-related elements
        DOM.taskCheckboxes = document.querySelectorAll('.task-checkbox');
        DOM.taskItems = document.querySelectorAll('.task-item');
        DOM.deleteTaskButtons = document.querySelectorAll('.delete-task-btn');
        
        // Goal-related elements
        DOM.goalCards = document.querySelectorAll('.goal-card');
        DOM.deleteGoalButton = document.querySelector('.delete-goal-btn');
        DOM.progressCircles = document.querySelectorAll('.progress-circle');
        
        // Form elements
        DOM.taskForms = document.querySelectorAll('.task-form');
        DOM.goalForms = document.querySelectorAll('.goal-form');
        
        // Filter elements
        DOM.filterButtons = document.querySelectorAll('.filter-button');
        DOM.sortSelect = document.getElementById('sort-select');
        
        // AI related elements
        DOM.generateTasksBtn = document.getElementById('generate-tasks-btn');
    }
    
    /**
     * Bind event listeners
     */
    function bindEvents() {
        // Task checkboxes
        if (DOM.taskCheckboxes.length) {
            DOM.taskCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', handleTaskCompletion);
            });
        }
        
        // Delete task buttons
        if (DOM.deleteTaskButtons.length) {
            DOM.deleteTaskButtons.forEach(button => {
                button.addEventListener('click', handleTaskDeletion);
            });
        }
        
        // Delete goal button
        if (DOM.deleteGoalButton) {
            DOM.deleteGoalButton.addEventListener('click', handleGoalDeletion);
        }
        
        // Task form submission
        if (DOM.taskForms.length) {
            DOM.taskForms.forEach(form => {
                form.addEventListener('submit', validateTaskForm);
            });
        }
        
        // Goal form submission
        if (DOM.goalForms.length) {
            DOM.goalForms.forEach(form => {
                form.addEventListener('submit', validateGoalForm);
            });
        }
        
        // Filter buttons
        if (DOM.filterButtons.length) {
            DOM.filterButtons.forEach(button => {
                button.addEventListener('click', handleFilterToggle);
            });
        }
        
        // Sort select
        if (DOM.sortSelect) {
            DOM.sortSelect.addEventListener('change', handleSort);
        }
        
        // AI Task generation
        if (DOM.generateTasksBtn) {
            DOM.generateTasksBtn.addEventListener('click', handleAITaskGeneration);
        }
    }
    
    /**
     * Initialize UI components
     */
    function initComponents() {
        // Initialize progress circles
        initProgressCircles();
        
        // Initialize date pickers
        initDatePickers();
        
        // Initialize tooltips
        initTooltips();
    }
    
    /**
     * Handle task completion toggle
     * @param {Event} e - The event object
     */
    function handleTaskCompletion(e) {
        const checkbox = e.target;
        const taskId = checkbox.dataset.taskId;
        const taskItem = document.getElementById(`task-${taskId}`);
        
        if (checkbox.checked) {
            // Add completed class and animation
            taskItem.classList.add('task-completed');
            taskItem.classList.add('task-complete-animation');
            
            // AJAX request to mark task as completed
            const url = `/taskbud/tasks/${taskId}/complete`;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update goal progress if available
                    updateGoalProgress(data.goal_progress);
                    
                    // After animation completes, you might want to refresh or update UI
                    setTimeout(() => {
                        // Optional: refresh or update UI
                    }, 500);
                }
            })
            .catch(error => {
                console.error('Error completing task:', error);
                
                // Revert UI change on error
                checkbox.checked = false;
                taskItem.classList.remove('task-completed', 'task-complete-animation');
            });
        }
    }
    
    /**
     * Handle task deletion UI
     * @param {Event} e - The event object
     */
    function handleTaskDeletion(e) {
        const taskId = e.currentTarget.dataset.taskId;
        
        // Show confirmation dialog
        const confirmed = confirm('Are you sure you want to delete this task?');
        
        if (confirmed) {
            // Submit deletion form
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/taskbud/tasks/${taskId}/delete`;
            document.body.appendChild(form);
            form.submit();
        }
    }
    
    /**
     * Handle goal deletion UI
     * @param {Event} e - The event object
     */
    function handleGoalDeletion(e) {
        // Modal handling is done in individual templates
        console.log('Goal deletion triggered');
    }
    
    /**
     * Validate task form before submission
     * @param {Event} e - The event object
     */
    function validateTaskForm(e) {
        const form = e.target;
        const titleInput = form.querySelector('input[name="title"]');
        
        if (!titleInput.value.trim()) {
            e.preventDefault();
            alert('Task title is required');
            titleInput.focus();
        }
    }
    
    /**
     * Validate goal form before submission
     * @param {Event} e - The event object
     */
    function validateGoalForm(e) {
        const form = e.target;
        const titleInput = form.querySelector('input[name="title"]');
        
        if (!titleInput.value.trim()) {
            e.preventDefault();
            alert('Goal title is required');
            titleInput.focus();
        }
    }
    
    /**
     * Initialize progress circles
     */
    function initProgressCircles() {
        if (!DOM.progressCircles.length) return;
        
        DOM.progressCircles.forEach(circle => {
            const progressCircle = circle.querySelector('.progress');
            const percentageText = circle.querySelector('.percentage').textContent;
            const percentage = parseInt(percentageText);
            
            // Calculate stroke-dashoffset
            const radius = parseInt(progressCircle.getAttribute('r'));
            const circumference = 2 * Math.PI * radius;
            const offset = circumference * (1 - (percentage / 100));
            
            progressCircle.style.strokeDasharray = circumference;
            progressCircle.style.strokeDashoffset = offset;
            
            // Set color based on progress
            if (percentage < 25) {
                progressCircle.style.stroke = '#EF4444'; // Red
            } else if (percentage < 50) {
                progressCircle.style.stroke = '#F97316'; // Orange
            } else if (percentage < 75) {
                progressCircle.style.stroke = '#3B82F6'; // Blue
            } else {
                progressCircle.style.stroke = '#10B981'; // Green
            }
        });
    }
    
    /**
     * Update goal progress UI
     * @param {number} progress - The new progress percentage
     */
    function updateGoalProgress(progress) {
        if (!DOM.progressCircles.length) return;
        
        const progressCircle = DOM.progressCircles[0];
        const progressElement = progressCircle.querySelector('.progress');
        const percentageElement = progressCircle.querySelector('.percentage');
        
        // Update percentage text
        percentageElement.textContent = `${Math.round(progress)}%`;
        
        // Update circle
        const radius = parseInt(progressElement.getAttribute('r'));
        const circumference = 2 * Math.PI * radius;
        const offset = circumference * (1 - (progress / 100));
        
        progressElement.style.strokeDashoffset = offset;
        
        // Update color based on progress
        if (progress < 25) {
            progressElement.style.stroke = '#EF4444'; // Red
        } else if (progress < 50) {
            progressElement.style.stroke = '#F97316'; // Orange
        } else if (progress < 75) {
            progressElement.style.stroke = '#3B82F6'; // Blue
        } else {
            progressElement.style.stroke = '#10B981'; // Green
        }
        
        // Add pulse animation to progress circle
        progressCircle.classList.add('progress-update');
        setTimeout(() => {
            progressCircle.classList.remove('progress-update');
        }, 1000);
    }
    
    /**
     * Initialize date pickers
     */
    function initDatePickers() {
        // This would integrate with a date picker library if used
        console.log('Date pickers initialized');
    }
    
    /**
     * Initialize tooltips
     */
    function initTooltips() {
        // This would integrate with a tooltip library if used
        console.log('Tooltips initialized');
    }
    
    /**
     * Handle filter button toggling
     * @param {Event} e - The event object
     */
    function handleFilterToggle(e) {
        e.preventDefault();
        
        // URL-based filtering is handled server-side in our implementation
        // This function is reserved for client-side filtering if needed later
        
        console.log('Filter toggled:', e.currentTarget.textContent.trim());
    }
    
    /**
     * Handle sorting of goals or tasks
     * @param {Event} e - The event object
     */
    function handleSort(e) {
        const sortValue = e.target.value;
        console.log('Sort changed to:', sortValue);
        
        // Specific sorting logic is implemented in individual views
        // This is just a placeholder for shared functionality
    }
    
    /**
     * Handle AI task generation
     * @param {Event} e - The event object
     */
    function handleAITaskGeneration(e) {
        console.log('AI Task generation triggered');
        // Specific AI generation logic is implemented in view_goal.html
    }
    
    // Return public methods and properties
    return {
        init: init
    };
    
})();

// Initialize on page load
document.addEventListener('DOMContentLoaded', TaskBud.init);