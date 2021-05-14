from flask import Flask
import eventlet
import socketio
from keras.models import load_model
from PIL import Image
import cv2
import numpy as np
import base64
from io import BytesIO

sio = socketio.Server()
app = Flask(__name__)
speed_limit = 10

def preprocess(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img = cv2.GaussianBlur(img, (3,3), 0)
    img = cv2.resize(img, (200,66))
    img = img/255
    return img

#collecting our model data to use for the simulator
@sio.on('telemetry')
def telemetry(sid, data):
	speed = float(data['speed'])
	image = Image.open(BytesIO(base64.b64decode(data['image'])))
	image = np.asarray(image)
	image = preprocess(image)
	image = np.array([image])
	steering_angle = float(model.predict(image))
	throttle = 1.0 - speed/speed_limit
	print('{}, {}, {}'.format(steering_angle, throttle, speed))
	control_car(steering_angle, throttle)


#for establishing connection between the code and the simulator
@sio.on('connect')
def connect(sid, environment):
	print('connected')
	control_car(0, 0 )
#for controling the car
def control_car(steering_angle, throttle):
	sio.emit('steer', data = {
		'steering_angle': steering_angle.__str__(),
		'throttle' : throttle.__str__()
	})



if __name__ == '__main__':
	model = load_model('model.h5')
	app = socketio.Middleware(sio, app)
	eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
