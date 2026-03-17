import requests
from bs4 import BeautifulSoup

def debug_weather(my_city):
    url = "http://www.weather.com.cn/textFC/hd.shtml"
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    text = resp.text
    soup = BeautifulSoup(text, 'html5lib')
    div_conMidtab = soup.find("div", class_="conMidtab")
    tables = div_conMidtab.find_all("table")
    for table in tables:
        trs = table.find_all("tr")[2:]
        for index, tr in enumerate(trs):
            tds = tr.find_all("td")
            # The structure might vary
            # usually: city, weather_day, wind_day, high_temp, weather_night, wind_night, low_temp
            # The code uses specific indices: -8 for city, -5 for high, -2 for low.
            try:
                city_td = tds[-8]
                this_city = list(city_td.stripped_strings)[0]
                if this_city == my_city:
                    print(f"Found city: {this_city}")
                    high_temp_td = tds[-5]
                    low_temp_td = tds[-2]
                    print(f"High TD: {high_temp_td}")
                    print(f"Low TD: {low_temp_td}")
                    
                    high = list(high_temp_td.stripped_strings)
                    low = list(low_temp_td.stripped_strings)
                    print(f"High Val: {high}")
                    print(f"Low Val: {low}")
                    return
            except Exception as e:
                continue

debug_weather("青岛")
