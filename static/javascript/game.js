let columns, indicator;

const drop_sounds = [1, 2, 3, 4, 5].map(number => new Audio(`/static/audio/disc-drop-${number}.mp3`));
const end_sound = new Audio('static/audio/game-end.mp3');

const game_id = new URLSearchParams(window.location.search).get('game_id');
const socket = io.connect({ query: { game_id } });


document.addEventListener('DOMContentLoaded', () => {
    columns = Array.from(document.querySelectorAll('.column'));
    indicator = document.getElementById('indicator');

    columns.forEach(column => column.addEventListener('click', request_move));
});

function request_move() {
    socket.emit('request move', columns.indexOf(this));
}

socket.on('make move', move_data => {
    const space = columns[move_data["column"]].children[move_data["row"]];
    const player = move_data["player"];

    drop_sounds[Math.floor(Math.random() * drop_sounds.length)].play(); // Plays random drop sound
    space.style.backgroundColor = colors[player];
    indicator.firstElementChild.style.backgroundColor = colors[player ^ 1]; // var bitwise-XOR 1 toggles var between 0 and 1
});


socket.on('end game', result => {
    end_sound.play();
    indicator.innerHTML = result; 
    indicator.classList.add('result');
});