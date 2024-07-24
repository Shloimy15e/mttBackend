from django.db import models

# Create your models here.
class Video(models.Model):
    """
    A model representing a video.
    
    Attributes:
        video_id (str): The unique identifier for the video.
        title (str): The title of the video.
        topic (str): The topic of the video.
        subtopic (str): The subtopic of the video.
        likes (int): The number of likes for the video.

    Methods:
        __str__: Returns a string representation of the video.
    """
    video_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=50)
    subtopic = models.CharField(max_length=50, blank=True)
    likes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.topic}"
