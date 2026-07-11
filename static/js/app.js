document.addEventListener("DOMContentLoaded", function () {
    const searchBox = document.getElementById("searchBox");
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    const sidebarClose = document.getElementById("sidebarClose");
    const backdrop = document.getElementById("sidebarBackdrop");
    const themeToggle = document.getElementById("themeToggle");

    if (searchBox) {
        searchBox.addEventListener("keyup", function () {
            const value = this.value.toLowerCase();
            const rows = document.querySelectorAll("tbody tr");

            rows.forEach(function (row) {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(value) ? "" : "none";
            });
        });
    }

    function closeSidebar() {
        sidebar?.classList.remove("open");
        backdrop?.classList.remove("show");
        document.body.classList.remove("sidebar-open");
    }

    function openSidebar() {
        sidebar?.classList.add("open");
        backdrop?.classList.add("show");
        document.body.classList.add("sidebar-open");
    }

    menuToggle?.addEventListener("click", openSidebar);
    sidebarClose?.addEventListener("click", closeSidebar);
    backdrop?.addEventListener("click", closeSidebar);

    const savedTheme = localStorage.getItem("balance-sheet-theme") || "light";
    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
        if (themeToggle) {
            themeToggle.textContent = "☀️";
        }
    }

    themeToggle?.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");
        const isDark = document.body.classList.contains("dark-mode");
        localStorage.setItem("balance-sheet-theme", isDark ? "dark" : "light");
        themeToggle.textContent = isDark ? "☀️" : "🌙";
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 991) {
            closeSidebar();
        }
    });

    document.querySelectorAll(".flash-toast").forEach(function (toast, index) {
        setTimeout(function () {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-8px)";
            setTimeout(function () {
                toast.remove();
            }, 250);
        }, 3200 + index * 200);
    });
});