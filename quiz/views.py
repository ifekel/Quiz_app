from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, QuizProfile, AttemptedQuestion, Category, SelectedChoice, Message, Announcement, Choice
from users.models import CustomUser
from django.db.models import Q
from operator import attrgetter
from django.forms import inlineformset_factory
from django.utils.timezone import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404, HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from .forms import QuestionForm, ChoiceInlineFormset, ChoiceForm, CategoryForm
from django.db import transaction
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
    login_url = 'login'
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
    login_url = 'login'
    context_object_name = 'categories'
    template_name = 'question/quiz_category.html'
    
class SearchResultListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'question/search_result.html'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        return Category.objects.filter(
            Q(category__icontains=query) | Q(category__icontains=query)
        )
    
class Leaderboard(LoginRequiredMixin, TemplateView):
    login_url = 'login'
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
    login_url = 'login'
    fields = ["first_name", "last_name", "username", "gender"]    
    template_name = 'profile/edit-profile.html'
    success_url = reverse_lazy('profile')

class MessageList(LoginRequiredMixin, ListView):
    model = Message
    login_url = 'login'
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
    login_url = 'login'
    template_name = "message/message-detail.html"    

class CreateMessage(LoginRequiredMixin, CreateView):
    model = Message
    login_url = 'login'
    template_name = 'message/create-message.html'
    success_url = reverse_lazy('messages')
    fields = ['recipient', 'message']
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super(CreateMessage, self).form_valid(form)
    
class DeleteMessage(LoginRequiredMixin, DeleteView):
    model = Message
    login_url = 'login'
    context_object_name = "message"
    template_name = 'message/delete-message.html'
    success_url = reverse_lazy('messages')
    
class AnnouncementList(LoginRequiredMixin, ListView):
    model = Announcement
    login_url = 'login'
    context_object_name = "announcements"
    template_name = "announcement/announcement.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement_list'] = context['announcements']
        context['announcements_total'] = context['announcements'].count()
        return context
    
class AnnouncementDetail(LoginRequiredMixin, DetailView):
    model = Announcement
    login_url = 'login'
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

@login_required()
def quiz(request, category_id, page=1):
    category = get_object_or_404(Category, id=category_id)
    questions = category.question_set.all().order_by('created_at')
    paginator = Paginator(questions, 1)  # Show 1 question per page
    page_obj = paginator.get_page(page)
    num_questions = len(questions)
    score = 0

    if request.method == 'POST':
        for question in page_obj:
            selected_choice_id = request.POST.get(f'question-{question.id}')
            selected_choice = question.choice_set.get(pk=selected_choice_id)
            if selected_choice.is_correct:
                score += question.maximum_marks

        # Update QuizProfile score
        quiz_profile = QuizProfile.objects.get(user=request.user)
        quiz_profile.total_score += score
        quiz_profile.save()

        context = {
            'category': category,
            'page_obj': page_obj,
            'score': score,
            'num_questions': num_questions,
            'quiz_profile': quiz_profile,
        }
        return render(request, 'question/quiz.html', context)

    context = {
        'category': category,
        'page_obj': page_obj,
        'num_questions': num_questions,
    }
    return render(request, 'question/quiz.html', context)

@login_required()
def quiz_results(request):
    categories = Category.objects.filter(author=request.user)
    quiz_results = []

    for category in categories:
        questions = category.question_set.all()
        results = {}

        for question in questions:
            quiz_profiles = QuizProfile.objects.filter(question=question)
            for quiz_profile in quiz_profiles:
                user = quiz_profile.user.username
                score = quiz_profile.total_score
                if user in results:
                    results[user] += score
                else:
                    results[user] = score

        quiz_results.append({'category': category, 'results': results})

    if request.GET.get('pdf'):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="quiz_results.pdf"'

        buffer = BytesIO()

        p = canvas.Canvas(buffer)

        for quiz_result in quiz_results:
            p.drawString(100, 800, quiz_result['category'].category)

            y = 750
            for user, score in quiz_result['results'].items():
                p.drawString(150, y, f"{user}: {score}")
                y -= 20

            p.showPage()

        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        response.write(pdf)

        return response

    context = {
        'quiz_results': quiz_results,
    }

    return render(request, 'question/quiz_results.html', context)


def loginView(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
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
    if request.user.is_authenticated:
        return redirect('/')
    else:
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
    return render(request, 'error_500.html', {'page_title': 'Error: Page not found'})

@transaction.atomic
def create_question(request):
    category_form = CategoryForm()
    question_form = QuestionForm()
    ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, formset=ChoiceInlineFormset, extra=4, max_num=4)
    choice_formset = ChoiceFormSet()

    if request.method == 'POST':
        if 'create_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category = category_form.save(commit=False)
                category.author = request.user
                category.save()
                return redirect('create_question', category_id=category.id)

        elif 'create_question' in request.POST:
            category_id = request.POST.get('category')
            category = Category.objects.get(id=category_id)
            question_form = QuestionForm(request.POST, request.FILES)
            choice_formset = ChoiceFormSet(request.POST)

            if question_form.is_valid() and choice_formset.is_valid():
                question = question_form.save(commit=False)
                question.category = category
                question.save()

                choice_instances = choice_formset.save(commit=False)
                for choice in choice_instances:
                    choice.question = question
                    choice.save()

                quiz_profile, created = QuizProfile.objects.get_or_create(user=request.user, category=category)
                quiz_profile.question = question
                quiz_profile.save()

                return redirect('category')

    context = {
        'category_form': category_form,
        'question_form': question_form,
        'choice_formset': choice_formset,
    }
    return render(request, 'question/create_question.html', context)
