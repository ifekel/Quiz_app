from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'
    
    def ready(self):
        from .models import QuizProfile
        # connect signal handlers
        from . import signals
        