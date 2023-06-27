#!/usr/bin/python3
import flask
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
from settings import settings
from src.robot import Robot
from src.utils import cuda_to_jpeg
from src.image import Image
from settings import settings

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*": {
        "origins": "*"
    }
})


app.autodrive_is_on = False
app.robot: Robot = Robot.instance(stereo=False)
app.dir = 0
app.speed = settings.robot_drive_speed
app.turn_speed = settings.robot_turn_speed
app.num_cameras = settings.default_model.num_cameras

def _get_stream(index: int = 1):
    while True:
        # ret, buffer = cv2.imencode('.jpg', frame)
        try:
            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + app.robot.get_image(index) + b'\r\n'
            )  # concat frame one by one and show result
        except Exception as ex:
            pass


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/autodrive')
def toggle_autodrive():
    app.robot.autodrive.running = not app.robot.autodrive.running
    
    return jsonify({"autodrive": app.robot.autodrive.running})


@app.get('/api/categories')
def categories():
    return jsonify(app.robot.collector.categories)


@app.get('/api/categories/counts')
def category_counts():
    return jsonify([{"name": k, "count": v} for (k, v) in app.robot.collector.counts.items()])


@app.get('/api/categories/<category>/images')
def category_images(category: str):
    return {"images": app.robot.collector.get_images(category)}


@app.get('/api/categories/<category>/images/<name>')
def get_image(category, name):
    bytes_str = app.robot.collector.load_image(category, name, 1)
    response = flask.make_response(bytes_str)
    response.headers.set('Content-Type', 'image/jpeg')
    return response

@app.get('/api/categories/<category>/images/<name>/<cam_index>')
def get_image2(category, name, cam_index):
    bytes_str = app.robot.collector.load_image(category, name, int(cam_index))
    response = flask.make_response(bytes_str)
    response.headers.set('Content-Type', 'image/jpeg')
    return response

@app.delete('/api/categories/<category>/images/<name>')
def delete_image(category, name):
    resp = app.robot.collector.delete_image(category, name)
    return {"status": resp}


@app.post('/api/categories/<category>/collect')
def collect(category):
    try:
        image1 = Image()
        image1.value = cuda_to_jpeg(app.robot.input.value1)
        images = [image1]
        if app.num_cameras > 1:
            image2 = Image()
            image2.value = cuda_to_jpeg(app.robot.input.value2)
            images.append(image2)
        for image in images:
            if not image.value:
                return {category: -1}
        
        return {category: app.robot.collector.collect(category, images)}
        
    except Exception as ex:
        print(ex)
        return {category: -1}


@app.route('/api/stream')
def stream():
    return Response(_get_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stream/<input>')
def stream_camera(input: str):
    print(f"Got Stream Request for {input}")
    index = 1 if input == "input1" else 2
    return Response(_get_stream(index), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/drive/<cmd>/<speed>')
def drive(cmd, speed):
    speed = float(speed)
    app.speed = speed
    app.turn_speed = speed

    app.robot.drivetrain.drive(cmd, app.speed)
    return {
        "cmd": cmd,
        "speed": speed
    }


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
