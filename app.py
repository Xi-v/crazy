from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import base64
from flask_socketio import SocketIO, emit, disconnect

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_password():
    length = 35
    return base64.b64encode(os.urandom(length)).decode('utf-8')[:length]

PASSWORD = generate_password()
print(f"Today's password: {PASSWORD}")

socketio = SocketIO(app)

@socketio.on("message")
def handle_message(data):
    emit("message", data, broadcast=True)

@socketio.on("connect")
def handle_connect():
    if not session.get("authenticated"):
        disconnect()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    entered = request.form.get("password")
    username = request.form.get("username")

    if not username:
        return render_template("index.html", error="Please enter a username.")
    if entered == PASSWORD:
        session["authenticated"] = True
        session["username"] = username
        return redirect(url_for("chatroom"))
    else:
        return render_template("index.html", error="Wrong password, try again.")

@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("authenticated"):
        return jsonify({"error": "Unauthorized"}), 401
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No file"}), 400
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
        return jsonify({"error": "Invalid file type"}), 400
    filename = base64.b64encode(os.urandom(8)).decode('utf-8').replace("/", "")[:12] + "." + ext
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"url": f"/static/uploads/{filename}"})

@app.route("/chatroom")
def chatroom():
    if not session.get("authenticated"):
        return redirect(url_for("home"))
    return render_template("chatroom.html", username=session["username"])



if __name__ == "__main__":
    socketio.run(app, debug=True)