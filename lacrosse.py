import requests
import os
import time
import utils
import sys
import configparser
from datetime import datetime

LACROSSE_EMAIL=os.environ.get("LACROSSE_EMAIL")
LACROSSE_PW=os.environ.get("LACROSSE_PW")

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
temperature_config = splitDef(sensor_map,"temperature")
rain_config = splitDef(sensor_map,"rain")
humidity_config = splitDef(sensor_map,"humidity")

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
        print(device_dict)
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
        

def processFeed(device_id, feed, aggregate):    
    # print("in process - " + device_id)
    # print(humidity_config)
    # print(temperature_config)
    # print(rain_config)
    # print(wind_config)
    if wind_config["device_id"] == device_id:
        value = getSensorValue(feed,"WindSpeed")
        aggregate["windspeedmph"]= value['s'] * 0.621371        
    if humidity_config["device_id"] == device_id:
        value = getSensorValue(feed,"Humidity")
        aggregate["humidity"]= value['s']
    if temperature_config["device_id"] == device_id:
        value = getSensorValue(feed,"Temperature")
        if "humidity" in aggregate:
            aggregate["dewptf"] = (value['s'] - ((100-aggregate["humidity"])/5))* 1.8 + 32
        aggregate["tempf"]= (value['s']* 1.8 + 32)
    if rain_config["device_id"] == device_id:
        value = getSensorValue(feed,"Rain")
        aggregate["dailyrainin"]= value['s']
    return aggregate
        
