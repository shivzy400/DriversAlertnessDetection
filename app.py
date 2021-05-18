from flask import Flask , render_template , redirect , url_for ,Response
from camera import VideoCamera

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home() :
    return render_template('home.html' , title='Home Page')

@app.route('/detection')
def detection() :
    return render_template('detection.html' , title='Detection')

def gen(camera):
    while True:
        #get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__' :

    app.run(debug = True)