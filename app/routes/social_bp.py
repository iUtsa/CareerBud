from flask import Blueprint, request, render_template, flash, redirect, url_for,current_app
from flask_login import login_required, current_user
from app.models import (
    search_users, User, add_connection, accept_connection, get_connection,
    get_conversations, get_messages, create_conversation,
    get_feed, create_post, add_comment, like_post, unlike_post,
    create_group, get_user_groups, get_group_messages
)
from app.forms import PostForm, GroupForm
from app import db
from app.models import Connection  # Adjust the import path as needed
from app.models import Notification
from app.models import get_connections
from app.models import get_connection_status
from app.forms import ProfileForm 
from flask_wtf import FlaskForm
from app.models import Conversation
from app.forms import MessageForm
from app.models import Message
from app.models import get_post






social_bp = Blueprint('social', __name__, url_prefix='/social')

@social_bp.route('/social/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    try:
        # Retrieve user data
        user_data = User.query.get_or_404(user_id)

        # Determine the connection status
        connection_status = get_connection_status(current_user.id, user_id)

        # Get the connection object if it exists
        connection = get_connection(current_user.id, user_id)

        # Create an instance of DummyForm for CSRF token
        form = DummyForm()

        return render_template(
            'social/view_profile.html',
            user=user_data,
            connection_status=connection_status,
            connection=connection,
            form=form  # Pass this form to the template
        )
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error in view_profile: {e}")
        # Roll back any pending transactions
        db.session.rollback()
        flash("An error occurred while loading the profile.", "danger")
        return redirect(url_for('dashboard.index'))



@social_bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    if len(query) < 3:
        return render_template('social/search.html', results=[], query='')

    results = search_users(query)
    results = [user for user in results if user.id != current_user.id]

    return render_template('social/search.html', results=results, query=query)



@social_bp.route('/connect/<int:user_id>', methods=['POST'])
@login_required
def connect(user_id):
    add_connection(current_user.id, user_id)
    flash('Connection request sent!', 'success')
    return redirect(url_for('social.view_profile', user_id=user_id))


@social_bp.route('/accept/<int:user_id>', methods=['POST'])
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

    convo_list = []
    for convo in conversations:
        other_id = convo.user2_id if convo.user1_id == current_user.id else convo.user1_id
        other_user = User.query.get(other_id)

        latest_message = Message.query.filter_by(conversation_id=convo.id).order_by(Message.created_at.desc()).first()
        unread_count = Message.query.filter_by(conversation_id=convo.id, recipient_id=current_user.id, read=False).count()

        convo_list.append({
            'conversation': convo,
            'other_user': other_user,
            'latest_message': latest_message,
            'unread_count': unread_count
        })

    return render_template('social/messages.html', conversations=convo_list)



@social_bp.route('/messages/<int:conversation_id>', methods=['GET', 'POST'])
@login_required
def view_conversation(conversation_id):
    from app.models import Conversation, Message

    form = MessageForm()

    convo = db.session.get(Conversation, conversation_id)
    if not convo or current_user.id not in [convo.user1_id, convo.user2_id]:
        flash('Conversation not found or unauthorized.', 'danger')
        return redirect(url_for('social.messages'))

    if form.validate_on_submit():
        content = form.content.data
        print(f"Received message content: {content}")  # Debug
        new_msg = Message(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            content=content
        )
        db.session.add(new_msg)
        db.session.commit()
        print(f"Saved message with ID: {new_msg.id}, content: {new_msg.content}")  # Debug
        return redirect(url_for('social.view_conversation', conversation_id=conversation_id))

    # Get messages
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
    print(f"Retrieved {len(messages)} messages")  # Debug
    for msg in messages:
        print(f"Message ID: {msg.id}, Sender: {msg.sender_id}, Content: '{msg.content}'")  # Debug

    other_id = convo.user2_id if convo.user1_id == current_user.id else convo.user1_id
    other_user = User.query.get(other_id)

    return render_template('social/conversation.html',
                           conversation_id=conversation_id,
                           messages=messages,
                           other_user=other_user,
                           form=form)



@social_bp.route('/messages/new/<int:user_id>')
@login_required
def new_conversation(user_id):
    conversation_id = create_conversation(current_user.id, user_id)
    return redirect(url_for('social.view_conversation', conversation_id=conversation_id))


@social_bp.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    per_page = 5

    if form.validate_on_submit():
        image_filename = None
        
        # Handle image upload if present
        if 'image' in request.files and request.files['image'].filename:
            from werkzeug.utils import secure_filename
            import time
            import os
            from flask import current_app
            
            image = request.files['image']
            if image.filename != '':
                # Create a secure filename with timestamp to avoid collisions
                filename = secure_filename(image.filename)
                image_filename = f"{current_user.id}_{int(time.time())}_{filename}"
                
                # Save the file
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
        
        # Create post with image
        post_id = create_post(
            user_id=current_user.id, 
            content=form.content.data, 
            visibility=form.visibility.data, 
            image_filename=image_filename
        )
        
        if post_id:
            flash('Post created successfully!', 'success')
        else:
            flash('Error creating post. Please try again.', 'danger')
        return redirect(url_for('social.feed'))

    # Get posts for feed with pagination
    posts_query = get_feed(current_user.id)
    posts = posts_query.paginate(page=page, per_page=per_page)
    
    # Get any additional data needed for the template
    notifications_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Get connection suggestions for the sidebar
    # Find users who aren't connected to the current user
    # This is a simple example - you might want a more sophisticated algorithm
    connection_suggestions = User.query.filter(
        User.id != current_user.id
    ).limit(5).all()  # Limit to 5 suggestions
    
    # Get counts for badges
    unread_messages_count = Message.query.filter_by(
        recipient_id=current_user.id, 
        read=False
    ).count()
    
    pending_connections_count = Connection.query.filter_by(
        recipient_id=current_user.id,
        status='pending'
    ).count()

    # Handle AJAX request for infinite scroll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('social/_posts.html', posts=posts)

    return render_template(
        'social/feed.html', 
        posts=posts, 
        form=form, 
        notifications_count=notifications_count,
        connection_suggestions=connection_suggestions,
        unread_messages_count=unread_messages_count,
        pending_connections_count=pending_connections_count
    )






#@social_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        create_post(current_user.id, form.content.data, form.visibility.data)
        flash('Post created successfully!', 'success')
        return redirect(url_for('social.feed'))
    return render_template('social/new_post.html', form=form)


# Fixed view_post route
#@social_bp.route('/post/<int:post_id>')
#@login_required
#def view_post(post_id):
 #   post = get_post(post_id, current_user.id)
  #  if not post:
   #     flash('Post not found or you do not have permission to view it.', 'danger')
    #    return redirect(url_for('social.feed'))
    #return render_template('social/view_posts.html', post=post)

@social_bp.route('/messages/<int:conversation_id>/mark-read', methods=['POST'])
@login_required
def mark_messages_read(conversation_id):
    # Get all unread messages in this conversation sent to current user
    unread_messages = Message.query.filter_by(
        conversation_id=conversation_id, 
        recipient_id=current_user.id,
        read=False
    ).all()
    
    # Mark them as read
    for message in unread_messages:
        message.read = True
    
    db.session.commit()
    
    return jsonify({'success': True})

# Fixed comment_post route
@social_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    # Check if the user has permission to view the post first
    post = get_post(post_id, current_user.id)
    if not post:
        flash('Post not found or you do not have permission to interact with it.', 'danger')
        return redirect(url_for('social.feed'))
        
    content = request.form.get('content')
    if content:
        add_comment(post_id, current_user.id, content)
        flash('Comment added', 'success')
    
    # Redirect to feed with anchor to the specific post and open the comments section
    return redirect(url_for('social.feed', _anchor=f'post-{post_id}', show_comments=post_id))


@social_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post_route(post_id):
    post = get_post(post_id, current_user.id)
    if not post:
        flash('Post not found or unauthorized.', 'danger')
        return redirect(url_for('social.feed'))

    if like_post(post_id, current_user.id):  # helper function
        flash('Post liked.', 'success')
    else:
        flash('You already liked this post.', 'warning')
    
    # Redirect to feed with anchor to the specific post
    return redirect(url_for('social.feed', _anchor=f'post-{post_id}'))



@social_bp.route('/post/<int:post_id>/unlike', methods=['POST'])
@login_required
def unlike_post_route(post_id):
    if unlike_post(post_id, current_user.id):
        flash('Unliked the post!', 'success')
    else:
        flash('You have not liked this post yet.', 'warning')
    
    # Redirect to feed with anchor to the specific post
    return redirect(url_for('social.feed', _anchor=f'post-{post_id}'))



@social_bp.route('/groups')
@login_required
def groups():
    user_groups = get_user_groups(current_user.id)
    return render_template('social/groups.html', groups=user_groups)


@social_bp.route('/groups/new', methods=['GET', 'POST'])
@login_required
def new_group():
    form = GroupForm()
    connections = get_connections(current_user.id)
    form.members.choices = [(str(user.id), user.full_name()) for user in connections]

    if form.validate_on_submit():
        group_id = create_group(current_user.id, form.name.data, form.description.data, form.members.data)
        flash('Group created successfully!', 'success')
        return redirect(url_for('social.view_group', group_id=group_id))

    return render_template('social/new_group.html', form=form)


@social_bp.route('/groups/<int:group_id>')
@login_required
def view_group(group_id):
    group = db.session.get(Group, group_id)
    if not group or current_user.id not in [member.id for member in group.members]:
        flash('Group not found or access denied.', 'danger')
        return redirect(url_for('social.groups'))

    messages = get_group_messages(group_id)
    members = group.members

    return render_template('social/group_chat.html',
                           group=group,
                           group_id=group_id,
                           messages=messages,
                           members=members,
                           is_creator=(group.creator_id == current_user.id))



# In social_bp.py

@social_bp.route('/send-connection-request/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_connection_request(user_id):
    # Check if user exists
    recipient = User.query.get_or_404(user_id)
    
    # Don't allow connections to self
    if recipient.id == current_user.id:
        flash('You cannot connect with yourself.', 'warning')
        return redirect(url_for('social.find_students'))
    
    # Check if connection already exists
    existing_connection = Connection.query.filter(
        ((Connection.requester_id == current_user.id) & (Connection.recipient_id == user_id)) |
        ((Connection.requester_id == user_id) & (Connection.recipient_id == current_user.id))
    ).first()
    
    if existing_connection:
        flash('A connection already exists or is pending.', 'info')
    else:
        # Create new connection request
        new_connection = Connection(
            requester_id=current_user.id,
            recipient_id=user_id,
            status='pending'
        )
        db.session.add(new_connection)
        db.session.commit()
        
        # Fix send_connection_request
        notification = Notification(
            user_id=user_id,
            message=f"{current_user.first_name} {current_user.last_name} sent you a connection request."
        )

        db.session.add(notification)
        db.session.commit()
        
        flash('Connection request sent!', 'success')
    
    return redirect(url_for('social.view_profile', user_id=user_id))



@social_bp.route('/accept-connection/<int:connection_id>', methods=['POST'])
@login_required
def accept_connection(connection_id):
    connection = Connection.query.get_or_404(connection_id)
    
    if connection.recipient_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('social.connections'))
    
    connection.status = 'accepted'
    db.session.commit()
    
    # Fix accept_connection
    notification = Notification(
        user_id=connection.requester_id,
     message=f"{current_user.first_name} {current_user.last_name} accepted your connection request."
    )

    db.session.add(notification)
    db.session.commit()
    
    flash('Connection accepted!', 'success')
    return redirect(url_for('social.connections'))


@social_bp.route('/notifications')
@login_required
def notifications():
    return render_template('social/notifications.html', notifications=current_user.notifications.order_by(Notification.created_at.desc()).all())


@social_bp.route('/reject-connection/<int:connection_id>', methods=['POST'])
@login_required
def reject_connection(connection_id):
    connection = Connection.query.get_or_404(connection_id)
    
    # Verify this user is the recipient of the request
    if connection.recipient_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('social.connections'))
    
    connection.status = 'rejected'
    db.session.commit()
    
    flash('Connection rejected.', 'info')
    return redirect(url_for('social.connections'))



@social_bp.route('/connections')
@login_required
def connections():
    # Get pending connection requests
    pending_requests = Connection.query.filter_by(
        recipient_id=current_user.id, 
        status='pending'
    ).order_by(Connection.created_at.desc()).all()
    
    # Get accepted connections
    accepted_connections = Connection.query.filter(
        ((Connection.requester_id == current_user.id) | (Connection.recipient_id == current_user.id)),
        Connection.status == 'accepted'
    ).all()
    
    # Get the users who are connected with the current user
    connected_users = []
    for conn in accepted_connections:
        if conn.requester_id == current_user.id:
            connected_users.append(User.query.get(conn.recipient_id))
        else:
            connected_users.append(User.query.get(conn.requester_id))
    
    return render_template(
        'social/connection.html',
        pending_requests=pending_requests,
        connections=connected_users
    )


@social_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post_route(post_id):
    """
    Route to handle deletion of a post.
    Verifies the current user is the owner of the post before deletion.
    """
    from app.models import delete_post, get_post
    
    # First check if the post exists and the user has permission to access it
    post = get_post(post_id, current_user.id)
    if not post:
        flash('Post not found or you do not have permission to view it.', 'danger')
        return redirect(url_for('social.feed'))
    
    # Check if the user is the owner of the post
    if post.user_id != current_user.id:
        flash('You can only delete your own posts.', 'danger')
        return redirect(url_for('social.feed'))
    
    # Try to delete the post
    if delete_post(post_id, current_user.id):
        flash('Post deleted successfully.', 'success')
    else:
        flash('An error occurred while trying to delete the post.', 'danger')
    
    # Redirect back to the feed
    return redirect(url_for('social.feed'))


class DummyForm(FlaskForm):
    pass
