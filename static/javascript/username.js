document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#username button').addEventListener('click', function() {
        this.parentElement.style.display = 'none';
        document.querySelector('#username form').style.display = 'flex';
    });
});