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
    api_key = os.environ.get('LOCATION_API')
    url = f'https://us1.locationiq.com/v1/search/structured?city={data.city}&state={data.state}&country={data.country}&key={api_key}&format=json'
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
        return 'Invalid'
    
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
        historic_weather(lat=lat, lon=lon, date_list=date_list, historic=historic)
    elif end_unix >= boundry:
        both_weather(lat=lat,lon=lon,date_list=date_list,forecast=forecast,historic=historic,boundry=boundry)
    else:
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
        date = date_format(date_list[x])
        historic[date] = {
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
        date = date_format(date_list[x])
        forecast[date] = {
            'code': weather_codes[f"{return_data['weather_code'][x]}"]['description'],
            'img': weather_codes[f"{return_data['weather_code'][x]}"]['image'],
            'high': return_data['temperature_2m_max'][x],
            'low': return_data['temperature_2m_min'][x]            
        }
    return forecast

def both_weather(lat,lon,date_list,forecast,historic, boundry):
    forecast_dates = []
    historic_dates = []

    for date in date_list:
        date_unix = datetime_object.timestamp(datetime_object.fromisoformat(date))
        if date_unix >= boundry:
            historic_dates.append(date)
        else:
            forecast_dates.append(date)
    historic_weather(lat=lat,lon=lon,date_list=historic_dates,historic=historic)
    forecast_weather(lat=lat,lon=lon,date_list=forecast_dates,forecast=forecast)
    return

def date_format(date):
    days_of_week = {'0': 'Monday','1': 'Tuesday','2': 'Wednesday','3': 'Thursday','4': 'Friday','5': 'Saturday','6': 'Sunday'}
    months = {'1': 'January','2': 'February','3': 'March','4': 'April','5': 'May','6': 'June','7': 'July','8': 'August','9': 'September','10': 'October','11': 'November','12': 'December'}
    formatted_date = datetime_object.fromisoformat(date)
    weekday = days_of_week[f'{formatted_date.weekday()}']
    day = str(formatted_date.day)
    day_string = ''
    if day[-1] == '2':
        day_string += f'{day}nd'
    elif day[-1] == '3':
        day_string += f'{day}rd'  
    elif day[-1] in ['1']:
        day_string += f'{day}st'
    else:
        day_string += f'{day}th'
    month = months[f'{formatted_date.month}']
    year = formatted_date.year
    complete_string = f"{weekday}, The {day_string} of {month}, {year}"
    return complete_string