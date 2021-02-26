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

### ubuntu autostart klikaanklikuit2mqtt.py
1. Create service file `sudo nano /lib/systemd/system/kaku2mqtt.service
2. add service information to the text file and replace "/path/to/klikaanklikuit2mqtt.py":
```
[Unit]
Description=klikaanklikuit2mqtt Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3.8 /path/to/klikaanklikuit2mqtt.py
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
```
3. reload systemctl daemon `sudo systemctl daemon-reload`
4. enable service to autostart `sudo systemctl enable kaku2mqtt.service`
5. start service with `sudo systemctl start kaku2mqtt.service`

sometimes it helps to run `sudo pip3 install -r requirements.txt` to install python packages for the root user.