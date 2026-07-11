document.addEventListener("DOMContentLoaded", function () {

    const searchBox = document.getElementById("searchBox");

    if (!searchBox) return;

    searchBox.addEventListener("keyup", function () {

        let value = this.value.toLowerCase();

        let rows = document.querySelectorAll("tbody tr");

        rows.forEach(function (row) {

            row.style.display =
                row.innerText.toLowerCase().includes(value)
                    ? ""
                    : "none";

        });

    });

});