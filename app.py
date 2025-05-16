from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app)

players = {}
current_question = {}
scores = {}

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/player/<name>")
def player(name):
    return render_template("player.html", player_name=name)

@socketio.on("join")
def handle_join(data):
    name = data["name"]
    players[name] = {"score": 0}
    print(f"{name} joined")

@socketio.on("submit_answer")
def handle_answer(data):
    name = data["name"]
    answer = data["answer"]
    print(f"{name} answered: {answer}")
    
    # Example: update score (replace with actual logic)
    if answer == current_question.get("answer"):
        players[name]["score"] += 1
    
    # Update leaderboard for admin
    emit("leaderboard_update", players, broadcast=True)

@socketio.on("next_question")
def handle_next_question(data):
    question = data["question"]
    answer = data["answer"]
    current_question["text"] = question
    current_question["answer"] = answer
    
    # Broadcast to all players
    emit("new_question", {"question": question}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
