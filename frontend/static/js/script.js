document.addEventListener('DOMContentLoaded', () => {
    // Navigation Item Click Handling
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active class from all nav items
            navItems.forEach(navItem => {
                navItem.classList.remove('active');
            });
            
            // Add active class to clicked item
            item.classList.add('active');
            
            // TODO: Implement view switching logic
            // For now, just log the selected view
            const viewLabel = item.querySelector('.nav-label').textContent;
            console.log(`Selected view: ${viewLabel}`);
        });
    });

    // Notification Button Click Handling
    const notificationBtn = document.querySelector('.notification-btn');
    notificationBtn.addEventListener('click', () => {
        // TODO: Implement notification view/dropdown
        console.log('Notifications clicked');
    });

    // Profile Button Click Handling
    const profileBtn = document.querySelector('.profile-btn');
    profileBtn.addEventListener('click', () => {
        // TODO: Implement profile view/dropdown
        console.log('Profile clicked');
    });
});



// Updated JavaScript to integrate with existing code
document.addEventListener('DOMContentLoaded', () => {
    // Navigation Item Click Handling
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        // Remove active class from all nav items
        navItems.forEach(navItem => navItem.classList.remove('active'));
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // View switching logic based on the data-view attribute
        const view = item.getAttribute('data-view');
        if (view) {
          switch (view) {
            case 'progress':
              loadProgressTrackerView();
              break;
            case 'home':
            default:
              loadHomeView();
              break;
          }
        } else {
          // Fallback: log the view label if data-view attribute is missing
          const viewLabelElement = item.querySelector('.nav-label');
          const viewLabel = viewLabelElement ? viewLabelElement.textContent : 'Unknown View';
          console.log(`Selected view: ${viewLabel}`);
        }
      });
    });
  
    // Notification Button Click Handling
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
      notificationBtn.addEventListener('click', () => {
        // TODO: Implement notification view/dropdown
        console.log('Notifications clicked');
      });
    }
  
    // Profile Button Click Handling
    const profileBtn = document.querySelector('.profile-btn');
    if (profileBtn) {
      profileBtn.addEventListener('click', () => {
        // TODO: Implement profile view/dropdown
        console.log('Profile clicked');
      });
    }
  
    // Function to load the Progress Tracker View
    function loadProgressTrackerView() {
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        mainContent.innerHTML = `
          <div class="min-h-screen bg-black text-white pl-64 p-8">
            <div class="container mx-auto">
              <h1 class="text-4xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">
                Progress Tracker
              </h1>
              <div class="dashboard-grid">
                <!-- Skill Development Card -->
                <div class="card skill-development">
                  <h3>Skill Development</h3>
                  <div class="skill-section">
                    <h4>Technical Skills</h4>
                    <ul>
                      <li>
                        <span>Python</span>
                        <small>Advanced (90%)</small>
                      </li>
                      <li>
                        <span>Machine Learning</span>
                        <small>Intermediate (75%)</small>
                      </li>
                      <li>
                        <span>React</span>
                        <small>Intermediate (80%)</small>
                      </li>
                    </ul>
                  </div>
                  <div class="skill-section">
                    <h4>Soft Skills</h4>
                    <ul>
                      <li>
                        <span>Communication</span>
                        <small>Advanced (85%)</small>
                      </li>
                      <li>
                        <span>Leadership</span>
                        <small>Intermediate (70%)</small>
                      </li>
                    </ul>
                  </div>
                  <div class="skill-section">
                    <h4>Certificates</h4>
                    <ul>
                      <li>
                        <span>AWS Certified Cloud Practitioner</span>
                        <small>Verified until 2026-01-15</small>
                      </li>
                    </ul>
                  </div>
                </div>
                
                <!-- Academic Progress Card -->
                <div class="card academic-progress">
                  <h3>Academic Progress</h3>
                  <ul>
                    <li>
                      <span>GPA</span>
                      <small>3.7 / 4.0</small>
                    </li>
                    <li>
                      <span>Credits</span>
                      <small>72 / 120</small>
                    </li>
                    <li>
                      <span>Current Semester</span>
                      <small>4</small>
                    </li>
                  </ul>
                </div>
                
                <!-- Professional Journey Card -->
                <div class="card professional-journey">
                  <h3>Professional Journey</h3>
                  <div class="skill-section">
                    <h4>Internships</h4>
                    <ul>
                      <li>
                        <span>Tech Innovations Inc.</span>
                        <small>Software Engineering Intern</small>
                      </li>
                    </ul>
                  </div>
                  <div class="skill-section">
                    <h4>Job Applications</h4>
                    <ul>
                      <li>
                        <span>Google</span>
                        <small>Software Engineer (Applied)</small>
                      </li>
                      <li>
                        <span>Microsoft</span>
                        <small>Data Science Intern (Interview Scheduled)</small>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
      }
    }
  
    // Function to load the Home View (placeholder - replace with your actual home content)
    function loadHomeView() {
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        mainContent.innerHTML = ''; // Replace with your home view content
      }
    }
  });
  

    // Notification Button Click Handling
    const notificationBtn = document.querySelector('.notification-btn');
    notificationBtn.addEventListener('click', () => {
        // TODO: Implement notification view/dropdown
        console.log('Notifications clicked');
    });

    // Profile Button Click Handling
    const profileBtn = document.querySelector('.profile-btn');
    profileBtn.addEventListener('click', () => {
        // TODO: Implement profile view/dropdown
        console.log('Profile clicked');
    });
});