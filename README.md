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

The Lacrosse WeatherView API will be checked every 30 seconds for updates.  Additionally, only the last 60 seconds of sensor data is queried.  An aggregation of the sensor data is maintained and provided to Wunderground as a single HTTP post.  Wunderground seems to want all raw data provided at once or else you will see `--` appear on sensors.  Updates will only be sent to Wunderground if there is atleast one updated sensor in a given poll of the WeatherView API.

Some sensors such as barometric pressure are not accessible via the API(atleast not that I could find).  

