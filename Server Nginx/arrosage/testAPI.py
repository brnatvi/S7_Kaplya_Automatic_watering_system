import json
import requests

date = '2023-05-07'

response = requests.get('https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&hourly=temperature_2m,relativehumidity_2m,precipitation&start_date=' + date + '&end_date=' + date).text

response_info = json.loads(response)
hourly = response_info['hourly']
temperatures = hourly['temperature_2m']
humidities = hourly['relativehumidity_2m']
precipitations = hourly['precipitation']

def weighted_average(list):
        n_measurements = len(list)
        durations = [1] * n_measurements

        # calculate the total duration for the day
        total_duration = sum(durations)

        # calculate the sum of the products of temperatures and durations
        weighted_sum = sum([temp * duration for temp, duration in zip(list, durations)])

        # calculate the weighted average temperature
        weighted_average = weighted_sum / total_duration

        return weighted_average

average_temp = weighted_average(temperatures)
average_humidity = weighted_average(humidities)
average_precipitation = weighted_average(precipitations)

print("For %s : average temp = %s; humidity = %s; precipitation = %s." 
        % (date, average_temp, average_humidity, average_precipitation))
