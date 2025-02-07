const username_socket = io.connect();

document.addEventListener('DOMContentLoaded', () => {
    const button = document.querySelector('#username button');
    
    button.addEventListener('click', function() {
        this.parentElement.style.display = 'none';
    });
});