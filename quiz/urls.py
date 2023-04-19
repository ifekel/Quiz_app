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
    SearchResultListView,
    quiz_results
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
    path('<int:category_id>/question/<int:page>/', quiz, name='play'),
    path('quiz/new/', create_question, name="quiz_new"),
    path('quiz_results/', quiz_results, name="quiz_results"),
    path('category/', CategoryList.as_view(), name="category"),
    path('search/', SearchResultListView.as_view(), name="search_result"),
    path('submission_result/', submission_Result, name='submission_result'),
    path('profile/', Profile.as_view(), name="profile"),
    path('profile-edit/<int:pk>/', EditProfile.as_view(), name="edit_profile"),
    path('messages/', MessageList.as_view(), name="messages"),
    path('messages/new/', CreateMessage.as_view(), name="messages_new"),
    path('messages/<uuid:pk>/', MessageDetail.as_view(), name="message_detail"),
    path('messages/delete/<uuid:pk>/', DeleteMessage.as_view(), name="message_delete"),
    path('announcement/', AnnouncementList.as_view(), name="announcements"),
    path('announcement/<uuid:pk>/', AnnouncementDetail.as_view(), name="announcement_detail"),
    
]