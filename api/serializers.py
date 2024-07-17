from rest_framework import serializers
from users.models import UserSavedVideo
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSavedVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSavedVideo
        fields = ['id', 'user', 'video_id', 'title', 'description', 'thumbnail_url']
