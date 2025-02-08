def propagate_username_change(games, player_id, new_username):
    for game in games.values():
        for i in [1, 2]:
            if game.players[i] == player_id:
                game.usernames[i] = new_username
                return

