from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import UserLoginSerializer


# Create your views here.

class UserRegisterView(APIView):
    """
    A view for registering a user
    """
    def post(self, request):
        """
        A post method for registering a user
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    A view for logging in a user
    """

    def post(self, request):
        """
        A post method for logging in a user
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        serialized_user = UserLoginSerializer(user).data

        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)
        return Response(
            {
                "access": access_token,
                "refresh": str(refresh_token),
                "user": serialized_user,
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutView(APIView):
    """
    A view for user logout using jwt tokens.
    """

    def post(self, request):
        """
        Handle user logout.
        """
        try:
            refresh_token = request.data["refreshToken"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": "Succesful"}, status=status.HTTP_205_RESET_CONTENT)
