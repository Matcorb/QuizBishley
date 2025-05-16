import os
import json
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app)

current_question = {}
scores = {}
active_quizzes = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/host/<quiz_file>")
def host(quiz_file):
    return render_template("host.html", quiz_file=quiz_file)

@app.route("/creation")
def creation():
    return render_template("creation.html")

@app.route("/player/<name>/<room>")
def player(name, room):
    return render_template("player.html", player_name=name, room_id=room)

@app.route("/save_quiz", methods=["POST"])
def save_quiz():
    quiz = request.json
    title = quiz.get("title", "untitled").replace(" ", "_")

    os.makedirs("quizzes", exist_ok=True)
    with open(f"quizzes/{title}.json", "w") as f:
        json.dump(quiz, f, indent=2)

    emit("update_quiz_list", broadcast=True)
    return {"status": "success", "message": f"{title}.json saved"}

@app.route("/quiz_list")
def quiz_list():
    quiz_dir = "quizzes"
    quiz_files = [f for f in os.listdir(quiz_dir) if f.endswith(".json")]
    
    quiz_list = []
    for f in quiz_files:
        with open(os.path.join(quiz_dir, f)) as file:
            data = json.load(file)
            quiz_list.append({
                "file": f,
                "title": data.get("title", f.replace(".json", ""))
            })
    
    return jsonify(quiz_list)

@app.route("/active_quizzes")
def active_games_list():
    return jsonify([
        {"room": room, "title": quiz["title"]}
        for room, quiz in active_quizzes.items()
    ])

@socketio.on("identify")
def handle_identify(data):
    if data["role"] == "host":
        emit("leaderboard_update", {}, to=request.sid)
        room_id = lowest_available_room_id()
        active_quizzes[room_id] = {"host": request.sid, "file": data["file"], "title": data["file"].replace(".json", ""), "players": {}}
        join_room(room_id)
        emit("update_active_games", broadcast=True)

@socketio.on("join")
def handle_join(data):
    name = data["name"]
    room = data["room"]
    print(active_quizzes)
    active_quizzes[room]["players"][request.sid] = {"name": name, "score": 0}
    join_room(room)
    print(f"{name} joined")
    emit("leaderboard_update", active_quizzes[room]["players"], to=active_quizzes[room]["host"])

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    room_id, is_host = find_user_room(sid)
    if not is_host and room_id:
        name = active_quizzes[room_id]["players"][sid]["name"]
        if name:
            print(f"{name} disconnected")
            active_quizzes[room_id]["players"].pop(sid, None)
            emit("leaderboard_update", active_quizzes[room_id]["players"], to=active_quizzes[room_id]["host"])
    # add host handling

def lowest_available_room_id():
    id = 0
    for i in range(len(active_quizzes)):
        if id + i not in list(active_quizzes.keys()):
            return str(id + i)
    return str(len(active_quizzes))

def find_user_room(sid):
    for room in list(active_quizzes.keys()):
        if active_quizzes[room]["host"] == sid:
            return room, True
        for player in list(active_quizzes[room]["players"].keys()):
            if player == sid:
                return room, False
    return None, None

if __name__ == "__main__":
    socketio.run(app, debug=True)
