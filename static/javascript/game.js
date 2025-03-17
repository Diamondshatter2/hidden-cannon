const move_sound = new Audio('static/audio/public_sound_standard_Move.mp3');
const capture_sound = new Audio('static/audio/public_sound_standard_Capture.mp3');
const notify = new Audio('static/audio/public_sound_standard_GenericNotify.mp3');

let board, indicator;
const socket = io.connect({ query: { game_id } });

document.addEventListener('DOMContentLoaded', () => {
    indicator = document.getElementById('indicator');
    
    board = Chessboard('board', {
        orientation: (player == 0 ? 'black' : 'white'),
        draggable: true,
        dropOffBoard: 'snapback',
        position: fen,
        pieceTheme: '/static/images/{piece}.png',

        onDrop: (source, target, piece) => {
            let promotion = null; 

            if (piece[1] == 'P' && (target[1] == 1 || target[1] == 8)) {
                promotion = 5 // python chess.QUEEN
            }

            if (source != target && target != 'offboard') {
                socket.emit('request move', { from: source, to: target, promotion });
            }
        }
    });

    if (player != 'None' && is_active == 'False') {
        if (rook_cannon == 'None') {
            offer_cannon_selection('rook');
        } else if (bishop_cannon == 'None') {
            offer_cannon_selection('bishop');
        }
    }
});

function offer_cannon_selection(piece) {
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
}

socket.on('update board state', board_state => board.position(board_state));

socket.on('play move sound', is_capture => {
    if (is_capture) {
        capture_sound.play();
    } else {
        move_sound.play();
    }
});

socket.on('end game', result => {
    notify.play();
    document.getElementById('game_options').style.display = 'none'; // redundant selection
    indicator.innerHTML = result; 
    indicator.classList.add('result');
});

// testing
socket.on('test', message => console.log(message));

socket.on('alert', message => alert(message));