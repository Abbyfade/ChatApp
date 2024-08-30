from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    # You can add additional fields here if needed
    phone_number = PhoneNumberField()

class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat ID: {self.id}"

class Friendship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships', on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_of', on_delete=models.CASCADE)
    chat = models.OneToOneField('Chat', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')  # Ensure that each friendship is unique
        constraints = [
            models.UniqueConstraint(fields=['friend', 'user'], name='unique_friendship_reverse')
        ]

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"

    def delete(self, *args, **kwargs):
        # Delete the associated chat if it exists
        if self.chat:
            self.chat.delete()  # This will also delete related messages due to cascade
        super().delete(*args, **kwargs)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')  # Reference to the chat room
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the user who sent the message
    content = models.TextField()  # Content of the message
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp for when the message was sent

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}... in Room {self.chat.id}"