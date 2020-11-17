# wunder-uploader

Derived from work in project https://github.com/dbconfession78/py_weather_station

The intent of this project is to feed data to the Weather Underground for data derived from the Lacrosse WeatherView API.  To use this project you must have the following:

- WeatherView login information
- PWS ID and push key from the Weather Underground
- The device IDs of the devices you wish to monitor
- The mapping of those device IDs to key metrics

~~~
export LACROSSE_EMAIL=user@mail.com
export LACROSSE_PW=yourpw
export WUNDER_ID=your-id
export WUNDER_KEY=your-push-key

python3 ./weather.py
~~~

