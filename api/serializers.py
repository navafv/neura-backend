import json
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, EventRound, Participant, Gallery, Feedback, Fest, TeamMember, Schedule

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EventRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRound
        fields = ['id', 'event', 'round_number', 'name', 'selection_limit']

class EventSerializer(serializers.ModelSerializer):
    rounds = EventRoundSerializer(many=True, read_only=True)
    registration_count = serializers.IntegerField(source='registrations.count', read_only=True)
    coordinator_name = serializers.ReadOnlyField(source='coordinator.username')
    fest_name = serializers.ReadOnlyField(source='fest.name')
    is_registration_open = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = '__all__'

    # Converts stringified JSON from FormData back to Python Dict
    def to_internal_value(self, data):
        data = data.copy()
        if 'custom_fields' in data and isinstance(data['custom_fields'], str):
            try:
                data['custom_fields'] = json.loads(data['custom_fields'])
            except ValueError:
                data['custom_fields'] = []
        return super().to_internal_value(data)

class ParticipantSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = Participant
        fields = '__all__'

    # Converts stringified JSON from FormData back to Python Dict
    def to_internal_value(self, data):
        data = data.copy()
        if 'custom_responses' in data and isinstance(data['custom_responses'], str):
            try:
                data['custom_responses'] = json.loads(data['custom_responses'])
            except ValueError:
                data['custom_responses'] = {}
        return super().to_internal_value(data)

    def validate(self, data):
        event = data['event']
        if not event.is_registration_open:
            raise serializers.ValidationError("Registration is closed for this event.")
        if event.registrations.count() >= event.max_participants:
            raise serializers.ValidationError("Event Full.")
        if event.is_team_event and not data.get('team_name'):
            raise serializers.ValidationError("Team Name is required for team events.")
        return data

class PublicParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['name', 'team_name', 'college', 'current_round', 'is_winner', 'rank']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class FestSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, read_only=True)
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

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'