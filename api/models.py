from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255, default="Main Auditorium")
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    is_fest_event = models.BooleanField(default=False) # True if part of the IT Fest

    def __str__(self):
        return self.title

class Leaderboard(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='winners')
    participant_name = models.CharField(max_length=100)
    rank = models.IntegerField() # 1 for 1st place, etc.
    points = models.IntegerField(default=0)

class Gallery(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)