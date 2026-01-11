from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255, default="Main Auditorium")
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    pdf_resource = models.FileField(upload_to='event_pdfs/', null=True, blank=True) 
    is_fest_event = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=100) 

    @property
    def is_registration_open(self):
        return timezone.now() < self.date

    def __str__(self):
        return self.title

class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    college = models.CharField(max_length=200)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"

class Leaderboard(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='winners')
    participant_name = models.CharField(max_length=100)
    rank = models.IntegerField() 
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