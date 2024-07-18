from django.contrib.auth import authenticate
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


from .serializers import UserSavedVideoSerializer


# Create your views here.
class UserSavedVideoViewSet(ModelViewSet):
    """
    A viewset for the UserSavedVideo model.
    """

    serializer_class = UserSavedVideoSerializer
    queryset = UserSavedVideoSerializer.Meta.model.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        """
        Create a new UserSavedVideo instance.
        """
        try:
            data = request.data.copy()
            data["user"] = request.user.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            if serializer.data.get("user") != request.user.id:
                return Response(
                    {"error": "User does not match"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Check if video_id + user.id match is already in the UserSavedVideo table
            if self.queryset.filter(
                video_id=serializer.data.get("video_id"), user=request.user
            ).exists():
                return Response(
                    {"error": "Video already saved"}, status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, *args, **kwargs):
        """
        List all UserSavedVideo instances for the authenticated user.
        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            Response: A response object with the serialized data.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single UserSavedVideo instance for the authenticated user.
        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            Response: A response object with the serialized data.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        """
        Delete a UserSavedVideo instance for the authenticated user.
        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
                Response: A response object with the serialized data.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
