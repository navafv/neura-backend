from django.contrib import admin
from .models import Event, Participant, Leaderboard, Gallery, Feedback

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'is_fest_event')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'registered_at')
    list_filter = ('event',)

admin.site.register(Leaderboard)
admin.site.register(Gallery)
admin.site.register(Feedback)