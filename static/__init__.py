from flask import Flask, render_template, request, session, url_for, redirect
import paho.mqtt.client as mqtt
import datetime
import qrcode
import os
from escpos.printer import Usb

app = Flask(__name__)
app.secret_key = 'secret_key'

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
        base64 = (image_data_url[-55:-5])

        now = datetime.datetime.now()
        jam = now.strftime("%Y-%m-%d %H-%M-%S")

        # MQTT Client Setup
        mqtt_client = mqtt.Client()
        
        # Connect MQTT
        mqtt_client.connect(host='broker.mqtt-dashboard.com', port=1883)
        # Send timestamp as a message to the MQTT broker with the topic '/service'
        mqtt_client.publish(topic=str(service_key), payload=str(base64), qos=0)
        # Disconnect from MQTT broker
        mqtt_client.disconnect()

        # Generate a QR code based on the image_data_url now
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(base64)
        qr.make(fit=True)

        # EXPERIMENT JIKA QRCODE MAU DITAMPILKAN DI LAYAR
        # Create a QR code image
        qr_image_path = f'./static/photos/{jam}_qr_code.png'
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(qr_image_path)

        # # EXPERIMENT JIKA QRCODE MAU DITAMPILKAN DI LAYAR
        # Parsing gambar QRCode ke URL Queue
        qr_code_path = f'./photos/{jam}_qr_code.png'

        # Setting Printer
        # Create a new instance of the printer object
        printer = Usb(0x4b43, 0x3830, 0, 0x81, 0x03)
        
        # Mulai Print Text Tiketnya
        # Set align
        printer.set(align='center')
        printer.text('SATPAS POLRES PURWOREJO\n')
        printer.set(align='center')
        printer.text('------------------------\n')
        printer.set(align='center')
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
        printer.qr(base64, size=16)
        printer.set(align='center')
        printer.text('\n')
        printer.text('------------------------\n')
        printer.set(align='center')
        printer.text('Mohon sabar menunggu\n')
        printer.set(align='center')
        printer.text(jam)
        printer.text('\n')
        printer.set(align='center')

        # # Cut the paper
        # printer.cut()
    return render_template('mqttgate/capture.html', qr_code_path=qr_code_path,data=base64, ks=ks, lay=lay, queue_number=session['queue_number_' + service_key], jam=jam)

if __name__ == "__main__":
    app.run(host='localhost', port=5000,  debug=True)