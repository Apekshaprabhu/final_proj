from flask import Flask, render_template, url_for, redirect, request
import numpy as np
import cv2
from keras.models import load_model
import webbrowser
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


# Replace with your client ID and client secret obtained from the Spotify Developer Dashboard
username = "apeksh@gmail.com"
client_id = '84605e926cc941d191f8263ead2accad'
client_secret = '703230a9f2c846b6bf28a6d2d91da2fc'
scope = 'user-modify-playback-state,user-modify-playback-state'
redirect_uri = "http://google.com/callback/"

# Authenticate your application by requesting an access token
auth_manager = SpotifyOAuth(
    scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri
)

sp = spotipy.Spotify(auth_manager=auth_manager)
devices = sp.devices()
device_id = devices['devices'][0]['id']
track_uri = ''
results = []

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

gu = 'blah blah'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

info = {}

haarcascade = "haarcascade_frontalface_default.xml"
label_map = ['Anger', 'Neutral', 'Fear', 'Happy', 'Sad', 'Surprise']
print("+"*50, "loadin gmmodel")
model = load_model('model.h5')
cascade = cv2.CascadeClassifier(haarcascade)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):

    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "4 - 8 characters"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "minimum 8 characters"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/choose_singer', methods=["POST"])
def choose_singer():
    info['language'] = request.form['language']
    print(info)
    return render_template('choose_singer.html', data=info['language'])


@app.route('/choose_lang', methods=["GET"])
def choose_lang():
    return render_template('index.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/emotion_detect', methods=["POST"])
def emotion_detect():
    global results
    info['singer'] = request.form['singer']

    found = False

    cap = cv2.VideoCapture(0)
    while not (found):
        _, frm = cap.read()
        gray = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)

        faces = cascade.detectMultiScale(gray, 1.4, 1)

        for x, y, w, h in faces:
            found = True
            roi = gray[y:y+h, x:x+w]
            cv2.imwrite("static/face.jpg", roi)

    roi = cv2.resize(roi, (48, 48))

    roi = roi/255.0

    roi = np.reshape(roi, (1, 48, 48, 1))

    prediction = model.predict(roi)

    print(prediction)

    prediction = np.argmax(prediction)
    prediction = label_map[prediction]

    cap.release()

    results = sp.search(
        f"{info['singer']} {prediction} {info['language']}", type="track", limit=1)

    track_uri = results["tracks"]["items"][0]["uri"]
    sp.start_playback(device_id=device_id, uris=[track_uri])

    return render_template('index1.html')
    # return redirect(url_for('play'))

    # link  = f"https://www.youtube.com/results?search_query={info['singer']}+{prediction}+{info['language']}+song"
    #

    # webbrowser.open(link)

    # return render_template("emotion_detect.html", data=prediction, link='')


@app.route('/search', methods=['POST'])
def search():
    global track_uri
    prediction = request.form[{info['singer']} +
                              'prediction'+{info['language']}]
    track_results = sp.search(
        q='track:' + {info['singer']} + prediction + {info['language']}, type='track', limit=1)

    if len(track_results['tracks']['items']) > 0:
        track_uri = track_results['tracks']['items'][0]['uri']
        return 'success'
    else:
        return 'error'


@app.route('/play')
def play():
    if track_uri != '':
        sp.start_playback(uris=[track_uri])
        return 'success'
    else:
        return 'error'


@app.route('/pause')
def pause():
    sp.pause_playback()
    return 'success'


@app.route('/next')
def next():
    track_uri = results["tracks"]["items"][1]["uri"]
    sp.start_playback(device_id=device_id, uris=[track_uri])
    return 'success'


if __name__ == "__main__":
    app.run(debug=True)
