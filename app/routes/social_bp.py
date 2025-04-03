# Create a new blueprint: social_bp.py

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from bson import ObjectId
from app import db
from app.models import (
    search_users, User, add_connection, accept_connection, get_connections,
    get_conversations, get_messages, create_conversation,  # already imported
    get_feed, create_post, add_comment, like_post, unlike_post,   # new functions
    create_group, get_user_groups, get_group_messages                # new functions
)
from app.forms import PostForm, GroupForm  # assuming you have these defined in app/forms.py


social_bp = Blueprint('social', __name__, url_prefix='/social')


@social_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if len(query) < 3:
        return render_template('social/search.html', results=[], query='')
    
    results = search_users(query)
    
    # Don't include current user in results
    results = [user for user in results if str(user['_id']) != current_user.id]
    
    return render_template('social/search.html', results=results, query=query)

@social_bp.route('/profile/<user_id>')
@login_required
def view_profile(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if not user_data:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    # Check if there's a connection
    connection = db.connections.find_one({
        '$or': [
            {'user_id': ObjectId(current_user.id), 'friend_id': ObjectId(user_id)},
            {'user_id': ObjectId(user_id), 'friend_id': ObjectId(current_user.id)}
        ]
    })
    
    connection_status = None
    if connection:
        if connection['status'] == 'accepted':
            connection_status = 'connected'
        elif connection['status'] == 'pending':
            if connection['user_id'] == ObjectId(current_user.id):
                connection_status = 'pending_sent'
            else:
                connection_status = 'pending_received'
    
    user = User(user_data)
    return render_template('social/view_profile.html', user=user, connection_status=connection_status)

@social_bp.route('/connections')
@login_required
def connections():
    # Get accepted connections
    connections = get_connections(current_user.id, 'accepted')
    
    # Get pending connection requests (sent to current user)
    pending_requests = list(db.connections.find({
        'friend_id': ObjectId(current_user.id),
        'status': 'pending'
    }))
    
    # Get user details for pending requests
    pending_users = []
    for req in pending_requests:
        user_data = db.users.find_one({'_id': req['user_id']})
        if user_data:
            pending_users.append(User(user_data))
    
    return render_template('social/connections.html', 
                          connections=connections, 
                          pending_requests=pending_users)

@social_bp.route('/connect/<user_id>', methods=['POST'])
@login_required
def connect(user_id):
    add_connection(current_user.id, user_id)
    flash('Connection request sent!', 'success')
    return redirect(url_for('social.view_profile', user_id=user_id))

@social_bp.route('/accept/<user_id>', methods=['POST'])
@login_required
def accept(user_id):
    if accept_connection(current_user.id, user_id):
        flash('Connection accepted!', 'success')
    else:
        flash('Connection request not found', 'danger')
    return redirect(url_for('social.connections'))

@social_bp.route('/messages')
@login_required
def messages():
    conversations = get_conversations(current_user.id)
    return render_template('social/messages.html', conversations=conversations)

@social_bp.route('/messages/<conversation_id>')
@login_required
def view_conversation(conversation_id):
    # Verify user is part of this conversation
    conv = db.conversations.find_one({
        '_id': ObjectId(conversation_id),
        'participants': ObjectId(current_user.id)
    })
    
    if not conv:
        flash('Conversation not found', 'danger')
        return redirect(url_for('social.messages'))
    
    # Get other participant
    other_id = next(p for p in conv['participants'] if p != ObjectId(current_user.id))
    other_user = db.users.find_one({'_id': other_id})
    other_user = User(other_user)
    
    # Get messages
    messages = get_messages(conversation_id, current_user.id)
    
    return render_template('social/conversation.html', 
                          conversation_id=conversation_id,
                          messages=messages,
                          other_user=other_user)

@social_bp.route('/messages/new/<user_id>')
@login_required
def new_conversation(user_id):
    # Create or get existing conversation
    conversation_id = create_conversation(current_user.id, user_id)
    return redirect(url_for('social.view_conversation', conversation_id=conversation_id))

@social_bp.route('/feed')
@login_required
def feed():
    posts = get_feed(current_user.id)
    return render_template('social/feed.html', posts=posts)

@social_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    
    if form.validate_on_submit():
        content = form.content.data
        visibility = form.visibility.data
        
        create_post(current_user.id, content, visibility)
        flash('Post created successfully!', 'success')
        return redirect(url_for('social.feed'))
    
    return render_template('social/new_post.html', form=form)

@social_bp.route('/post/<post_id>')
@login_required
def view_post(post_id):
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('social.feed'))
    
    # Attach user info
    user_data = db.users.find_one({'_id': post['user_id']})
    post['user'] = User(user_data)
    
    # Attach comment user info
    for comment in post.get('comments', []):
        commenter = db.users.find_one({'_id': comment['user_id']})
        comment['user'] = User(commenter)
    
    return render_template('social/view_post.html', post=post)

@social_bp.route('/post/<post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form.get('content')
    
    if content:
        add_comment(post_id, current_user.id, content)
        flash('Comment added', 'success')
    
    return redirect(url_for('social.view_post', post_id=post_id))

@social_bp.route('/post/<post_id>/like', methods=['POST'])
@login_required
def like_post_route(post_id):
    like_post(post_id, current_user.id)
    return redirect(url_for('social.view_post', post_id=post_id))

@social_bp.route('/post/<post_id>/unlike', methods=['POST'])
@login_required
def unlike_post_route(post_id):
    unlike_post(post_id, current_user.id)
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/groups')
@login_required
def groups():
    user_groups = get_user_groups(current_user.id)
    return render_template('social/groups.html', groups=user_groups)

@social_bp.route('/groups/new', methods=['GET', 'POST'])
@login_required
def new_group():
    form = GroupForm()
    
    # Populate connection choices
    connections = get_connections(current_user.id)
    form.members.choices = [(str(c['_id']), f"{c['first_name']} {c['last_name']}") for c in connections]
    
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        members = form.members.data
        
        group_id = create_group(current_user.id, name, description, members)
        flash('Group created successfully!', 'success')
        return redirect(url_for('social.view_group', group_id=group_id))
    
    return render_template('social/new_group.html', form=form)

@social_bp.route('/groups/<group_id>')
@login_required
def view_group(group_id):
    # Verify user is member of this group
    group = db.groups.find_one({
        '_id': ObjectId(group_id),
        'members': ObjectId(current_user.id)
    })
    
    if not group:
        flash('Group not found or you are not a member', 'danger')
        return redirect(url_for('social.groups'))
    
    # Get messages
    messages = get_group_messages(group_id, current_user.id)
    
    # Get member info
    members = []
    for member_id in group['members']:
        user_data = db.users.find_one({'_id': member_id})
        if user_data:
            members.append(User(user_data))
    
    return render_template('social/group_chat.html',
                          group=group,
                          group_id=group_id,
                          messages=messages,
                          members=members,
                          is_creator=(group['creator_id'] == ObjectId(current_user.id)))