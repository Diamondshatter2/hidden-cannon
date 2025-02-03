from flask import Flask, session, render_template, request
from flask_socketio import SocketIO, join_room
from uuid import uuid4 as generate_id; from secrets import token_hex
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
def serve_lobby():
    return render_template("lobby.html", games=games)


@app.route("/play")
def serve_game(): 
    try:
        return render_template("game.html", game=games[request.args.get("game_id")])
    except KeyError:
        return "Invalid game ID", 404


@socketio.on("connect")
def add_connection_to_room():
    game_id = request.args.get("game_id")
    if game_id:
        join_room(game_id)


@socketio.on("new game")
def create_game(game_name):
    game_id = str(generate_id())

    if not game_name:
        game_name = f"Game by {session['username']}"

    games[game_id] = {
        "name": game_name,
        "creator": session["username"],
        "players": [None, None],
        "usernames": [None, None],
        "messages": [],
        "board": [[None for row in range(6)] for column in range(7)],
        "whose_turn": 0,
        "outcome": None
    }

    socketio.emit("add game to list", { "id": game_id, "name": game_name })


@socketio.on("request seat")
def assign_seat(seat_number):
    game_id = request.args.get("game_id")
    game = games[game_id]

    if game["players"][seat_number] is None:
        game["players"][seat_number] = session["player_id"]
        game["usernames"][seat_number] = session["username"]

        socketio.emit("grant seat", { "number": seat_number, "user": session["username"] }, room=game_id) 


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

    row = sum(space is not None for space in game["board"][column])
    if row >= 6:
        return
    
    move_data = { "column": column, "row": row, "player": whose_turn }

    game["board"][column][row] = whose_turn
    game["outcome"] = outcome(game["board"], (column, row))
    game["whose_turn"] = int(not whose_turn)

    socketio.emit("make move", move_data, room=game_id)

    if game["outcome"] is not None:
        socketio.emit("end game", game["outcome"], room=game_id)


@socketio.on("submit message")
def send_message(message_content):
    game_id = request.args.get("game_id")
    message = { "sender": session["username"], "content": message_content }
    games[game_id]["messages"].append(message)
    socketio.emit("update chat", message, room=game_id)
    

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)