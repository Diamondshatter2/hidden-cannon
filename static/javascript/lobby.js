const socket = io.connect();

socket.emit('connect to lobby');

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('button').addEventListener('click', () => { socket.emit('new game') });
});

function add_game_to_list(game) {
    const id = game['id'], creator = game['creator'];
    const link = document.createElement('a');
    link.classList.add('game');
    link.href = `/play?game_id=${id}` 
    link.innerText = `Game by ${creator}`; 
    document.getElementById('games').appendChild(link);
}

socket.on('add game to list', add_game_to_list);
socket.on('refresh games list', games => games.forEach(game => add_game_to_list(game)));
