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