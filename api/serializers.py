from rest_framework import serializers
from django.utils import timezone
from .models import Event, Gallery, Feedback, Participant, EventRound, Fest

class EventRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRound
        fields = ['id', 'round_number', 'name', 'selection_limit']

class EventSerializer(serializers.ModelSerializer):
    rounds = EventRoundSerializer(many=True, read_only=True)
    registration_count = serializers.IntegerField(source='registrations.count', read_only=True)
    coordinator_name = serializers.ReadOnlyField(source='coordinator.username')

    class Meta:
        model = Event
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Participant
        fields = '__all__'

    def validate(self, data):
        event = data['event']
        
        # Check Date
        if timezone.now() >= event.date:
            raise serializers.ValidationError("Registration is closed.")
        
        # Check Capacity
        if event.registrations.count() >= event.max_participants:
            raise serializers.ValidationError("Event Full.")
            
        # Check Team Logic
        if event.is_team_event and not data.get('team_name'):
            raise serializers.ValidationError("Team Name is required for this event.")
            
        return data

class FestSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    class Meta:
        model = Fest
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'