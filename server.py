from flask import Flask, session, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room
from uuid import uuid4 as generate_id
from secrets import token_hex
from game import outcome

app = Flask(__name__)
app.secret_key = token_hex(32) 
socketio = SocketIO(app, async_mode="eventlet")
games = {}


@app.before_request
def assign_player_id():
    if "player_id" not in session:
        session["player_id"] = str(generate_id())
        session["username"] = f"Guest_{str(generate_id())[:4]}"


@app.route("/")
def serve_index():
    return render_template("index.html")


@app.route("/play")
def serve_game(): 
    if request.args.get("game_id") not in games:
        return "Invalid game ID", 404
    
    return render_template("game.html")


@socketio.on("connect to index")
def refresh_games_list():
    socketio.emit("refresh games list", [{ "id": game_id, "creator": games[game_id]["creator"] } for game_id in games], room=request.sid)


@socketio.on("connect to game")
def connect_to_game():
    game_id = request.args.get("game_id")
    game = games[game_id]
    join_room(game_id)  

    socketio.emit("refresh board", game["board"], room=request.sid)
    socketio.emit("refresh indicator", { "outcome": game["outcome"], "whose_turn": game["whose_turn"] }, room=request.sid)
    socketio.emit("refresh seats", game["usernames"], room=request.sid) 
    socketio.emit("refresh chat", game["messages"])


@socketio.on("new game")
def create_game():
    game_id = str(generate_id())

    games[game_id] = {
        "creator": session["username"],
        "players": [None, None],
        "usernames": [None, None],
        "messages": [],
        "board": [[None for row in range(6)] for column in range(7)],
        "fullness": [0 for column in range(7)],
        "whose_turn": 0,
        "outcome": None
    }

    socketio.emit("add game to list", { "id": game_id, "creator": games[game_id]["creator"] })


@socketio.on("request seat")
def assign_seat(seat_number):
    game_id = request.args.get("game_id")
    game = games[game_id]

    if game["players"][seat_number] == None:
        game["players"][seat_number] = session["player_id"]
        game["usernames"][seat_number] = session["username"]

        socketio.emit("refresh seats", game["usernames"], room=game_id) 


@socketio.on("request move")
def handle_move_request(column): 
    game_id = request.args.get("game_id")
    if game_id not in games:
        return

    game = games[game_id] 
    if game["outcome"] is not None:
        return
    
    whose_turn = game["whose_turn"]
    if game["players"][whose_turn] != session["player_id"]:
        return

    if not 0 <= column < 7:
        return

    row = game["fullness"][column]
    if row >= 6:
        return
    
    move_data = { "column": column, "row": row, "player": whose_turn }

    game["board"][column][row] = whose_turn
    game["fullness"][column] += 1
    game["outcome"] = outcome(game["board"], (column, row))
    game["whose_turn"] = int(not whose_turn)

    socketio.emit("make move", move_data, room=game_id)
    socketio.emit("refresh indicator", { "outcome": game["outcome"], "whose_turn": game["whose_turn"] }, room=game_id)


@socketio.on("submit message")
def send_message(message_content):
    message = { "sender": session["username"], "content": message_content }
    games[request.args.get("game_id")]["messages"].append(message)
    socketio.emit("update chat", message)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)