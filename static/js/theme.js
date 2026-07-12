document.addEventListener('DOMContentLoaded', function () {
    const toggles = [
        document.getElementById('themeToggle'),
        document.getElementById('themeToggleMobile'),
    ].filter(Boolean);

    const themeColorMeta = document.querySelector('meta[name="theme-color"]');

    function applyTheme() {
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
        if (themeColorMeta) {
            themeColorMeta.setAttribute('content', '#020617');
        }
        localStorage.setItem('balance-sheet-theme', 'dark');
    }

    function applyIcon() {
        toggles.forEach(function (btn) {
            btn.textContent = '🌙';
            btn.classList.add('d-none');
        });
    }

    applyTheme();
    applyIcon();
});
