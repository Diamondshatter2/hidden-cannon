let chat, message_box;
const chat_socket = io.connect({ query: { game_id } });


chat_socket.emit('connect to chat');

document.addEventListener('DOMContentLoaded', () => {
    chat = document.getElementById('messages'), message_box = document.getElementById('message_box');
    chat.scrollTop = chat.scrollHeight;
    
    document.getElementById('chat_form').addEventListener('submit', event => {
        event.preventDefault();
        chat_socket.emit('submit message', message_box.value);
        message_box.value = null;
    });
});

function update_chat(message) {
    const sender = document.createElement('span'), content = document.createElement('span'); 
    sender.innerText = message['sender'], content.innerText = message['content']; 
    sender.style.fontWeight = 'bold';
    chat.appendChild(sender), chat.appendChild(content), chat.appendChild(document.createElement('br'));
}

chat_socket.on('update chat', update_chat);

chat_socket.on('refresh chat', messages => {
    messages.forEach(message => update_chat(message));
});