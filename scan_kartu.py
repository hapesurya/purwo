import paho.mqtt.client as mqtt
import json
import time


# Replace with your MQTT broker host and port
broker_host = "localhost"
broker_port = 1883
topic_template = "mqtt/face/{}/Card"
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
    "1962857",
    "1962858",
    "1992021"]

# Replace with the actual list of cards
allowed_cards = [
    "1673558526",
    "3008662014",
    "6409902",
    "1673431294",
    "861887743",
    "857836286",
    "2199811582",
    "1131969022",
    "326791934",
    "3013380862",
    "861239038",
    "60326398",
    "3272045054",
    "3549239550",
    "591731710",
    "328104190",
    "326006782",
    "2746976766",
    "50427902",
    "2208465662",
    "2214554110",
    "595620350",
    "3018853630",
    "2478377726",
    "1667045886",
    "4077195006",
    "2740848638",
    "55450110",
    "862653950",
    "1124629502",
    "1127040517",
    "4087495941",
    "320828926",
    "3553324030",
    "1666139653",
    "3018481919",
    "1406366974",
    "596998654",
    "602307326",
    "3275781886",
    "3814817278",
    "1397192446",
    "591165182",
    "3276895998",
    "3007143167",
    "3815344126",
    "2212251909",
    "2474593797",
    "1408862974",
    "2205187838"]

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    for face_id in face_ids:
        client.subscribe(topic_template.format(face_id))

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        card_num = payload.get("info", {}).get("CardInfo",{}).get('CardNum', '')
        
        if card_num and card_num in allowed_cards:
            # Replace <ID> with the actual ID extracted from the topic
            face_id = msg.topic.split("/")[2]

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
            
            # Publish messages on the topic "mqtt/face/<ID>"
            client.publish(f"mqtt/face/{face_id}", payload=msg_unlock)
            time.sleep(1)
            client.publish(f"mqtt/face/{face_id}", payload=msg_voiceplay)
            print(f"Messages published for face ID {face_id}")
        else:
            print(card_num)
            print("Card not authorized.")
    except Exception as e:
        print(f"Error processing message: {str(e)}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Replace with your MQTT broker username and password if applicable
client.username_pw_set(username="admin", password="admin")

client.connect(broker_host, broker_port, 60)

client.loop_forever()
