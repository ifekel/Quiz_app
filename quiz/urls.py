from django.urls import path
from .views import (
    QuestionList,
    loginView,
    # play_quiz,
    PlayQuizView,
    Leaderboard,
    submission_Result,
    Profile,
    signupView,
    verify_email,
    category_list,
    MessageDetail,
    MessageList,
    AnnouncementDetail,
    AnnouncementList,
    CreateMessage,
    EditProfile,
    create_question,
    DeleteMessage,
    SearchResultListView,
    quiz_results,
    results,
    quiz_analytics,
    quiz_taken,
    quiz_created
)
app_name = "quiz"


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
    path('quiz_taken', quiz_taken, name="quiz_taken"),
    path('quiz_created', quiz_created, name="quiz_created"),
    path('play-quiz/<int:category_id>/', PlayQuizView.as_view(), name='play'),
    path('quiz/new/', create_question, name="quiz_new"),
    path('analytics/', quiz_analytics, name="quiz_analytics"),
    path('quiz-results/', quiz_results, name="quiz_results"),
    path('results/<int:category_id>/', results, name='results'),
    path('category/', category_list, name="category"),
    path('search/', SearchResultListView.as_view(), name="search_result"),
    path('submission_result/', submission_Result, name='submission_result'),
    path('profile/', Profile.as_view(), name="profile"),
    path('profile-edit/<int:pk>/', EditProfile.as_view(), name="edit_profile"),
    path('messages/', MessageList.as_view(), name="messages"),
    path('messages/new/', CreateMessage.as_view(), name="messages_new"),
    path('messages/<uuid:pk>/', MessageDetail.as_view(), name="message_detail"),
    path('messages/delete/<uuid:pk>/',
         DeleteMessage.as_view(), name="message_delete"),
    path('announcement/', AnnouncementList.as_view(), name="announcements"),
    path('announcement/<uuid:pk>/', AnnouncementDetail.as_view(),
         name="announcement_detail"),

]
