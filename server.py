from flask import Flask, session, render_template, request
from flask_socketio import SocketIO, join_room
from uuid import uuid4 as generate_id; from secrets import token_hex
from game import Game

app = Flask(__name__)
app.secret_key = token_hex(32) 
socketio = SocketIO(app, async_mode="eventlet")
games = {}


@app.before_request
def assign_player_id_and_username():
    if "player_id" not in session:
        session["player_id"] = str(generate_id())
        session["username"] = f"Guest ({str(generate_id())[:4]})"
    else:
        new_username = request.form.get("new_username")
        if new_username and " " not in new_username:
            session["username"] = new_username + session["username"][-7:]


@app.route("/", methods=['GET', 'POST']) 
def serve_lobby():
    return render_template("lobby.html", games=games, username=session["username"])


@app.route("/rules")
def serve_rules():
    return render_template("rules.html")


@app.route("/play", methods=['GET', 'POST'])
def serve_game(): 
    try:
        return render_template("game.html", game=games[request.args.get("game_id")], username=session["username"])
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

    if not game_name or set(game_name) == { " " }:
        game_name = f"Game by {session['username']}"

    games[game_id] = Game(game_name, session['username'])

    socketio.emit("add game to list", { "id": game_id, "name": game_name })


@socketio.on("request seat")
def assign_seat(seat_number):
    game_id = request.args.get("game_id")
    game = games[game_id]

    if game.players[seat_number] is None:
        game.players[seat_number] = session["player_id"]
        game.usernames[seat_number] = session["username"]

        socketio.emit("grant seat", { "number": seat_number, "user": session["username"] }, room=game_id) 


@socketio.on("request move")
def handle_move_request(move): 
    game_id = request.args.get("game_id")
    if game_id not in games:
        return

    game = games[game_id]
    if game.players[game.whose_turn] != session["player_id"]:
        socketio.emit("update board state", game.board.fen(), room=request.sid)
        return
    
    
    move_data = game.make_move(move)
    if not move_data:
        socketio.emit("update board state", game.board.fen(), room=request.sid)
        return
    
    move_type, new_board_state = move_data
    socketio.emit("make move sound", move_type)
    socketio.emit("update board state", new_board_state, room=game_id)

    if game.outcome is not None:
        game.result_message = "Draw" if game.outcome == 'draw' else f"{session['username']} wins"
        socketio.emit("end game", game.result_message, room=game_id)


@socketio.on("submit message")
def send_message(message_content):
    if not message_content or set(message_content) == { " " }:
        return
    
    game_id = request.args.get("game_id")
    message = { "sender": session["username"], "content": message_content }
    games[game_id].messages.append(message)
    socketio.emit("update chat", message, room=game_id)
    

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)