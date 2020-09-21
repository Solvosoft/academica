from django.urls import path

from api.news_letter import NewsLetterTaskView

urlpatterns = [

    path('news_letter/task/<int:pk>/', NewsLetterTaskView.as_view(), name="api_news_letter_task"),
]