from rest_framework import serializers
from django.utils import timezone
from .models import Event, Leaderboard, Gallery, Feedback, Participant

class ParticipantSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Participant
        fields = '__all__'

    def validate(self, data):
        event = data['event']
        
        # Logic: No registration if event started
        if timezone.now() >= event.date:
            raise serializers.ValidationError("Registration is closed. The event has already started.")
        
        # Logic: No registration if limit reached
        if event.registrations.count() >= event.max_participants:
            raise serializers.ValidationError("This event is full.")
            
        return data

class EventSerializer(serializers.ModelSerializer):
    registration_count = serializers.IntegerField(source='registrations.count', read_only=True)
    is_open = serializers.ReadOnlyField(source='is_registration_open')

    class Meta:
        model = Event
        fields = '__all__'

class LeaderboardSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source='event.title')
    class Meta:
        model = Leaderboard
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'