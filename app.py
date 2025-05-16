from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app)

players = {}
current_question = {}
scores = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/host")
def admin():
    return render_template("host.html")

@app.route("/creation")
def admin():
    return render_template("creation.html")

@app.route("/player/<name>")
def player(name):
    return render_template("player.html", player_name=name)

@socketio.on("join")
def handle_join(data):
    name = data["name"]
    players[name] = {"score": 0}
    print(f"{name} joined")
    emit("leaderboard_update", players, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
