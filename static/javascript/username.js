document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#username button').addEventListener('click', function() {
        this.parentElement.style.display = 'none';
        const form = document.querySelector('#username form');
        form.style.display = 'flex';
        form.firstElementChild.focus();
    });
});