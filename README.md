# KlikAanKlikUit2mqtt
Connect KlikAanKlikUit 433mhz devices to Home Assistant.

## requirements
- arduino
- 433mhx reciever and transmitter.
- pc/server/raspberry pi to run the python serial interface.
- python 3.8
- visual studio code with platformio.

## installation
the purpose of the arduino is to send kaku signals to devices and recieve from devices.

### arduino
1. Open `./arduino/` with platformio in visual studio code.
2. Connect arduino nano to pc.
3. Go to the platformio tab and click on upload.

### server
1. install python requirements `pip3 install -r requirements.txt`.
2. change `HOST = "0.0.0.0"` to your mqtt brokers host.
3. use `python3 klikaanklikuit2mqtt.py` to run the mqtt client.