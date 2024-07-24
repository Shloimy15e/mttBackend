from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserSavedVideo
from users.models import UserVideoList
from videos.models import Video

User = get_user_model()

class VideoSerializer(serializers.ModelSerializer):
    """
    A serializer for the Video model.
    
    Returns:
        dict: Serialized data for the Video model fields.
    """
    
    class Meta:
        """
        Meta options for the VideoSerializer class.
        """
        model = Video
        fields = ["id", "video_id", "title", "topic", "subtopic", "likes"]

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

    
    


class UserVideoListSerializer(serializers.ModelSerializer):
    """
    A serializer for the UserVideoList model.

    Returns:
        dict: Serialized data for the UserVideoList model fields.
    """

    class Meta:
        """
        Meta options for the UserVideoListSerializer class.

        Returns:
            None
        """

        model = UserVideoList
        fields = [
            "id",
            "user",
            "list_id",
            "title",
            "description",
            "thumbnail",
            "created_at",
        ]

    def to_representation(self, instance):
        """
            Customize the representation of the UserVideoList model.
            Args:
                instance: The instance of the UserVideoList model to be serialized.
                Returns:
                    dict: Serialized data for the UserVideoList model fields.
        """
        data = super().to_representation(instance)
        data["list_id"] = instance.list_id
        data["title"] = instance.title
        data["description"] = instance.description
        data["thumbnail"] = instance.thumbnail
        data["created_at"] = instance.created_at
        return data
    
    def create(self, validated_data):
        """
            Create a new UserVideoList instance.
            Args:
                validated_data: The validated data to create the UserVideoList instance with.
                Returns:
                    UserVideoList: The created UserVideoList instance.
        """
        user = self.context["request"].user
        list_id = validated_data.pop("list_id")
        title = validated_data.pop("title")
        description = validated_data.pop("description")
        thumbnail = validated_data.pop("thumbnail")
        user_video_list, created = UserVideoList.objects.get_or_create(
            user=user,
            list_id=list_id,
            title=title,
            description=description,
            thumbnail=thumbnail,
        )
        if not created:
            raise serializers.ValidationError("Video list already exists.")
        return user_video_list