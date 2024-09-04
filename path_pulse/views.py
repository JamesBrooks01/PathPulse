from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from authlib.integrations.django_client import OAuth
from django.conf import settings
from urllib.parse import urlencode, quote_plus

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

def index(request):
    data =  request.session.get('user')
    trips = None
    user_grab = None
    if data:
        try:
            user_grab = get_object_or_404(User, user_email=data['userinfo']['email'])
        except (Http404):
            user = User(user_email=data['userinfo']['email'])
            user.save()
            return HttpResponseRedirect(reverse('path_pulse:index'))
        else:
            trips = Trip.objects.filter(user=user_grab)
    return render(request,'path_pulse/index.html',
        context={
            'session': data,
            'trips': trips,
            'user': user_grab,
                 },
        )
    
def vote(request, user_id):
    logged_in_user = request.session.get('user')
    if logged_in_user:
        try:
            db_user = get_object_or_404(User, user_email= logged_in_user['userinfo']['email'])
        except(Http404):
            return render(request, 'path_pulse/error.html', {'session': logged_in_user, 'error_message': "Authentication Failed. User does not exist in the database. If you believe this is in error, please contact the Developer."})
        else:
            if db_user.id != user_id:
                return render(request, 'path_pulse/error.html', {'session': logged_in_user, 'error_message': "Authentication Failed. The currently logged in user doesn't match with the user provided in the request. If you believe this is in error, please contact the Developer."})
            else:
                user = db_user
                try:
                    form_data = request.POST
                    trip = Trip()
                    trip.user = user
                    trip.city = form_data['city']
                    trip.state = form_data['state']
                    trip.country = form_data['country']
                    trip.start_date = form_data['start_date']
                    trip.end_date = form_data['end_date']
                except (KeyError, user.DoesNotExist):
                    return render(request,'path_pulse/error.html', {'session': logged_in_user, 'error_message': "An Error has occurred. The most likely culprit is an incomplete form. If you believe this is wrong, please contact the Developer.",},)
                else:
                    trip.save()
                    return HttpResponseRedirect(reverse('path_pulse:index'))
    else:
        return HttpResponseRedirect(reverse('path_pulse:index'))
    
def delete_trip(request, trip_id):
    logged_in_user = request.session.get('user')
    if logged_in_user:
        try:
            trip = get_object_or_404(Trip, pk=trip_id)
            user = get_object_or_404(User, user_email=logged_in_user['userinfo']['email'])
        except(Http404):
            return render(request, 'path_pulse/error.html', {'session': logged_in_user, 'error_message': "An Error has occurred. Either the Trip or User does not Exist. If you believe this is wrong, please contact the Developer."})
        else:
            if user.id == trip.user_id:
                trip.delete()
                return HttpResponseRedirect(reverse('path_pulse:index'))
            else:
                return render(request, 'path_pulse/error.html', {'session': logged_in_user, 'error_message': "An Error has occurred. Either the Trip does not exist Or this action is unauthorized via the user id assosiated with the trip does not match the logged in user"})  
    else:
        return HttpResponseRedirect(reverse('path_pulse:index'))
    
def trip_print(request, trip_id, user_id):
    logged_in_user = request.session.get('user')
    if logged_in_user:
        try:
            trip = get_object_or_404(Trip, pk=trip_id)
        except(Http404):
                return render(request, 'path_pulse/error.html', {'session': logged_in_user, 'error_message': "An Error has Occurred. The requested trip does not Exist. If you believe this is in error, please contact the Developer."})   
        else:
            if trip.user.user_email == logged_in_user['userinfo']['email']:
                data = weather_data.weather_data(trip)
                return render(request,'path_pulse/trip_print.html', {'session': logged_in_user, 'trip': data, 'user': user_id, 'object': trip})
            else:
                return render(request, 'path_pulse/error.html', {'session': logged_in_user, 'error_message': "Authentication Failed. The currently logged in user doesn't match with the user assosiated with the requested trip. If you believe this is in error, please contact the Developer."})
    else:
        return HttpResponseRedirect(reverse('path_pulse:index'))