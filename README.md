# bane-manor-ambient-controller

## Prerequisites
* Install PAHO MQTT client for Python: ```sudo pip install paho-mqtt```
* Run via Docker: 
  * docker build --rm=true -t ambient-controller .
  * docker run --rm -e MQTT_HOST=192.168.1.118 -ti ambient-controller

