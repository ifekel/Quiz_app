from django.urls import path
from .views import (
    QuestionList, 
    loginView, 
    quiz, 
    Leaderboard, 
    submission_Result, 
    Profile, 
    signupView,
    verify_email,
    CategoryList,
    MessageDetail,
    MessageList,
    AnnouncementDetail,
    AnnouncementList,
    CreateMessage,
    EditProfile,
    create_question,
    DeleteMessage,
    QuizDetailView
)

urlpatterns = [
    # ===============================
    # Both Unauthenticated Users 
    # ===============================
    path('leaderboard/', Leaderboard.as_view(), name='leaderboard'),
    path('login/', loginView, name='login'),
    path('signup/', signupView, name='signup'),
    path('verify-email/', verify_email, name="verify_email"),
    
    # ===============================
    # Authenticated Users Only 
    # ===============================
    path('quiz', QuestionList.as_view(), name="question_list"),
    path('start_quiz/<int:category_id>/', quiz, name='play'),
    path('quiz/new/', create_question, name="quiz_new"),
    path('category/', CategoryList.as_view(), name="category"),
    path('category/<uuid:pk>/', QuizDetailView.as_view(), name='category_detail'),
    path('submission_result/', submission_Result, name='submission_result'),
    path('profile/', Profile.as_view(), name="profile"),
    path('profile-edit/', EditProfile.as_view(), name="edit_profile"),
    path('messages/', MessageList.as_view(), name="messages"),
    path('messages/new/', CreateMessage.as_view(), name="messages_new"),
    path('messages/<uuid:pk>/', MessageDetail.as_view(), name="message_detail"),
    path('messages/delete/<uuid:pk>/', DeleteMessage.as_view(), name="message_delete"),
    path('announcement/', AnnouncementList.as_view(), name="announcements"),
    path('announcement/<uuid:pk>/', AnnouncementDetail.as_view(), name="announcement_detail"),
    
]