from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()

class UserLoginSerializer(serializers.ModelSerializer):
    """
    Serializer for the user login 
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

       