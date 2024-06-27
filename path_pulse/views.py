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
    try:
        user = get_object_or_404(User, pk=user_id)
    except (KeyError, User.DoesNotExist):
        return render(request,'path_pulse/index.html')
    else:
        user.user_trips[0].append(['Moclips', '06-26-2024', '06-29-2024'])
        user.save()
        return HttpResponseRedirect(reverse('path_pulse:index'))