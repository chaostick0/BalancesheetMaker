document.addEventListener('DOMContentLoaded', function () {
    // Single source of truth for dark mode. Both the desktop (#themeToggle)
    // and mobile (#themeToggleMobile) buttons are kept in sync here so a
    // toggle in either location updates the other and never double-fires.
    const toggles = [
        document.getElementById('themeToggle'),
        document.getElementById('themeToggleMobile'),
    ].filter(Boolean);

    const savedTheme = localStorage.getItem('balance-sheet-theme') || 'light';

    function applyIcon(isDark) {
        toggles.forEach(function (btn) {
            btn.textContent = isDark ? '☀️' : '🌙';
        });
    }

    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    applyIcon(savedTheme === 'dark');

    function toggleTheme() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('balance-sheet-theme', isDark ? 'dark' : 'light');
        applyIcon(isDark);
    }

    toggles.forEach(function (btn) {
        btn.addEventListener('click', toggleTheme);
    });
});
