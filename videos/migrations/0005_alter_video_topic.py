# Generated by Django 5.0.7 on 2024-08-05 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0003_alter_video_description_alter_video_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='topic',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='video',
            name='subtopic',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
