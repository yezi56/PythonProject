import requests
import json

def test_weather(city_name):
    try:
        url = f'http://wthrcdn.etouch.cn/weather_mini?city={city_name}'
        response = requests.get(url)
        response.encoding = 'utf-8' # or check response.apparent_encoding
        print(f"Status Code: {response.status_code}")
        print(f"Content: {response.text}")
        
        try:
            data = response.json()
            print("JSON Data:", json.dumps(data, ensure_ascii=False, indent=2))
        except:
            print("Failed to parse JSON")
    except Exception as e:
        print(f"Error: {e}")

test_weather("青岛")
