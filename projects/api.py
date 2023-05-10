from flask import Flask, render_template, Response
from jetbot.camera import Camera
from jetbot.robot import Robot

app = Flask(__name__)

app.robot = Robot()

def gen_frames():  
    while True:
        # ret, buffer = cv2.imencode('.jpg', frame)
        try:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + app.robot.get_image_capture() + b'\r\n'
                )  # concat frame one by one and show result
        except Exception as ex:
            pass


html = """

<body>
    <div class="container">
        <div class="row">
            <div class="col-lg-8  offset-lg-2">
                <h3 class="mt-5">Live Streaming</h3>
                <img src="http://nano1:5000/stream" width="1080px" height="720px">
            </div>
        </div>
    </div>
    </body>
"""

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stream')
def stream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
            
if __name__ == "__main__":

    app.run(host='0.0.0.0', debug=False)



