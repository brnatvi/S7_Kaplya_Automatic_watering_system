import json
import requests

response = requests.get('https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&hourly=temperature_2m,relativehumidity_2m,rain,showers&forecast_days=1').text

response_info = json.loads(response)
hourly = response_info['hourly']
times = hourly['time']
temperature = hourly['temperature_2m']
humidity = hourly['relativehumidity_2m']
rain = hourly['rain']
showers = hourly['showers']

date = '2023-05-03'
time = '10:00'
datetime = date + 'T' + time

index = times.index(datetime)

print("For %s, %s : temperature = %s; humidity = %s; rain = %s; showers = %s." 
        % (date, time, temperature[index], humidity[index], rain[index], showers[index]))
