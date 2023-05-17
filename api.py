#!/usr/bin/python3

from flask import Flask, render_template, Response, jsonify
from src.camera import Camera
from src.robot import Robot
from src.collector import ImageCollector
from flask_cors import CORS
from settings import settings

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

app.image_collector = ImageCollector(training_config=settings.default_model)

app.robot: Robot = Robot()

def _get_stream():  
    while True:
        # ret, buffer = cv2.imencode('.jpg', frame)
        try:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + app.robot.get_image_capture() + b'\r\n'
                )  # concat frame one by one and show result
        except Exception as ex:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.get('/api/categories')
def categories():
    return jsonify(app.image_collector.categories)

@app.get('/api/categories/counts')
def category_counts():
    return jsonify([{"name": k, "entries": v} for (k,v) in app.image_collector.counts.items()])
    
@app.post('/api/categories/<category>/collect')
def collect(category):
    try:
        image = app.robot.camera.image
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

@app.route('/api/drive/<cmd>/<speed>')
def drive(cmd, speed):
    app.robot.drive(cmd, int(speed))
    return {
        "cmd": cmd,
        "speed": speed
    }
            
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)





