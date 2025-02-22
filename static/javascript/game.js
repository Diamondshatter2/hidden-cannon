const end_sound = new Audio('static/audio/game-end.mp3');

let board;
const game_id = new URLSearchParams(window.location.search).get('game_id');
const socket = io.connect({ query: { game_id } });

document.addEventListener('DOMContentLoaded', () => {
    board = Chessboard('board', {
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

    document.querySelector('#options button').addEventListener('click', () => {
        let board_classes = document.querySelector('.board-b72b1').classList;
        if (board_classes.contains('upside-down')) {
            board_classes.remove('upside-down');
        } else {
            board_classes.add('upside-down');
        }
    });
})

socket.on('update board state', board_state => {
    console.log(board_state);
    board.position(board_state);
})

socket.on('end game', result => {
    end_sound.play();
    indicator.innerHTML = result; 
    indicator.classList.add('result');
});

// testing
socket.on('test', message => console.log(message));