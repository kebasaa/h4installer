import sys
import time
import paho.mqtt.client as mqtt
device=sys.argv[1][-6:]

def on_connect(client, userdata, flags, rc):
#    print("Connected with result code "+str(rc)+" pub "+device+"/h4/toggle")
    client.publish(device+"/h4/toggle")

def on_publish(client,userdata,mid):
    client.disconnect()
    exit(0)

client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

client.connect("192.168.1.4", 1883, 60)
client.loop_forever()