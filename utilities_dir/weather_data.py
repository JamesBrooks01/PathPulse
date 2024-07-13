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
    start_date_formatted = datetime_object.fromisoformat(data.start_date)
    end_date_formatted = datetime_object.fromisoformat(data.end_date)
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
        marker += 86400

    lat = coords['lat']
    lon = coords['lon']

    if start_unix >= boundry:
        print("Historic Hit")
        historic_weather(lat=lat, lon=lon, date_list=date_list, historic=historic)
    elif end_unix >= boundry:
        print("Both Weather Hit")
        both_weather(lat=lat,lon=lon,date_list=date_list,forecast=forecast,historic=historic,boundry=boundry)
    else:
        print("Forecast Hit")
        forecast_weather(lat=lat,lon=lon,date_list=date_list,forecast=forecast)

    if forecast == {}:
        return historic
    elif historic == {}:
        return forecast
    else:
        all_weather.update(forecast)
        all_weather.update(historic)
        return all_weather


def historic_weather(lat,lon,date_list, historic):
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    start_date_past= datetime_object.fromisoformat(date_list[0]) - datetime.timedelta(366)
    end_date_past= datetime_object.fromisoformat(date_list[-1]) - datetime.timedelta(366)
    start_date_formatted = start_date_past.date()
    end_date_formatted = end_date_past.date()
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date_formatted.isoformat(),
        "end_date": end_date_formatted.isoformat(),
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto" 
    }

    response = requests.get(url,params=params)
    converted = json.loads(response.text)
    return_data = converted['daily']


    for x in range(len(return_data['time'])):
        historic[date_list[x]] = {
            'code': weather_codes[f"{return_data['weather_code'][x]}"]['description'],
            'img': weather_codes[f"{return_data['weather_code'][x]}"]['image'],
            'high': return_data['temperature_2m_max'][x],
            'low': return_data['temperature_2m_min'][x]
        }
    return historic

def forecast_weather(lat,lon,date_list,forecast):
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_list[0],
        "end_date": date_list[-1],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto" 
    }
    
    response = requests.get(url, params=params)
    converted = json.loads(response.text)
    return_data = converted['daily']

    for x in range(len(return_data['time'])):
        forecast[date_list[x]] = {
            'code': weather_codes[f"{return_data['weather_code'][x]}"]['description'],
            'img': weather_codes[f"{return_data['weather_code'][x]}"]['image'],
            'high': return_data['temperature_2m_max'][x],
            'low': return_data['temperature_2m_min'][x]            
        }
    return forecast

def both_weather():
    pass