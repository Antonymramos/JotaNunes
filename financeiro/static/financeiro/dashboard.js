document.addEventListener('DOMContentLoaded', function () {
    window.createChart = function (labels, vendasData, comprasData) {
        console.log('Criando gráfico:', labels, vendasData, comprasData); // Depuração
        const ctx = document.getElementById('transacoesChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Vendas',
                    data: vendasData,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }, {
                    label: 'Compras',
                    data: comprasData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Valor (R$)' }
                    }
                }
            }
        });
    };

    // Verifica se já há dados para inicializar
    if (window.chartData) {
        createChart(window.chartData.labels, window.chartData.vendas, window.chartData.compras);
    } else {
        console.log('Nenhum dado de gráfico disponível.');
    }
});