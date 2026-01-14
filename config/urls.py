from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from api.views import (
    EventViewSet, FeedbackViewSet, GalleryViewSet, ScheduleViewSet,
    ParticipantViewSet, FestViewSet, UserViewSet, TeamMemberViewSet, EventRoundViewSet, current_user
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'rounds', EventRoundViewSet)
router.register(r'fests', FestViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'gallery', GalleryViewSet)
router.register(r'participants', ParticipantViewSet, basename='participants')
router.register(r'users', UserViewSet)
router.register(r'team', TeamMemberViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/user/me/', current_user, name='current_user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)