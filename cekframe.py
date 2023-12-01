from flask import Flask, render_template, request, redirect, url_for, session
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# MQTT configuration
mqtt_broker_address = "localhost"
mqtt_port = 1883
mqtt_topic_template = "mqtt/face/{}/Ack"

client_ids = ["ID1", "ID2", "ID3"]

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to the Ack topics for all clients
    for client_id in client_ids:
        client.subscribe(mqtt_topic_template.format(client_id))

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload} on topic: {msg.topic}")
        
    # Check if the message contains a JSON payload
    try:
        payload_json = json.loads(msg.payload)
        code_value = payload_json.get("code")
        print(f"Code value: {code_value}")
        if code_value is not None and code_value != "200":
            # Set a session variable to indicate an issue with the response
            session["upgrade_response_issue"] = True
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON payload: {e}")

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker_address, mqtt_port)
mqtt_client.loop_forever()

@app.route('/upgrade', methods=['GET', 'POST'])
def upgrade():
    service_key = 'upgrade'
    
    # Check if there was an issue with the response in the session
    if session.pop("upgrade_response_issue", False):
        return render_template('mqttgate/error.html', error_message="Invalid response from MQTT")

    if request.method == 'POST':
        session['queue_number_' + service_key] += 1
        return "BERHASIL"

    return render_template('mqttgate/peningkatan.html', session=session['queue_number_' + service_key])

if __name__ == '__main__':
    app.run(debug=True)
