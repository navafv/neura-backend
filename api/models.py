from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_resized import ResizedImageField

class Fest(models.Model):
    name = models.CharField(max_length=200, help_text="e.g. 'Intra IT Fest 2026'")
    year = models.IntegerField(default=timezone.now().year)
    is_active = models.BooleanField(default=True)
    brochure = models.FileField(upload_to='fest_docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.year})"

class Event(models.Model):
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinated_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255, default="Main Auditorium")
    image = ResizedImageField(size=[800, 600], quality=75, upload_to='events/', blank=True, null=True)
    pdf_resource = models.FileField(upload_to='event_pdfs/', null=True, blank=True)
    is_team_event = models.BooleanField(default=False)
    min_team_size = models.IntegerField(default=1)
    max_team_size = models.IntegerField(default=1)
    max_participants = models.PositiveIntegerField(default=100)

    @property
    def is_registration_open(self):
        return timezone.now() < self.date

    def __str__(self):
        return self.title

class EventRound(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField(default=1)
    name = models.CharField(max_length=100, default="Preliminary Round")
    selection_limit = models.IntegerField(default=10, help_text="How many teams/people qualify for the next round?")
    
    class Meta:
        ordering = ['round_number']

    def __str__(self):
        return f"{self.event.title} - R{self.round_number}: {self.name}"

class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    team_name = models.CharField(max_length=100, blank=True, null=True)
    team_members = models.TextField(blank=True, null=True, help_text="Comma separated names of members")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    college = models.CharField(max_length=200)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    current_round = models.IntegerField(default=1)
    is_winner = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True, help_text="1 for 1st Prize, 2 for 2nd, etc.")

    def __str__(self):
        return f"{self.team_name or self.name} - {self.event.title}"

class Gallery(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Lower number appears first")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.role}"