from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, QuizProfile, Category, Message, Announcement, Choice, QuizResult
from users.models import CustomUser
from django.db.models import Q, Count
from operator import attrgetter
from chartjs.views.lines import BaseLineChartView
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
from urllib.parse import urlencode
from django.conf import settings
from django.contrib.auth.hashers import make_password
import random
from random import shuffle
from django.views import View
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
        context = {'question_group': question_group}
        return render(request, 'question/question.html', context)


@login_required
def category_list(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'question/category_list.html', context)


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
        context['sending'] = context['messages_list'].filter(
            sender=self.request.user)
        context['recieving'] = context['messages_list'].filter(
            recipient=self.request.user)
        context['sent'] = context['messages_list'].filter(sent=True).count()
        context['recieved'] = context['messages_list'].filter(
            recipient=self.request.user).count()
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

    def get_queryset(self):
        # Get the user's signup date
        signup_date = self.request.user.date_joined

        # Filter announcements created after the user's signup date
        queryset = super().get_queryset().filter(created_at__gte=signup_date)

        return queryset

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


@login_required
def submission_Result(request, attempted_question_pk):
    attempted_question = get_object_or_404(
        AttemptedQuestion, pk=attempted_question_pk)
    context = {
        'attempted_question': attempted_question,
    }
    return render(request, 'submission_result.html', context)


# def play_quiz(request, category_id):
#     category = Category.objects.get(pk=category_id)
#     questions = list(category.question_set.all())
#     random.shuffle(questions)
#     num_questions = len(questions)
#     current_question_index = int(request.GET.get('question_index', 0))

#     # Get user's quiz profile for the category
#     quiz_profile, created = QuizProfile.objects.get_or_create(
#         user=request.user, category=category)

#     if request.method == 'POST':
#         answer = request.POST.get('answer')
#         if answer:
#             request.session['answers'][current_question_index] = answer
#         if 'next' in request.POST:
#             current_question_index += 1
#         elif 'prev' in request.POST:
#             current_question_index -= 1
#     if 'answers' not in request.session:
#         request.session['answers'] = {}

#     # Save the quiz result when all questions are answered
#     if current_question_index == num_questions:
#         score = 0
#         for i, question in enumerate(questions):
#             if str(i) in request.session['answers']:
#                 if question.is_correct(request.session['answers'][str(i)]):
#                     score += 1
#         total_score = (score / num_questions) * 100
#         quiz_profile.total_score = total_score
#         quiz_profile.save()

#     # Get user's quiz history
#     quiz_history = QuizProfile.objects.filter(user=request.user)

#     context = {
#         'questions': questions,
#         'num_questions': num_questions,
#         'category': category,
#         'current_question_index': current_question_index,
#         'current_question_number': current_question_index + 1,
#         'answers': request.session.get('answers', {}),
#         'quiz_profile': quiz_profile,
#         'quiz_history': quiz_history
#     }

#     return render(request, 'question/quiz.html', context)

class PlayQuizView(View):
    template_name = 'question/quiz.html'
    questions_limit = 15  # Number of questions to show

    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        questions = list(Question.objects.filter(category=category))
        shuffle(questions)
        questions = questions[:self.questions_limit]

        # Retrieve previously selected answers from session
        answers = request.session.get('answers', {})

        return render(request, self.template_name, {
            'category': category,
            'questions': questions,
            'total_points': 150,
            'answers': answers,
        })

    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        questions = list(Question.objects.filter(category=category))
        shuffle(questions)
        questions = questions[:self.questions_limit]
        total_points = 150

        user_profile = QuizProfile.objects.get(user=request.user)

        # Retrieve previously selected answers from session
        answers = request.session.get('answers', {})

        for question in questions:
            answer = request.POST.get(f"question_{question.id}")

            if answer:
                choices = list(question.choices.all())
                correct_choices = list(filter(lambda c: c.is_correct, choices))

                if len(correct_choices) != 1:
                    raise ValueError(
                        f"Question {question.id} has no or multiple correct choices")

                if answer == str(correct_choices[0].id):
                    user_profile.total_score += 20
                    answers[question.id] = 1
                else:
                    messages.warning(
                        request, f"You got question {question.id} wrong")
                    answers[question.id] = 0
            else:
                messages.warning(
                    request, f"You did not answer question {question.id}")
                total_points -= 20
                answers[question.id] = 0

        user_profile.total_score += total_points
        user_profile.save()

        # Store updated answers in the session
        request.session['answers'] = answers

        results_url = reverse('quiz:results', args=[category_id])
        return redirect(results_url)


@login_required
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


def results(request, category_id):
    category = Category.objects.get(pk=category_id)
    questions = list(category.question_set.all())
    num_questions = len(questions)
    answers = request.session.get('answers', {})
    score = sum(answers.values())
    percentage_score = (score / num_questions) * 100

    # Create the share link with registration URL
    # Replace with your registration URL
    base_url = 'http://127.0.0.1:8000/signup'

    share_data = {
        'category_id': category_id,
        'score': score,
        'percentage_score': percentage_score,
    }
    share_link = f'{base_url}?{urlencode(share_data)}'

    context = {
        'category': category,
        'num_questions': num_questions,
        'score': score,
        'percentage_score': percentage_score,
        'share_link': share_link,
        'base_url': base_url
    }
    return render(request, 'question/results.html', context)


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
                messages.error(
                    request, "An account with that email already exist!")
                return redirect(reverse('quiz:signup'))
            elif len(firstname) <= 0:
                messages.error(request, "Fill in the required fields")
                return redirect(reverse('signup'))
            elif len(lastname) <= 0:
                messages.error(request, "Fill in the required fields")
                return redirect(reverse('quiz:signup'))
            else:
                try:
                    hashed_password = make_password(password)
                    user = CustomUser.objects.create(
                        first_name=firstname, last_name=lastname, username=username, email=email, password=hashed_password, is_active=True)
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
                    send_message = f"Welcome {firstname} {lastname} your account was created successfully\n use this code to verify your account\n\n{verification_code}"
                    send_mail("Verification Code", send_message,
                              "quizzer.sup@gmail.com", (email,))

                    return redirect('quiz:verify_email')
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
                    user = CustomUser.objects.get(email=email_sent)
                    user.verified_email = True
                    user.save()
                    messages.success(
                        request, "Email Address Verified Successfully!")
                    return redirect(reverse('quiz:login'))
                except CustomUser.DoesNotExist:
                    messages.error(request, "User does not exist!")
            else:
                messages.error(request, "Invalid verification code!")
        else:
            messages.error(request, "Invalid email address")

    return render(request, 'account/verify_email.html')


def error404(request, e):
    return render(request, 'error_404.html', {'page_title': 'Error: Page not found'})


def error_500(request):
    return render(request, 'error_500.html', {'page_title': 'Error: Page not found'})


@transaction.atomic
def create_question(request):
    category_form = CategoryForm()
    question_form = QuestionForm()
    ChoiceFormSet = inlineformset_factory(
        Question, Choice, form=ChoiceForm, formset=ChoiceInlineFormset, extra=4, max_num=4)
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

                quiz_profile, created = QuizProfile.objects.get_or_create(
                    user=request.user, category=category)
                quiz_profile.question = question
                quiz_profile.save()

                return redirect('category')

    context = {
        'category_form': category_form,
        'question_form': question_form,
        'choice_formset': choice_formset,
    }
    return render(request, 'question/create_question.html', context)


def quiz_analytics(request):
    categories = Category.objects.all()

    quiz_data = []
    for category in categories:
        quiz_profiles = QuizProfile.objects.filter(category=category)

        quiz_stats = []
        for quiz_profile in quiz_profiles:
            results = QuizResult.objects.filter(quiz_profile=quiz_profile)
            num_times_taken = results.count()
            num_failed = results.filter(passed=False).count()

            quiz_stats.append({
                'times_taken': num_times_taken,
                'num_failed': num_failed
            })

            quiz_profile.times_taken = num_times_taken
            quiz_profile.has_failed = num_failed > 0
            quiz_profile.save()

        quiz_data.append({
            'category': category.category,
            'quizzes': quiz_stats
        })

    return render(request, 'question/quiz_analytics.html', {
        'quiz_data': quiz_data
    })


class QuizAnalyticsView(BaseLineChartView):
    def get_labels(self):
        return [quiz['category'] for quiz in self.kwargs['quiz_data']]

    def get_providers(self):
        return ['Times Taken', 'Failed']

    def get_data(self):
        datasets = []


def quiz_taken(request):
    quiz_history = QuizProfile.objects.filter(
        user=request.user).order_by('-id')
    context = {'quiz_history': quiz_history}
    return render(request, 'question/quiz_taken.html', context)


@login_required
def quiz_created(request):
    user = request.user
    categories = Category.objects.filter(author=user)
    quiz_data = []

    for category in categories:
        quizzes = Quiz.objects.filter(category=category)
        quiz_profiles = QuizProfile.objects.filter(quiz__in=quizzes)
        quiz_data.append({
            'category': category,
            'num_quizzes': len(quizzes),
            'quiz_profiles': quiz_profiles
        })

    context = {
        'quiz_data': quiz_data
    }
    return render(request, 'question/quiz_created.html', context)
