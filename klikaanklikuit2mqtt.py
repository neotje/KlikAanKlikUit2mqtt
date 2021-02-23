"""
change HOST to your mqtt broker address.
"""
from json.decoder import JSONDecodeError
import threading
import serial
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import json
import logging
import sys
import pathlib

HOST = "0.0.0.0"
PORT = 1883
USB_PORT = "/dev/ttyUSB0"
JSON_CONF = pathlib.Path(__file__).parent / "devices.json"

Serial = serial.Serial(USB_PORT, 9600)

DEVICE = {
    "name": "KlikAanKlikUit",
    "identifiers": "KAKUHOPJES1"
}

devices: dict = {}

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(funcName)s:[%(lineno)d]   %(message)s'
)
_LOGGER = logging.getLogger(__name__)

def gen_id(data):
    return f"{data['A']}U{data['U']}"


def gen_cmd_topic(data):
    return f"homeassistant/light/{gen_id(data)}/set"


def gen_conf_topic(data):
    return f"homeassistant/light/{gen_id(data)}/config"


def gen_state_topic(data):
    return f"homeassistant/light/{gen_id(data)}/state"


def load_devices():
    with open(JSON_CONF, "r") as f:
        try:
            devices = json.load(f)
        except JSONDecodeError:
            return

        for d in devices.items():
            _LOGGER.info(f"Loaded: {d[0]}")
            register_device(d[1])

def save_devices():
    with open(JSON_CONF, "w") as f:
        json.dump(devices, f, indent= 3)

def register_device(data):
    id = gen_id(data)
    conf_topic = gen_conf_topic(data)
    cmd_topic = gen_cmd_topic(data)
    state_topic = gen_state_topic(data)

    _LOGGER.info("registering new device.")

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

    devices[id] = data
    save_devices()


def register_loop():
    try:
        while True:
            if Serial.readable():
                line = Serial.readline()
                _LOGGER.info(f"Serial IN: {line}")
                
                data = json.loads(line)

                # ignore device unit 255
                if data['U'] == 255:
                    _LOGGER.info("Ignoring 255 devices.")
                    continue

                id = gen_id(data)
                state_topic = gen_state_topic(data)

                if not id in devices:
                    register_device(data)

                # update devices data.
                devices[id] = data

                # send state
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
        _LOGGER.info(f"Serial OUT: {d['A']} {d['U']} {data['S']}")
        Serial.write(f"{d['A']} {d['U']} {data['S']}\n".encode())


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(HOST, PORT, 60)
# client.loop_start()

load_devices()

try:
    while True:
        # time.sleep(5)
        client.loop()


except KeyboardInterrupt:
    client.disconnect()
    Serial.close()
    save_devices()
