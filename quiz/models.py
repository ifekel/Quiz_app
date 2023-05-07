from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from model_utils.models import TimeStampedModel
import uuid
import random


class Category(models.Model):
    easy = 'Easy'
    medium = 'Medium'
    hard = 'Hard'
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.CharField(max_length=500)
    difficulty = models.CharField(max_length=50, choices=(
        (easy, easy), (medium, medium), (hard, hard)), default=easy)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} -> {self.difficulty}"


class Question(models.Model):
    DIFFICULTY_LEVELS = (
        ("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard"))
    ALLOWED_NUMBER_OF_CORRECT_CHOICES = 1

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.TextField()
    image = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} -> {self.question}"


class Choice(models.Model):
    MAX_CHOICE_COUNT = 4
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='choices')
    is_correct = models.BooleanField(
        _('Is this the correct answer'), default=False)
    choice_text = models.TextField(_('Choice Text'))

    def __str__(self):
        return self.choice_text


class QuizProfile(TimeStampedModel):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    total_score = models.DecimalField(
        _('Total Score'), default=0, decimal_places=2, max_digits=10)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    good_performance = models.PositiveIntegerField(default=0)
    bad_performance = models.PositiveIntegerField(default=0)
    times_taken = models.PositiveIntegerField(default=0)
    has_failed = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def start_quiz(self):
        self.start_time = timezone.now()
        self.save()

    def end_quiz(self):
        self.end_time = timezone.now()
        self.save()

    def get_duration(self):
        if self.start_time and self.end_time:
            return timesince(self.start_time, self.end_time)
        else:
            return '-'

    def __str__(self):
        return f'<QuizProfile: user={self.user}>'


class QuizResult(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quiz_profile = models.ForeignKey(QuizProfile, on_delete=models.CASCADE)
    score = models.DecimalField(
        _('Score'), decimal_places=2, max_digits=10)
    passed = models.BooleanField(_('Passed'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.quiz_profile.question}'


class Announcement(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('announcement_detail', args=[str(self.id)])


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    sender = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="Sender")
    recipient = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="Reciever")
    message = models.TextField()
    sent = models.BooleanField(default=True)
    received = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"Sent from {self.sender.username} to {self.recipient.username}"

    def get_absolute_url(self):
        return reverse('message_detail', args=[str(self.id)])


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email_address}"
