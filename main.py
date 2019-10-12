import datetime
import time
import math
import paho.mqtt.client as mqtt
import onzo.device
import os

sensor_name = os.environ["SENSOR_NAME"]
username = os.environ["MQTT_USERNAME"]
password = os.environ["MQTT_PASSWORD"]
hostname = os.environ["MQTT_HOSTNAME"]
port = os.getenv('MQTT_PORT', 1883)

topic_prefix = "homeassistant/sensor/"+sensor_name

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code "+str(rc))
    client.publish(topic_prefix+"/power/config","{\"device_class\": \"power\", \"name\": \""+sensor_name+" power\", \"state_topic\": \""+topic_prefix+"/state\", \"unit_of_measurement\": \"W\", \"unique_id\":\""+sensor_name+"power\", \"value_template\": \"{{ value_json.power}}\" }", 0, True)
    client.publish(topic_prefix+"/battery/config","{\"name\": \""+sensor_name+" battery\", \"state_topic\": \""+topic_prefix+"/state\", \"unit_of_measurement\": \"mV\", \"unique_id\":\""+sensor_name+"battery\", \"value_template\": \"{{ value_json.battery}}\" }", 0, True)


conn = onzo.device.Connection()
try:
    conn.connect()
    disp = onzo.device.Display(conn)
    clamp = onzo.device.Clamp(conn)

    print("Connected to meter")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.username_pw_set(username,password)
    client.connect(hostname, port, 60)
  
    client.loop_start()  

    p_reactive = None
    counter = 0
    while True:
        p_real = clamp.get_power()

        # reactive power only updates onces every 15s, so there is no use
        # querying more often, this just wastes clamp battery
        p_reactive = clamp.get_powervars()
        # Only update battery once every 10mins
        if counter % (20) == 0:
            battery = clamp.get_batteryvolts()

        p_apparent = int(math.sqrt(p_real**2 + p_reactive**2))
        ear = clamp.get_cumulative_kwh()

        client.publish(topic_prefix+"/state","{\"power\":\""+str(p_real)+"\", \"battery\":\""+str(battery)+"\"}")

        counter += 1
        time.sleep(30)

finally:
    conn.disconnect()
