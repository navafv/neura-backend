from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_resized import ResizedImageField

class Fest(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(default=timezone.now().year)
    is_active = models.BooleanField(default=True)
    brochure = models.FileField(upload_to='fest_docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.year})"

class Sponsor(models.Model):
    TIER_CHOICES = [('Gold', 'Gold'), ('Silver', 'Silver'), ('Bronze', 'Bronze')]
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='sponsors')
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='sponsors/')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    website = models.URLField(blank=True)

class Event(models.Model):
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='events', null=True)
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='coordinated_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255, default="Main Auditorium")
    image = ResizedImageField(size=[800, 600], quality=75, upload_to='events/', blank=True, null=True)
    is_team_event = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=100)
    results_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Resource(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='resources/')

class EventRound(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['event', 'round_number']

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    college = models.CharField(max_length=200)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    attended = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    current_round = models.IntegerField(default=1)
    is_winner = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"

class Gallery(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Score(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='scores')
    round = models.ForeignKey(EventRound, on_delete=models.CASCADE)
    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks', null=True)
    name = models.CharField(max_length=100)
    rating = models.IntegerField(default=5)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.role}"