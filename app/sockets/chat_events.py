from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio, db
from app.models import send_message, send_group_message
from datetime import datetime
from bson import ObjectId

@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        return False
    
    # Join rooms for each conversation
    conversations = db.conversations.find({
        'participants': ObjectId(current_user.id)
    })
    
    for conv in conversations:
        join_room(str(conv['_id']))

@socketio.on('join_conversation')
def handle_join_conversation(data):
    room = data['conversation_id']
    join_room(room)

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    room = data['conversation_id']
    leave_room(room)

@socketio.on('new_message')
def handle_new_message(data):
    if not current_user.is_authenticated:
        return
    
    conversation_id = data['conversation_id']
    content = data['content']
    
    # Store message in database
    send_message(conversation_id, current_user.id, content)
    
    # Broadcast to room
    emit('message', {
        'sender_id': current_user.id,
        'sender_name': f"{current_user.first_name} {current_user.last_name}",
        'content': content,
        'timestamp': datetime.now().isoformat()
    }, room=conversation_id)

# Add to chat_events.py
@socketio.on('join_group')
def handle_join_group(data):
    room = f"group_{data['group_id']}"
    join_room(room)

@socketio.on('leave_group')
def handle_leave_group(data):
    room = f"group_{data['group_id']}"
    leave_room(room)

@socketio.on('new_group_message')
def handle_new_group_message(data):
    if not current_user.is_authenticated:
        return
    
    group_id = data['group_id']
    content = data['content']
    
    # Store message in database
    send_group_message(group_id, current_user.id, content)
    
    # Broadcast to room
    room = f"group_{group_id}"
    emit('group_message', {
        'sender_id': current_user.id,
        'sender_name': f"{current_user.first_name} {current_user.last_name}",
        'content': content,
        'timestamp': datetime.now().isoformat()
    }, room=room)
    