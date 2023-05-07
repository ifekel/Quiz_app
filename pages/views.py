from django.shortcuts import render, redirect
from quiz.models import Announcement, ContactMessage, Question, Message, QuizProfile
from django.views.generic import UpdateView, CreateView, DeleteView, ListView, DetailView, TemplateView
from django.contrib import messages
from django.db.models import Count
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
import base64

# Create your views here.


def home(request):
    if request.user.is_superuser == True:
        return redirect('/admin')
    else:
        if request.user.is_authenticated:
            messages = Message.objects.all().filter(recipient=request.user)
            total_messages = len(messages)
            quiz_created_by_user = Question.objects.all().filter(author=request.user)
            total_quiz_created_by_user = len(quiz_created_by_user)
            quiz_profile = QuizProfile.objects.get(user=request.user)

            # Get quiz data for the bar chart
            quiz_categories = QuizProfile.objects.filter(user=request.user).values(
                'category__category').annotate(count=Count('category__category')).order_by('-count')
            categories = [category['category__category']
                          for category in quiz_categories]
            counts = [category['count'] for category in quiz_categories]

            # Generate the bar chart
            plt.barh(categories, counts)
            plt.xlabel('Number of Participants')
            plt.ylabel('Quiz Category')
            plt.title('Most Participants')

            chart_image = BytesIO()
            plt.savefig(chart_image, format='png')
            chart_image.seek(0)

            # Pass the chart image to the template context
            context = {
                'quiz_profile': 'quiz_profile',
                'total_message': total_messages,
                'total_quiz_created_by_user': total_quiz_created_by_user,
                'chart_image': base64.b64encode(chart_image.getvalue()).decode('utf8')
            }
            return render(request, 'index.html', context)
        return render(request, 'index.html')


class AboutPageView(TemplateView):
    template_name = 'about.html'


def ContactPageView(request):
    if request.method == "POST":
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        email = request.POST.get('email')
        phoneNumber = request.POST.get('phoneNumber')
        message = request.POST.get('message')

        error_message = "Please fill all fields!"

        if len(firstName) <= 0:
            messages.error(request, error_message)
            return redirect('contact_page')
        elif len(lastName) <= 0:
            messages.error(request, error_message)
            return redirect('contact_page')
        elif ContactMessage.objects.filter(email_address=email).exists():
            messages.error(request, "Sorry, you have already sent a message.")
            return redirect('contact_page')
        elif len(phoneNumber) < 7:
            messages.error(request, "Enter a valid phone number")
            return redirect('contact_page')
        elif len(message) <= 0:
            messages.error(request, error_message)
            return redirect('contact_page')
        else:
            contact = ContactMessage.objects.create(
                first_name=firstName, last_name=lastName, email_address=email, phone_number=phoneNumber, message=message)
            contact.save()
            messages.success(request, "Your message was sent successfully!")

        return render(request, "contact.html")
    else:
        return render(request, "contact.html")
