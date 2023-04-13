from django.urls import path
from .views import HomePageView, AboutPageView, ContactPageView

urlpatterns = [
    path('', HomePageView.as_view(), name="home_page"),
    path('about/', AboutPageView.as_view(), name="about_page"),
    path('contact/', ContactPageView, name="contact_page"),
]