// JavaScript code for capturing and submitting images
let camera_button = document.querySelector("#start-camera");
let video = document.querySelector("#video");
let photo = document.querySelector("#photo");
let canvas = document.querySelector("#canvas");
let dataurl = document.querySelector("#dataurl");
let dataurl_container = document.querySelector("#dataurl-container");

//## load kamera saat document di load
document.addEventListener('DOMContentLoaded', async function() {
    let stream = null;

    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    }
    catch(error) {
        alert(error.message);
        return;
    }

    video.srcObject = stream;

    video.style.display = 'block';
    camera_button.style.display = 'none';
    click_button.style.display = 'block';
});


//## click untuk capture, hasilnya simpan di canvas (id="canvas")
photo.addEventListener('click', function() {
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    let image_data_url = canvas.toDataURL('image/jpeg');

    dataurl.value = image_data_url;
    //dataurl_container.style.display = 'block';
    //console.log("dataurl.value")
    
    //document.getElementById("frm-daftar").submit()    
});
// Ensure to submit the captured image using AJAX to the /service endpoint

//## Cek apakah wajah sudah di foto dengan benar
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-daftar');
    const alertContainer = document.getElementById('alert-container');
    const alertMessage = document.getElementById('alert-message');

    document.getElementById('photo').addEventListener('click', function () {
        // Subscribe to the MQTT topic
        const mqttClient = new MQTTClient('mqtt/face/1962821/Ack');
        mqttClient.subscribe(handleMQTTMessage);
    });

    function handleMQTTMessage(message) {
        // Parse the JSON message
        const data = JSON.parse(message.payload);

        // Check the 'code' value
        if (data.code === '200') {
            // Submit the form if code is 200
            form.submit();
        } else {
            // Display the alert message
            alertMessage.textContent = 'Foto Gagal. Pastikan Wajah masuk dalam kotak. Kode: ' + data.code;
            alertContainer.style.display = 'block';
        }
    }

    // Simple MQTT Client class
    class MQTTClient {
        constructor(topic) {
            this.client = new Paho.MQTT.Client("localhost", 1883, "P1" + new Date().getTime());
            this.topic = topic;
            this.client.onMessageArrived = this.onMessageArrived.bind(this);
            this.client.connect({onSuccess: this.onConnect.bind(this)});
        }

        onConnect() {
            this.client.subscribe(this.topic);
        }

        onMessageArrived(message) {
            this.handleMessage(message);
        }

        handleMessage(message) {
            const payloadString = message.payloadString;
            const payload = JSON.parse(payloadString);
            this.handleMessageCallback(payload);
        }

        subscribe(callback) {
            this.handleMessageCallback = callback;
        }
    }
});