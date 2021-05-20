from flask import Flask , render_template , redirect , url_for , Response , flash , request
from modules.forms import SettingsForm
from camera import VideoCamera
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a5c5cbdf1428d6fe3f40a3114eea2ac4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///settings.db'
db = SQLAlchemy(app)

#model
class Settings(db.Model) :
    
    id = db.Column(db.Integer , primary_key = True)
    lct = db.Column(db.Float(10) , nullable = False)
    mef = db.Column(db.Integer , nullable = False)
    dft = db.Column(db.Integer , nullable = False)
    rat = db.Column(db.Integer , nullable = False)
    raft = db.Column(db.Integer , nullable = False)

    def __init__(self , lct , mef , dft , rat , raft) :
        self.lct = lct
        self.mef = mef
        self.dft = dft
        self.rat = rat
        self.raft = raft

    def __repr__(self) :
        return f'Settings({self.lct} , {self.mef} , {self.dft} , {self.rat} , {self.raft})'

# global videocam object..
videocam = VideoCamera()

@app.route('/')
@app.route('/home')
def home() :
    global videocam
    # initialize thresholds through database
    setting = Settings.query.get(1)
    videocam.LOW_CONTRAST_THRESH = setting.lct
    videocam.EAR_FRAME_PIPLINE = setting.mef
    videocam.DIVERSION_FRAME_TRESHHOLD = setting.dft
    videocam.REST_ALERT_THRESH = setting.rat
    videocam.REST_ALERT_FRAME_THRESH = setting.raft
    return render_template('home.html' , title='Home Page' , videocam = videocam)

@app.route('/detection')
def detection() :
    global videocam
    return render_template('detection.html' , title='Detection')

def gen(camera):
    while True:
        #get camera frame
        frame , message = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
               
@app.route('/video_feed')
def video_feed():
    global videocam
    return Response(gen(videocam) ,
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/settings' , methods=['GET' , 'POST']) 
def settings() :

    global videocam
    setting_form = SettingsForm()
    setting = Settings.query.get(1)
    if setting_form.validate_on_submit() :
        setting.lct = setting_form.lowConThresh.data
        setting.mef = setting_form.earFramePipeline.data
        setting.dft = setting_form.divFrameThresh.data
        setting.rat = setting_form.restAlertThresh.data
        setting.raft = setting_form.restAlertFrameThresh.data
        db.session.commit()

        videocam.LOW_CONTRAST_THRESH = setting_form.lowConThresh.data
        videocam.EAR_FRAME_PIPLINE = setting_form.earFramePipeline.data
        videocam.DIVERSION_FRAME_TRESHHOLD = setting_form.divFrameThresh.data
        videocam.REST_ALERT_THRESH = setting_form.restAlertThresh.data
        videocam.REST_ALERT_FRAME_THRESH = setting_form.restAlertFrameThresh.data

        flash('Changes Saved Successfully' , 'success')
        return redirect(url_for('home'))

    elif request.method == 'GET' :
        setting_form.lowConThresh.data = setting.lct
        setting_form.earFramePipeline.data = setting.mef
        setting_form.divFrameThresh.data = setting.dft
        setting_form.restAlertThresh.data = setting.rat
        setting_form. restAlertFrameThresh.data = setting.raft

    return render_template('settings.html' , form = setting_form , title = 'Settings')

if __name__ == '__main__' :

    app.run(debug = True)