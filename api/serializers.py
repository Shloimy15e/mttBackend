from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserSavedVideo

User = get_user_model()


class UserSavedVideoSerializer(serializers.ModelSerializer):
    """
    A serializer for the UserSavedVideo model.

    Returns:
        dict: Serialized data for the UserSavedVideo model fields.
    """

    class Meta:
        """
        Meta options for the UserSavedVideoSerializer class.

        Returns:
            None
        """
        model = UserSavedVideo
        fields = ["id", "user", "video_id"]
        
    
