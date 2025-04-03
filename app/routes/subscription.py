from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.models import update_subscription
import stripe
from datetime import datetime, timedelta

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscription/plans')
@login_required
def plans():
    # Get subscription plans from app config
    plans = current_app.config.get('SUBSCRIPTION_PLANS')
    
    # Set Stripe publishable key for frontend
    stripe_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    
    return render_template(
        'subscription/plans.html',
        title='Subscription Plans',
        plans=plans,
        current_plan=current_user.subscription_tier,
        stripe_key=stripe_key
    )

@subscription_bp.route('/subscription/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    # Initialize Stripe with secret key
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    
    # Get plan details
    plans = current_app.config.get('SUBSCRIPTION_PLANS')
    plan = plans.get('premium')
    
    if not plan or not plan.get('stripe_price_id'):
        flash('Invalid subscription plan', 'danger')
        return redirect(url_for('subscription.plans'))
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': plan['stripe_price_id'],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('subscription.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('subscription.plans', _external=True),
            client_reference_id=current_user.id
        )
        
        return jsonify({'id': checkout_session.id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/subscription/success')
@login_required
def success():
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid checkout session', 'danger')
        return redirect(url_for('subscription.plans'))
    
    # For demo purposes, we'll just update the subscription
    # In a production app, you'd verify the checkout session with Stripe
    
    # Set subscription end date to 30 days from now
    end_date = datetime.now() + timedelta(days=30)
    
    if update_subscription(current_user.id, 'premium', end_date):
        flash('Subscription upgraded successfully!', 'success')
    else:
        flash('Failed to update subscription', 'danger')
    
    return redirect(url_for('dashboard.dashboard'))

@subscription_bp.route('/subscription/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_ENDPOINT_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle specific webhook events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    return jsonify({'status': 'success'})

def handle_checkout_session(session):
    # Get user ID from client_reference_id
    user_id = session.get('client_reference_id')
    
    if not user_id:
        return
    
    # Set subscription end date to 30 days from now
    end_date = datetime.now() + timedelta(days=30)
    update_subscription(user_id, 'premium', end_date)

def handle_subscription_deleted(subscription):
    # In a real app, you'd have a mapping between Stripe customer/subscription IDs and your users
    # For this demo, we don't have that, so this function is just a placeholder
    pass

@subscription_bp.route('/subscription/cancel', methods=['POST'])
@login_required
def cancel():
    # In a real app, you'd cancel the subscription in Stripe
    # For this demo, we'll just downgrade the user to free tier
    
    if update_subscription(current_user.id, 'free', None):
        flash('Subscription cancelled successfully', 'success')
    else:
        flash('Failed to cancel subscription', 'danger')
    
    return redirect(url_for('subscription.plans'))