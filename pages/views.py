from django.shortcuts import render, redirect
from quiz.models import Announcement, ContactMessage
from django.views.generic import UpdateView, CreateView, DeleteView, ListView, DetailView, TemplateView
from django.contrib import messages

# Create your views here.

class HomePageView(TemplateView):    
    def get(self, request):
        if request.user.is_superuser == True :
            return redirect('/admin')
        else:
            announcements = Announcement.objects.all()
            total_announcement = Announcement.objects.all().count()
            context = {
                'announcements': announcements,
                'total_announcement': total_announcement,
            }
            return render(request, 'index.html', context)
    
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
            contact = ContactMessage.objects.create(first_name=firstName, last_name=lastName, email_address=email, phone_number=phoneNumber, message=message)
            contact.save()
            messages.success(request, "Your message was sent successfully!")
        
        return render(request, "contact.html")
    else:
        return render(request, "contact.html")
    