from django.contrib import admin
from .models import Question, Choice, Category, Announcement, Message, QuizProfile, ContactMessage
from .forms import QuestionForm, ChoiceForm, ChoiceInlineFormset, MessageForm

class ChoiceInline(admin.TabularInline):
    model = Choice
    can_delete = False
    max_num = Choice.MAX_CHOICE_COUNT
    min_num = Choice.MAX_CHOICE_COUNT
    form = ChoiceForm
    formset = ChoiceInlineFormset
    
class QuestionAdmin(admin.ModelAdmin):
    model = Question
    inlines = (ChoiceInline,)
    list_display = ['author', 'category', 'question', 'image', 'maximum_marks', 'difficulty_level', 'has_timer', 'created_at', 'updated_at']
    search_fields = ['category', 'author', 'choices__choice_text', 'question']
    actions = None
    form = QuestionForm
    
class AnnouncementAdmin(admin.ModelAdmin):
    model = Announcement
    list_display = ['title', 'created_at', 'updated_at']

class QuizProfileAdmin(admin.ModelAdmin):
    model = QuizProfile
    list_display = ['user', 'total_score']
    
class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ['sender', 'recipient', 'message', 'sent', 'received', 'created_at', 'updated_at']
    form = MessageForm

class ContactMessageAdmin(admin.ModelAdmin):
    model = ContactMessage
    list_display = ['first_name', 'last_name', 'email_address', 'phone_number', 'message', 'created_at']

admin.site.register(Category)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(QuizProfile, QuizProfileAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)