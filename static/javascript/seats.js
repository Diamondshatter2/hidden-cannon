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

seats_socket.on('change player view', seat_number => {
    resign_button.style.display = 'block';

    if (seat_number == 1) {
        board.orientation('black');
    }
});

seats_socket.on('offer cannon selection', piece => {
    positions = (piece == 'rook' ? [0, 7] : [2, 5]);

    let home_row = document.querySelector('.board-b72b1').lastElementChild.children;
    for (const i of positions) {
        home_row[i].classList.add('piece_highlight');
    } 

    // This function is found in chat.js
    post_message({ sender: 'HIDDEN CANNON SERVER', content: 'Press Q or K to select a ' + piece });

    document.addEventListener('keydown', function transmit_selection(event) {
        let key = event.key.toUpperCase();
        if (key == 'Q' || key == 'K') {
            seats_socket.emit('select cannon', { piece, side: key });

            for (const i of positions) {
                home_row[i].classList.remove('piece_highlight');
            } 

            document.removeEventListener('keydown', transmit_selection);
        }
    });
});

seats_socket.on('highlight cannon', square => {
    document.querySelector('.square-' + square).querySelector('img').classList.add('cannon');   
});

seats_socket.on('begin game', () => notify.play());