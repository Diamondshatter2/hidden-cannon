let seats, resign_button;

const seats_socket = io.connect({ query: { game_id } });


seats_socket.emit('connect to game');

document.addEventListener('DOMContentLoaded', () => {
    seats = Array.from(document.querySelectorAll('.seat'));
    resign_button = document.getElementById('resign');

    resign_button.addEventListener('click', () => seats_socket.emit('resign'));
});

seats_socket.on('grant seat', seat => seats[seat["number"]].innerHTML = seat["user"]);

seats_socket.on('change player view', seat_number => {
    resign_button.style.display = 'block';

    if (seat_number == 1) {
        board.orientation('black');
    }
});

// This function is found in game.js
seats_socket.on('offer cannon selection', piece => offer_cannon_selection(piece)); // redundant syntax?

seats_socket.on('highlight cannon', square => {
    document.querySelector('.square-' + square).querySelector('img').classList.add('cannon');   
});

seats_socket.on('begin game', () => notify.play());