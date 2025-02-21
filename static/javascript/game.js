document.addEventListener('DOMContentLoaded', () => {
    var board = Chessboard('board', {
        draggable: true,
        dropOffBoard: 'snapback',
        position: 'start',
        pieceTheme: '/static/images/{piece}.png'
    });
})

const end_sound = new Audio('static/audio/game-end.mp3');

const game_id = new URLSearchParams(window.location.search).get('game_id');
const socket = io.connect({ query: { game_id } });

socket.on('end game', result => {
    end_sound.play();
    indicator.innerHTML = result; 
    indicator.classList.add('result');
});