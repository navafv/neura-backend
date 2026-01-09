from rest_framework import serializers
from .models import Event, Leaderboard, Gallery, Feedback

class EventSerializer(serializers.ModelSerializer):
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