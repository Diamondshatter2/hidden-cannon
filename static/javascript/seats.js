let seats, seat_buttons, resign_button;

const seats_socket = io.connect({ query: { game_id } });

document.addEventListener('DOMContentLoaded', () => {
    seats = Array.from(document.querySelectorAll('.seat'));
    seat_buttons = Array.from(document.querySelectorAll('.seat_button'));
    resign_button = document.getElementById('resign');

    seat_buttons.forEach(button => button.addEventListener('click', request_seat));
});

function request_seat() {
    seats_socket.emit('request seat', seats.indexOf(this.parentElement)); 
}

seats_socket.on('grant seat', seat => seats[seat["number"]].innerHTML = seat["user"]);

seats_socket.on('show resign button', () => resign_button.style.display = 'block');

seats_socket.on('flip board', flip_board);

seats_socket.on('begin game', () => {
    notify.play();
    resign_button.addEventListener('click', () => seats_socket.emit('resign'));
});