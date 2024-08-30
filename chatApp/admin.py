from django.contrib import admin
from .models import User, Chat, Friendship,Message

admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Friendship)
admin.site.register(Message)