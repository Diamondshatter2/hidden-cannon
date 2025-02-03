const player_names = ['Red', 'Yellow'], player_colors = ['red', 'yellow'];
let columns, seats, seat_buttons, indicator;

const drop_sounds = [1, 2, 3, 4, 5].map(number => new Audio(`/static/audio/disc-drop-${number}.mp3`));
const end_sound = new Audio('static/audio/game-end.mp3');

const game_id = new URLSearchParams(window.location.search).get('game_id');
const socket = io.connect({ query: { game_id } });


socket.emit('connect to game');

document.addEventListener('DOMContentLoaded', () => {
    columns = Array.from(document.querySelectorAll('.column'));
    seats = Array.from(document.querySelectorAll('.seat'));
    seat_buttons = Array.from(document.querySelectorAll('.seat_button'));
    indicator = document.getElementById('indicator');

    seat_buttons.forEach(button => button.addEventListener('click', request_seat));
    columns.forEach(column => column.addEventListener('click', request_move));
});

function request_seat() {
    socket.emit('request seat', seat_buttons.indexOf(this)); 
}

function request_move() {
    socket.emit('request move', columns.indexOf(this));
}

socket.on('make move', move_data => {
    const column_index = move_data["column"], row_index = move_data["row"], player = move_data["player"];
    const space = columns[column_index].children[row_index];

    drop_sounds[Math.floor(Math.random() * drop_sounds.length)].play();
    space.style.backgroundColor = player_colors[player];
});


socket.on('refresh indicator', data => {
    const outcome = data['outcome'], whose_turn = data['whose_turn'];

    if (outcome == null) {
        indicator.firstElementChild.style.backgroundColor = player_colors[whose_turn];
    }
    else {
        end_sound.play();
        indicator.innerHTML = ((outcome == 'draw') ? 'Draw' : `${player_names[outcome]} wins`); 
        indicator.classList.add('outcome');
    }
});

socket.on('refresh seats', usernames => {
    for (let i = 0; i < 2; i++) {
        if (usernames[i] != null) {
            seats[i].innerHTML = usernames[i];
        }
    }
});
