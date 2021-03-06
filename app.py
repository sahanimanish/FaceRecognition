from flask import Flask,jsonify,request
from flask_socketio import SocketIO, send, emit
from flask import render_template, Response
from queue import Queue
from os.path import dirname, abspath
import os
import base64
import cv2
import numpy as np
from PIL import Image
import io
from trainer import train
from recognizer import recognize,updateModel
import cmake
d = os.getcwd()

app = Flask(__name__)
app.queue = Queue()
socketio = SocketIO(app)
last_frame = None

def save_images_to_server(sketch64, sketch_path):
    with open(sketch_path, "wb") as fh:
        fh.write(base64.decodebytes(sketch64.encode()))

def gen_livestream():
    global last_frame
    while True:
        if app.queue.qsize():
            frame = base64.b64decode(app.queue.get().split('base64')[-1])
            last_frame = frame
        else:
            if last_frame is None:
                fh = open(d+"/static/black.jpg", "rb")
                frame = fh.read()
                fh.close()
            else:
                frame = last_frame
        if last_frame:
            img_np = np.array(Image.open(io.BytesIO(frame)))
            img_np=recognize(img_np)
            frame = cv2.imencode('.jpg', cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def home():
    return render_template('index.html')



@app.route('/api/train',methods=['POST'])
def train_model():
    data=request.get_json()
    name=data['name'].upper()
    c=0
    os.mkdir(f'Dataset/{name}')
    for i in data['images_data']:
        c=c+1
        save_images_to_server(i[22:],f'Dataset/{name}/{c}.jpg')
    train(model_save_path="trained_knn_model.clf", n_neighbors=2)
    updateModel()  
    return jsonify({"result":"Training is Completed"})


@app.route('/train')
def train_page():
    return render_template('train.html')

@socketio.on('connect', namespace='/live')
def test_connect():
    print('Client wants to connect.')
    emit('response', {'data': 'OK'})


@socketio.on('disconnect', namespace='/live')
def test_disconnect():
    print('Client disconnected')


@socketio.on('event', namespace='/live')
def test_message(message):
    emit('response',{'data': message['data']})
    print(message['data'])


@socketio.on('livevideo', namespace='/live')
def test_live(message):   
    app.queue.put(message['data'])

@app.route('/video_feed')
def video_feed():
    return Response(gen_livestream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, host = 'facerecb.herokuapp.com')
#     socketio.run(app)
#     app.run()

