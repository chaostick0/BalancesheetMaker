document.addEventListener('DOMContentLoaded', function () {
    const searchBox = document.getElementById('searchBox');
    if (!searchBox) return;

    let timer;
    searchBox.addEventListener('input', function () {
        const value = this.value.toLowerCase();
        clearTimeout(timer);
        timer = setTimeout(function () {
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach(function (row) {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(value) ? '' : 'none';
            });
        }, 120);
    });

    document.addEventListener('keydown', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
            event.preventDefault();
            searchBox.focus();
            searchBox.select();
        }
    });
});
