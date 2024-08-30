from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, LoginForm
from .models import User, Chat, Friendship, Message
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
# Create your views here.


def home(request):
    if request.user.is_authenticated:
        return redirect('base')
    return render(request, 'home.html')

# def format_timestamp(timestamp):
#     now = datetime.now()
#     nigerian_timezone = pytz.timezone('Africa/Lagos')

#     # Convert the timestamp to Nigerian time
#     timestamp_ngr = timestamp.astimezone(nigerian_timezone)
#     if timestamp_ngr.date() == now.date():
#         return timestamp_ngr.strftime("%H:%M")  # Show time
#     elif timestamp_ngr.date() == (now - timedelta(days=1)).date():
#         return "Yesterday"  # Show yesterday
#     else:
#         return timestamp_ngr.strftime("%Y-%m-%d")

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)  # Exclude the logged-in user
    grouped_users = {}
    for user in users:
        first_letter = user.username[0].upper()
        if first_letter not in grouped_users:
            grouped_users[first_letter] = []
        grouped_users[first_letter].append(user)

    # Pass the grouped users dictionary to the template
    return render(request, 'chat/user_list.html', {'grouped_users': grouped_users})
    
@login_required
def chat_list_view(request):
    return render(request, 'chat/base.html')


@login_required
def chat(request, room_id):
    username = request.user.username
    chat = get_object_or_404(Chat, id=room_id)
    messages = chat.messages.all()
    friendship = Friendship.objects.get(chat=chat)
    friend_username = friendship.friend.username if friendship.user == request.user else friendship.user.username
    return render(request, 'chat/chat_room.html', {'room_id': room_id, 'messages': messages, 'username': username, 'friend_username': friend_username,})


@login_required
def start_chat(request, username):
    friend = get_object_or_404(User, username=username)

    # Check if a friendship already exists
    friendship = Friendship.objects.filter(user=request.user, friend=friend).first()
    reverse_friendship = Friendship.objects.filter(user=friend, friend=request.user).first()

    if friendship != None or reverse_friendship != None:
        # If a friendship exists in either direction, check if there is an associated chat
        if friendship != None and friendship.chat:
            chat = friendship.chat
        elif reverse_friendship != None and reverse_friendship.chat:
            chat = reverse_friendship.chat
        else:
            # If there is no chat, create one
            chat = Chat.objects.create()
            friendship.chat = chat
            friendship.save()  # Save the friendship with the new chat
    else:
        # Create a new friendship
        friendship = Friendship.objects.create(user=request.user, friend=friend)
        # Create a new chat instance and associate it with the friendship
        chat = Chat.objects.create()
        friendship.chat = chat
        friendship.save()

    # Redirect to the chat room
    return redirect('chat', room_id=chat.id)  # Adjust to your chat view URL name


def authView(request):
    if request.user.is_authenticated:
        return redirect('base')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('base')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.login(request)
            if user:
                login(request, user)
                return redirect('base')  # Redirect to the home page or any other URL
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')




# @login_required
# def chat_list_view(request):
    # # Get all friendships where the user is either the user or the friend
    # friendships = Friendship.objects.filter(
    #     Q(user=request.user) | Q(friend=request.user)
    # )
    # # Prepare a list to hold chat data
    # chat_list = []
    # formatted_chats = []

    # for friendship in friendships:
    #     # Determine the friend user based on the friendship relationship
    #     friend_user = friendship.friend if friendship.user == request.user else friendship.user

    #     # Get the chat associated with the friendship
    #     chat = friendship.chat

    #     # Get the most recent message in the chat
    #     recent_message = Message.objects.filter(chat=chat).order_by('-timestamp').first()

    #     chat_data = {
    #         'friend_name': friend_user.username,
    #         'most_recent_message': recent_message.content if recent_message else 'No messages yet',
    #         'timestamp': recent_message.timestamp if recent_message else None,
    #     }
        
    #     chat_list.append(chat_data)
    #     chat_list = [chat for chat in chat_list if chat['timestamp'] is not None]
    #     chat_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
    #     for chat in chat_list:
    #         formatted_chats.append({
    #             "friend_name": chat["friend_name"],
    #             "most_recent_message": chat["most_recent_message"],
    #             "timestamp": format_timestamp(chat["timestamp"])
    #         })

    # context = {
    #     'chat_list': formatted_chats,
    # }

    # return render(request, 'chat/base.html', context)