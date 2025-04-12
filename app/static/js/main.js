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


// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use default (dark)
    const currentTheme = localStorage.getItem('theme') || 'dark';
    
    // Apply the saved theme or default with anti-flicker
    document.documentElement.classList.add('theme-transition');
    document.body.setAttribute('data-theme', currentTheme);
    setTimeout(function() {
        document.documentElement.classList.remove('theme-transition');
    }, 100);
    
    // Update toggle switch state to match current theme
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.checked = currentTheme === 'light';
    }
    
    // Theme switch event listener
    document.querySelector('.theme-switch')?.addEventListener('change', function(e) {
        // Add class to prevent transition flicker
        document.documentElement.classList.add('theme-transition');
        
        if (e.target.checked) {
            document.body.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        } else {
            document.body.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        }
        
        // Add fade effect when changing themes - keeping your original functionality
        document.body.style.opacity = '0.9';
        setTimeout(() => {
            document.body.style.opacity = '1';
            // Remove transition prevention class after fade completes
            document.documentElement.classList.remove('theme-transition');
        }, 300);
    });
    
    // Sidebar toggle functionality for mobile
    const sidebarToggle = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
    
    // Add subtle animation when cards enter viewport
    const cards = document.querySelectorAll('.card');
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                cardObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        cardObserver.observe(card);
    });
    
    // Add gradient hover effect to buttons
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.style.backgroundPosition = 'right center';
        });
        
        button.addEventListener('mouseout', function() {
            this.style.backgroundPosition = 'left center';
        });
        
        // Set initial background position
        button.style.backgroundSize = '200% auto';
        button.style.backgroundPosition = 'left center';
    });
});