const renderIncomeChart = (data, labels) => {
    const ctx = document.getElementById('incomeChart');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Last 6 months income',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Income by Source',
                    color: '#fff'
                },
                legend: {
                    labels: {
                        color: '#fff'
                    }
                }
            }
        }
    });
};

const loadIncomeData = () => {
    fetch('/income/income_category_summary')
        .then(res => res.json())
        .then(results => {
            const source_data = results.income_source_data;
            const [labels, data] = [Object.keys(source_data), Object.values(source_data)];
            renderIncomeChart(data, labels);
        });
};

window.addEventListener('DOMContentLoaded', loadIncomeData);
