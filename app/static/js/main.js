// StudentHub Main JavaScript

// Handle mobile sidebar toggle
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
                }
            })
            .catch(error => {
                console.error('Error:', error);
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
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
    
    // Job application form status field
    const statusField = document.getElementById('status');
    const interviewDateField = document.querySelector('.interview-date-field');
    
    if (statusField && interviewDateField) {
        statusField.addEventListener('change', function() {
            if (this.value === 'Interview') {
                interviewDateField.style.display = 'block';
            } else {
                interviewDateField.style.display = 'none';
            }
        });
        
        // Initialize on page load
        if (statusField.value === 'Interview') {
            interviewDateField.style.display = 'block';
        }
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
                });
            }
        });
    }
});