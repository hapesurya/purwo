from flask import Flask, render_template, request, session, url_for, redirect
import paho.mqtt.client as mqtt
import datetime
import time
import qrcode
import os
from escpos.printer import Usb
import json
from flask_sqlalchemy import SQLAlchemy
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

now = datetime.datetime.now()
tanggaljam_now = now.strftime("%d-%m-%Y %H:%M:%S")
datehour_now = now.strftime("%Y-%m-%d %H:%M:%S")

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
    if request.method == 'POST':
        session['queue_number_' + service_key] += 1
        return redirect(url_for('capture', service_key=service_key))
    return render_template('mqttgate/daftar-baru.html', session=session['queue_number_daftar-baru'])

@app.route('/perpanjangan')
def perpanjangan():
    service_key = 'perpanjangan'
    reset_queue_number(service_key)
    if request.method == 'POST':
        session['queue_number_' + service_key] += 1
        return redirect(url_for('capture', service_key=service_key, session=session['queue_number_perpanjangan']))
    return render_template('mqttgate/perpanjangan.html', session=session['queue_number_perpanjangan'])

@app.route('/ujian-ulang')
def ujianulang():
    service_key = 'ujian-ulang'
    reset_queue_number(service_key)
    if request.method == 'POST':
        session['queue_number_' + service_key] += 1
        return redirect(url_for('capture', service_key=service_key, session=session['queue_number_ujian-ulang']))
    return render_template('mqttgate/ujian-ulang.html', session=session['queue_number_ujian-ulang'])

@app.route('/peningkatan')
def peningkatan():
    service_key = 'peningkatan'
    reset_queue_number(service_key)
    if request.method == 'POST':
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
        # Data base64 diperkecil dulu
        base64_edit = (image_data_url[-55:-5])
        # kita akan jadikan kode service (ks) dan antrian sebagai base64
        base64_dummy = f'{ks}{antrian}'

        # SETTING QRCODE
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(base64_dummy)
        qr.make(fit=True)

        qr_image_path = f'./static/photos/{datehour_now}_qr_code.png'
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(qr_image_path)
        
        # EXPERIMENT JIKA QRCODE MAU DITAMPILKAN DI LAYAR
        # Parsing gambar QRCode ke URL Queue
        qr_code_path = f'./photos/{datehour_now}_qr_code.png'

        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # MQTT Client Setup
        mqtt_client = mqtt.Client("P1")
        
        msg_id    = round(time.time()*1000)
        tiket_id  = "QR%s" % msg_id       # untuk personId
        date       = now.strftime("%Y-%m-%d")
        hangus    = "23:59:59"

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
        # print(msg) #uncomment for testing
        # print(FACE_COMMAND_TOPIC) #uncomment for testing

        # Send QRCodeMQTT
        msg_qrcode = {
            "messageId":"{}".format(msg_id),
            "operator": "QRCodePush", 
            "info": { 
                "ImageType":"3",
                "AbsX":"10",
                "AbsY":"10",
                "ImageW":"200",
                "ImageH":"200",
                "QRCodeData":"{}".format(base64_edit)
                }
            }
        
        msg_qrcode = json.dumps(msg_qrcode, indent = 4)

        # Connect MQTT
        mqtt_client.username_pw_set(username='admin', password='admin')
        mqtt_client.connect(host='localhost', port=1883)
        # Send timestamp as a message to the MQTT broker with the topic 'SN FR nya'
        mqtt_client.publish(topic='mqtt/face/1962821', payload=msg, qos=0)
        time.sleep(1)
        mqtt_client.publish(topic='mqtt/face/1962821/QRCode', payload=msg_qrcode, qos=0)
    
        # Setting Printer
        printkarcis(lay, ks, antrian, msg_id)

        # DIPISAH DALAM FUNGSI TERPISAH
        # # Create a new instance of the printer object
        # printer = Usb(0x4b43, 0x3830, 0, 0x81, 0x03)
        
        # # Mulai Print Text Tiketnya
        # # Set align
        # printer.set(align='center')
        # printer.text('SATPAS POLRES PURWOREJO\n')
        # printer.text('\n')
        # printer.set(align='center')
        # printer.text('------------------------\n')
        # printer.set(align='center')
        # printer.text('\n')
        # printer.text(lay)
        # printer.text('\n')
        # printer.set(align='center')
        # printer.text((ks) + str(antrian))
        # printer.text('\n')
        # printer.set(align='center')
        # printer.text('------------------------\n')
        # printer.set(align='center')
        # printer.text('\n')
        # #kode QR Code nya
        # printer.qr(msg_id, size=14)
        # printer.set(align='center')
        # printer.text('\n')
        # printer.text('------------------------\n')
        # printer.text('\n')
        # printer.set(align='center')
        # printer.text('Mohon sabar menunggu\n')
        # printer.set(align='center')
        # printer.text('\n')
        # printer.text(tanggaljam_now)
        # printer.text('\n')
        # printer.set(align='center')

        # # Cut the paper
        # printer.cut()
    return render_template('mqttgate/capture.html', qr_code_path=qr_code_path, ks=ks, lay=lay, queue_number=session['queue_number_' + service_key], jam=tanggaljam_now)

##===========================================================
# sending data (image (base64 jpeg format) to broker
# other MQTT which subscribe to this TOPIC will receive 
# the data image, so it can recognize when he access the door
##===========================================================

# Set Up Fungsi Scan QRCode dari Face Detector
# MQTT configuration
broker_host = "localhost"
broker_port = 1883
client_id = "P1"
username = "admin"
password = "admin"
topic_template = "mqtt/face/{}/QRCode"

msg_id    = round(time.time()*1000)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to the topic when connected
        client.subscribe(topic_template.format("1962821"))
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload} on topic: {msg.topic}")
    
    # Extract ID from the received topic
    topic_parts = msg.topic.split("/")
    print(topic_parts)
    if len(topic_parts) == 4:
        face_id = topic_parts[2]
        print(face_id)
        
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
client = mqtt.Client(client_id)
client.username_pw_set(username=username, password=password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_host, broker_port)
# client.loop_forever()

if __name__ == "__main__":
    app.run(host='localhost', port=5000,  debug=True)