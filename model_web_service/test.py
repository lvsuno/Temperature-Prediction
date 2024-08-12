import requests

datetime_str = '2024-08-09 23:00:00'

data = {"Station ID": 50840, "Date/Time (LST)": datetime_str}

url = 'http://localhost:9696/predict'

response = requests.post(url, json=data, timeout=300)

print(response.json())
