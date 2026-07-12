document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    const sidebarClose = document.getElementById("sidebarClose");
    const backdrop = document.getElementById("sidebarBackdrop");

    // NOTE: dark-mode toggling and the #searchBox filter are handled solely
    // by theme.js and search.js respectively, to avoid double-binding the
    // same listeners twice (that used to cause the toggle/filter to fire
    // more than once per click/keystroke).

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

    window.addEventListener("resize", function () {
        if (window.innerWidth > 991) {
            closeSidebar();
        }
    });

    // --- Topbar "Search" button: focuses the current page's in-page search
    // box instead of doing nothing. If the current page has no searchable
    // table, the button is hidden so it never appears as dead UI.
    const pageSearchBox = document.getElementById("searchBox");
    const topbarSearch = document.getElementById("topbarSearch");
    const topbarSearchMobile = document.getElementById("topbarSearchMobile");

    function focusPageSearch() {
        if (!pageSearchBox) return;
        pageSearchBox.scrollIntoView({ behavior: "smooth", block: "center" });
        pageSearchBox.focus();
    }

    if (pageSearchBox) {
        topbarSearch?.addEventListener("click", focusPageSearch);
        topbarSearchMobile?.addEventListener("click", focusPageSearch);
    } else {
        topbarSearch?.classList.add("d-none");
        topbarSearchMobile?.closest("li")?.classList.add("d-none");
    }

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
