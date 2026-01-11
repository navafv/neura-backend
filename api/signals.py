import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Participant

@receiver(post_save, sender=Participant)
def on_registration(sender, instance, created, **kwargs):
    if created:
        # Generate QR Code
        qr_data = f"Participant: {instance.name}, Event: {instance.event.title}"
        qr = qrcode.make(qr_data)
        canvas = BytesIO()
        qr.save(canvas, format='PNG')
        instance.qr_code.save(f'qr_{instance.id}.png', File(canvas), save=False)
        instance.save()

        # Send Automatic Email
        send_mail(
            f"Registration Confirmed: {instance.event.title}",
            f"Hi {instance.name}, your spot is secured! Find your QR code in the portal.",
            'noreply@neura.com',
            [instance.email],
            fail_silently=True,
        )