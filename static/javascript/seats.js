let seats, seat_buttons;

const seats_socket = io.connect({ query: { game_id } });

document.addEventListener('DOMContentLoaded', () => {
    seats = Array.from(document.querySelectorAll('.seat'));
    seat_buttons = Array.from(document.querySelectorAll('.seat_button'));

    seat_buttons.forEach(button => button.addEventListener('click', request_seat));
});

function request_seat() {
    seats_socket.emit('request seat', seats.indexOf(this.parentElement)); 
}

seats_socket.on('grant seat', seat => seats[seat["number"]].innerHTML = seat["user"]);

seats_socket.on('flip board', () => board.orientation('black'));

seats_socket.on('begin game', () => notify.play());