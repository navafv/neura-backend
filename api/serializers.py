from rest_framework import serializers
from .models import Event, Leaderboard, Gallery, Feedback, Participant

class ParticipantSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source='event.title')
    class Meta:
        model = Participant
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    # This logic shows you the total registrations for each event in the API
    registration_count = serializers.IntegerField(source='registrations.count', read_only=True)
    
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