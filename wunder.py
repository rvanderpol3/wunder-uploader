import requests
import os
import sys
import time
import utils
from datetime import datetime

WUNDER_ID=os.environ.get("WUNDER_ID")
WUNDER_KEY=os.environ.get("WUNDER_KEY")

if WUNDER_ID == "" or WUNDER_KEY == "":
    print("The evnironment variables `WUNDER_ID` and `WUNDER_KEY` must be exported.")
    sys.exit(1)

def uploadDataSet(data):
    if data == {}:
        print("No data to upload")
        return
    
    WUcreds = "ID=" + WUNDER_ID + "&PASSWORD="+ WUNDER_KEY
    date_str = "&dateutc=now"
    action_str = "&action=updateraw"

    url='https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?'+WUcreds+ date_str+action_str

    for key in data:
        url = url +"&"+key+"="+str(data[key])
    print(url)
    response = requests.get(url)
    print("response from wunder " + str(response.status_code))

