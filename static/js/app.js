document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    const sidebarClose = document.getElementById("sidebarClose");
    const backdrop = document.getElementById("sidebarBackdrop");
    const themeToggle = document.getElementById("themeToggle");

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

    const forms = document.querySelectorAll("#assetsForm, #liabilitiesForm");
    const unsavedBanner = document.getElementById("unsavedBanner");
    const amountInputs = document.querySelectorAll(".amount-input");
    const removeButtons = document.querySelectorAll(".remove-row-btn");
    const groupSelectors = document.querySelectorAll("select[name='group_name_select']");

    function saveFormState(form, storageKey) {
        if (!form) return;
        const state = {};
        Array.from(form.elements).forEach(function (element) {
            if (!element.name || element.disabled) return;
            if (element.type === "checkbox" || element.type === "radio") {
                state[element.name] = element.checked;
            } else {
                state[element.name] = element.value;
            }
        });
        sessionStorage.setItem(storageKey, JSON.stringify(state));
    }

    function restoreFormState(form, storageKey) {
        if (!form) return;
        const stored = sessionStorage.getItem(storageKey);
        if (!stored) return;
        try {
            const state = JSON.parse(stored);
            Array.from(form.elements).forEach(function (element) {
                if (!element.name || !(element.name in state)) return;
                if (element.type === "checkbox" || element.type === "radio") {
                    element.checked = Boolean(state[element.name]);
                } else {
                    element.value = state[element.name];
                }
            });
        } catch (error) {
            console.warn("Unable to restore form state", error);
        }
    }

    amountInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            if (unsavedBanner) {
                unsavedBanner.classList.remove("d-none");
            }
            window.onbeforeunload = function () {
                return "You have unsaved changes.";
            };
        });
    });

    function validateAmounts() {
        let hasError = false;
        amountInputs.forEach(function (input) {
            const errorNode = document.querySelector(`[data-error-for="${input.name}"]`);
            const value = input.value.trim();
            const isValid = value === "" || /^\d+(\.\d{1,2})?$/.test(value);
            if (!isValid) {
                hasError = true;
                input.classList.add("is-invalid");
                if (errorNode) {
                    errorNode.textContent = "Enter a valid non-negative amount.";
                }
            } else {
                input.classList.remove("is-invalid");
                if (errorNode) {
                    errorNode.textContent = "";
                }
            }
        });
        return !hasError;
    }

    forms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!validateAmounts()) {
                event.preventDefault();
                return;
            }
            if (unsavedBanner) {
                unsavedBanner.classList.add("d-none");
            }
            window.onbeforeunload = null;
        });
    });

    removeButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            if (!window.confirm("Delete this row?")) {
                return;
            }
            fetch(button.getAttribute("data-remove-url"), {
                method: "POST",
                headers: {"X-Requested-With": "XMLHttpRequest"},
            }).then(function (response) {
                if (response.ok) {
                    button.closest("tr").remove();
                }
            });
        });
    });

    groupSelectors.forEach(function (select) {
        const relatedInput = select.parentElement.querySelector("input[name='group_name']");
        select.addEventListener("change", function () {
            if (this.value === "__new__") {
                relatedInput?.classList.remove("d-none");
            } else {
                relatedInput?.classList.add("d-none");
            }
        });
    });

    const assetAddForm = document.getElementById("assetAddForm");
    const liabilityAddForm = document.getElementById("liabilityAddForm");
    const assetsForm = document.getElementById("assetsForm");
    const liabilitiesForm = document.getElementById("liabilitiesForm");
    restoreFormState(assetsForm, "balance-sheet-assets-state");
    restoreFormState(liabilitiesForm, "balance-sheet-liabilities-state");

    [assetAddForm, liabilityAddForm].forEach(function (form) {
        if (!form) return;
        form.addEventListener("submit", function (event) {
            const formData = new FormData(form);
            if (!formData.get("item_name")) {
                event.preventDefault();
                return;
            }
            if (form.id === "assetAddForm") {
                saveFormState(assetsForm, "balance-sheet-assets-state");
            } else if (form.id === "liabilityAddForm") {
                saveFormState(liabilitiesForm, "balance-sheet-liabilities-state");
            }
            fetch(form.action, {
                method: "POST",
                headers: {"X-Requested-With": "XMLHttpRequest"},
                body: formData,
            }).then(function (response) {
                if (response.ok) {
                    window.location.reload();
                }
            });
            event.preventDefault();
        });
    });
});