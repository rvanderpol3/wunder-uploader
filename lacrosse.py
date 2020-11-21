import requests
import os
import time
import utils
import sys
import configparser
import ast
import os.path
from os import path
from datetime import datetime

LACROSSE_EMAIL=os.environ.get("LACROSSE_EMAIL")
LACROSSE_PW=os.environ.get("LACROSSE_PW")

if LACROSSE_EMAIL == "" or LACROSSE_PW == "":
    print("The environment variables `LACROSSE_EMAIL` and `LACROSSE_PW` must be exported.")
    sys.exit(1)

SENSOR_CONFIG={}

def splitDef(sensor_map, sensor):
    if sensor in sensor_map:
        entry = sensor_map[sensor]
        tokens = entry.split(".")
        if len(tokens) == 2:
            return {"device_id": tokens[0],"sensor_name": tokens[1]}
    return None

configp = configparser.ConfigParser()
configp.read('sensors.cfg')
if 'sensor_map' not in configp:
    print("Could not find sensor_map in sensors.cfg")

sensor_map=configp["sensor_map"]

wind_config = splitDef(sensor_map,"wind")
wind_config["history"] = []
wind_config["last_timestamp"] = 0

temperature_config = splitDef(sensor_map,"temperature")
temperature_config["last_temp_c"] = None
rain_config = splitDef(sensor_map,"rain")
rain_config["last_timestamp"] = 0
rain_config["history"] = []
humidity_config = splitDef(sensor_map,"humidity")

lastUpdateTime = 0

statep = {
    "date": -1,
    "rainfall": 0.00,
    "last_rainfall_timestamp": 0
}

if path.exists("state.cfg"):
    with open("state.cfg") as cfg:
        data = cfg.read()
        statep = ast.literal_eval(data)
        print("Restored state: " + str(statep))



def getLacrosseToken():
    url='https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyD-Uo0hkRIeDYJhyyIg-TvAv8HhExARIO4'
    payload = {
        "email": LACROSSE_EMAIL,
        "returnSecureToken": True,
        "password": LACROSSE_PW
    }
    response = requests.post(url, data = payload)
    if response.status_code == 200:
        return response.json()
    print("Unable to get auth - " + response.content)
    return None

def init_locations(auth):
    req_url = "https://lax-gateway.appspot.com/_ah/api/lacrosseClient/v1.1/active-user/locations"
    headers = {"Authorization": "Bearer " + auth}
    response = requests.get(req_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    print("Unable to get locations - " + response.content)
    return None

def init_location_devices(location, auth):
    req_url = "https://lax-gateway.appspot.com/_ah/api/lacrosseClient/v1.1/active-user/location/"+ location["id"] + "/sensorAssociations?prettyPrint=false"
    headers = {"Authorization": "Bearer " + auth}
    response = requests.get(req_url, headers=headers)
    if response.status_code != 200:
        print("Unable to get devices at location - " + response.content)
        return None

    body = response.json()
    
    deviceList = []
    devices = body.get('items')
    for device in devices:
        sensor = device.get('sensor')
        device_name = device.get('name').lower().replace(' ', '_')
        device_dict = {
            "device_name": device_name,
            "device_id": device.get('id'),
            "sensor_type_name": sensor.get('type').get('name'),
            "sensor_id": sensor.get('id'),
            "sensor_field_names": [x for x in sensor.get('fields')
                                   if x != "NotSupported"],
            "last_timestamp_written": None,
            "location": location}        
        deviceList.append(device_dict)
    return deviceList

def printDeviceDetails(device):
    print("\nSensor Name: " + device["sensor_type_name"])
    print("Device ID: " + device["device_id"])
    print("Sensor ID: " + device["sensor_id"])
    for field in device["sensor_field_names"]:
        print("\tField: " + field)

def request_feed(auth, device, start=None, end=None):
    fields_list = device["sensor_field_names"]
    fields_str = ",".join(fields_list)
    time_zone = "America/Los_Angeles"
    end = str(utils.datetime_to_int_seconds(datetime.utcnow()))
    start = str(utils.datetime_to_int_seconds(datetime.utcnow())-60)
    aggregates = "ai.ticks.1"
    start = "from={}&".format(start) if start else ""
    end = "to={}&".format(end) if end else ""
    req_url = "https://ingv2.lacrossetechnology.com/" \
          "api/v1.1/active-user/device-association/ref.user-device.{id}/" \
          "feed?fields={fields}&" \
          "tz={tz}&" \
          "{_from}" \
          "{to}" \
          "aggregates={agg}&" \
          "types=spot".format(id=device["device_id"],
                              fields=fields_str, tz=time_zone,
                              _from=start, to=end, agg=aggregates)

    headers = {"Authorization": "Bearer " + auth}
    response = requests.get(req_url, headers=headers)
    body = response.json()
    return body.get('ref.user-device.' + device["device_id"]).get('ai.ticks.1').get('fields')

def getSensorValue(feed, sensorName):
    if sensorName not in feed:
        return None
    sensor = feed[sensorName]
    if "values" in sensor:
        values = sensor["values"]
        if len(values) == 0:
            return None
        return values[0]
    return None
        

def checkDailyRollover(aggregate):
    today = datetime.today()   
    print(today)
    if statep["date"] != today.day:
        print("New day rollover - " + str(today))
        statep["date"] = today.day
        statep["rainfall"] = 0.00
        aggregate["dailyrainin"] = 0.00 

def getWindStats(aggregate, value):
    currentSpeed = aggregate["windspeedmph"]
    currentTime = value['u']
    if currentTime == wind_config["last_timestamp"]:
        return
    wind_config["last_timestamp"] = currentTime
    gust10minTimeout = currentTime - 600
    avg2minTimeout = currentTime - 120
    wind_config["history"].insert(0,{"speed":currentSpeed, "time":currentTime}) 
    hasAverage = False
    speedAccum=0
    maxSpeed = 0
    for index in range(len(wind_config["history"])):
        val = wind_config["history"][index]        
        if hasAverage == False:
            if val["time"] > avg2minTimeout:
                speedAccum = speedAccum + val["speed"]
            else:
                aggregate["windspdmph_avg2m"] = speedAccum / (index+1)
                hasAverage = True
        if val["time"] > gust10minTimeout:
            if val["speed"] > maxSpeed:
                maxSpeed = val["speed"]
        else:
            wind_config["history"] = wind_config["history"][0:index]
            break
    aggregate["windgustmph_10m"] = maxSpeed
    print("wind history len["+str(len(wind_config["history"]))+"]- ["+str(wind_config["history"])+"]")

def processWind(feed, aggregate):
    value = getSensorValue(feed,"WindSpeed")
    aggregate["windspeedmph"]= value['s'] * 0.621371        
    getWindStats(aggregate, value)    
    print("--> Got wind speed ["+str(aggregate["windspeedmph"])+"]")

def processHumidity(feed, aggregate):
    value = getSensorValue(feed,"Humidity")
    aggregate["humidity"]= value['s']
    print("--> Got humidity ["+str(aggregate["humidity"])+"%]")

def processTemperature(feed, aggregate):
    value = getSensorValue(feed,"Temperature")
    tempC = value['s']
    lastTemp = temperature_config["last_temp_c"]
    # occassionally the temperature sensor flakes out and this is an attempt to filter that flake
    if lastTemp == None or abs(lastTemp-tempC) < 20:
        if "humidity" in aggregate:
            aggregate["dewptf"] = (value['s'] - ((100-aggregate["humidity"])/5))* 1.8 + 32
        aggregate["tempf"]= (value['s']* 1.8 + 32)            
        print("--> Got temp ["+str(aggregate["tempf"])+"F]")        
        temperature_config["last_temp_c"] = tempC

def processRain(feed, aggregate):
    value = getSensorValue(feed,"Rain")        
    if statep["last_rainfall_timestamp"] != value['u']:
        statep["last_rainfall_timestamp"] = value['u']
        statep["rainfall"] = statep["rainfall"] + value['s']                    
        aggregate["dailyrainin"] = statep["rainfall"]        
        rain_config["history"].insert(0, value)
        print("--> Got rain current["+str(value['s'])+"] aggregate["+str(aggregate["dailyrainin"])+"]")

    if len(rain_config["history"]) > 0:
        currentTime = rain_config["history"][0]['u']
        accum60minTimeout = currentTime - 3600
        rainInLastHour=0
        for index in range(len(rain_config["history"])):
            val = rain_config["history"][index]   
            if val['u'] > accum60minTimeout:
                rainInLastHour = rainInLastHour + value['s']
            else:
                rain_config["history"] = rain_config["history"][0:index]
                break
        aggregate["rainin"] = rainInLastHour
    print("rain history len["+str(len(rain_config["history"]))+"] - ["+str(rain_config["history"])+"]")

def writeStateFile():
    with open("state.cfg","wt") as cfg:
        cfg.write(str(statep))

def processFeed(device_id, feed, aggregate):    
    checkDailyRollover(aggregate)

    if wind_config["device_id"] == device_id:
        processWind(feed,aggregate)

    if humidity_config["device_id"] == device_id:
        processHumidity(feed,aggregate)

    if temperature_config["device_id"] == device_id:
        processTemperature(feed,aggregate)

    if rain_config["device_id"] == device_id:
        processRain(feed,aggregate)

    writeStateFile()
    return aggregate
        
