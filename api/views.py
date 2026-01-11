import io
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from .models import Event, Leaderboard, Gallery, Feedback, Participant
from .serializers import *

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_fest_event'] 
    search_fields = ['title', 'description']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def generate_certificates(self, request, pk=None):
        """Generates PDF certificates for all participants of an event and emails them."""
        event = self.get_object()
        participants = event.registrations.all()
        
        if not participants.exists():
            return Response({"error": "No participants found for this event."}, status=400)

        for participant in participants:
            # 1. Generate PDF in memory
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=landscape(letter))
            width, height = landscape(letter)

            # Simple Design
            p.setFont("Helvetica-Bold", 40)
            p.drawCentredString(width / 2, height - 150, "CERTIFICATE OF PARTICIPATION")
            
            p.setFont("Helvetica", 20)
            p.drawCentredString(width / 2, height - 250, "This is to certify that")
            
            p.setFont("Helvetica-Bold", 30)
            p.drawCentredString(width / 2, height - 300, participant.name.upper())
            
            p.setFont("Helvetica", 20)
            p.drawCentredString(width / 2, height - 350, f"participated in the event")
            
            p.setFont("Helvetica-Bold", 25)
            p.drawCentredString(width / 2, height - 400, event.title.upper())
            
            p.setFont("Helvetica", 15)
            p.drawCentredString(width / 2, 100, f"Issued on: {timezone.now().strftime('%Y-%m-%d')}")
            
            p.showPage()
            p.save()

            # 2. Save PDF to model
            filename = f"Certificate_{participant.id}.pdf"
            participant.certificate.save(filename, ContentFile(buffer.getvalue()))
            participant.save()

            # 3. Email the Link
            cert_url = request.build_absolute_uri(participant.certificate.url)
            subject = f"Your Certificate: {event.title}"
            message = f"Hi {participant.name},\n\nThank you for participating in {event.title}. You can download your certificate here:\n{cert_url}\n\nKeep innovating!\n- Neura IT Club"
            
            send_mail(
                subject, message, 
                settings.EMAIL_HOST_USER, 
                [participant.email], 
                fail_silently=True
            )

        return Response({"detail": f"Successfully forged and emailed {participants.count()} certificates."})

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all().order_by('-registered_at')
    serializer_class = ParticipantSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = Leaderboard.objects.all().order_by('rank')
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all().order_by('-uploaded_at')
    serializer_class = GallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]