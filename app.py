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
shelly_device_list = []
device_number = 1
while True:
    ip = getenv(f"D{device_number}_IP")

    ### Exit if no more devices (ip) are found
    if ip is None:
        break

    shelly_device_list.append({
        "gen": getenv(f"D{device_number}_GEN"),
        "ip": ip,
        "port": getenv(f"D{device_number}_PORT", 80), # Optional
        "username": getenv(f"D{device_number}_USERNAME", None), # Optional
        "password": getenv(f"D{device_number}_PASSWORD", None) # Optional
    })
    device_number += 1
print(f"-> Found {len(shelly_device_list)} Shelly devices.\n")


### Create Prometheus metrics for each Shelly device
def create_metrics(device_ip):
    ### Replace dots with underscores in the IP address
    ### TODO: Might add a optional "D{n}_NAME" to set a custom name for the device
    ### Prometheus doesn't allow dots in metric names
    metric_name_ip = device_ip.replace(".", "_")

    ### Create Prometheus metrics for Shelly device
    return {
        "temperature": Gauge(f"shelly_temperature_{metric_name_ip}", "Temperature from Shelly Device"),
        "uptime": Gauge(f"shelly_uptime_{metric_name_ip}", "Uptime from Shelly Device"),
        "power": Gauge(f"shelly_power_consumption_{metric_name_ip}", "Shelly power consumption from Shelly Device"),
    }

### Call the function to create Prometheus metrics for each Shelly device and store them in a list
for device in shelly_device_list:
    device["metrics"] = create_metrics(device["ip"])


### API endpoint for Prometheus metrics
### NOTE: This method will be called when accessing the /metrics endpoint!
@app.route("/metrics")
def metrics():
    ### Loop through all Shelly devices and fetch metrics
    for shelly_device in shelly_device_list:
        base_url = f"http://{shelly_device['ip']}:{shelly_device['port']}"

        ### Send a GET request to the Shelly device depending on the device type
        if shelly_device["gen"] == "1":
            api_endpoint = "status"

            try:
                ### Send HTTP GET request to Shelly device
                response = requests.get(f"{base_url}/{api_endpoint}", auth=HTTPBasicAuth(shelly_device['username'], shelly_device['password']))

                ### Check if the request was successful
                if response.status_code == 200:
                    shelly_data = response.json()
                    metrics = shelly_device["metrics"]

                    ### Set Prometheus metrics
                    metrics["temperature"].set(shelly_data.get("temperature"))
                    metrics["uptime"].set(shelly_data.get("uptime"))
                    metrics["power"].set(shelly_data.get("meters")[0].get("power", None))
                else:
                    print(f"Failed to fetch Shelly metrics for {shelly_device['ip']}. Status code: {response.status_code}")
                    raise Exception(f"Failed to fetch Shelly metrics for {shelly_device['ip']}. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")
        elif shelly_device["gen"] == "2":
            api_endpoint = "rpc/Shelly.GetStatus"

            try:
                ### Send HTTP GET request to Shelly device
                response = requests.get(f"{base_url}/{api_endpoint}", auth=HTTPBasicAuth(shelly_device['username'], shelly_device['password']))

                ### Check if the request was successful
                if response.status_code == 200:
                    shelly_data = response.json()
                    metrics = shelly_device["metrics"]

                    ### Set Prometheus metrics
                    metrics["temperature"].set(shelly_data.get("switch:0", {}).get("temperature", {}).get("tC"))
                    metrics["uptime"].set(shelly_data.get("sys", {}).get("uptime"))
                    metrics["power"].set(shelly_data.get("switch:0", {}).get("apower", None))
                else:
                    print(f"Failed to fetch Shelly metrics for {shelly_device['ip']}. Status code: {response.status_code}")
                    raise Exception(f"Failed to fetch Shelly metrics for {shelly_device['ip']}. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    ### Return Prometheus metrics
    return generate_latest(REGISTRY)

if __name__ == '__main__':
    app.run()
