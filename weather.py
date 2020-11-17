import requests
import os
import time
import lacrosse
import wunder
from datetime import datetime


token = lacrosse.getLacrosseToken()
idToken = None
if token != None:
    idToken = token["idToken"]

locations = lacrosse.init_locations(idToken)

devices = []

for location in locations["items"]:
    device = lacrosse.init_location_devices(location,idToken)
    if device == None:
        continue    
    devices.append(device)

aggregate = {}


while True:
    print("Getting auth token")
    token = lacrosse.getLacrosseToken()
    idToken = None
    if token != None:
        idToken = token["idToken"]
    dataUpdated = False
    for device in devices:            
        for _device in device:
            print("Processing device " + _device["device_name"])        
            try:
                print("Requesting feed")
                feed = lacrosse.request_feed(idToken, _device)                        
                if feed == None or feed == {}:
                    continue            
                print("Processing feed")
                aggregate = lacrosse.processFeed(_device["device_id"], feed, aggregate)
                dataUpdated = True
            except Exception:
                print("Unable to get or process feed for device.")
                print(_device)
                pass           
    if dataUpdated:        
        try:
            print("Uploading data to wunderground")
            wunder.uploadDataSet(aggregate)
        except Exception:
            print("Error in uploading data.")
            pass
    time.sleep(30)

