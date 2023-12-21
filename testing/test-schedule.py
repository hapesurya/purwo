import schedule
import time
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

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
    "1962857", 
    "1962858", 
    "1992021"]

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

def mqtt_publisher_job():
    # Run MQTT publisher function for each ID
    for client_id in face_ids:
        topic = f"mqtt/face/{client_id}"
        message = msg_deleteallperson
        publish.single(topic=topic, payload=message, hostname='localhost', port=1883, auth={'username': 'admin', 'password': 'admin'})

#schedule.every().day.at("10:30").do(mqtt_publisher_job)
schedule.every().day.at("15:50", "Asia/Jakarta").do(mqtt_publisher_job)

while True:
    schedule.run_pending()
    time.sleep(1)