document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('balanceChart');
    if (!canvas) return;

    if (typeof Chart === 'undefined') {
        canvas.parentElement.innerHTML = '<div class="chart-placeholder d-flex align-items-center justify-content-center">Chart unavailable</div>';
        return;
    }

    // Real figures come from the server via data attributes on the canvas
    // (see dashboard.html) instead of being hardcoded here.
    const assets = parseFloat(canvas.dataset.assets || '0');
    const liabilities = parseFloat(canvas.dataset.liabilities || '0');
    const netWorth = parseFloat(canvas.dataset.netWorth || '0');

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: ['Assets', 'Liabilities', 'Net Worth'],
            datasets: [{
                label: 'Current Position',
                data: [assets, liabilities, netWorth],
                backgroundColor: ['#2563eb', '#14b8a6', '#7c3aed'],
                borderRadius: 10
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { color: '#64748b' } },
                x: { ticks: { color: '#64748b' } }
            }
        }
    });
});
