const socket = io.connect();

document.addEventListener('DOMContentLoaded', () => {
    const name = document.getElementById('game_name');

    document.getElementById('new_game_form').addEventListener('submit', event => { 
        event.preventDefault();
        socket.emit('new game', name.value);
        name.value = '';
    });
});

socket.on('add game to list', game => {
    const id = game['id'], name = game['name'];
    const link = document.createElement('a');
    link.classList.add('game');
    link.href = `/play?game_id=${id}` 
    link.innerText = name;
    document.getElementById('games').appendChild(link);
});