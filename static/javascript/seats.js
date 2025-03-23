let seats, options;

const seats_socket = io.connect({ query: { game_id } });


seats_socket.emit('connect to game');

document.addEventListener('DOMContentLoaded', () => {
    seats = Array.from(document.querySelectorAll('.seat'));
    options = document.getElementById('game_options');
    // following could be refactored with for-of loop
    resign = document.getElementById('resign');
    offer_draw = document.getElementById('offer_draw');

    offer_draw.addEventListener('click', () => {
        seats_socket.emit('offer draw');
        alert('Sorry, this feature is still in development.');
    });
    resign.addEventListener('click', () => seats_socket.emit('resign'));
});

seats_socket.on('grant seat', seat => seats[seat["number"]].innerHTML = seat["user"]);

seats_socket.on('flip board', () => board.orientation('black'));

// These functions arw found in game.js
seats_socket.on('offer cannon selection', piece => offer_cannon_selection(piece)); // redundant syntax?
seats_socket.on('highlight cannon', square => highlight_cannon(square));


seats_socket.on('begin game', () => {
    notify.play(); // this will only play for players 
    options.style.display = 'block';
});
