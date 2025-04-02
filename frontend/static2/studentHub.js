import React, { useState, useEffect, useRef } from 'react';

const StudentHub = () => {
  // State Management
  const [activeView, setActiveView] = useState('home');
  const [userProfile, setUserProfile] = useState({
    name: 'Alex Rodriguez',
    major: 'Computer Science',
    university: 'Global Tech University',
    achievements: [
      { title: 'Hackathon Winner', date: '2024-03-15' },
      { title: 'Machine Learning Certification', date: '2024-01-22' }
    ]
  });

  const [notifications, setNotifications] = useState([
    { 
      id: 1, 
      type: 'job', 
      title: 'New Internship Opportunity', 
      company: 'Tech Innovations Inc.', 
      timestamp: '2024-04-02T10:30:00Z' 
    },
    { 
      id: 2, 
      type: 'course', 
      title: 'Advanced AI Course Available', 
      platform: 'Coursera', 
      timestamp: '2024-04-01T15:45:00Z' 
    }
  ]);

  // Holographic Card Component (Reusable)
  const HolographicCard = ({ children, className = '', onClick }) => {
    const cardRef = useRef(null);

    useEffect(() => {
      const card = cardRef.current;
      const handleMouseMove = (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
      };

      card.addEventListener('mousemove', handleMouseMove);
      return () => card.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
      <div 
        ref={cardRef}
        onClick={onClick}
        className={`holographic-card relative overflow-hidden rounded-xl p-6 
          bg-gray-900 border border-gray-700 cursor-pointer
          before:absolute before:top-0 before:left-0 before:w-full before:h-full 
          before:opacity-0 hover:before:opacity-30 
          before:bg-gradient-to-br before:from-white/10 before:to-transparent 
          before:transition-opacity before:duration-300 
          after:absolute after:top-0 after:left-0 after:w-full after:h-full 
          after:bg-radial-gradient after:opacity-0 hover:after:opacity-20 
          transition transform hover:scale-105 
          ${className}`}
        style={{
          '--mouse-x': '0px',
          '--mouse-y': '0px',
          background: 'radial-gradient(800px circle at var(--mouse-x) var(--mouse-y), rgba(255,255,255,0.1), transparent 40%)'
        }}
      >
        {children}
      </div>
    );
  };

  // Placeholder Progress Tracker Component
  const ProgressTracker = () => (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">
          Progress Tracker
        </h1>
        {/* Add more progress tracking content here */}
      </div>
    </div>
  );

  // Main Navigation Bar
  const NavigationBar = () => (
    <nav className="w-64 bg-gray-900 bg-opacity-50 backdrop-blur-lg p-6 fixed left-0 top-0 h-full">
      <h1 className="text-3xl font-bold mb-10 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">
        StudentHub
      </h1>
      <div className="space-y-4">
        {[
          { 
            icon: '🏠', 
            label: 'Dashboard', 
            action: () => setActiveView('home') 
          },
          { 
            icon: '📊', 
            label: 'Progress Tracker', 
            action: () => setActiveView('progress') 
          },
          { 
            icon: '💼', 
            label: 'Jobs', 
            action: () => setActiveView('jobs') 
          },
          { 
            icon: '📚', 
            label: 'Courses', 
            action: () => setActiveView('courses') 
          },
          { 
            icon: '✅', 
            label: 'Todo', 
            action: () => setActiveView('todo') 
          },
          { 
            icon: '💰', 
            label: 'Passive Income', 
            action: () => setActiveView('passive-income') 
          }
        ].map(item => (
          <button 
            key={item.label}
            onClick={item.action}
            className="w-full text-left p-3 rounded-lg hover:bg-gray-800 transition flex items-center space-x-3"
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );

  // Render Home Page
  const renderHomePage = () => (
    <div className="min-h-screen bg-black text-white pl-64 p-8">
      <NavigationBar />
      <div className="container mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-2xl font-semibold">Welcome, {userProfile.name}</h2>
            <p className="text-gray-400">{userProfile.major} | {userProfile.university}</p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="relative">
              <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">
                {notifications.length}
              </span>
              🔔
            </button>
            <button className="bg-gray-800 p-2 rounded-full">👤</button>
          </div>
        </header>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Job Opportunities */}
          <HolographicCard>
            <h3 className="text-2xl font-semibold mb-4 text-green-400">Job Opportunities</h3>
            <div className="space-y-4">
              {['Software Intern', 'Data Analyst', 'ML Research Assistant'].map(job => (
                <div 
                  key={job} 
                  className="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition"
                >
                  <p className="font-medium">{job}</p>
                </div>
              ))}
            </div>
          </HolographicCard>

          {/* Achievements */}
          <HolographicCard>
            <h3 className="text-2xl font-semibold mb-4 text-blue-400">Achievements</h3>
            {userProfile.achievements.map(achievement => (
              <div 
                key={achievement.title} 
                className="bg-gray-800 rounded-lg p-4 mb-3 last:mb-0 hover:bg-gray-700 transition"
              >
                <p className="font-medium">{achievement.title}</p>
                <p className="text-sm text-gray-400">{achievement.date}</p>
              </div>
            ))}
          </HolographicCard>

          {/* Notifications */}
          <HolographicCard>
            <h3 className="text-2xl font-semibold mb-4 text-purple-400">Notifications</h3>
            {notifications.map(notification => (
              <div 
                key={notification.id} 
                className="bg-gray-800 rounded-lg p-4 mb-3 last:mb-0 hover:bg-gray-700 transition"
              >
                <p className="font-medium">{notification.title}</p>
                <p className="text-sm text-gray-400">{notification.company || notification.platform}</p>
              </div>
            ))}
          </HolographicCard>
        </div>
      </div>
    </div>
  );

  // Render View
  const renderView = () => {
    switch(activeView) {
      case 'progress':
        return (
          <div className="min-h-screen bg-black text-white pl-64">
            <NavigationBar />
            <ProgressTracker />
          </div>
        );
      default:
        return renderHomePage();
    }
  };

  // Global Styles
  useEffect(() => {
    const styleSheet = document.createElement("style");
    styleSheet.type = "text/css";
    styleSheet.innerText = `
      body { 
        margin: 0; 
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        background: #000;
        color: #fff;
      }
    `;
    document.head.appendChild(styleSheet);
    return () => document.head.removeChild(styleSheet);
  }, []);

  return renderView();
};

export default StudentHub;