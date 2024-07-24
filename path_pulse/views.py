from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.views import generic
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse

from authlib.integrations.django_client import OAuth
from django.conf import settings
from urllib.parse import urlencode, quote_plus
import json

from .models import User, Trip
from utilities_dir import weather_data

oauth = OAuth()

oauth.register(
    'auth0',
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration"
)

# Create your views here.

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse('path_pulse:callback'))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session['user'] = token
    return redirect(request.build_absolute_uri(reverse('path_pulse:index')))

def logout(request):
    request.session.clear()

    return redirect(
        f'https://{settings.AUTH0_DOMAIN}/v2/logout?'
        + urlencode(
            {
                'returnTo': request.build_absolute_uri(reverse('path_pulse:index')),
                'client_id': settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

# class IndexView(generic.ListView):
#     template_name = 'path_pulse/index.html'
#     context_object_name = 'user'
#     def get_queryset(self):
#         return get_list_or_404(User)

def index(request):
    data =  request.session.get('user')
    user_grab = User.objects.filter(user_email=data['userinfo']['email'])
    if not user_grab:
        user = User(user_email=data['userinfo']['email'])
        user.save()
        return HttpResponseRedirect(reverse('path_pulse:index'))
    else:
        trips = Trip.objects.filter(user=user_grab[0])
    return render(request,'path_pulse/index.html',
        context={
            'session': data,
            'trips': trips,
                 },
        )
    
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
    
def trip_print(request, trip_id, user_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    data = weather_data.weather_data(trip)
    return render(request,'path_pulse/trip_print.html', {'trip': data, 'user': user_id})