from django import forms
from django.utils.translation import gettext as _
from .models import Question, Choice, Category, Message


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'image', 'difficulty']

    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))
    image = forms.ImageField(required=False)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'message']
        
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 80})
        }
    
class ChoiceInlineFormset(forms.BaseInlineFormSet):
    def clean(self):
        super(ChoiceInlineFormset, self).clean()
        
        correct_choices_count = 0
        for form in self.forms:
            if not form.is_valid():
                return
            
            if form.cleaned_data and form.cleaned_data.get('is_correct') is True:
                correct_choices_count += 1

        try:
            assert correct_choices_count == Question.ALLOWED_NUMBER_OF_CORRECT_CHOICES
        except AssertionError:
            raise forms.ValidationError(_('Exactly one correct choice is allowed.'))