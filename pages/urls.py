from django.urls import path
from .views import home, AboutPageView, ContactPageView

urlpatterns = [
    path('', home, name="home_page"),
    path('about/', AboutPageView.as_view(), name="about_page"),
    path('contact/', ContactPageView, name="contact_page"),
]
