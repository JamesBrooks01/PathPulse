import datetime
from datetime import date
from datetime import datetime as datetime_object
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
    today = datetime_object.today()
    start_date_formatted = datetime_object.fromisoformat(data['start_date'])
    end_date_formatted = datetime_object.fromisoformat(data['end_date'])
    start_unix = datetime_object.timestamp(start_date_formatted)
    end_unix = datetime_object.timestamp(end_date_formatted)
    today_unix = datetime_object.timestamp(datetime_object.today())

    if start_unix < today_unix:
        return 'Invalid Date, Start Date is in the Past'
    
    boundry = today_unix + (7 * 86400)

    forecast = {}
    historic = {}
    all_weather = {}
    date_list = []

    marker = start_unix
    while marker <= end_unix:
        date_list.append(str(date.fromtimestamp(marker)))
        marker + 86400

    if start_unix >= boundry:
        historic_weather(lat=coords['lat'], lon=coords['lon'], date_list=date_list, historic=historic)
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


    for x in range(len(return_data['time'])):
        return_dict[return_data['time'][x]] = {
            'code': weather_codes[f"{return_data['weather_code'][x]}"]['description'],
            'img': weather_codes[f"{return_data['weather_code'][x]}"]['image'],
            'high': return_data['temperature_2m_max'][x],
            'low': return_data['temperature_2m_min'][x]
        }
    return return_dict

def forecast_weather():
    pass

def both_weather():
    pass