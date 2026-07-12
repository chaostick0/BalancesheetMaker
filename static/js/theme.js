document.addEventListener('DOMContentLoaded', function () {
    // Single source of truth for dark mode. Both the desktop (#themeToggle)
    // and mobile (#themeToggleMobile) buttons are kept in sync here so a
    // toggle in either location updates the other and never double-fires.
    const toggles = [
        document.getElementById('themeToggle'),
        document.getElementById('themeToggleMobile'),
    ].filter(Boolean);

    const savedTheme = localStorage.getItem('balance-sheet-theme') || 'light';
    const themeColorMeta = document.querySelector('meta[name="theme-color"]');

    function applyIcon(isDark) {
        toggles.forEach(function (btn) {
            btn.textContent = isDark ? '☀️' : '🌙';
        });
    }

    function applyTheme(isDark) {
        document.body.classList.toggle('dark-mode', isDark);
        if (themeColorMeta) {
            themeColorMeta.setAttribute('content', isDark ? '#020617' : '#0f172a');
        }
    }

    if (savedTheme === 'dark') {
        applyTheme(true);
    } else {
        applyTheme(false);
    }
    applyIcon(savedTheme === 'dark');

    function toggleTheme() {
        const isDark = !document.body.classList.contains('dark-mode');
        applyTheme(isDark);
        localStorage.setItem('balance-sheet-theme', isDark ? 'dark' : 'light');
        applyIcon(isDark);
    }

    toggles.forEach(function (btn) {
        btn.addEventListener('click', toggleTheme);
    });
});
