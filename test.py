import os
import time
import board
import busio
from flask import Flask, render_template, request
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# Wi-Fi Access Point (AP) Setup
os.system("sudo systemctl stop wpa_supplicant")
os.system("sudo systemctl start hostapd")

# Initialize Flask Web Server
app = Flask(__name__)

# Initialize I2C and PCA9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50  # Servo frequency 50Hz

# Initialize 8 servos
servos = [servo.Servo(pca.channels[i]) for i in range(8)]

# Set servos to neutral position (90 degrees)
for s in servos:
    s.angle = 90

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Spider Robot Control</title></head>
    <body>
    <h1>Spider Robot Control</h1>
    <form method="post" action="/move">
        <button name="action" value="forward">Forward</button>
        <button name="action" value="backward">Backward</button>
        <button name="action" value="left">Left</button>
        <button name="action" value="right">Right</button>
        <button name="action" value="stop">Stop</button>
    </form>
    </body>
    </html>
    '''

@app.route('/move', methods=['POST'])
def move():
    action = request.form.get('action')

    if action == "forward":
        for s in servos[:4]: s.angle = 120
        time.sleep(0.5)
        for s in servos[4:]: s.angle = 60
    elif action == "backward":
        for s in servos[:4]: s.angle = 60
        time.sleep(0.5)
        for s in servos[4:]: s.angle = 120
    elif action == "left":
        for i in range(4): servos[i].angle = 120
        time.sleep(0.5)
        for i in range(4, 8): servos[i].angle = 60
    elif action == "right":
        for i in range(4): servos[i].angle = 60
        time.sleep(0.5)
        for i in range(4, 8): servos[i].angle = 120
    elif action == "stop":
        for s in servos: s.angle = 90

    return index()

if __name__== '__main__':
    app.run(host='0.0.0.0', port=5000)
