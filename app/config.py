import os
from dotenv import load_dotenv

load_dotenv()

# Application Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/studenthub')

# Stripe Configuration (for subscription)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_ENDPOINT_SECRET = os.getenv('STRIPE_ENDPOINT_SECRET', '')

# Subscription Plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free Tier',
        'price': 0,
        'features': [
            'Basic Dashboard',
            'Limited Job Listings',
            'Progress Tracking',
            'Basic Course Access'
        ]
    },
    'premium': {
        'name': 'Premium Plan',
        'price': 9.99,
        'stripe_price_id': os.getenv('STRIPE_PREMIUM_PRICE_ID', ''),
        'features': [
            'Advanced Dashboard',
            'Full Job Listings',
            'Detailed Progress Analytics',
            'All Courses Access',
            'Todo List Manager',
            'Passive Income Tools'
        ]
    }
}