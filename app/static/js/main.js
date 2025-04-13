// StudentHub Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle (if we add a toggle button later)
    const toggleSidebarBtn = document.querySelector('.toggle-sidebar');
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }
    
    // Todo item checkbox toggling
    const todoCheckboxes = document.querySelectorAll('.todo-checkbox');
    todoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const todoId = this.dataset.id;
            const completed = this.checked;
            
            fetch('/todos/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `todo_id=${todoId}&completed=${completed}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const todoText = document.querySelector(`label[for="todo-${todoId}"]`);
                    if (completed) {
                        todoText.classList.add('todo-completed');
                    } else {
                        todoText.classList.remove('todo-completed');
                    }
                } else {
                    alert('Failed to update task, please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred, please try again later.');
            });
        });
    });
    
    // Delete todo item
    const deleteTodoBtns = document.querySelectorAll('.delete-todo');
    deleteTodoBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const todoId = this.dataset.id;
            
            fetch('/todos/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `todo_id=${todoId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const todoItem = document.querySelector(`#todo-item-${todoId}`);
                    if (todoItem) {
                        todoItem.style.opacity = '0';
                        setTimeout(() => {
                            todoItem.remove();
                        }, 300);
                    }
                } else {
                    alert('Failed to delete task, please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred, please try again later.');
            });
        });
    });
    
    // Job application form status field
    const statusField = document.getElementById('status');
    const interviewDateField = document.querySelector('.interview-date-field');
    
    if (statusField && interviewDateField) {
        const toggleInterviewDateField = function() {
            if (statusField.value === 'Interview') {
                interviewDateField.style.display = 'block';
            } else {
                interviewDateField.style.display = 'none';
            }
        };
        
        statusField.addEventListener('change', toggleInterviewDateField);
        toggleInterviewDateField();  // Initialize on page load
    }
    
    // Apply Job Modal - Pre-fill company and position when button is clicked
    const applyJobModal = document.getElementById('applyJobModal');
    if (applyJobModal) {
        applyJobModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const company = button.getAttribute('data-job-company');
            const position = button.getAttribute('data-job-position');
            
            const companyField = this.querySelector('#company');
            const positionField = this.querySelector('#position');
            
            if (company && companyField) {
                companyField.value = company;
            }
            
            if (position && positionField) {
                positionField.value = position;
            }
        });
    }
    
    // Clear completed tasks button
    const clearCompletedBtn = document.getElementById('clearCompletedBtn');
    if (clearCompletedBtn) {
        clearCompletedBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear all completed tasks?')) {
                const completedCheckboxes = document.querySelectorAll('.todo-checkbox:checked');
                const deletePromises = [];
                
                completedCheckboxes.forEach(checkbox => {
                    const todoId = checkbox.dataset.id;
                    
                    const deletePromise = fetch('/todos/delete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `todo_id=${todoId}`
                    });
                    
                    deletePromises.push(deletePromise);
                });
                
                Promise.all(deletePromises)
                .then(() => {
                    // Refresh the page to update statistics
                    window.location.reload();
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while deleting tasks, please try again.');
                });
            }
        });
    }

    // Disable "Clear Completed" button if there are no completed tasks
    const completedCheckboxes = document.querySelectorAll('.todo-checkbox:checked');
    if (clearCompletedBtn) {
        clearCompletedBtn.disabled = completedCheckboxes.length === 0;
    }
});


// Theme Toggle Functionality - Improved
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    
    // Initialize the toggle to match current theme
    if (themeToggle) {
        const currentTheme = localStorage.getItem('theme') || 'dark';
        themeToggle.checked = currentTheme === 'light';
        
        // Set theme on both document element and body for consistency
        document.documentElement.setAttribute('data-theme', currentTheme);
        document.body.setAttribute('data-theme', currentTheme);
        
        // Handle toggle change
        themeToggle.addEventListener('change', function() {
            // Prevent transition flicker
            document.documentElement.classList.add('theme-transition');
            
            const newTheme = this.checked ? 'light' : 'dark';
            
            // Apply theme to both document element and body
            document.documentElement.setAttribute('data-theme', newTheme);
            document.body.setAttribute('data-theme', newTheme);
            
            // Store preference
            localStorage.setItem('theme', newTheme);
            
            // Remove transition prevention class after transition completes
            setTimeout(function() {
                document.documentElement.classList.remove('theme-transition');
            }, 300);
        });
    }
});