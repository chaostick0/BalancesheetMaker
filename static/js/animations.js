document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.card-hover, .btn, .form-control').forEach(function (el) {
        el.classList.add('fade-in');
    });
});
