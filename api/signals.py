from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Participant

@receiver(post_save, sender=Participant)
def send_registration_email(sender, instance, created, **kwargs):
    if created:
        subject = f"Registration Confirmed: {instance.event.title}"
        message = f"Hi {instance.name},\n\nYou have successfully registered for {instance.event.title}.\nLocation: {instance.event.location}\nDate: {instance.event.date}\n\nSee you there!"
        from_email = 'no-reply@itclub.com'
        recipient_list = [instance.email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=True)