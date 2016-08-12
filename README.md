# bane-manor-ambient-controller

## Execution
* Run interactively via Docker: 
  * ```docker build --rm=true -t ambient-controller .```
  * ```docker run --rm -e MQTT_HOST=192.168.1.118 -ti ambient-controller```
* Run background via Docker:
  * ```docker build --rm=true -t ambient-controller .```
  * ```docker run -d -e MQTT_HOST=mosquitto --link mosquitto -it --name ambient-controller ambient-controller```
