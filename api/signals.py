import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Participant

@receiver(post_save, sender=Participant)
def on_registration(sender, instance, created, **kwargs):
    if created:
        # Generate QR Code
        qr_data = f"ID:{instance.id}|Name:{instance.name}|Event:{instance.event.title}"
        qr = qrcode.make(qr_data)
        canvas = BytesIO()
        qr.save(canvas, format='PNG')
        instance.qr_code.save(f'qr_{instance.id}.png', File(canvas), save=False)
        instance.save(update_fields=['qr_code'])