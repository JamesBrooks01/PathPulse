from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views import generic
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import User, Trip
from utilities_dir import weather_data

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'path_pulse/index.html'
    context_object_name = 'user'
    def get_queryset(self):
        return get_list_or_404(User)
    
class DetailView(generic.ListView):
    template_name = 'path_pulse/detail.html'
    context_object_name = 'trips'
    def get_queryset(self):
        return Trip.objects.filter(user_id = self.kwargs['pk'])
    
class VoteView(generic.ListView):
    model = Trip
    template_name = 'path_pulse/vote.html'
    context_object_name = 'user'
    def get_queryset(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])
    
def vote(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    try:
        form_data = request.POST
        trip = Trip(user=user, location=form_data['location'], start_date=form_data['start_date'], end_date=form_data['end_date'])
    except (KeyError, user.DoesNotExist):
        return render(request,'path_pulse/index.html', {'user': user, 'error_message': "Please provide trip information",},)
    else:
        trip.save()
        return HttpResponseRedirect(reverse('path_pulse:index'))
    
def delete_trip(request, trip_id, user_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    user = get_object_or_404(User, pk=user_id)
    try:
        trip.delete()
    except(KeyError, trip.DoesNotExist, user.id != trip.user_id):
        return render(request,'path_pulse/index.html', {'user': user, 'error_message': "Trip does not Exist",},)
    else:
        return HttpResponseRedirect(reverse('path_pulse:index'))
    
def trip_print(request):
    data = weather_data.historic_weather(52.52,13.41,'2024-06-01','2024-06-07')
    return render(request,'path_pulse/trip_print.html', {'trip': data})