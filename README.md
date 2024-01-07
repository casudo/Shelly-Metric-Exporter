<div align="center">
  <h1>Shelly Metric Exporter (SMEX)</h1>
  The <b>S</b>helly <b>M</b>etric <b>Ex</b>porter is a Prometheus exporter for Shelly devices. It is written in Python and uses the <a href="https://shelly-api-docs.shelly.cloud/">Shelly API</a> to retrieve the data.

  ---

  <!-- Placeholder for badges -->
  ![GitHub License](https://img.shields.io/github/license/casudo/Shelly-Metric-Exporter) ![GitHub release (with filter)](https://img.shields.io/github/v/release/casudo/Shelly-Metric-Exporter)
</div>

> Note: This is a hobby project and still in development. It is not recommended to use it in production environments yet. Feel free to create issues and contribute.

##### Table of Contents
- [Installation](#installation)
- [Docker](#docker)
  - [Environment variables](#environment-variables)
  - [docker run](#docker-run)
  - [Docker Compose](#docker-compose)
- [Planned for the future](#planned-for-the-future)
- [License](#license)

## Installation
To make full use of the Shelly Metric Exporter, you need to have a Prometheus server running. If you don't have one yet, you can find a guide [here](https://prometheus.io/docs/prometheus/latest/getting_started/). Edit your `prometheus.yml` file and add the following lines to include the Shelly Metric Exporter (SMEX):
```yaml
scrape_configs:
  - job_name: smex
    scrape_interval: 15s # you can leave this out if you want to use the default value
    static_configs:
      - targets: [<CONTAINER_NAME>:<EXPOSED_PORT>]
```

Make sure that your Prometheus server can reach the SMEX container.  
> NOTE: If you are running both containers in the same network (other than Dockers default **bridge** network!), you can use the container name as the target.
> The default **bridge** network does not allow containers to communicate with each other by their name ([source](https://docs.docker.com/network/drivers/bridge/#connect-a-container-to-the-default-bridge-network)).

# Docker
If you want to run this in a Docker container, you'll first need to set some mandatory environment variables:  

**Required:**
| Variable |  Description |
| --- | --- |
| `D1_DEVICETYPE` | Supported devices types are: `plugs`, `1` |
| `D1_HOST` | IP address of the Shelly device |
| `DISCORD_WEBHOOK` | The Discord webhook URL to send notifications to. |

**Optional:**
| Variable |  Description |
| --- | --- |
| `EXPORTER_PORT` | The port the exporter should listen on. If not set, defaults to `5000`. |
| `D1_PORT` | Port of the Shelly device. If not set, defaults to `80`. |
| `D1_USERNAME` | Username of the Shelly device if authentication is enabled. |
| `D1_PASSWORD` | Password of the Shelly device if authentication is enabled. |


You can add as many devices as you want, just follow the above format like this:  

| Variable | Required | Description |
| --- | --- | --- |
| `D<n>_DEVICETYPE` | **Yes** | Supported devices types are: `plugs`, `1` |
| `D<n>_HOST` | **Yes** | IP address of the Shelly device |
| `D<n>_PORT` | No | Port of the Shelly device. If not set, defaults to `80`. |
| `D<n>_USERNAME` | No | Username of the Shelly device if authentication is enabled. |
| `D<n>_PASSWORD` | No | Password of the Shelly device if authentication is enabled. |

## docker run
```bash
docker run -d \
  --name=smex \
  --restart=unless-stopped \
  -p <host_port>:<exposed_port>
  -e D1_DEVICETYPE=<device_type> \
  -e D1_HOST=<ip_address> \
  -e DISCORD_WEBHOOK=<discord_webhook_url> \
  -e TZ=<your_timezone> \
  <image_name>:<tag>
```

You can choose between two different image providers:
- Docker Hub: [casudo1/smex]()
- GitHub: [ghcr.io/casudo/smex]()

## Docker Compose
```yaml
version: "3.8"

services:
  smex:
    image: <image_name>:<tag>
    container_name: smex
    restart: unless-stopped
    ports:
      - <host_port>:<exposed_port>
    environment:
        - D1_DEVICETYPE=<device_type>
        - D1_HOST=<ip_address>
        - DISCORD_WEBHOOK=<discord_webhook_url>
        - TZ=<your_timezone>
```

## Plannend for the future
- Add support for more devices
- Add support for more metrics
- Add support for more notification services
- Add frontend for easier configuration

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details