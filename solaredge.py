import requests
import json
import daytime
from datetime import datetime, time
from requests.structures import CaseInsensitiveDict

def getPowerGenerationInKw():
    if daytime.is_time_between(time(21,00), time(6,0)):
        if daytime.is_after_midnight():
            print("resetting daily stats")
            return  {"current": 0,
                     "today": 0}
        return

    url = "https://monitoringpublic.solaredge.com/solaredge-apigw/api/v3/sites/xxxxxx?web=true"

    headers = CaseInsensitiveDict()
    headers["authority"] = "monitoringpublic.solaredge.com"

    headers["x-requested-with"] = "XMLHttpRequest"
    headers["x-csrf-token"] = "xxxxxxxxx"
    headers["sec-ch-ua-mobile"] = "?0"
    headers["user-agent"] = "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    headers["sec-ch-ua-platform"] = "Linux"
    headers["accept"] = "*/*"
    headers["sec-fetch-site"] = "same-origin"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-dest"] = "empty"
    headers["referer"] = "https://monitoringpublic.solaredge.com/solaredge-web/p/site/public?name=xxxxxxxxxx"
    headers["accept-language"] = "en-US,en;q=0.9"
    headers["cookie"] = "SolarEdge_Client-1.6=xxxxxxxxx"


    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return
    data = json.loads(resp.text)

    if "fieldOverview" not in data:
        return
    data = data["fieldOverview"]

    if "fieldOverview" not in data:
        return
    fieldOverview = data["fieldOverview"]

    if "currentPower" not in fieldOverview:
        return
    currentPower = fieldOverview["currentPower"]
    power = currentPower["currentPower"]
    if currentPower["unit"] == 'W':
        power = power / 1000

    if "lastDayData" not in fieldOverview:
        return
    
    return {"current": power,
    "today": fieldOverview["lastDayData"]["energy"] / 1000}
    
print(getPowerGenerationInKw())