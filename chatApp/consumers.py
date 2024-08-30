import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import User, Message, Chat, Friendship  # Import your models
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
import pytz


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_id = f'chat_{self.room_id}'
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_id,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_id,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        new_message = text_data_json['message']
        room_id = text_data_json['room_id']
        username = text_data_json['username']
        timestamp = text_data_json['timestamp']
        
        user = self.scope['user']
        user_id = user.id

        await self.save_message(user_id, room_id, new_message)
        
        # Send the message to the specific room group
        await self.channel_layer.group_send(
            f'chat_{room_id}',
            {
                'type': 'send_message',
                'message': new_message,
                'room_id': room_id,
                'username': username,
                'timestamp': timestamp
            }
        )
        # Notify all users who are part of the chat to update their chat list
        users_in_chat = await self.get_users_in_chat(room_id)
        for user in users_in_chat:
            await self.channel_layer.group_send(
                f'chat_list_{user.id}',
                {
                    'type': 'chat_list_update'
                }
            )

    async def send_message(self, event):
        message = event['message']
        room_id = event['room_id']
        username = event['username']
        timestamp = event['timestamp']
    
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'room_id': room_id,
            'username': username,
            'timestamp': timestamp,
        }))

    @database_sync_to_async
    def save_message(self, user_id, room_id, message):
        chat = Chat.objects.get(id=room_id)  # Get the chat instance
        user = User.objects.get(id=user_id)

        # Create a new Message instance
        Message.objects.create(chat=chat, user=user, content=message)

    @database_sync_to_async
    def get_users_in_chat(self, room_id):
        """Get all users in a chat room by room_id."""
        chat = Chat.objects.get(id=room_id)

        # Fetch both users associated with the chat
        friendships = Friendship.objects.filter(chat=chat)

        # Extract all users from these friendships
        users = []
        for friendship in friendships:
            users.append(friendship.user)
            users.append(friendship.friend)

        unique_users = list(set(users))

        return unique_users  

def format_timestamp(timestamp):
    now = datetime.now()
    nigerian_timezone = pytz.timezone('Africa/Lagos')

    # Convert the timestamp to Nigerian time
    timestamp_ngr = timestamp.astimezone(nigerian_timezone)
    if timestamp_ngr.date() == now.date():
        return timestamp_ngr.strftime("%H:%M")  # Show time
    elif timestamp_ngr.date() == (now - timedelta(days=1)).date():
        return "Yesterday"  # Show yesterday
    else:
        return timestamp_ngr.strftime("%Y-%m-%d")
            
class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.group_name = f'chat_list_{user.id}'

        # Join the user's personal group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Optionally, send the initial chat list on connection
        await self.send_chat_list()

    async def disconnect(self, close_code):
        # Handle disconnection if needed
        pass

    async def chat_list_update(self, event):
        """Handle the chat list update event."""
        await self.send_chat_list()

    async def send_chat_list(self):
        """Send the updated chat list to the client."""
        chat_list = await self.get_chat_list()
        await self.send(text_data=json.dumps({
            'type': 'chat_list_update',
            'chat_list': chat_list,
        }))

    async def receive(self, text_data):
        pass

    @database_sync_to_async
    def get_chat_list(self):
        """Retrieve the chat list for the logged-in user."""
        user = self.scope['user']
        friendships = Friendship.objects.filter(
            Q(user=user) | Q(friend=user)
        )

        chat_list = []
        for friendship in friendships:
            friend_user = friendship.friend if friendship.user == user else friendship.user

            chat = friendship.chat
            recent_message = chat.messages.order_by('-timestamp').first()

            chat_data = {
                'chat_id': chat.id,
                'friend_name': friend_user.username,
                'most_recent_message': recent_message.content if recent_message else 'No messages yet',
                'timestamp': recent_message.timestamp if recent_message else None,
            }
            chat_list.append(chat_data)

        chat_list = [chat for chat in chat_list if chat['timestamp'] is not None]
        # Sort by the most recent message timestamp
        chat_list.sort(key=lambda x: x['timestamp'], reverse=True)
        formatted_chats = []
        for chat in chat_list:
            formatted_chats.append({
                "friend_name": chat["friend_name"],
                "most_recent_message": chat["most_recent_message"],
                "timestamp": format_timestamp(chat["timestamp"])
            })
        chat_list = formatted_chats
        return chat_list

