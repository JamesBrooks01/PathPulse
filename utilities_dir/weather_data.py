import datetime
from datetime import date
import os
import openmeteo_requests
import requests_cache
from retry_requests import retry
import json
import requests

cache_session = requests_cache.CachedSession('requests_cache', backend='memory', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor = 0.2)
open_metro = openmeteo_requests.Client(session=retry_session)

with open('utilities_dir/weather_codes.json') as weather_file:  
    weather_codes = json.load(weather_file)


def location_data(data):
    sanitized_spaces = data.location.replace(' ', '%20')
    api_key = os.environ.get('LOCATION_API')
    url = f'https://us1.locationiq.com/v1/search?key={api_key}&q={sanitized_spaces}&format=json'
    response = requests.get(url)
    converted = json.loads(response.text)
    return_dict = {
        'lat': converted[0]['lat'],
        'lon': converted[0]['lon']
    }
    return return_dict

def weather_data(data):
    coords = location_data(data)
    today = date.today()
    start_unix = datetime.datetime.fromisoformat(data['start_date'])
    end_unix = datetime.datetime.fromisoformat(data['end_date'])
    days_from_today = round((start_unix - today) // 86400)
    if days_from_today < 0:
        return 'Invalid Date, Start Date is in the Past'
    boundry = today + (7 * 86400)

    forecast = []
    historic = []
    all_weather = {}
    date_list = []

    marker = start_unix
    while marker <= end_unix:
        date_list.append(marker)
        marker + 86400

    if start_unix >= boundry:
        historic_weather()
    elif end_unix >= boundry:
        both_weather()
    else:
        forecast_weather()


def historic_weather(lat,lon,start,end):
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto" 
    }

    response = requests.get(url,params=params)
    converted = json.loads(response.text)
    return_data = converted['daily']
    return_dict = {}

    with open('') as weather_codes:
        codes = json.load(weather_codes)

    for x in range(len(return_data['time'])):
        return_dict[return_data['time'][x]] = {
            'code': codes[f"{return_data['weather_code'][x]}"]['description'],
            'img': codes[f"{return_data['weather_code'][x]}"]['image'],
            'high': return_data['temperature_2m_max'][x],
            'low': return_data['temperature_2m_min'][x]
        }
    return return_dict

def forecast_weather():
    pass

def both_weather():
    pass