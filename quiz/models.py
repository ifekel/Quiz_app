from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from model_utils.models import TimeStampedModel
import uuid
import random


class Category(models.Model):
    category = models.CharField(max_length=500)
    
    def __str__(self):
        return self.category
    
class Question(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    ALLOWED_NUMBER_OF_CORRECT_CHOICES = 1
    DIFFICULTY = (('Easy', 'Easy'), ('Regular', 'Regular'), ('Hard', 'Hard'))
    
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    question = models.TextField()
    maximum_marks = models.DecimalField(default=4, decimal_places=2, max_digits=6)
    difficulty_level = models.CharField(max_length=100, choices=DIFFICULTY, default=1)
    image = models.ImageField(blank=True, null=True)
    has_timer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.category} -> {self.question} -> {self.difficulty_level}"
    
class Choice(models.Model):
    MAX_CHOICE_COUNT = 4
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(_('Is this the correct answer'), default=False)
    choice_text = models.TextField(_('Choice Text'))
    
    def __str__(self):
        return self.choice_text
    
class QuizProfile(TimeStampedModel):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    total_score = models.DecimalField(_('Total Score'), default=0, decimal_places=2, max_digits=10)

    def __str__(self):
        return f'<QuizProfile: user={self.user}>'

    def get_new_question(self):
        used_questions_pk = AttemptedQuestion.objects.filter(quiz_profile=self).values_list('question__pk', flat=True)
        remaining_questions = Question.objects.exclude(pk__in=used_questions_pk)
        if not remaining_questions.exists():
            return
        return random.choice(remaining_questions)

    def create_attempt(self, question):
        attempted_question = AttemptedQuestion(question=question, quiz_profile=self)
        attempted_question.save()

    def evaluate_attempt(self, attempted_question, selected_choice):
        if attempted_question.question_id != selected_choice.question_id:
            return

        attempted_question.selected_choice = selected_choice
        if selected_choice.is_correct is True:
            attempted_question.is_correct = True
            attempted_question.marks_obtained = attempted_question.question.maximum_marks

        attempted_question.save()
        self.update_score()

    def update_score(self):
        marks_sum = self.attempts.filter(is_correct=True).aggregate(
            models.Sum('marks_obtained'))['marks_obtained__sum']
        self.total_score = marks_sum or 0
        self.save()
    
class AttemptedQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    quiz_question = models.ForeignKey(QuizProfile, on_delete=models.CASCADE, related_name='attempts')
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(_('Was this attempt correct?'), default=False)
    marks_obtained = models.DecimalField(_('Marks Obtained'), default=0, decimal_places=2, max_digits=6)

class SelectedChoice(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Selected choice')
        verbose_name_plural = _('Selected choiced')
        
    def __str__(self):
        return f"{self.user.username} - {self.question.question} - {self.choice.question}"
    
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
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="Sender")
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="Reciever")
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