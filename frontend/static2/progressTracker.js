import React, { useState, useEffect, useRef } from 'react';

const ProgressTracker = () => {
  // Comprehensive Progress State
  const [progressData, setProgressData] = useState({
    academic: {
      gpa: 3.7,
      completedCredits: 72,
      totalCredits: 120,
      currentSemester: 4,
      courses: [
        { 
          name: 'Advanced Machine Learning', 
          progress: 85,
          grade: 'A',
          skills: ['Python', 'Data Analysis', 'Neural Networks']
        },
        { 
          name: 'Cloud Computing', 
          progress: 65,
          grade: 'B+',
          skills: ['AWS', 'Docker', 'Kubernetes']
        }
      ]
    },
    professional: {
      internships: [
        {
          company: 'Tech Innovations Inc.',
          role: 'Software Engineering Intern',
          duration: '3 months',
          status: 'Completed',
          skills: ['React', 'Node.js', 'Agile Methodology']
        }
      ],
      jobApplications: [
        { 
          company: 'Google', 
          position: 'Software Engineer', 
          status: 'Applied',
          applicationDate: '2024-03-15'
        },
        { 
          company: 'Microsoft', 
          position: 'Data Science Intern', 
          status: 'Interview Scheduled',
          interviewDate: '2024-04-10'
        }
      ]
    },
    skillDevelopment: {
      technicalSkills: [
        { name: 'Python', level: 'Advanced', progress: 90 },
        { name: 'Machine Learning', level: 'Intermediate', progress: 75 },
        { name: 'React', level: 'Intermediate', progress: 80 }
      ],
      softSkills: [
        { name: 'Communication', level: 'Advanced', progress: 85 },
        { name: 'Leadership', level: 'Intermediate', progress: 70 }
      ],
      certificates: [
        {
          name: 'AWS Certified Cloud Practitioner',
          issuer: 'Amazon Web Services',
          dateEarned: '2024-01-15',
          validUntil: '2026-01-15'
        }
      ]
    }
  });

  // Skill Progression Visualization
  const SkillProgressBar = ({ skill }) => {
    return (
      <div className="mb-2 bg-gray-800 rounded-full overflow-hidden">
        <div 
          className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full"
          style={{ width: `${skill.progress}%` }}
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>{skill.name}</span>
          <span>{skill.level} ({skill.progress}%)</span>
        </div>
      </div>
    );
  };

  // Futuristic Holographic Effect Component
  const HolographicCard = ({ children, className = '' }) => {
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
        className={`holographic-card relative overflow-hidden rounded-xl p-6 
          bg-gray-900 border border-gray-700 
          before:absolute before:top-0 before:left-0 before:w-full before:h-full 
          before:opacity-0 hover:before:opacity-30 
          before:bg-gradient-to-br before:from-white/10 before:to-transparent 
          before:transition-opacity before:duration-300 
          after:absolute after:top-0 after:left-0 after:w-full after:h-full 
          after:bg-radial-gradient after:opacity-0 hover:after:opacity-20 
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

  // Main Render
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">
          Progress Tracker
        </h1>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Academic Progress */}
          <HolographicCard>
            <h2 className="text-2xl font-semibold mb-4 text-green-400">Academic Progress</h2>
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex justify-between mb-2">
                  <span>GPA</span>
                  <span className="font-bold">{progressData.academic.gpa} / 4.0</span>
                </div>
                <div className="bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${(progressData.academic.gpa / 4.0) * 100}%` }}
                  />
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex justify-between mb-2">
                  <span>Credits</span>
                  <span className="font-bold">
                    {progressData.academic.completedCredits} / {progressData.academic.totalCredits}
                  </span>
                </div>
                <div className="bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ 
                      width: `${(progressData.academic.completedCredits / progressData.academic.totalCredits) * 100}%` 
                    }}
                  />
                </div>
              </div>

              <div>
                <h3 className="text-xl mb-2">Current Courses</h3>
                {progressData.academic.courses.map((course, index) => (
                  <div key={index} className="mb-2 bg-gray-800 rounded-lg p-3">
                    <div className="flex justify-between mb-1">
                      <span className="font-medium">{course.name}</span>
                      <span className="text-green-400">{course.grade}</span>
                    </div>
                    <div className="bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-purple-500 h-2 rounded-full"
                        style={{ width: `${course.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </HolographicCard>

          {/* Professional Progress */}
          <HolographicCard>
            <h2 className="text-2xl font-semibold mb-4 text-blue-400">Professional Journey</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-xl mb-2">Internships</h3>
                {progressData.professional.internships.map((internship, index) => (
                  <div key={index} className="bg-gray-800 rounded-lg p-4 mb-2">
                    <div className="flex justify-between mb-2">
                      <span className="font-medium">{internship.company}</span>
                      <span className="text-green-400">{internship.status}</span>
                    </div>
                    <p className="text-gray-400 mb-2">{internship.role}</p>
                    <div className="text-sm text-gray-500">
                      Skills: {internship.skills.join(', ')}
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <h3 className="text-xl mb-2">Job Applications</h3>
                {progressData.professional.jobApplications.map((application, index) => (
                  <div key={index} className="bg-gray-800 rounded-lg p-4 mb-2">
                    <div className="flex justify-between mb-2">
                      <span className="font-medium">{application.company}</span>
                      <span className={`
                        ${application.status === 'Applied' ? 'text-yellow-400' : 'text-green-400'}
                      `}>
                        {application.status}
                      </span>
                    </div>
                    <p className="text-gray-400">{application.position}</p>
                    {application.interviewDate && (
                      <div className="text-sm text-gray-500 mt-1">
                        Interview: {application.interviewDate}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </HolographicCard>

          {/* Skill Development */}
          <HolographicCard>
            <h2 className="text-2xl font-semibold mb-4 text-purple-400">Skill Development</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-xl mb-2">Technical Skills</h3>
                {progressData.skillDevelopment.technicalSkills.map((skill, index) => (
                  <SkillProgressBar key={index} skill={skill} />
                ))}
              </div>

              <div>
                <h3 className="text-xl mb-2">Soft Skills</h3>
                {progressData.skillDevelopment.softSkills.map((skill, index) => (
                  <SkillProgressBar key={index} skill={skill} />
                ))}
              </div>

              <div>
                <h3 className="text-xl mb-2">Certificates</h3>
                {progressData.skillDevelopment.certificates.map((cert, index) => (
                  <div key={index} className="bg-gray-800 rounded-lg p-4 mb-2">
                    <div className="flex justify-between mb-1">
                      <span className="font-medium">{cert.name}</span>
                      <span className="text-green-400">Verified</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Issued by: {cert.issuer}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      Valid until: {cert.validUntil}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </HolographicCard>
        </div>
      </div>

      {/* Global Styles */}
      <style jsx global>{`
        body {
          background-color: black;
          color: white;
          font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
      `}</style>
    </div>
  );
};

export default ProgressTracker;