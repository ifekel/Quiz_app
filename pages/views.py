from django.shortcuts import render, redirect
from quiz.models import Announcement, ContactMessage, Question, Message, QuizProfile, Category
from django.views.generic import UpdateView, CreateView, DeleteView, ListView, DetailView, TemplateView
from django.contrib import messages
from django.db.models import Count
import matplotlib.pyplot as plt
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
import base64
from chartjs.views.lines import BaseLineChartView

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

            # Retrieve the category with the highest participation
            category_participation = Category.objects.annotate(num_participants=Count(
                'question__quizprofile')).order_by('-num_participants').first()

            # Get the category name and its participation count
            category_name = category_participation.category
            participation_count = category_participation.num_participants

            # Create the chart using Chart.js
            class ChartView(BaseLineChartView):
                def get_labels(self):
                    return [category_name]

                def get_providers(self):
                    return ["Participation Count"]

                def get_data(self):
                    return [[int(participation_count)]]

                def get_options(self):
                    return {
                        'scales': {
                            'y': {
                                'beginAtZero': True,
                                'precision': 0
                            }
                        },
                        'responsive': True,
                        'maintainAspectRatio': False
                    }

                def render_to_response(self, context, **response_kwargs):
                    chart = self.get_chart()
                    chart.generate()
                    chart_data = chart.chart.to_data_uri()

                    # Render the chart in the template
                    template = get_template('index.html')
                    context = {
                        'quiz_profile': 'quiz_profile',
                        'total_message': total_messages,
                        'total_quiz_created_by_user': total_quiz_created_by_user,
                        'chart_data': chart_data,
                    }
                    html = template.render(context)

                    # Generate PDF from the HTML template
                    result = BytesIO()
                    pdf = pisa.pisaDocument(
                        BytesIO(html.encode("UTF-8")), result)
                    if not pdf.err:
                        response = HttpResponse(
                            result.getvalue(), content_type='application/pdf')
                        response['Content-Disposition'] = 'attachment; filename="chart.pdf"'
                        return response

                    return HttpResponse("Error generating PDF", status=500)

            chart_view = ChartView()
            chart_data = chart_view.get_options()

            context = {
                'chart_data': chart_data,
                'quiz_profile': 'quiz_profile',
                'total_message': total_messages,
                'total_quiz_created_by_user': total_quiz_created_by_user,
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
