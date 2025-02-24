const move_sound = new Audio('static/audio/public_sound_standard_Move.mp3');
const capture_sound = new Audio('static/audio/public_sound_standard_Capture.mp3');
const notify = new Audio('static/audio/public_sound_standard_GenericNotify.mp3');

let board, indicator;
const game_id = new URLSearchParams(window.location.search).get('game_id');
const socket = io.connect({ query: { game_id } });

socket.emit('connect to game');

document.addEventListener('DOMContentLoaded', () => {
    indicator = document.getElementById('indicator');
    
    let orientation = (player == 0 || player == 'None' ? 'white' : 'black');
    board = Chessboard('board', {
        orientation: orientation,
        draggable: true,
        dropOffBoard: 'snapback',
        position: fen,
        pieceTheme: '/static/images/{piece}.png',
        onDrop: (source, target) => {
            if (source != target) {
                socket.emit('request move', { from: source, to: target });
            }
        }
    });
});

socket.on('update board state', board_state => board.position(board_state));

socket.on('make move sound', move_type => {
    if (move_type == 'capture') {
        capture_sound.play();
    } else {
        move_sound.play();
    }
});

socket.on('end game', result => {
    notify.play();
    document.getElementById('resign').style.display = 'none';
    indicator.innerHTML = result; 
});

// testing
socket.on('test', message => console.log(message));