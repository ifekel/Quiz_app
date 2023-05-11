from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import QuizProfile


@receiver(post_save, sender=get_user_model())
def create_quiz_profile(sender, instance, created, **kwargs):
    if created:
        QuizProfile.objects.create(user=instance)
