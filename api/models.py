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

class Event(models.Model):
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='events', null=True)
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='coordinated_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    registration_deadline = models.DateTimeField(blank=True, null=True)
    registration_fee = models.IntegerField(default=0, help_text='0 for free events')
    payment_qr = models.ImageField(upload_to='payment_qrs/', blank=True, null=True)
    location = models.CharField(max_length=255, default="Main Auditorium")
    image = ResizedImageField(size=[800, 600], quality=75, upload_to='events/', blank=True, null=True)
    pdf_resource = models.FileField(upload_to='event_pdfs/', blank=True, null=True)
    is_team_event = models.BooleanField(default=False)
    min_team_size = models.IntegerField(default=1)
    max_team_size = models.IntegerField(default=1)
    max_participants = models.PositiveIntegerField(default=100)
    results_published = models.BooleanField(default=False)
    custom_fields = models.JSONField(blank=True, default=list, help_text="List of extra field labels")

    @property
    def is_registration_open(self):
        if self.registration_deadline:
            return timezone.now() < self.registration_deadline
        return timezone.now() < self.date

    def __str__(self):
        return self.title

class EventRound(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    selection_limit = models.IntegerField(default=10)
    
    class Meta:
        unique_together = ['event', 'round_number']
        ordering = ['round_number']

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    college = models.CharField(max_length=200)
    
    # Team fields
    team_name = models.CharField(max_length=100, blank=True, null=True)
    team_members = models.TextField(blank=True, null=True)
    
    # Payment fields
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    
    # Dynamic fields
    custom_responses = models.JSONField(blank=True, default=dict)

    # Status fields
    attended = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    current_round = models.IntegerField(default=1)
    is_winner = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"

class Gallery(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks', null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(default="") 
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

class Schedule(models.Model):
    fest = models.ForeignKey(Fest, on_delete=models.CASCADE, related_name='schedules')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)