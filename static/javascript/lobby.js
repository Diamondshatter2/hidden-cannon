const socket = io.connect();


document.addEventListener('DOMContentLoaded', () => {
    const new_game_overlay = document.getElementById('new_game_popup_overlay');
    const color = document.querySelector('#color_selection select');

    document.getElementById('new_game_button').addEventListener('click', () => {
        new_game_overlay.style.display = 'flex';
    });

    document.addEventListener('click', event => {
        if (event.target === new_game_overlay || event.target === document.getElementById('cancel_new_game')) {
            color.value = 'random';
            new_game_overlay.style.display = 'none';
        }
    });    

    document.getElementById('new_game_form').addEventListener('submit', event => { 
        event.preventDefault();
        socket.emit('new game', color.value);
        color.value = 'random';
        new_game_overlay.style.display = 'none';
    });
});

socket.on('add game to list', game => {
    const id = game['id'], name = game['name'];
    const link = document.createElement('a');
    link.classList.add('game');
    link.href = `/play?game_id=${id}` 
    link.innerText = name;
    document.getElementById('games').prepend(link);
});

socket.on('redirect to game', game_id => {
    window.location.href = '/play?game_id=' + game_id;
});