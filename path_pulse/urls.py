from django.urls import path

from . import views

app_name = 'path_pulse'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('callback', views.callback, name='callback'),
    path('<int:user_id>/vote', views.vote, name='vote'),
    path('<int:trip_id>/delete', views.delete_trip, name='delete_trip'),
    path('print/<int:trip_id>', views.trip_print, name='print_test'),
]