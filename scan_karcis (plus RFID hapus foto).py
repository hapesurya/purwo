import paho.mqtt.client as mqtt
import json
import time
import schedule

# MQTT configuration
broker_host = "localhost"
broker_port = 1883
client_id = "P1"
username = "admin"
password = "admin"
topic_subsQR = "mqtt/face/{}/QRCode"
topic_subsCARD = "mqtt/face/{}/IDCard"
topic_pubFR = "mqtt/face/{}"
msg_id = round(time.time()*1000)

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

IDCARDS = [
    'CARD NUMBER 1',
    'CARD NUMBER 2',
    'CARD NUMBER 3',
    'CARD NUMBER 4',
    'CARD NUMBER 5',
    'CARD NUMBER 6',
    'CARD NUMBER 7',
    'CARD NUMBER 8',
    'CARD NUMBER 9',
    'CARD NUMBER 10',
    'CARD NUMBER 11',
    'CARD NUMBER 12',
    'CARD NUMBER 13',
    'CARD NUMBER 14',
    'CARD NUMBER 15',
    'CARD NUMBER 16',
    'CARD NUMBER 17',
    'CARD NUMBER 18',
    'CARD NUMBER 19',
    'CARD NUMBER 20',
    'CARD NUMBER 21',
    'CARD NUMBER 22',
    'CARD NUMBER 23',
    'CARD NUMBER 24',
    'CARD NUMBER 25',
    'CARD NUMBER 26',
    'CARD NUMBER 27',
    'CARD NUMBER 28',
    'CARD NUMBER 29',
    'CARD NUMBER 30',
    'CARD NUMBER 31',
    'CARD NUMBER 32',
    'CARD NUMBER 33',
    'CARD NUMBER 34',
    'CARD NUMBER 35',
    'CARD NUMBER 36',
    'CARD NUMBER 37',
    'CARD NUMBER 38',
    'CARD NUMBER 39',
    'CARD NUMBER 40',
    'CARD NUMBER 41',
    'CARD NUMBER 42',
    'CARD NUMBER 43',
    'CARD NUMBER 44',
    'CARD NUMBER 45',
    'CARD NUMBER 46',
    'CARD NUMBER 47',
    'CARD NUMBER 48',
    'CARD NUMBER 49',
    'CARD NUMBER 50',
]

def delete_data_task():
    # Schedule this task at 5 P.M. UTC+7 to publish "DELETE DATA" message for each face ID
    for face_id in face_ids:
        # Create an MQTT publisher
        publisher = mqtt.Client()
        publisher.username_pw_set(username=username, password=password)
        publisher.connect(broker_host, broker_port)

        msg_deleteallperson = {
        "messageId":"ID:devicehost-637046811507388956:23952:65:48",
        "operator":"DeleteAllPerson",
        "info":
        {
            "facesluiceId":"{}",
            "deleteall":"1",
            }
        }

        msg_deleteallperson = json.dumps(msg_deleteallperson, indent = 4)

        # Publish the "DELETE DATA" message
        publisher.publish(topic_pubFR.format(face_id), payload=msg_deleteallperson)

        # Disconnect the publisher
        publisher.disconnect()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to the topic when connected
        for face_id in face_ids:
            client.subscribe(topic_subsQR.format(face_id))
            client.subscribe(topic_subsCARD.format(face_id))
        
        # Schedule the "DELETE DATA" task at 5 P.M. UTC+7
        schedule.every().day.at("12:00").do(delete_data_task)  # Assuming the server is in UTC, change the time accordingly
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload} on topic: {msg.topic}")

    for IDCARD in IDCARDS:
        if msg.payload.decode() == IDCARD:
            pesan = IDCARD
            messages(msg.topic, pesan)
        else:
            # Extract ID from the received topic mqtt/face/ID/QRCode
            messages(msg.topic, msg.payload.decode())

def messages(topic, pesan):
    # Extract ID from the received topic mqtt/face/IDCard
    topic_parts = topic.split("/")
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
        publisher.publish(topic_pubFR.format(face_id), payload=msg_unlock)
        time.sleep(1)
        publisher.publish(topic_pubFR.format(face_id), payload=msg_voiceplay)

        # Disconnect the publisher
        publisher.disconnect()

# Set up MQTT client
client = mqtt.Client(client_id)
client.username_pw_set(username=username, password=password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_host, broker_port)
client.loop_forever()
