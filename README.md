# TIM
Autonomous traffic management for autonomous vehicles
### Wolfbot
Beaglebone Black based bot with 4 wheels and a bunch of sensors. We mainly use an IR sensor and a color sensor along with WiFi adapter for network connectivity.
https://research.ece.ncsu.edu/aros/project/wolfbot/
### TIM (Traffic Intersection Manager)
Software that handles traffic at junctions. It's goal is to avoid collisions and optimally control traffic.

### Dependencies
#### Install Mosquitto server
```
sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
sudo apt-get update
sudo apt-get install mosquitto
```

#### Install MQTT client for Python
`sudo pip install paho-mqtt`
