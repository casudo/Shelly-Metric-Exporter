import subprocess
from os import getenv

### ===============================================================================

### Get the environment variables
D1_SHELLY_DEVICETYPE = getenv("D1_SHELLY_DEVICETYPE")
D1_SHELLY_HOST = getenv("D1_SHELLY_HOST")
D1_SHELLY_PORT = getenv("D1_SHELLY_PORT")
D1_SHELLY_USERNAME = getenv("D1_SHELLY_USERNAME", None)
D1_SHELLY_PASSWORD = getenv("D1_SHELLY_PASSWORD", None)

DISCORD_WEBHOOK = getenv("DISCORD_WEBHOOK")
EXPORTER_PORT = getenv("EXPORTER_PORT", 5000)

### Display a welcoming message in Docker logs
print("👍 Container started. Welcome!")
print("⏳ Checking environment variables...")

### Check if the environment variables are set
### Required one device
if D1_SHELLY_DEVICETYPE is None or D1_SHELLY_HOST is None or D1_SHELLY_PORT is None: 
    print("  ❌ D1 information are not fully set. Exiting...")
    exit()
else:
    print("  ✅ D1 information are set.")
### Check for optional D1 device username and password
if D1_SHELLY_USERNAME is not None and D1_SHELLY_PASSWORD is not None:
    print("  ✅ D1 credentials are set.")
elif D1_SHELLY_USERNAME is not None and D1_SHELLY_PASSWORD is None:
    print("  ❌ D1 username is set but password is missing. Exiting...")
    exit()
elif D1_SHELLY_USERNAME is None and D1_SHELLY_PASSWORD is not None:
    print("  ❌ D1 password is set but username is missing. Exiting...")
    exit()
else:
    print("  ⚠️ D1 doesn't require credentials.")

### Discord Webhook URL
if DISCORD_WEBHOOK is None:
    print("  ❌ DISCORD_WEBHOOK is not set. Exiting...")
    exit()
else:
    print("  ✅ DISCORD_WEBHOOK is set.")

### Exporter Port
if EXPORTER_PORT == 5000:
    print("  ✅ Using default value exporter port 5000.")
### TODO: Add port check
else:
    print("  ✅ Using custom value exporter port " + str(EXPORTER_PORT) + ".")

### Check for additional optional devices starting from D2 and beyond
device_number = 2
while True:
    devicetype = getenv(f"D{device_number}_SHELLY_DEVICETYPE")
    host = getenv(f"D{device_number}_SHELLY_HOST")
    port = getenv(f"D{device_number}_SHELLY_PORT")
    username = getenv(f"D{device_number}_SHELLY_USERNAME", None)
    password = getenv(f"D{device_number}_SHELLY_PASSWORD", None)

    ### TODO: Add check for device type (plugs, 3em, etc.)
    if devicetype is None and host is None and port is None:
        break
    elif devicetype is None or host is None or port is None:
        print(f"  ❌ D{device_number} information are not fully set. Exiting...")
        exit()
    else:
        print(f"  ✅ D{device_number} information are set.")

    ### Check for optional D{n} device username and password
    if username is not None and password is not None:
        print(f"  ✅ D{device_number} credentials are set.")
    elif username is not None and password is None:
        print(f"  ❌ D{device_number} username is set but password is missing. Exiting...")
        exit()
    elif username is None and password is not None:
        print(f"  ❌ D{device_number} password is set but username is missing. Exiting...")
        exit()
    else:
        print(f"  ⚠️ D{device_number} doesn't require credentials.")

    device_number += 1

### ===============================================================================

print("\n🚀 Starting SMEX...")
flask_api = subprocess.run(["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0", f"--port={EXPORTER_PORT}"])
