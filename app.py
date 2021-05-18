from flask import Flask , render_template , redirect , url_for

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home() :
    return render_template('home.html' , title='Home Page')

@app.route('/detection')
def detection() :
    return render_template('detection.html' , title='Detection')


if __name__ == '__main__' :

    app.run(debug = True)