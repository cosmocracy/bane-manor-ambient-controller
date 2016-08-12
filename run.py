__author__ = "Eric Kramer"
__copyright__ = "Copyright (C) Eric Kramer"

import logging
import os
import signal
import socket
import sys
import time
import paho.mqtt.client as mqtt

# Pull MQTT server connect info from environment
mqtt_host = os.environ.get('MQTT_HOST', 'localhost')
mqtt_port = int(os.environ.get('MQTT_PORT', '1883'))
mqtt_username = os.environ.get('MQTT_USERNAME', None)
mqtt_password = os.environ.get('MQTT_PASSWORD', None)
mqtt_client_id = os.environ.get('MQTT_CLIENT_ID', 'ambient-controller')
mqtt_top_level_topic = '/fireblimp/out/#'

# Number of seconds after sensors close to still notify (glow) of recent open status
GLOW_DELAY = 120

# Number of seconts after start to ignore "closed" event messages (i.e., retained close event messages)
IGNORE_RETAINED_CLOSE_DURATION = 5

# Connection time (so we can ignore any retained messages
connect_time = time.time()

# MQTT topic info for our sensors
mqtt_front_door_topic = '/fireblimp/out/16'
mqtt_front_door_open = '0'
mqtt_front_door_closed = '1'
mqtt_front_gate_topic = '/fireblimp/out/15'
mqtt_front_gate_open = '0'
mqtt_front_gate_closed = '1'
mqtt_back_door_west_topic = '/fireblimp/out/22'
mqtt_back_door_west_open = '0'
mqtt_back_door_west_closed = '1'
mqtt_back_door_east_topic = '/fireblimp/out/18'
mqtt_back_door_east_open = '0'
mqtt_back_door_east_closed = '1'
mqtt_back_gate_topic = '/fireblimp/out/13'
mqtt_back_gate_open = '0'
mqtt_back_gate_closed = '1'

# Variables to track last activity timestamps by sensor
front_door_last_open = 0
front_door_last_closed = 0
front_gate_last_open = 0
front_gate_last_closed = 0
back_door_west_last_open = 0
back_door_west_last_closed = 0
back_door_east_last_open = 0
back_door_east_last_closed = 0
back_gate_last_open = 0
back_gate_last_closed = 0

# Connect to MQTT broker (clean session since we only want new events)
mqttc = mqtt.Client(mqtt_client_id, clean_session=True)

# MQTT callbacks
def on_connect(mosq, obj, result_code):
    """
    Handle connections (or failures) to the broker.
    This is called after the client has received a CONNACK message
    from the broker in response to calling connect().
    The parameter rc is an integer giving the return code:
    0: Success
    1: Refused . unacceptable protocol version
    2: Refused . identifier rejected
    3: Refused . server unavailable
    4: Refused . bad user name or password (MQTT v3.1 broker only)
    5: Refused . not authorised (MQTT v3.1 broker only)
    """
    global connect_time
    if result_code == 0:
        print("Connected to %s:%s" % (mqtt_host, mqtt_port))
        # Subscribe to our incoming topic
        connect_time = time.time()
        mqttc.subscribe(mqtt_top_level_topic, qos=0)
    elif result_code == 1:
        print("Connection refused - unacceptable protocol version")
    elif result_code == 2:
        print("Connection refused - identifier rejected")
    elif result_code == 3:
        print("Connection refused - server unavailable")
    elif result_code == 4:
        print("Connection refused - bad user name or password")
    elif result_code == 5:
        print("Connection refused - not authorised")
    else:
        print("Connection failed - result code %d" % (result_code))

def on_message(mosq, obj, msg):
    """
    Handle incoming messages
    """
    global front_door_last_open
    global front_door_last_open
    global front_door_last_closed
    global front_gate_last_open
    global front_gate_last_closed
    global back_door_west_last_open
    global back_door_west_last_closed
    global back_door_east_last_open
    global back_door_east_last_closed
    global back_gate_last_open
    global back_gate_last_closed
    global connect_time

    print("Message: topic=%s, payload=%s", (msg.topic, msg.payload))

    if (time.time() - connect_time) < IGNORE_RETAINED_CLOSE_DURATION and msg.payload == "1":
        print "(Ignoring retained closed message)"
        return

    if msg.topic == mqtt_front_door_topic:
        if msg.payload == mqtt_front_door_open:
            front_door_last_open = time.time()
        elif msg.payload == mqtt_front_door_closed:
            front_door_last_closed = time.time()

    if msg.topic == mqtt_front_gate_topic:
        if msg.payload == mqtt_front_gate_open:
            front_gate_last_open = time.time()
        elif msg.payload == mqtt_front_gate_closed:
            front_gate_last_closed = time.time()

    if msg.topic == mqtt_back_door_west_topic:
        if msg.payload == mqtt_back_door_west_open:
            back_door_west_last_open = time.time()
        elif msg.payload == mqtt_back_door_west_closed:
            back_door_west_last_closed = time.time()

    if msg.topic == mqtt_back_door_east_topic:
        if msg.payload == mqtt_back_door_east_open:
            back_door_east_last_open = time.time()
        elif msg.payload == mqtt_back_door_east_closed:
            back_door_east_last_closed = time.time()

# TODO - Debug wiring of gate... For now force closed
    back_gate_last_closed = time.time() - 60*10
#    if msg.topic == mqtt_back_gate_topic:
#        if msg.payload == mqtt_back_gate_open:
#            back_gate_last_open = time.time()
#        elif msg.payload == mqtt_back_gate_closed:
#            back_gate_last_closed = time.time()

    print("--- EVENT: %s, %s", (msg.topic, msg.payload))
    print("front_door_last_open = %s", front_door_last_open)
    print("front_door_last_closed = %s", front_door_last_closed)
    print("front_gate_last_open = %s", front_gate_last_open)
    print("front_gate_last_closed = %s", front_gate_last_closed)
    print("back_door_west_last_open = %s", back_door_west_last_open)
    print("back_door_west_last_closed = %s", back_door_west_last_closed)
    print("back_door_east_last_open = %s", back_door_east_last_open)
    print("back_door_east_last_closed = %s", back_door_east_last_closed)
    print("back_gate_last_open = %s", back_gate_last_open)
    print("back_gate_last_closed = %s", back_gate_last_closed)

    print("--- ANALYSIS")
    # Entry doors open
    if front_door_last_open > front_door_last_closed or \
       back_door_east_last_open > back_door_east_last_closed or   \
       back_door_west_last_open > back_door_west_last_closed:
         print "Entry door open"
         # Pulsate red
         mqttc.publish(topic="ambient/input", payload="throb:255:0:0:", retain=True)
    elif front_gate_last_open > front_gate_last_closed  or \
         back_gate_last_open > back_gate_last_closed:
         print "Gate open"
         # Pulsate yellow
         mqttc.publish(topic="ambient/input", payload="throb:255:255:0:", retain=True)


def on_disconnect(mosq, obj, result_code):
    """
    Handle disconnections from the broker
    """
    if result_code == 0:
        print("Clean disconnection from broker")
    else:
        print("Broker connection lost. Retrying in 5s...")
        time.sleep(5)

def cleanup(signum, frame):
    mqttc.disconnect()
    mqttc.loop_stop()
    print("Exiting on signal %d" % (signum))
    sys.exit(signum)

def connect():
    """
    Connect to the broker, define the callbacks, and subscribe
    """
    # Add the callbacks
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    mqttc.on_message = on_message

    # Set the login details
    if mqtt_username:
        mqttc.username_pw_set(mqtt_username, mqtt_password)

    # Attempt to connect
    print("Connecting to %s:%d..." % (mqtt_host, mqtt_port))
    try:
        mqttc.connect(mqtt_host, mqtt_port, 60)
    except Exception, e:
        print("Error connecting to %s:%d: %s" % (mqtt_host, mqtt_port, str(e)))
        sys.exit(2)

    # Let the message handling run constantly (in the background)
    mqttc.loop_start()

def poll():
    global front_door_last_open
    global front_door_last_open
    global front_door_last_closed
    global front_gate_last_open
    global front_gate_last_closed
    global back_door_west_last_open
    global back_door_west_last_closed
    global back_door_east_last_open
    global back_door_east_last_closed
    global back_gate_last_open
    global back_gate_last_closed

    # Loop indefinitely
    while True:
        # Yield (e.g., allow MQTT message handling)
        time.sleep(1)
        # Skip remaining logic if any sensors open
        if front_door_last_open > front_door_last_closed or \
           back_door_east_last_open > back_door_east_last_closed or   \
           back_door_west_last_open > back_door_west_last_closed or \
           front_gate_last_open > front_gate_last_closed  or \
           back_gate_last_open > back_gate_last_closed:
           continue
        # Else check for doors/gates that closed recently so we can glow (not flash)
        elif (time.time() - front_door_last_closed) < GLOW_DELAY or \
             (time.time() - back_door_east_last_closed) < GLOW_DELAY or   \
             (time.time() - back_door_west_last_closed) < GLOW_DELAY:
            print "Entry door closed but was open recently"
            # Glow  red
            mqttc.publish(topic="ambient/input", payload="glow:255:0:0:", retain=True)
        elif (time.time() - front_gate_last_closed) < GLOW_DELAY  or \
             (time.time() - back_gate_last_closed) < GLOW_DELAY:
            print "Gate closed but was open recently"
            # Glow yellow
            mqttc.publish(topic="ambient/input", payload="glow:255:255:0:", retain=True)
        else:
           # Happiness
           # print "All clear"
           mqttc.publish(topic="ambient/input", payload="glow:0:50:50:", retain=True)

# Start everything up!
connect()
poll()
