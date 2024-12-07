import subprocess
from os import getenv

### ===============================================================================

### Get the environment variables
D1_GEN = getenv("D1_GEN")
D1_IP = getenv("D1_IP")
D1_PORT = getenv("D1_PORT", 80)
D1_USERNAME = getenv("D1_USERNAME", None)
D1_PASSWORD = getenv("D1_PASSWORD", None)

EXPORTER_PORT = getenv("EXPORTER_PORT", 5000)

### Display a welcoming message in Docker logs
print("👍 Container started. Welcome!")
print("⏳ Checking environment variables...")

### Check if the environment variables are set
### Exporter Port
if EXPORTER_PORT == 5000:
    print("  ✅ Using default exporter port 5000.")
### TODO: Add port check
else:
    print(f"  ✅ Using custom exporter port {EXPORTER_PORT}.")
    
### Required one device
if D1_GEN is None or D1_IP is None: 
    print("  ❌ D1 information are not fully set. Exiting...")
    exit()
else:
    print("  ✅ D1 information are set.")
### Check for optional D1 device port
if D1_PORT == 80:
    print("  ✅ D1 using default port 80.")
else:
    print(f"  ✅ D1 using custom port {D1_PORT}.")
### Check for optional D1 device username and password
if D1_GEN == "1":
    if D1_USERNAME is not None and D1_PASSWORD is not None:
        print("  ✅ D1 credentials are set.")
    elif (D1_USERNAME is None) != (D1_PASSWORD is None):
        print("  ❌ D1 credentials are incomplete. Both username and password must be set. Exiting...")
        exit()
    else:
        print("  ⚠️ D1 doesn't require credentials.")
elif D1_GEN == "2":
    if D1_PASSWORD is not None:
        print("  ✅ D1 password is set.")
    else:
        print("  ⚠️ Warning: D1 password is not set. This is insecure.")

### Check for additional optional devices starting from D2 and beyond
device_number = 2
while True:
    gen = getenv(f"D{device_number}_GEN")
    ip = getenv(f"D{device_number}_IP")
    port = getenv(f"D{device_number}_PORT", 80)
    username = getenv(f"D{device_number}_USERNAME", None)
    password = getenv(f"D{device_number}_PASSWORD", None)

    ### TODO: Add check for device type (plugs, 3em, etc.)
    if gen is None and ip is None:
        break
    elif gen is None or ip is None:
        print(f"  ❌ D{device_number} information are not fully set. Exiting...")
        exit()
    else:
        print(f"  ✅ D{device_number} information are set.")
    ### Check for optional D{n} device port
    if port == 80:
        print(f"  ✅ D{device_number} using default port 80.")
    else:
        print(f"  ✅ D{device_number} using custom port {port}.")
    ### Check for optional D{n} device username and password
    if gen == "1":
        if username is not None and password is not None:
            print(f"  ✅ D{device_number} credentials are set.")
        elif (username is None) != (password is None):
            print(f"  ❌ D{device_number} credentials are incomplete. Both username and password must be set. Exiting...")
            exit()
        else:
            print(f"  ⚠️ D{device_number} doesn't require credentials.")
    elif gen == "2":
        if password is not None:
            print(f"  ✅ D{device_number} password is set.")
        else:
            print(f"  ⚠️ Warning: D{device_number} password is not set. This is insecure.")

    device_number += 1

### ===============================================================================

print("\n🚀 Starting SMEX...")
flask_api = subprocess.run(["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0", f"--port={EXPORTER_PORT}"])