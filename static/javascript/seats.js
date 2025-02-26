let seats, seat_buttons, resign_button;

const seats_socket = io.connect({ query: { game_id } });

document.addEventListener('DOMContentLoaded', () => {
    seats = Array.from(document.querySelectorAll('.seat'));
    seat_buttons = Array.from(document.querySelectorAll('.seat_button'));
    resign_button = document.getElementById('resign');

    seat_buttons.forEach(button => button.addEventListener('click', request_seat));
    resign_button.addEventListener('click', () => seats_socket.emit('resign'));
});

function request_seat() {
    seats_socket.emit('request seat', seats.indexOf(this.parentElement)); 
}

seats_socket.on('grant seat', seat => seats[seat["number"]].innerHTML = seat["user"]);

seats_socket.on('offer player options', seat_number => {
    resign_button.style.display = 'block';

    if (seat_number == 1) {
        board.orientation('black');
    }

    let home_row = document.querySelector('.board-b72b1').lastElementChild.children;
    for (const i of [0, 7]) {
        home_row[i].classList.add('piece_highlight');
    } 

    // This function is found in chat.js
    post_message({ sender: 'HIDDEN CANNON SERVER', content: 'Press Q or K to select a rook' });

    document.addEventListener('keydown', event => {
        let key = event.key.toUpperCase();
        if (key == 'Q' || key == 'K') {
            seats_socket.emit('select rook', key);
        }
    });
});

seats_socket.on('begin game', () => notify.play());