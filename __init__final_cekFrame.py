from flask import Flask, render_template, request, session, url_for, redirect
import paho.mqtt.client as mqtt
import datetime
import time
import qrcode
import os
from escpos.printer import Usb
import json
from flask_sqlalchemy import SQLAlchemy
from flask import flash
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

now = datetime.datetime.now()
tanggaljam_now = now.strftime("%d-%m-%Y %H:%M:%S")
datehour_now = now.strftime("%Y-%m-%d %H:%M:%S")

# MQTT configuration
mqtt_broker_address = "localhost"
mqtt_broker_port = 1883
mqtt_topic_Ack = "mqtt/face/{}/Ack"

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
    print(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to the Ack topics for all clients
    for client_id in face_ids:
        client.subscribe(mqtt_topic_Ack.format(client_id))

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload} on topic: {msg.topic}")    
    # Check if the message contains a JSON payload
    try:
        payload_json = json.loads(msg.payload)
        code_value = payload_json.get("code")
        print(code_value)
        if code_value is not None and code_value != "200":
            # Set a session variable to indicate an issue with the response
            session["upgrade_response_issue"] = True
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON payload: {e}")

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(host=mqtt_broker_address, port=mqtt_broker_port)
mqtt_client.loop_forever()

class VisitorDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.String(100), nullable=False)
    layanan = db.Column(db.String(100), nullable=False)
    antrian = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Visitor %r>' % self.id

def printkarcis(lay, ks, antrian, msg_id):
    # Setting Printer
        # Create a new instance of the printer object
        printer = Usb(0x4b43, 0x3830, 0, 0x81, 0x03)
        
        # Mulai Print Text Tiketnya
        # Set align
        printer.set(align='center')
        printer.text('SATPAS POLRES PURWOREJO\n')
        printer.text('\n')
        printer.set(align='center')
        printer.text('------------------------\n')
        printer.set(align='center')
        printer.text('\n')
        printer.text(lay)
        printer.text('\n')
        printer.set(align='center')
        printer.text((ks) + str(antrian))
        printer.text('\n')
        printer.set(align='center')
        printer.text('------------------------\n')
        printer.set(align='center')
        printer.text('\n')
        #kode QR Code nya
        printer.qr(msg_id, size=14)
        printer.set(align='center')
        printer.text('\n')
        printer.text('------------------------\n')
        printer.text('\n')
        printer.set(align='center')
        printer.text('Mohon sabar menunggu\n')
        printer.set(align='center')
        printer.text('\n')
        printer.text(tanggaljam_now)
        printer.text('\n')
        printer.set(align='center')

        # Cut the paper
        printer.cut()
        
#1. Reset queue number and date when the day changes
#2. Get ks from URL query parameter
#3. Get queue number from session
def reset_queue_number(service_key):
    # Reset queue number and date when the day changes
    today = datetime.date.today()
    if 'date_' + service_key not in session or session['date_' + service_key] != today.strftime('%Y-%m-%d'):
        session['date_' + service_key] = today.strftime('%Y-%m-%d')
        session['queue_number_' + service_key] = 0

#make dir to save photos
try:
    os.makedirs('./static/photos')
except OSError as error:
    pass

@app.route('/')
def index():
    return render_template('mqttgate/index.html')

@app.route('/daftar-baru')
def daftarbaru():
    service_key = 'daftar-baru'
    reset_queue_number(service_key)

    # Check if there was an issue with the response in the session
    if session.pop("upgrade_response_issue", False):
        return render_template('mqttgate/error.html', error_message="Foto Gagal Diambil. Ulangi Pengambilan Foto Sesuai Petunjuk.")
    
    if request.method == 'POST':
        session['queue_number_' + service_key] += 1
        return redirect(url_for('capture', service_key=service_key))
    return render_template('mqttgate/daftar-baru.html', session=session['queue_number_daftar-baru'])

@app.route('/perpanjangan')
def perpanjangan():
    service_key = 'perpanjangan'
    reset_queue_number(service_key)

    # Check if there was an issue with the response in the session
    if session.pop("upgrade_response_issue", False):
        return render_template('mqttgate/error.html', error_message="Foto Gagal Diambil. Ulangi Pengambilan Foto Sesuai Petunjuk.")
    
    if request.method == 'POST':
        session['queue_number_' + service_key] += 1
        return redirect(url_for('capture', service_key=service_key, session=session['queue_number_perpanjangan']))
    return render_template('mqttgate/perpanjangan.html', session=session['queue_number_perpanjangan'])

@app.route('/ujian-ulang')
def ujianulang():
    service_key = 'ujian-ulang'
    reset_queue_number(service_key)

    # Check if there was an issue with the response in the session
    if session.pop("upgrade_response_issue", True):
        return render_template('mqttgate/error.html', error_message="Foto Gagal Diambil. Ulangi Pengambilan Foto Sesuai Petunjuk.")

    if request.method == 'POST':
        session['queue_number_' + service_key] += 1
        return redirect(url_for('capture', service_key=service_key, session=session['queue_number_ujian-ulang']))
    return render_template('mqttgate/ujian-ulang.html', session=session['queue_number_ujian-ulang'])

@app.route('/peningkatan')
def peningkatan():
    service_key = 'peningkatan'
    reset_queue_number(service_key)

    if request.method == 'POST':
    # Check if there was an issue with the response in the session
        if session.pop("upgrade_response_issue", True):
            return render_template('mqttgate/peningkatan.html', session=session['queue_number_peningkatan'], error_message="Foto Gagal Diambil. Ulangi Pengambilan Foto Sesuai Petunjuk.")
        else:
            session['queue_number_' + service_key] += 1
            return redirect(url_for('capture', service_key=service_key, session=session['queue_number_peningkatan']))
    return render_template('mqttgate/peningkatan.html', session=session['queue_number_peningkatan'])

@app.route('/capture', methods=['GET', 'POST'])
def capture():
    if request.method == 'POST':
        # nomor antrian
        service_key = request.form['service_key']
        reset_queue_number(service_key)
        session['queue_number_' + service_key] += 1
        # Antrian ke
        antrian=session['queue_number_' + service_key]
        # Get ks from form
        ks = request.form['ks']
        lay = request.form['lay']
        # Get image data from form
        image_data_url = request.form['img']

        msg_id = round(time.time()*1000)
        tiket_id = "QR%s" % msg_id       # untuk personId
        date = now.strftime("%Y-%m-%d")
        hangus = "23:59:59"

        # SETTING QRCODE
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(str(msg_id))
        qr.make(fit=True)

        qr_image_path = f'./static/photos/{datehour_now}_qr_code.png'
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(qr_image_path)
        
        # EXPERIMENT JIKA QRCODE MAU DITAMPILKAN DI LAYAR
        qr_code_path = f'./photos/{datehour_now}_qr_code.png'

        # MQTT Client Setup
        mqtt_client = mqtt.Client("P1")

        msg = {"msg":
        {
            "messageId":"{}".format(msg_id),
            "operator":"EditPerson",
            "info":
            {
            "personId":"{}".format(tiket_id),
            "customId":"{}".format(msg_id),
            "name": "{}{}".format(ks, antrian),
            "nation":1,
            "gender":0,
            "birthday":"{}".format(date),
            "address":"Purworejo",
            "idCard":"421381199504030001",
            "tempCardType":0,
            "EffectNumber":3,
            "cardValidBegin":"{}".format(datehour_now),
            "cardValidEnd":"{} {}".format(date, hangus),
            "telnum1":"18888888888",
            "Native": "Polres Purworejo, Jawa Tengah",
            "cardType2":0,
            "cardNum2":"",
            "notes":"{}",
            "personType":0,
            "cardType":0,
            "dwidentity":0,
            "pic": "{}".format(image_data_url) #base64 murni hasil foto
            }
        }
        }
        msg = json.dumps(msg, indent = 4)

        # Connect MQTT
        mqtt_client.username_pw_set(username='admin', password='admin')
        mqtt_client.connect(host=mqtt_broker_address, port=mqtt_broker_port)
        # Send timestamp as a message to the MQTT broker with the topic 'SN FR nya'
        for face_id in face_ids:
            mqtt_client.publish(topic='mqtt/face/{}'.format(face_id), payload=msg, qos=0)
    
        # Setting Printer
        #printkarcis(lay, ks, antrian, msg_id)

    return render_template('mqttgate/capture.html', qr_code_path=qr_code_path, ks=ks, lay=lay, queue_number=session['queue_number_' + service_key], jam=tanggaljam_now)

if __name__ == "__main__":
    app.run(host='localhost', port=5000,  debug=True)