const socket = io.connect();


document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('new_game_button').addEventListener('click', () => {
        // menu pops up
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