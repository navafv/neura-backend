import io
import csv
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from .models import *
from .serializers import *
from .permissions import IsCoordinatorOrReadOnly

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "is_superuser": request.user.is_superuser
    })

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class FestViewSet(viewsets.ModelViewSet):
    queryset = Fest.objects.all().order_by('-year')
    serializer_class = FestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all().order_by('start_time')
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fest']

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCoordinatorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['fest', 'is_team_event']
    search_fields = ['title']

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_events(self, request):
        if request.user.is_superuser:
            events = Event.objects.all()
        else:
            events = Event.objects.filter(coordinator=request.user)
        return Response(EventSerializer(events, many=True).data)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        event = self.get_object()
        # Security: Only return data if published OR if admin requesting
        if not event.results_published:
             if not request.user.is_authenticated:
                 return Response({"detail": "Results not yet published"}, status=403)
             if not request.user.is_superuser and request.user != event.coordinator:
                 return Response({"detail": "Results not yet published"}, status=403)

        winners = event.registrations.filter(is_winner=True).order_by('rank')
        return Response(ParticipantSerializer(winners, many=True).data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def qualifiers(self, request, pk=None):
        """Returns list of participants for public view (No sensitive data)"""
        event = self.get_object()
        # Return all participants, frontend can filter by max round
        participants = event.registrations.all().order_by('-current_round', 'name')
        return Response(PublicParticipantSerializer(participants, many=True).data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def dashboard_data(self, request, pk=None):
        event = self.get_object()
        if request.user != event.coordinator and not request.user.is_superuser:
            return Response({"error": "Unauthorized"}, status=403)

        participants = event.registrations.all()
        return Response({
            "total_registrations": participants.count(),
            "rounds_config": EventRoundSerializer(event.rounds.all(), many=True).data,
            "participants": ParticipantSerializer(participants, many=True).data
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def export_registrations(self, request, pk=None):
        event = self.get_object()
        if request.user != event.coordinator and not request.user.is_superuser:
            return Response({"error": "Unauthorized"}, status=403)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{event.title}_registrations.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Team Name', 'Email', 'Phone', 'College', 'Attended', 'Current Round', 'Rank', 'Winner', 'Payment Ref'])

        for p in event.registrations.all():
            writer.writerow([
                p.id, p.name, p.team_name or "N/A", p.email, p.phone, p.college,
                "Yes" if p.attended else "No", p.current_round, p.rank or "-", "Yes" if p.is_winner else "No",
                p.transaction_id or "N/A"
            ])

        return response
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        event = self.get_object()
        stats = {
            "total_registrations": event.registrations.count(),
            "attendance_rate": (event.registrations.filter(attended=True).count() / event.registrations.count() * 100) if event.registrations.exists() else 0,
            "average_rating": event.feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0,
            "college_distribution": event.registrations.values('college').annotate(count=Count('id'))
        }
        return Response(stats)

    @action(detail=True, methods=['post'])
    def generate_certificates(self, request, pk=None):
        event = self.get_object()
        participants = event.registrations.filter(attended=True)
        
        for p in participants:
            template = 'certificates/participation.html'
            context = {
                'participant_name': p.name,
                'college': p.college,
                'event_title': event.title,
                'fest_name': event.fest.name if event.fest else "NEURA",
                'year': event.date.year,
                'title': 'Participation',
                'type_class': 'participation'
            }

            if p.is_winner:
                context['title'] = 'Excellence'
                context['type_class'] = 'excellence'
                context['rank'] = p.rank

            html = render_to_string(template, context)
            result = io.BytesIO()
            pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
            
            p.certificate.save(f"cert_{p.id}.pdf", ContentFile(result.getvalue()))
            p.save()
            
        return Response({"detail": "Certificates generated successfully."})

class ParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event', 'current_round', 'attended']
    search_fields = ['name', 'team_name', 'email']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Participant.objects.all().order_by('-registered_at')
        if user.is_authenticated:
            return Participant.objects.filter(event__coordinator=user).order_by('-registered_at')
        return Participant.objects.none()

    def get_permissions(self):
        if self.action == 'create': return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def promote(self, request):
        ids = request.data.get('ids', [])
        next_round = request.data.get('next_round')
        qs = self.get_queryset().filter(id__in=ids)
        updated = qs.update(current_round=next_round)
        return Response({"msg": f"Promoted {updated} participants"})

    @action(detail=True, methods=['patch'])
    def assign_rank(self, request, pk=None):
        p = self.get_object()
        p.rank = request.data.get('rank')
        p.is_winner = True
        p.save()
        return Response({"status": "Rank updated"})
    
    @action(detail=True, methods=['patch'])
    def toggle_attendance(self, request, pk=None):
        p = self.get_object()
        p.attended = not p.attended
        p.save()
        return Response({"status": "Attendance updated", "attended": p.attended})
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Dashboard endpoint for participants"""
        if not request.user.is_authenticated:
            return Response({"error": "Login required"}, status=401)
        registrations = Participant.objects.filter(user=request.user)
        return Response(ParticipantSerializer(registrations, many=True).data)

class EventRoundViewSet(viewsets.ModelViewSet):
    queryset = EventRound.objects.all()
    serializer_class = EventRoundSerializer
    permission_classes = [permissions.IsAuthenticated, IsCoordinatorOrReadOnly]

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all().order_by('-uploaded_at')
    serializer_class = GallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]

class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all().order_by('order')
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]