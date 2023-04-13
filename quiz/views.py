from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, QuizProfile, AttemptedQuestion, Category, SelectedChoice, Message, Announcement, Choice
from users.models import CustomUser
from operator import attrgetter
from django.forms import inlineformset_factory
from django.utils.timezone import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from .forms import QuestionForm, ChoiceInlineFormset, ChoiceForm
from django.core.exceptions import ObjectDoesNotExist
from itertools import groupby
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse, reverse_lazy
from django.contrib import messages
import time
from django.contrib.auth.hashers import make_password
import random
from django.views.generic import UpdateView, CreateView, DeleteView, ListView, DetailView, TemplateView
from django.core.mail import send_mail

# +++ Class Based Views 
class QuestionList(LoginRequiredMixin, ListView):
    def get(self, request):
        question = Question.objects.all().order_by('category', 'difficulty_level')
        question_group = {}
        for category, category_quizzes in groupby(question, key=attrgetter('category')):
            question_group[category] = {}
            for level, level_quizzes in groupby(category_quizzes, key=attrgetter('difficulty_level')):
                question_group[category][level] = list(level_quizzes)
        context = {'question_group' : question_group}
        return render(request, 'question/question.html', context)

class CategoryList(LoginRequiredMixin, ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'question/quiz_category.html'

class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'quiz/quiz_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_list'] = self.object.question_set.all()
        return context
    
class Leaderboard(LoginRequiredMixin, TemplateView):
    def get(self, request):
        top_quiz_profiles = QuizProfile.objects.order_by('-total_score')[:500]
        top_count = top_quiz_profiles.count()
        context = {
            'top_quiz_profiles': top_quiz_profiles,
            'total_count': top_count,
        }
        return render(request, 'leaderboard.html', context=context)
        
class Profile(TemplateView):
    template_name = 'profile/profile.html'

class EditProfile(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    fields = ["first_name", "last_name", "username", "gender", 'profile_pic']    
    template_name = 'profile/edit-profile.html'
    success_url = reverse_lazy('profile')

class MessageList(LoginRequiredMixin, ListView):
    model = Message
    context_object_name = "messages_list"
    template_name = "message/message.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sending'] = context['messages_list'].filter(sender=self.request.user)
        context['recieving'] = context['messages_list'].filter(recipient=self.request.user)
        context['sent'] = context['messages_list'].filter(sent=True).count()
        context['recieved'] = context['messages_list'].filter(recipient=self.request.user).count()
        return context
    
class MessageDetail(LoginRequiredMixin, DetailView):
    model = Message
    context_object_name = "message"
    template_name = "message/message-detail.html"    

class CreateMessage(LoginRequiredMixin, CreateView):
    model = Message
    template_name = 'message/create-message.html'
    success_url = reverse_lazy('messages')
    fields = ['recipient', 'message']
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super(CreateMessage, self).form_valid(form)
    
class DeleteMessage(LoginRequiredMixin, DeleteView):
    model = Message
    context_object_name = "message"
    template_name = 'message/delete-message.html'
    success_url = reverse_lazy('messages')
    
class AnnouncementList(LoginRequiredMixin, ListView):
    model = Announcement
    context_object_name = "announcements"
    template_name = "announcement/announcement.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement_list'] = context['announcements']
        context['announcements_total'] = context['announcements'].count()
        return context
    
class AnnouncementDetail(LoginRequiredMixin, DetailView):
    model = Announcement
    context_object_name = "announcement"
    template_name = "announcement/announcement-detail.html"

# +++ Function Based Views 
@login_required()
def submission_Result(request, attempted_question_pk):
    attempted_question = get_object_or_404(AttemptedQuestion, pk=attempted_question_pk)
    context = {
        'attempted_question': attempted_question,
    }
    return render(request, 'submission_result.html', context)   

def quiz(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    questions = category.question_set.all().order_by('created_at')
    question_list = list(enumerate(questions))
    num_questions = len(questions)
    score = 0

    if request.method == 'POST':
        for question in questions:
            selected_choice_id = request.POST.get(f'question-{question.id}')
            selected_choice = question.choice_set.get(pk=selected_choice_id)
            if selected_choice.is_correct:
                score += question.maximum_marks

        context = {
            'category': category,
            'questions': questions,
            'score': score,
        }
        return render(request, 'quiz.html', context)

    context = {
        'category': category,
        'question_list': question_list,
        'num_questions': num_questions
    }
    return render(request, 'question/quiz.html', context)


def loginView(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(email=email, password=password)
    
        if user != None:
            login(request, user)
            if user.is_superuser:
                return redirect("/admin/")
            else:
                return redirect(reverse('home_page'))
        else:
            messages.error(request, "Invalid credentials")
    else: 
        return render(request, 'account/login.html')
    return render(request, 'account/login.html')

def signupView(request):
    if request.method == 'POST':
        firstname = request.POST['fname']
        lastname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        gender = request.POST['gender']
        number = [x for x in range(100)]
        ran_num = ""
        for n in range(10):
            random_number = random.choice(number)
            ran_num += str(random_number)
        username = "user" + str(ran_num)
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account with that email already exist!")
            return redirect(reverse('signup'))
        elif len(firstname) <= 0:
            messages.error(request, "Fill in the required fields")
            return redirect(reverse('signup'))
        elif len(lastname) <= 0:
            messages.error(request, "Fill in the required fields")
            return redirect(reverse('signup'))
        else:
            try:
                hashed_password = make_password(password)
                user = CustomUser.objects.create(first_name=firstname, last_name=lastname, username=username, email=email, password=hashed_password, is_active=True)
                user.gender = gender
                user.save()
                messages.success(request, "Account successfully created!")
                numbers = [x for x in range(10)]
                verification_code = ""
                for i in range(5):
                    n = random.choice(numbers)
                    verification_code += str(n)
                
                request.session['email_sent'] = email
                request.session['verification_code'] = verification_code
                
                send_mail("Verification Code", verification_code, "ifeanyionyekwelu786@gmail.com", (email,))
                return redirect(reverse('verify_email'))
            except Exception as e:
                messages.error(request, str(e))
            else:
                messages.error(request, "Please fulfil all requirements!")
            
    return render(request, 'account/signup.html')

def verify_email(request):
    if request.method == 'POST':
        verification_code = request.POST.get('code')
        email_sent = request.session.get('email_sent')
        
        if email_sent is not None:
            if verification_code == str(request.session.get('verification_code')):
                try:
                    user =  CustomUser.objects.get(email=email_sent)
                    user.verified_email = True
                    user.save()
                    messages.success(request, "Email Address Verified Successfully!")
                    return redirect(reverse('login'))
                except CustomUser.DoesNotExist:
                    messages.error(request, "User does not exist!")
            else:
                messages.error(request, "Invalid verification code!")
        else:
            messages.error(request, "Invalid email address")
            
    return render(request, 'account/verify_email.html')

def error404(request, e):
    return render(request, 'error_404.html', {'page_title' : 'Error: Page not found'})

def error_500(request):
    return render(request, 'error_500.html', {'page_title': 'Error: Forbidden'})

def create_question(request):
    # create a new QuestionForm instance
    question_form = QuestionForm()
    # create a new ChoiceFormSet instance
    ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, formset=ChoiceInlineFormset, extra=4, max_num=4)
    choice_formset = ChoiceFormSet()

    if request.method == 'POST':
        # bind POST data to the form instances
        question_form = QuestionForm(request.POST, request.FILES)
        choice_formset = ChoiceFormSet(request.POST)

        if question_form.is_valid() and choice_formset.is_valid():
            # save the question instance
            question = question_form.save()
            # bind the question instance to the choice formset
            choice_instances = choice_formset.save(commit=False)
            for choice in choice_instances:
                choice.question = question
                choice.save()
            # redirect to some page
            return redirect('some-page')

    # render the template with the forms
    context = {
        'question_form': question_form,
        'choice_formset': choice_formset,
    }
    return render(request, 'question/create_question.html', context)