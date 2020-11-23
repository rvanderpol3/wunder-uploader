import http.client
import json
import sys
import os

PISENSORS_HOST=os.environ.get("PISENSORS_HOST")
PISENSORS_PORT=os.environ.get("PISENSORS_PORT")

def aggregatePiSensors(aggregate):
    if PISENSORS_HOST == "" or PISENSORS_PORT == "":
        print("The environment variables `PISENSORS_HOST` and `PISENSORS_PORT` must be exported.")
        sys.exit(1)
    try:
        print("Querying PI sensor server")
        conn = http.client.HTTPConnection(PISENSORS_HOST, PISENSORS_PORT)
        conn.request("GET", "/")
        response = conn.getresponse()
        if response.status != 200:
            return
        data = response.read().decode()
        data = json.loads(data)
        print(data)
        for key in data:
            aggregate[key] = data[key]
    except Exception:
        print("Error querying PI sensor server.")
        pass

    