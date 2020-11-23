#! /usr/bin/env python

import argparse
import requests
import os
import pisensors
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

parser = argparse.ArgumentParser(description='Uploads data to the Weather Underground from the WeatherView API')
parser.add_argument('-d','--dryrun', help='Downloads from WeatherView but does not upload to Wunderground', action="store_true")
parser.add_argument('-s','--pi-sensors', help='Downloads from WeatherView but does not upload to Wunderground', action="store_true")
parser.add_argument('-p','--poll_period', type=int, default=30, help='Period in seconds between polls of the WeatherView API')
args = parser.parse_args()

while True:
    print("Getting auth token")
    token = lacrosse.getLacrosseToken()
    idToken = None
    if token != None:
        idToken = token["idToken"]
    dataUpdated = False

    if args.pi_sensors:
        pisensors.aggregatePiSensors(aggregate)

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
                if args.dryrun:
                    Exception.with_traceback()
                pass           
    if dataUpdated and args.dryrun == False:        
        try:
            print("Uploading data to wunderground")
            wunder.uploadDataSet(aggregate)
        except Exception:
            print("Error in uploading data.")
            pass
    else:
        print("Would have sent this to Wunderground: " + str(aggregate))
    time.sleep(args.poll_period)

