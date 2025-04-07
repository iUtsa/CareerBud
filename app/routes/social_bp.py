from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import (
    search_users, User, add_connection, accept_connection, get_connections,
    get_conversations, get_messages, create_conversation,
    get_feed, create_post, add_comment, like_post, unlike_post,
    create_group, get_user_groups, get_group_messages
)
from app.forms import PostForm, GroupForm
from app import db

social_bp = Blueprint('social', __name__, url_prefix='/social')


@social_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if len(query) < 3:
        return render_template('social/search.html', results=[], query='')

    results = search_users(query)
    results = [user for user in results if user.id != current_user.id]

    return render_template('social/search.html', results=results, query=query)


@social_bp.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    user_data = User.query.get(user_id)
    if not user_data:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    connection = db.session.execute(
        db.select(User).join(User.connections)
        .filter((User.id == current_user.id) & (User.id == user_id))
    ).first()

    connection_status = None
    if connection:
        connection_status = 'connected' if connection.status == 'accepted' else 'pending'

    return render_template('social/view_profile.html', user=user_data, connection_status=connection_status)


@social_bp.route('/connections')
@login_required
def connections():
    connections = get_connections(current_user.id, 'accepted')
    pending_requests = db.session.query(User).join(User.connections).filter(
        Connection.friend_id == current_user.id, Connection.status == 'pending'
    ).all()

    return render_template('social/connections.html',
                           connections=connections,
                           pending_requests=pending_requests)


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
    return render_template('social/messages.html', conversations=conversations)


@social_bp.route('/messages/<int:conversation_id>')
@login_required
def view_conversation(conversation_id):
    messages = get_messages(conversation_id)
    other_user = None

    convo = db.session.get(Conversation, conversation_id)
    if convo and (convo.user1_id == current_user.id or convo.user2_id == current_user.id):
        other_id = convo.user2_id if convo.user1_id == current_user.id else convo.user1_id
        other_user = User.query.get(other_id)
    else:
        flash('Conversation not found', 'danger')
        return redirect(url_for('social.messages'))

    return render_template('social/conversation.html',
                           conversation_id=conversation_id,
                           messages=messages,
                           other_user=other_user)


@social_bp.route('/messages/new/<int:user_id>')
@login_required
def new_conversation(user_id):
    conversation_id = create_conversation(current_user.id, user_id)
    return redirect(url_for('social.view_conversation', conversation_id=conversation_id))


@social_bp.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    form = PostForm()  # Create an instance of the form

    # Check if the form was submitted and validated
    if form.validate_on_submit():
        # Call the create_post function to add a new post to the database
        create_post(current_user.id, form.content.data, form.visibility.data)
        flash('Post created successfully!', 'success')
        
        # After creating the post, get the latest feed for the user
        posts = get_feed(current_user.id)  # Get the updated feed
        return render_template('social/feed.html', posts=posts, form=form)

    # Get the feed posts to display if it's a GET request
    posts = get_feed(current_user.id)  # Fetch posts
    return render_template('social/feed.html', posts=posts, form=form)






@social_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        create_post(current_user.id, form.content.data, form.visibility.data)
        flash('Post created successfully!', 'success')
        return redirect(url_for('social.feed'))
    return render_template('social/new_post.html', form=form)


@social_bp.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = get_feed(current_user.id, post_id)
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('social.feed'))
    return render_template('social/view_post.html', post=post)


@social_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form.get('content')
    if content:
        add_comment(post_id, current_user.id, content)
        flash('Comment added', 'success')
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post_route(post_id):
    if like_post(post_id, current_user.id):
        flash('Liked the post!', 'success')
    else:
        flash('You already liked this post.', 'warning')
    return redirect(url_for('social.view_post', post_id=post_id))

@social_bp.route('/post/<int:post_id>/unlike', methods=['POST'])
@login_required
def unlike_post_route(post_id):
    if unlike_post(post_id, current_user.id):
        flash('Unliked the post!', 'success')
    else:
        flash('You have not liked this post yet.', 'warning')
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
