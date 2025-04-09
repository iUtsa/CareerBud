from app import create_app
from app.extensions import socketio, db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create the Flask application
app = create_app()

# Initialize database with sample data in development mode
def create_sample_data():
    with app.app_context():
        from app.models import Course, Job
        
        if os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't'):
            # Sample courses
            if Course.query.count() == 0:
                courses = [
                    Course(
                        id=1,
                        name='Advanced Machine Learning',
                        description='Deep dive into advanced ML algorithms and techniques including deep learning, reinforcement learning, and more.',
                        category='Data Science',
                        level='Advanced',
                        duration='12 weeks',
                        premium_only=False
                    ),
                    Course(
                        id=2,
                        name='Cloud Computing',
                        description='Learn about cloud architectures, services, deployment models, and best practices.',
                        category='Infrastructure',
                        level='Intermediate',
                        duration='8 weeks',
                        premium_only=False
                    ),
                    Course(
                        id=3,
                        name='Full Stack Web Development',
                        description='Build modern web applications using popular frameworks and tools for both frontend and backend.',
                        category='Web Development',
                        level='Intermediate',
                        duration='16 weeks',
                        premium_only=False
                    ),
                    Course(
                        id=4,
                        name='Blockchain Development',
                        description='Learn to develop applications on blockchain platforms with smart contracts.',
                        category='Blockchain',
                        level='Advanced',
                        duration='10 weeks',
                        premium_only=True
                    ),
                    Course(
                        id=5,
                        name='Advanced AI Applications',
                        description='Build cutting-edge AI applications with practical industry applications.',
                        category='Artificial Intelligence',
                        level='Advanced',
                        duration='14 weeks',
                        premium_only=True
                    )
                ]
                db.session.bulk_save_objects(courses)
                db.session.commit()

            # Sample jobs
            if Job.query.count() == 0:
                jobs = [
                    Job(
                        id=1,
                        title='Software Intern',
                        company='Tech Innovations Inc.',
                        description='Join our team to develop cutting-edge software solutions. You will work on real projects with experienced developers.',
                        requirements='Knowledge of Python, Basic understanding of algorithms, Good problem-solving skills',
                        location='San Francisco, CA',
                        salary='$25-30/hr',
                        job_type='Internship'
                    ),
                    Job(
                        id=2,
                        title='Data Analyst',
                        company='DataCorp',
                        description='Help analyze large datasets and extract meaningful insights for our clients across various industries.',
                        requirements='SQL proficiency, Experience with data visualization tools, Statistical analysis',
                        location='Remote',
                        salary='$70-85K/year',
                        job_type='Full-time'
                    ),
                    Job(
                        id=3,
                        title='ML Research Assistant',
                        company='AI Research Labs',
                        description='Assist senior researchers in developing and testing machine learning models for advanced applications.',
                        requirements='Machine learning fundamentals, Python, TensorFlow or PyTorch experience',
                        location='Boston, MA',
                        salary='$30-35/hr',
                        job_type='Part-time'
                    ),
                    Job(
                        id=4,
                        title='DevOps Engineer',
                        company='CloudTech Systems',
                        description='Develop and maintain our cloud infrastructure, CI/CD pipelines, and automation systems.',
                        requirements='Cloud platform experience, Containerization knowledge, Scripting abilities',
                        location='Seattle, WA',
                        salary='$90-120K/year',
                        job_type='Full-time'
                    ),
                    Job(
                        id=5,
                        title='Frontend Developer',
                        company='WebVision',
                        description='Create responsive and intuitive user interfaces for our web applications using modern frameworks.',
                        requirements='HTML/CSS/JavaScript proficiency, Experience with React or Vue, UI/UX sensibility',
                        location='Austin, TX',
                        salary='$80-95K/year',
                        job_type='Full-time'
                    ),
                    Job(
                        id=6,
                        title='Cybersecurity Analyst',
                        company='SecureNet',
                        description='Help protect our systems and data by identifying vulnerabilities and implementing security measures.',
                        requirements='Network security knowledge, Familiarity with security tools, Analytical mindset',
                        location='Washington, DC',
                        salary='$85-110K/year',
                        job_type='Full-time'
                    )
                ]
                db.session.bulk_save_objects(jobs)
                db.session.commit()

# Register sample data creation within app context
with app.app_context():
    db.create_all()  # ✅ Now it knows the app
    create_sample_data()

# Run the Flask application with SocketIO
if __name__ == '__main__':
    socketio.run(app, debug=True)