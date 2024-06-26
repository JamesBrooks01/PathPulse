from django.urls import path

from . import views

app_name = 'path_pulse'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.VoteView.as_view(), name='detail'),
    path('<int:user_id>/vote', views.vote, name='vote')
]