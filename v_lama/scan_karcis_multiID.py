import paho.mqtt.client as mqtt
import json
import time

# MQTT configuration
broker_host = "localhost"
broker_port = 1883
mqtt_clients=[]
nclients=11
username = "admin"
password = "admin"
topic_template = "mqtt/face/{}/QRCode"
msg_id = round(time.time()*1000)

#create clients
for i in range(nclients):
    cname="P"+str(i)
    mqtt_clients.append(cname)

#Daftar FaceID nya
face_ids = [
    "1962821", 
    "1962822", 
    "1962823", 
    "1962824", 
    "1962825", 
    "1962826", 
    "1962827", 
    "1962828", 
    "1962829", 
    "1962830", 
    "1962831"]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to the topic when connected
        for face_id in face_ids:
            client.subscribe(topic_template.format(face_id))
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload} on topic: {msg.topic}")
    
    # Extract ID from the received topic
    topic_parts = msg.topic.split("/")
    if len(topic_parts) == 4:
        face_id = topic_parts[2]
        
        # Create an MQTT publisher
        publisher = mqtt.Client()
        publisher.username_pw_set(username=username, password=password)
        publisher.connect(broker_host, broker_port)

        msg_unlock = {
            "operator": "Unlock",
            "messageId":"{}".format(msg_id),
            "info": {
                "uid":"00021",
                "openDoor":"1",
                "Showinfo": "please pass"
                }
            }
        
        msg_unlock = json.dumps(msg_unlock, indent = 4)

        msg_voiceplay = {
            "operator":"voiceplay", 
            "messageId":"{}".format(msg_id),
            "info": {
                "UsrType":"1",
                "voicetype":"welcome.wav"
                }
            }
        
        msg_voiceplay = json.dumps(msg_voiceplay, indent = 4)
        
        # Publish messages with the specified topics
        publisher.publish(f"mqtt/face/{face_id}", payload=msg_unlock)
        time.sleep(1)
        publisher.publish(f"mqtt/face/{face_id}", payload=msg_voiceplay)
        
        # Disconnect the publisher
        publisher.disconnect()

# Set up MQTT client
for mqtt_client in mqtt_clients:
    mqtt_client_id = mqtt.Client(mqtt_client)
    mqtt_client_id.username_pw_set(username=username, password=password)
    mqtt_client_id.on_connect = on_connect
    mqtt_client_id.on_message = on_message
    mqtt_client_id.connect(broker_host, broker_port)
    mqtt_client_id.loop_forever()
