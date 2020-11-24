# wunder-uploader

Derived from work in project https://github.com/dbconfession78/py_weather_station


## Overview

The intent of this project is to feed data to the [Weather Underground](https://support.weather.com/s/article/PWS-Upload-Protocol?language=en_US) for data derived from the Lacrosse WeatherView API.  To use this project you must have the following:

- WeatherView login information
- PWS ID and push key from the Weather Underground
- The device IDs of the devices you wish to monitor
- The mapping of those device IDs to key metrics
- python 3

## Usage

Prior to running `weather.py` you must export or define the following environment variables:

~~~
export LACROSSE_EMAIL=user@mail.com
export LACROSSE_PW=yourpw
export WUNDER_ID=your-id
export WUNDER_KEY=your-push-key
~~~

To run:
~~~
python3 ./weather.py
~~~

The Lacrosse WeatherView API will be checked every 30 seconds for updates.  Additionally, only the last 60 seconds of sensor data is queried.  An aggregation of the sensor data is maintained and provided to Wunderground as a single HTTP post.  Wunderground seems to want all raw data provided at once or else you will see `--` appear on sensors.  Updates will only be sent to Wunderground if there is atleast one updated sensor in a given poll of the WeatherView API.

Some sensors such as barometric pressure are not accessible via the API(atleast not that I could find).  

## Importing from other sensors

To enable reading of barometric pressure a `BMP180` was soldered to a Raspberry Pi 4. The value of the barometric pressure was exported from PI via a very simple HTTP server. The HTTP server responds with a json payload of:

~~~
{'baromin': 30.37816094557164}
~~~

While the returned value is for barometric pressure, and of the Wunderground HTTP paramters could also be returned.  This project will automatically consume and add any variables it finds to the payload to be sent to Wunderground.

To enable this feature:

~~~
export PISENSORS_HOST=host-or-ip-of-server-hosting-json
export PISENSORS_PORT=8080
~~~

To run:
~~~
python3 ./weather.py -s
~~~


