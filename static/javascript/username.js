const username_socket = io.connect();

document.addEventListener('DOMContentLoaded', () => {
    const button = document.querySelector('#username button');
    const form = document.getElementById('username_form');
    
    button.addEventListener('click', function() {
        this.parentElement.style.display = 'none';
        form.style.display = 'flex';
    });
});