# Generated by Django 5.0.7 on 2024-08-05 13:21

import django.db.models.deletion
from django.db import migrations, models

def create_topics_from_video_topics(apps, schema_editor):
    Topic = apps.get_model('topics', 'Topic')
    Video = apps.get_model('videos', 'Video')
    
    topic_names = Video.objects.values_list('topic', flat=True).distinct()
    
    for topic_name in topic_names:
        if not Topic.objects.filter(name=topic_name).exists():
            Topic.objects.create(name=topic_name)

def set_video_topic_foreign_keys(apps, schema_editor):
    Video = apps.get_model('videos', 'Video')
    Topic = apps.get_model('topics', 'Topic')

    for video in Video.objects.all():
        topic, created = Topic.objects.get_or_create(name=video.topic)
        video.topic_temp = topic
        video.save()
        
        
class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0001_initial'),
        ('videos', '0003_alter_video_description_alter_video_title'),
    ]

    operations = [
        migrations.AddField(
            model_name="video",
            name="topic_temp",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='videos_temp', to='topics.Topic'),
        ),
        migrations.RunPython(create_topics_from_video_topics),
        migrations.RunPython(set_video_topic_foreign_keys),
        
        migrations.RemoveField(
            model_name="video",
            name="topic",
        ),
        migrations.RenameField(
            model_name="video",
            old_name="topic_temp",
            new_name="topic",
        )
    ]