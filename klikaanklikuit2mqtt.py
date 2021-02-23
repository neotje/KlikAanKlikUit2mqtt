"""
change HOST to your mqtt broker address.
"""
HOST = "0.0.0.0"




import time
import sys
import logging
import json
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import serial
import threading


Serial = serial.Serial("/dev/ttyUSB0", 9600)

DEVICE = {
    "name": "KlikAanKlikUit",
    "identifiers": "KAKUHOPJES1"
}

devices = {}

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(funcName)s:[%(lineno)d]   %(message)s'
)
_LOGGER = logging.getLogger(__name__)


def register_loop():
    try:
        while True:
            if Serial.readable():
                line = Serial.readline()

                _LOGGER.info(f"Serial IN: {line}")

                data = json.loads(line)

                if data['U'] == 255:
                    _LOGGER.info("Ignoring 255 devices.")
                    continue

                id = f"{data['A']}U{data['U']}"
                prefix = f"homeassistant/light/{id}"

                conf_topic = f"{prefix}/config"
                cmd_topic = f"{prefix}/set"
                state_topic = f"{prefix}/state"

                if not id in devices:
                    _LOGGER.info("regestering new device.")

                    payload = {
                        "name": f"{id}_light",
                        "unique_id": f"{id}",

                        "device": DEVICE,

                        "command_topic": cmd_topic,
                        "state_topic": state_topic,

                        "schema": "json",
                    }

                    publish.single(conf_topic, json.dumps(
                        payload), hostname=HOST, retain=True)

                    client.subscribe(cmd_topic)

                devices[id] = {
                    "addr": data['A'],
                    "unit": data["U"],
                    "state": data["C"]
                }

                publish.single(state_topic, json.dumps({
                    "state": str(data["C"]).upper()
                }), hostname=HOST)
    except KeyboardInterrupt:
        return


register_thread = threading.Thread(target=register_loop)


def on_connect(c, userdata, flags, rc):
    _LOGGER.info("Connected to mqtt broker.")
    register_thread.start()


def on_message(client, userdata, msg: mqtt.MQTTMessage):
    id = str(msg.topic).split("/")[2]
    data = json.loads(msg.payload)

    if id in devices and "state" in data:
        d = devices[id]
        _LOGGER.info(f"Serial OUT: {d['addr']} {d['unit']} {data['state']}")
        Serial.write(f"{d['addr']} {d['unit']} {data['state']}\n".encode())


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(HOST, 1883, 60)
# client.loop_start()

try:
    while True:
        # time.sleep(5)
        client.loop()


except KeyboardInterrupt:
    client.disconnect()
    Serial.close()
