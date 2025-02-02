const socket = io.connect();

socket.emit('connect to lobby');

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('new_game_form'), name = document.getElementById('game_name');

    form.addEventListener('submit', event => { 
        event.preventDefault();
        socket.emit('new game', name.value) });
        name.value = null; // this isn't working for some reason
});

function add_game_to_list(game) {
    const id = game['id'], name = game['name'];
    const link = document.createElement('a');
    link.classList.add('game');
    link.href = `/play?game_id=${id}` 
    link.innerText = name;
    document.getElementById('games').appendChild(link);
}

socket.on('add game to list', add_game_to_list);
socket.on('refresh games list', games => games.forEach(game => add_game_to_list(game)));
