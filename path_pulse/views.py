from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views import generic
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import User, Trip

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'path_pulse/index.html'
    context_object_name = 'users'
    def get_queryset(self):
        return User.objects.filter(user_email='example@email.com')
    
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
    except (KeyError, User.DoesNotExist):
        return render(request,'path_pulse/index.html', {'user': user, 'error_message': "Please provide trip information",},)
    else:
        trip.save()
        return HttpResponseRedirect(reverse('path_pulse:index'))