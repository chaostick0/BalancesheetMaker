document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.flash-toast').forEach(function (toast, index) {
        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-8px)';
            setTimeout(function () {
                toast.remove();
            }, 250);
        }, 3600 + index * 200);
    });
});
