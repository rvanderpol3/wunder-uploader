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
    token = lacrosse.getLacrosseToken()
    idToken = None
    if token != None:
        idToken = token["idToken"]

    for device in devices:    
        for _device in device:        
            feed = lacrosse.request_feed(idToken, _device)                        
            if feed == None or feed == {}:
                continue            
            aggregate = lacrosse.processFeed(_device["device_id"], feed, aggregate)
            print(aggregate)
    
    wunder.uploadDataSet(aggregate)
    time.sleep(30)

