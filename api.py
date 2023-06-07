#!/usr/bin/python3
# https://maker.pro/nvidia-jetson/tutorial/how-to-use-gpio-pins-on-jetson-nano-developer-kit
from flask import Flask, render_template, Response, jsonify
from src.robot import Robot
from src.collector import ImageCollector
from src.drive_model import DriveModel
from flask_cors import CORS
from settings import settings
from src.calibrator import Calibrator


app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

app.image_collector = ImageCollector.instance(config=settings.default_model)
app.drive_model = DriveModel.instance(config=settings.default_model)
app.autodrive = False
app.robot: Robot = Robot.instance()
app.dir = 0
app.speed = settings.robot_drive_speed
app.turn_speed = settings.robot_turn_speed
app.calibrator: Calibrator = Calibrator()

def _autodrive(change):
    if not app.autodrive:
        app.dir = 0
        return
    
    y = app.drive_model.predict(change["new"])
    forward = float(y.flatten()[0])
    left = float(y.flatten()[1])
    right = float(y.flatten()[2])

    print(f"f: {forward}, l: {left}, r: {right}")
    
    if (left + right) < 0.5:
        app.dir = 0
    elif (left > right and app.dir == 0):
        app.dir = -1
    elif app.dir == 0:
        app.dir = 1

    if app.dir == 0:
        app.robot.forward(app.speed)
    elif app.dir == -1:
            app.robot.left(app.turn_speed)
    else:
        app.robot.right(app.turn_speed)

def _get_stream(img: str = "right"):  
    while True:
        # ret, buffer = cv2.imencode('.jpg', frame)
        try:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + app.robot.get_images()[img.lower()] + b'\r\n'
                )  # concat frame one by one and show result
        except Exception as ex:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/autodrive')
def toggle_autodrive():
    
    app.autodrive = not app.autodrive
    
    if(app.autodrive):
        app.robot.stop
        app.dir = 0
        app.robot.camera.observe(_autodrive, names='value_right')
    else:
        try:
            app.robot.camera.unobserve(_autodrive)
        except Exception as ex:
            print(ex)
        finally:
            app.robot.stop()

    return jsonify({"autodrive": app.autodrive})

@app.get('/api/categories')
def categories():
    return jsonify(app.image_collector.categories)

@app.get('/api/categories/counts')
def category_counts():
    return jsonify([{"name": k, "entries": v} for (k,v) in app.image_collector.counts.items()])
    
@app.post('/api/categories/<category>/collect')
def collect(category):
    try:
        image = app.robot.image_right
        if image:
            return {category: app.image_collector.collect(category, image)}
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

    app.robot.drive(cmd, app.speed)
    return {
        "cmd": cmd,
        "speed": speed
    }

@app.route('/api/calibration/images/count')
def get_calibration_image_counts():
    app.calibrator._get_counts()
    return {
        "right": app.calibrator.right_count,
        "left": app.calibrator.left_count,
        "stereo": app.calibrator.stereo_count
        }

@app.route('/api/calibration/images/collect/<img>')
def collect_calibration_image(img: str):

    count = 0
    try:
        if img.lower() == "right":
            image = app.robot.camera.value_right
            count = app.calibrator.collect_single(image, 0) if image is not None else app.calibrator.right_count
        elif img.lower() == "left":
            image = app.robot.camera.value_left
            count = app.calibrator.collect_single(image, 1) if image is not None else app.calibrator.left_count
        elif img.lower() == "stereo":
            image_right = app.robot.camera.value_right
            image_left = app.robot.camera.value_left
            if image_right is not None and image_left is not None:
                count = app.calibrator.collect_stereo(image_right, image_left)
            else:
                count = app.calibrator.stereo_count
    
    except Exception as ex:
        print(ex)
    
    return {"count": count}

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)





