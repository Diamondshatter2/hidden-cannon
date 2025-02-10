const socket = io.connect();


document.addEventListener('DOMContentLoaded', () => {
    const new_game_overlay = document.getElementById('new_game_popup_overlay');
    const name = document.getElementById('game_name');

    document.getElementById('new_game_button').addEventListener('click', () => {
        new_game_overlay.style.display = 'flex';
        name.focus();
    });

    document.addEventListener('click', event => {
        if (event.target === new_game_overlay || event.target === document.getElementById('cancel_new_game')) {
            name.value = '';
            new_game_overlay.style.display = 'none';
        }
    });    

    document.getElementById('new_game_form').addEventListener('submit', event => { 
        event.preventDefault();
        socket.emit('new game', name.value);
        name.value = '';
        new_game_overlay.style.display = 'none';
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