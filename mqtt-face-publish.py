import paho.mqtt.client as mqtt

##===========================================================
# sending data (image (base64 jpeg format) to broker
# other MQTT which subscribe to this TOPIC will receive 
# the data image, so it can recognize when he access the door
##===========================================================

## the topic:
## mqtt/face/<ID-FACE_RCOGINZER>
FACE_COMMAND_TOPIC = "mqtt/face/1962829"

def publish(data, pick):

    msg_id    = round(time.time()*1000)
    tiket_id  = "QR%s" % msg_id       # untuk personId
    no_antri  = last_antrian(pick)  # umtuk note
    image     = data
    tanggal   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tgl       = datetime.now().strftime("%Y-%m-%d")
    jam       = "23:59:59"

    msg = {"msg":
      {
        "messageId":"{}".format(msg_id),
        "operator":"EditPerson",
        "info":
        {
          "personId":"{}".format(tiket_id),
          "customId":"{}".format(msg_id),
          "name": "{}".format(no_antri),
          "nation":1,
          "gender":0,
          "birthday":"{}".format(tanggal),
          "address":"Purworejo",
          "idCard":"421381199504030001",
          "tempCardType":0,
          "EffectNumber":3,
          "cardValidBegin":"{}".format(tanggal),
          "cardValidEnd":"{} {}".format(tgl, jam),
          "telnum1":"18888888888",
          "Native": "Polres Purworejo, Jawa Tengah",
          "cardType2":0,
          "cardNum2":"",
          "notes":"{}",
          "personType":0,
          "cardType":0,
          "dwidentity":0,
          "pic": "{}".format(image)
        }
      }
    }
    #(msg_id,tiket_id,msg_id,tanggal,antrian,image) #.format(mid=msg_id, tid=tiket_id, tno=antrian, tgl=tanggal, img=image)
    msg = json.dumps(msg, indent = 4)
    print(msg)

    #msg = msg.format(tid=tiket_id, msg_id=msg_id, tno=antrian, tgl=tanggal, img=image)
    
    ## instance
    client = mqtt.Client("P1") #create new instance 
    #connect to broker
    broker_address="localhost"
    broker_port = 1883
    client.connect(broker_address, port=broker_port)
    
    ## send to face-recog 
    client.publish(FACE_COMMAND_TOPIC, msg)
