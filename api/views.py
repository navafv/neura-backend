from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, Participant, Gallery, Feedback, Fest
from .serializers import *
from .permissions import IsCoordinatorOrReadOnly

class FestViewSet(viewsets.ModelViewSet):
    queryset = Fest.objects.all().order_by('-year')
    serializer_class = FestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCoordinatorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['fest', 'is_team_event']
    search_fields = ['title']

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def dashboard_data(self, request, pk=None):
        """
        Returns data for the Event Admin Dashboard:
        - List of participants split by Round
        - Counts
        """
        event = self.get_object()
        
        # Security check: Only Coordinator or Superuser can access
        if request.user != event.coordinator and not request.user.is_superuser:
            return Response({"error": "Unauthorized"}, status=403)

        participants = event.registrations.all()
        data = {
            "total_registrations": participants.count(),
            "rounds_config": EventRoundSerializer(event.rounds.all(), many=True).data,
            "participants": ParticipantSerializer(participants, many=True).data
        }
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        event = self.get_object()
        # Get winners
        winners = event.registrations.filter(is_winner=True)
        return Response(ParticipantSerializer(winners, many=True).data)

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all().order_by('-registered_at')
    serializer_class = ParticipantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event', 'current_round', 'attended']
    search_fields = ['name', 'team_name', 'email']

    def get_permissions(self):
        # Allow anyone to register (create), but restrict listing to admins
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_attendance(self, request, pk=None):
        participant = self.get_object()
        participant.attended = True
        participant.save()
        return Response({"status": "Attended marked"})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def promote(self, request):
        """
        Bulk promote participants to next round.
        Body: { "ids": [1, 2, 5], "next_round": 2 }
        """
        ids = request.data.get('ids', [])
        next_round = request.data.get('next_round')
        
        if not ids or not next_round:
            return Response({"error": "Missing ids or next_round"}, status=400)

        participants = Participant.objects.filter(id__in=ids)
        updated_count = participants.update(current_round=next_round)
        
        return Response({"msg": f"Promoted {updated_count} participants to Round {next_round}"})
    
    @action(detail=False, methods=['get'], url_path='verify/(?Pf<cert_id>[^/.]+)')
    def verify(self, request,yz_id=None):
        # Logic to find participant by some hash or ID
        pass

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all().order_by('-uploaded_at')
    serializer_class = GallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]