from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import UserSavedVideoSerializer
from .serializers import VideoSerializer
from .serializers import TopicSerializer
from .serializers import SubtopicSerializer


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = None

class VideoViewSet(ModelViewSet):
    """
    A viewset for the Video model.
    """

    serializer_class = VideoSerializer
    queryset = VideoSerializer.Meta.model.objects.all()
    permission_classes = [IsAdminUser | AllowAny]

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "update_and_create_bulk",
            "delete_all",
        ]:
            return [IsAdminUser()]
        return [AllowAny()]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "topic": ["exact"],
        "video_id": ["exact"],
        "subtopic": ["exact"],
        "likes": ["exact", "gte", "lte", "range"],
        "views": ["exact", "gte", "lte", "range"],
    }
    ordering_fields = ["likes", "views", "publishedAt"]

    def create(self, request, *args, **kwargs):
        """
        create one or more video instances.
        """
        try:
            videos = request.data.get("videos")
            created_videos = []
            errors = []
            for video in videos:
                try:
                    serializer = self.get_serializer(data=video)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    created_videos.append(serializer.data)
                except Exception as e:
                    errors.append({"video": video, "error": str(e)})

            if errors and created_videos:
                return Response(
                    {"created_videos": created_videos, "errors": errors},
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )
            elif created_videos:
                return Response(
                    {"created_videos": created_videos}, status=status.HTTP_201_CREATED
                )
            else:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="update-and-create-bulk")
    def update_and_create_bulk(self, request, *args, **kwargs):
        """
        Update or create multiple videos in bulk.
        Iterate over the videos list and if video_id matches an existing video, update the video
        If video_id does not match an existing video, create a new video.
        """
        try:
            videos = request.data.get("videos")
            created_videos = []
            updated_videos = []
            errors = []
            for video in videos:
                if video_id := video.get("video_id"):
                    try:
                        existing_video = self.queryset.get(video_id=video_id)
                        serializer = self.get_serializer(
                            existing_video, data=video, partial=True
                        )
                        if serializer.is_valid():
                            self.perform_update(serializer)
                            updated_videos.append(serializer.data)
                        elif (
                            "Video matching query does not exist." in serializer.errors
                        ):
                            serializer = self.get_serializer(data=video)
                            if serializer.is_valid():
                                self.perform_create(serializer)
                                created_videos.append(serializer.data)
                            else:
                                errors.append(
                                    {"video": video, "error": serializer.errors}
                                )
                        else:
                            errors.append({"video": video, "error": serializer.errors})
                    except Exception as e:
                        errors.append({"video": video, "error": str(e)})
                else:
                    errors.append({"video": video, "error": "video_id is required"})

            if errors and created_videos and updated_videos:
                return Response(
                    {
                        "created_videos": created_videos,
                        "updated_videos": updated_videos,
                        "errors": errors,
                    },
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )
            elif created_videos and updated_videos:
                return Response(
                    {
                        "created_videos": created_videos,
                        "updated_videos": updated_videos,
                    },
                    status=status.HTTP_201_CREATED,
                )
            elif errors and created_videos:
                return Response(
                    {"created_videos": created_videos, "errors": errors},
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )
            elif errors and updated_videos:
                return Response(
                    {"updated_videos": updated_videos, "errors": errors},
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )
            elif created_videos:
                return Response(
                    {"created_videos": created_videos}, status=status.HTTP_201_CREATED
                )
            elif updated_videos:
                return Response(
                    {"updated_videos": updated_videos}, status=status.HTTP_200_OK
                )
            else:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        List all videos.
        """
        try:
            paginator = CustomLimitOffsetPagination()
            queryset = self.filter_queryset(self.get_queryset())
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single video by id or video_id.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Try to get the object by video_id first
        video_id = self.kwargs.get("pk")
        try:
            obj = queryset.get(video_id=video_id)
        except queryset.model.DoesNotExist:
            # If video_id lookup fails, try with pk (id)
            try:
                obj = queryset.get(pk=video_id)
            except queryset.model.DoesNotExist as e:
                raise NotFound(f"No video found with id or video_id: {video_id}") from e

        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Update a video by id or video_id.
        Requires admin user.
        """
        try:
            partial = kwargs.pop("partial", False)
            # Try to get the object by id first
            try:
                instance = self.get_object()
            except Exception:
                # If not found, try to get the object by video_id
                video_id = request.data.get("video_id") or kwargs.get("pk")
                instance = self.queryset.get(video_id=video_id)

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a video by id or video_id.
        """
        try:
            if video_id := request.query_params.get("video_id"):
                instance = self.queryset.filter(
                    video_id=video_id, user=request.user
                ).first()
            else:
                instance = self.get_object()
            if not instance:
                return Response(
                    {"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND
                )

            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["delete"], detail=False, url_path="delete-all")
    def delete_all(self, request):
        """
        Delete all videos.
        """
        try:
            self.queryset.all().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TopicViewSet(ModelViewSet):
    """
    A viewset for the Topic model.
    """
    serializer_class = TopicSerializer
    queryset = TopicSerializer.Meta.model.objects.all()
    permission_classes = [IsAdminUser | AllowAny]
    
    def get_permissions(self):
        return [AllowAny()] if self.action in ["list", "retrieve"] else [IsAdminUser()]
    
    def list(self, request, *args, **kwargs):
        """
        List all topics.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single topic by id.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request, *args, **kwargs):
        """
        Create a new topic.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, *args, **kwargs):
        """
        Update a topic by id.
        """
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        """
        Delete a topic by id.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class SubtopicViewSet(ModelViewSet):
    """
    A viewset for the Subtopic model.
    """
    serializer_class = SubtopicSerializer
    queryset = SubtopicSerializer.Meta.model.objects.all()
    permission_classes = [IsAdminUser | AllowAny]

    def get_permissions(self):
        return [AllowAny()] if self.action in ["list", "retrieve"] else [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        """
        List all subtopics.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single subtopic by id.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request, *args, **kwargs):
            """
            Create a new subtopic.
            """
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    def update(self, request, *args, **kwargs):
                """
                Update a subtopic by id.
                """
                try:
                    partial = kwargs.pop("partial", False)
                    instance = self.get_object()
                    serializer = self.get_serializer(instance, data=request.data, partial=partial)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)
                    return Response(serializer.data)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
                """
                Delete a subtopic by id.
                """
                try:
                    instance = self.get_object()
                    self.perform_destroy(instance)
                    return Response(status=status.HTTP_204_NO_CONTENT)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
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
