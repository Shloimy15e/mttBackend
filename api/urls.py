from django.urls import path
from django.urls import include

from rest_framework.routers import DefaultRouter

from .views import UserSavedVideoViewSet


app_name = "api"

router = DefaultRouter()
router.register(r"user-saved-videos", UserSavedVideoViewSet, basename="user-saved-videos")


urlpatterns = [
    path("", include(router.urls)),
]
