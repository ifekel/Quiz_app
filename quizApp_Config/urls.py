from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from quiz import views as quiz_views
from django.conf.urls import handler404, handler500, handler403

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quiz.urls')),
    path('', include('quiz.urls', namespace='quiz')),
    path('', include('pages.urls')),
    path('', include('allauth.urls')),
    path('accounts/', include('allauth.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = quiz_views.error404
handler500 = quiz_views.error_500
