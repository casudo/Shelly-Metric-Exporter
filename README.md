<div align="center">
  <h1>Shelly Metric Exporter (SMEX)</h1>
  The <b>S</b>helly <b>M</b>etric <b>Ex</b>porter is a Prometheus exporter for Shelly devices. It is written in Python and uses the <a href="https://shelly-api-docs.shelly.cloud/">Shelly API</a> to retrieve the data.

  ---

  <!-- Placeholder for badges -->
  ![GitHub License](https://img.shields.io/github/license/casudo/Shelly-Metric-Exporter) ![GitHub release (with filter)](https://img.shields.io/github/v/release/casudo/Shelly-Metric-Exporter)
  ![Docker Pulls](https://img.shields.io/docker/pulls/casudo1/smex) ![Docker Stars](https://img.shields.io/docker/stars/casudo1/smex) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/casudo1/smex/latest)
</div>

> [!NOTE]
This is a hobby project and still in development.

##### Table of Contents
- [Supported devices](#supported-devices)
- [Installation](#installation)
- [Docker](#docker)
  - [Environment variables](#environment-variables)
  - [docker run](#docker-run)
  - [Docker Compose](#docker-compose)
- [Planned for the future](#planned-for-the-future)
- [License](#license)

# Supported devices
Currently, all Gen 1 and Gen 2+ Shelly devices are supported. Keep in mind that not all devices have the metrics which are currently implemented and therefore might not work as expected! For example, not every device has a metric for the temperature.  

If your device is not fully supported, feel free to create an issue or contribute to the project.  

> [!TIP]
> You can see the API documentation for your device here:  
> [Gen 1](https://shelly-api-docs.shelly.cloud/gen1/)  
> [Gen 2+](https://shelly-api-docs.shelly.cloud/gen2/)

# Installation
To make full use of the Shelly Metric Exporter, you need to have a Prometheus server running. If you don't have one yet, you can find a guide [here](https://prometheus.io/docs/prometheus/latest/getting_started/). Edit your `prometheus.yml` file and add the following lines to include the Shelly Metric Exporter (SMEX):
```yaml
scrape_configs:
  - job_name: smex
    scrape_interval: 15s # you can leave this out if you want to use the default value
    static_configs:
      - targets: [<CONTAINER_NAME>:<EXPOSED_PORT>]
```

Make sure that your Prometheus server can reach the SMEX container.  
> [!NOTE]
> If you are running both containers in the same network (other than Dockers default **bridge** network!), you can use the container name as the target.
> The default **bridge** network does not allow containers to communicate with each other by their name ([source](https://docs.docker.com/network/drivers/bridge/#connect-a-container-to-the-default-bridge-network)).

# Docker
If you want to run this in a Docker container, you'll first need to set some mandatory environment variables:  

**Required:**
| Variable |  Description |
| --- | --- |
| `D1_GEN` | Supported generations are: `1`, `2` |
| `D1_IP` | IP address of the Shelly device |

**Optional:**
| Variable |  Description |
| --- | --- |
| `EXPORTER_PORT` | The port the exporter should listen on. If not set, defaults to `5000`. |
| `D1_PORT` | Port of the Shelly device. If not set, defaults to `80`. |
| `D1_USERNAME` | Username of the Shelly device if authentication is enabled. Defaults is `None`. |
| `D1_PASSWORD` | Password of the Shelly device if authentication is enabled. Defaults is `None`. |

You can add as many devices as you want, just follow the above format like this:  

| Variable | Required | Description |
| --- | --- | --- |
| `D<n>_GEN` | **Yes** | Supported generations are: `1`, `2` |
| `D<n>_IP` | **Yes** | IP address of the Shelly device |
| `D<n>_PORT` | No | Port of the Shelly device. If not set, defaults to `80`. |
| `D<n>_USERNAME` | No | Username of the Shelly device if authentication is enabled. Defaults is `None`. |
| `D<n>_PASSWORD` | No | Password of the Shelly device if authentication is enabled. Defaults is `None`. |

## docker run
```bash
docker run -d \
  --name=smex \
  --restart=unless-stopped \
  -p <host_port>:<exposed_port>
  -e D1_GEN=<device_generation> \
  -e D1_IP=<ip_address> \
  -e TZ=<your_timezone> \
  <image_name>:latest
```

You can choose between two different image providers:
- Docker Hub: [casudo1/smex](https://hub.docker.com/r/casudo1/smex)
- GitHub: [ghcr.io/casudo/smex](https://github.com/casudo/Shelly-Metric-Exporter/pkgs/container/smex)

## Docker Compose
```yaml
version: "3.8"

services:
  smex:
    image: <image_name>:latest
    container_name: smex
    restart: unless-stopped
    ports:
      - <host_port>:<exposed_port>
    environment:
        - D1_GEN=<device_generation>
        - D1_IP=<ip_address>
        - TZ=<your_timezone>
```

## Plannend for the future
- Add support for metrics which are device-specific 
- Add support for more metrics in general
- Add support for notification services (such as Discord)
- Add frontend for easier configuration instead of environment variables

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details