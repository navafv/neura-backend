from django.contrib import admin
from .models import Fest, Event, EventRound, Participant, Gallery, Feedback, TeamMember

class EventRoundInline(admin.TabularInline):
    model = EventRound
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'fest', 'coordinator', 'date', 'registration_count')
    inlines = [EventRoundInline]
    
    def registration_count(self, obj):
        return obj.registrations.count()

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_name', 'event', 'current_round', 'attended')
    list_filter = ('event', 'current_round', 'attended')
    search_fields = ('name', 'email', 'team_name')

admin.site.register(Fest)
admin.site.register(Gallery)
admin.site.register(Feedback)
admin.site.register(TeamMember)