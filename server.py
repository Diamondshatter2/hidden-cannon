from flask import Flask, session, render_template, request; from flask_socketio import SocketIO, join_room
from uuid import uuid4 as generate_id; from secrets import token_hex; from random import choice
from game import Game_state, ROOK, BISHOP

class Game:
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator
        self.players = [None, None]
        self.usernames = [None, None]
        self.messages = []
        self.state = Game_state()
        
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


@app.errorhandler(404) 
def serve_404_page(e):
    return render_template("404.html", missing="page", username=session["username"]), 404


@app.route("/", methods=["GET", "POST"]) 
def serve_lobby():
    return render_template("lobby.html", games=games, username=session["username"])


@app.route("/rules")
def serve_rules():
    return render_template("rules.html", username=session["username"])


@app.route("/play", methods=["GET", "POST"])
def serve_game(): 
    try:
        game = games[request.args["game_id"]]
    except KeyError:
        return render_template("404.html", missing="game", username=session["username"]), 404 # need to return 404?
    
    player = None
    for i in [0, 1]:
        if session["player_id"] == game.players[i]:
            player = i
            break 

    return render_template("game.html", game=game, player=player, username=session["username"], rook=ROOK, bishop=BISHOP)


@socketio.on("connect")
def add_connection_to_room():
    game_id = request.args.get("game_id")
    if game_id:
        join_room(game_id)


@socketio.on("new game")
def create_game(color):
    game_id = str(generate_id())

    game_name = f"Game by {session["username"]}"

    games[game_id] = Game(game_name, session["username"]) # second parameter needed?

    color = choice([0, 1]) if color == "random" else int(color)

    games[game_id].players[color] = session["player_id"]
    games[game_id].usernames[color] = session["username"]

    socketio.emit("redirect to game", game_id, room=request.sid)
    socketio.emit("add game to list", { "id": game_id, "name": game_name })


@socketio.on("connect to game")
def connect_to_game():
    game_id = request.args.get("game_id")
    game = games[game_id]

    for player in [0, 1]:
        if game.players[player] is None and session["player_id"] not in game.players:
            game.players[player] = session["player_id"]
            game.usernames[player] = session["username"]

            # Seat number is opposite of player number because seats are displayed as "White: <username>, "Black: <username>"
            socketio.emit("grant seat", { "number": 1 - player, "user": session["username"] }, room=game_id) 
            socketio.emit("flip board", player, room=request.sid) 
            socketio.emit("offer cannon selection", ROOK, room=request.sid)

            break


@socketio.on("select cannon")
def initialize_cannon(selection):
    game = games[request.args["game_id"]]
    piece = selection["piece"]

    # add a check making sure that player can't set bishop cannon before rook cannon

    player = game.players.index(session["player_id"])
    if player is None or game.state.cannons[piece][player] is not None:
        return
    
    positions = {"Q": "a", "K": "h"} if piece == ROOK else {"Q": "c", "K": "f"}            
    game.state.cannons[piece][player] = positions[selection["side"]] + ("1" if player == 1 else "8")

    socketio.emit("highlight cannon", game.state.cannons[piece][player], room=request.sid)

    if piece == ROOK:
        socketio.emit("offer cannon selection", BISHOP, room=request.sid)

    if None not in game.state.cannons[BISHOP]:
        game.state.is_active = True
        socketio.emit("begin game", room=request.args["game_id"])


@socketio.on("request move")
def handle_move_request(move): # switch move and move_data variable names
    game_id = request.args.get("game_id")
    if game_id not in games:
        return

    game = games[game_id]
    if game.players[game.state.board.turn] != session["player_id"]:
        socketio.emit("update board state", game.state.board.fen(), room=request.sid)
        return
    
    move_data = game.state.handle_move_request(move["from"], move["to"], move["promotion"])
    if not move_data:
        socketio.emit("update board state", game.state.board.fen(), room=request.sid)
        return
    
    socketio.emit("play move sound", move_data["is capture"], room=game_id)
    socketio.emit("update board state", move_data["fen"], room=game_id)
    if move_data["reveal cannon"]:
        socketio.emit("highlight cannon", move_data["reveal cannon"], room=game_id)

    if game.state.outcome:
        socketio.emit("end game", game.state.outcome, room=game_id)

    if move["promotion"]:
        socketio.emit("alert", "Promotion piece choice is still in development, but here's a queen!", room=request.sid)


@socketio.on("offer draw")
def offer_draw():
    game_id = request.args.get("game_id")
    game = games[game_id]
    if not game.state.is_active:
        return

    # NEED FUNCTIONALITY HERE


@socketio.on("resign")
def handle_resignation_request():
    game_id = request.args.get("game_id")
    game = games[game_id]
    if not game.state.is_active:
        return

    for i in [0, 1]:
        if session["player_id"] == game.players[i]:
            game.state.outcome = f"{game.state.colors[i - 1]} wins by resignation"
            game.state.is_active = False
            socketio.emit("end game", game.state.outcome, room=game_id)
            break


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