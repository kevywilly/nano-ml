#!/usr/bin/python3
# https://maker.pro/nvidia-jetson/tutorial/how-to-use-gpio-pins-on-jetson-nano-developer-kit
import flask
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
from settings import settings
from src.robot import Robot
from src.utils import cuda_to_jpeg
from src.image import Image

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


def _get_stream(img: str = "right"):
    while True:
        # ret, buffer = cv2.imencode('.jpg', frame)
        try:
            yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + app.robot.get_image1() + b'\r\n'
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
    bytes_str = app.robot.collector.load_image(category, name)
    response = flask.make_response(bytes_str)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.put('/api/categories/<category>/images/<name>/<category2>')
def move_image(category, name, category2):
    resp = app.robot.collector.move_image(category, name, category2)
    return {"status": resp}


@app.delete('/api/categories/<category>/images/<name>')
def delete_image(category, name):
    resp = app.robot.collector.delete_image(category, name)
    return {"status": resp}


@app.post('/api/categories/<category>/collect')
def collect(category):
    try:
        image = Image()
        image.value = cuda_to_jpeg(app.robot.input.value1)
        if image.value:
            return {category: app.robot.collector.collect(category, image)}
        else:
            return {category: -1}
    except Exception as ex:
        print(ex)
        return {category: -1}


@app.route('/api/stream')
def stream():
    return Response(_get_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stream/<img>')
def stream_camera(img: str):
    return Response(_get_stream(img), mimetype='multipart/x-mixed-replace; boundary=frame')


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
