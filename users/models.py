from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class UserVideoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list_id = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    thumbnail = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"


class ListVideo(models.Model):
    list_id = models.ForeignKey(UserVideoList, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.video_id}"


class UserSavedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.video_id}"

