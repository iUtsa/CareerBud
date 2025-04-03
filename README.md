# StudentHub

A modern web application for students to track academic progress, find job opportunities, manage tasks, and develop skills - all in one place. Built with Flask, MongoDB, Bootstrap, and modern frontend technologies.

## Features

- **User Authentication**: Secure signup, login, and profile management
- **Dashboard**: Overview of academic progress, job opportunities, and upcoming tasks
- **Progress Tracker**: Monitor GPA, credits, courses, and skill development
- **Job Opportunities**: Browse and apply for relevant jobs and internships
- **Course Management**: Enroll in courses and track your progress
- **Todo List**: Organize your tasks with due dates and priorities
- **Passive Income Tools**: Resources for developing income streams (Premium feature)
- **Subscription Model**: Free and Premium tiers with different feature sets

## Tech Stack

- **Backend**: Python/Flask
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login, Bcrypt
- **Payment Processing**: Stripe

## Project Structure

The application follows a modular structure with blueprints for different features:

- **Authentication**: User registration, login, and profile management
- **Dashboard**: Main user interface showing key information
- **Progress**: Academic progress tracking and skill development
- **Jobs**: Job listings and application management
- **Courses**: Course browsing and enrollment
- **Subscription**: Plan management and payment processing

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/studenthub.git
   cd studenthub
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up MongoDB:
   - Install MongoDB or use MongoDB Atlas cloud service
   - Update the MONGO_URI in .env file

5. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your MongoDB connection string
   - Add Stripe API keys (optional, for subscription features)

6. Run the application:
   ```
   python run.py
   ```

7. Access the application at `http://localhost:5000`

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Application Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/studenthub
# or for MongoDB Atlas
# MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/studenthub?retryWrites=true&w=majority

# Stripe Configuration (for subscription)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_ENDPOINT_SECRET=whsec_your_stripe_endpoint_secret
STRIPE_PREMIUM_PRICE_ID=price_your_stripe_price_id
```

## Deployment

This application can be deployed to any platform that supports Python/Flask applications:

1. Set `FLASK_ENV=production` in your environment variables
2. Use a production WSGI server like Gunicorn:
   ```
   pip install gunicorn
   gunicorn "app:create_app()"
   ```

3. For MongoDB, it's recommended to use MongoDB Atlas for production

## Subscription Plans

The application offers two subscription tiers:

**Free Tier**:
- Basic Dashboard
- Limited Job Listings
- Progress Tracking
- Basic Course Access

**Premium Plan** ($9.99/month):
- Advanced Dashboard
- Full Job Listings
- Detailed Progress Analytics
- All Courses Access
- Todo List Manager
- Passive Income Tools

## License

This project is licensed under the MIT License - see the LICENSE file for details.