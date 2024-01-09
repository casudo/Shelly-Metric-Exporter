import requests
import prometheus_client as prom

from flask import Flask
from prometheus_client import Gauge, generate_latest, REGISTRY
from requests.auth import HTTPBasicAuth
from os import getenv

app = Flask(__name__)

### Remove default collectors
prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
prom.REGISTRY.unregister(prom.GC_COLLECTOR)

### Create a list of all Shelly devices
shelly_devices = []
device_number = 1
while True:
    host = getenv(f"D{device_number}_HOST")
    ### Exit if no more devices (host) are found
    if host is None:
        break

    shelly_devices.append({
        "devicetype": getenv(f"D{device_number}_DEVICETYPE"),
        "host": host,
        "port": getenv(f"D{device_number}_PORT", 80),
        "username": getenv(f"D{device_number}_USERNAME", None), # Optional
        "password": getenv(f"D{device_number}_PASSWORD", None) # Optional
    })
    device_number += 1
print(f"-> Found {len(shelly_devices)} Shelly devices.\n")


### Create Prometheus metrics for each Shelly device
def create_metrics(device_type, device_ip):
    ### Replace dots with underscores in the IP address
    ### Prometheus doesn't allow dots in metric names
    metric_name_ip = device_ip.replace(".", "_")

    ### Create metrics according to the device type
    if device_type == "plugs":
        return {
            "temperature": Gauge(f"shellyplugs_temperature_{metric_name_ip}", "Temperature from Shelly plugs"),
            "uptime": Gauge(f"shellyplugs_uptime_{metric_name_ip}", "Uptime from Shelly plugs"),
            "power": Gauge(f"shellyplugs_power_consumption_{metric_name_ip}", "Shelly power consumption from Shelly plugs"),
            "has_update": Gauge(f"shellyplugs_has_update_{metric_name_ip}", "Shelly has new firmware available")
        }
    elif device_type == "1":
        return {
            "uptime": Gauge(f"shelly1_uptime_{metric_name_ip}", "Shelly Uptime from Shelly 1"),
            # Spike when button is pressed?
        }
    ### TODO: Not needed since we check that in entrypoint.py?
    # else:
    #     print(f"Unknown device type: {device_type}")
    #     return None

### Call the function to create Prometheus metrics for each Shelly device and store them in a list
for device in shelly_devices:
    device["metrics"] = create_metrics(device["devicetype"], device["host"])


### API endpoint for Prometheus metrics
@app.route("/metrics")
def metrics():
    ### Loop through all Shelly devices and fetch metrics
    for shelly_device in shelly_devices:
        url = f"http://{shelly_device['host']}:{shelly_device['port']}/status"

        try:
            ### Send HTTP GET request to Shelly device
            response = requests.get(url, auth=HTTPBasicAuth(shelly_device['username'], shelly_device['password']))

            ### Check if the request was successful
            if response.status_code == 200:
                shelly_data = response.json()
                metrics = shelly_device["metrics"]

                if shelly_device['devicetype'] == "plugs":
                    metrics["temperature"].set(shelly_data.get("temperature"))
                    metrics["uptime"].set(shelly_data.get("uptime"))
                    metrics["power"].set(shelly_data.get("meters")[0].get("power", None))
                    metrics["has_update"].set(shelly_data.get("has_update"))
                elif shelly_device['devicetype'] == "1":
                    metrics["uptime"].set(int(shelly_data.get("uptime")))
                    # Add more metrics specific to Shelly 3EM
                ### TODO: Not needed since we check that in entrypoint.py?
                # else:
                #     print(f"Unknown device type: {shelly_device['devicetype']}")
                #     continue
            else:
                print(f"Failed to fetch Shelly metrics for {shelly_device['host']}. Status code: {response.status_code}")
                raise Exception(f"Failed to fetch Shelly metrics for {shelly_device['host']}. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")

    ### Return Prometheus metrics
    return generate_latest(REGISTRY)

if __name__ == '__main__':
    app.run()
