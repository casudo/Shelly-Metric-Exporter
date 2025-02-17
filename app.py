import requests
import prometheus_client as prom

from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, REGISTRY
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
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
        "name": getenv(f"D{device_number}_NAME", ip), # Optional
        "username": getenv(f"D{device_number}_USERNAME", None), # Optional
        "password": getenv(f"D{device_number}_PASSWORD", None) # Optional
    })
    device_number += 1
print(f"-> Found {len(shelly_device_list)} Shelly devices.\n")


### Create Prometheus metrics for each Shelly device
def create_metrics():
    ### Create Prometheus metrics with labels instead of dynamically generated names
    return {
        "temperature": Gauge("shelly_temperature", "Temperature from Shelly Device", ["instance"]),
        "uptime": Gauge("shelly_uptime", "Uptime from Shelly Device", ["instance"]),
        "power": Gauge("shelly_power_consumption", "Shelly power consumption from Shelly Device", ["instance"]),
        "has_update": Gauge("shelly_has_update", "Shelly has new firmware available", ["instance"])
    }

### Call the function to create Prometheus metrics for all devices
global_metrics = create_metrics()


### API endpoint for Prometheus metrics
@app.route("/metrics")
def metrics():
    ### Loop through all Shelly devices and fetch metrics
    for shelly_device in shelly_device_list:
        base_url = f"http://{shelly_device['ip']}:{shelly_device['port']}"

        ### Determine the API endpoint based on generation
        if shelly_device["gen"] == "1":
            api_endpoint = "status"
        elif shelly_device["gen"] == "2":
            api_endpoint = "rpc/Shelly.GetStatus"
        else:
            print(f"Unknown generation for {shelly_device['ip']}. Skipping.")
            continue

        try:
            ### Fetch data from the Shelly device
            if shelly_device["gen"] == "2":
                if shelly_device["password"]:
                    ### Initial request to get the WWW-Authenticate header
                    initial_response = requests.get(f"{base_url}/{api_endpoint}", timeout=5)
                    if initial_response.status_code == 401:
                        ### Extract realm, nonce, and algorithm from WWW-Authenticate header
                        auth_header = initial_response.headers.get("WWW-Authenticate")
                        if auth_header:
                            auth = HTTPDigestAuth("admin", shelly_device["password"])
                            response = requests.get(f"{base_url}/{api_endpoint}", auth=auth, timeout=5)
                        else:
                            print(f"Failed to get WWW-Authenticate header from {shelly_device['ip']}.")
                            continue
                    else:
                        response = initial_response
                else:
                    response = requests.get(f"{base_url}/{api_endpoint}", timeout=5)
            else:
                response = requests.get(
                    f"{base_url}/{api_endpoint}",
                    auth=HTTPBasicAuth(shelly_device["username"], shelly_device["password"]),
                    timeout=5
                )
            response.raise_for_status()
            shelly_data = response.json()

            ### Parse and set metrics based on device generation
            if shelly_device["gen"] == "1":
                temperature = shelly_data.get("temperature", 0)
                uptime = shelly_data.get("uptime", 0)
                power = shelly_data.get("meters", [{}])[0].get("power", 0)
            elif shelly_device["gen"] == "2":
                temperature = shelly_data.get("switch:0", {}).get("temperature", {}).get("tC", 0)
                uptime = shelly_data.get("sys", {}).get("uptime", 0)
                power = shelly_data.get("switch:0", {}).get("apower", 0)

            ### Update Prometheus metrics with labels
            global_metrics["temperature"].labels(instance=shelly_device["name"]).set(float(temperature))
            global_metrics["uptime"].labels(instance=shelly_device["name"]).set(float(uptime))
            global_metrics["power"].labels(instance=shelly_device["name"]).set(float(power))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching metrics from {shelly_device['ip']}: {e}")
            continue
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error fetching metrics from IP {shelly_device['ip']}: {e}")
            continue
        except Exception as e:
            print(f"Unknown error appeared while fetching IP {shelly_device['ip']}: {e}")
            continue

    ### Return Prometheus metrics
    return Response(generate_latest(REGISTRY), mimetype="text/plain; charset=utf-8")


if __name__ == '__main__':
    app.run()
