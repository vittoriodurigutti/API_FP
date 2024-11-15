document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('#data-table tbody');

    // Función para actualizar la tabla
    function updateTable(data) {
        tableBody.innerHTML = data.map(d => `
            <tr>
                <td>${d.nodo_id}</td>
                <td>${d.temperatura.toFixed(2)}</td>
                <td>${d.humedad.toFixed(2)}</td>
                <td>${d.luz_ambiente.toFixed(2)}</td>
                <td>${d.humedad_suelo_cap}</td>
                <td>${d.humedad_suelo_res}</td>
                <td>${d.nivel_agua}</td>
                <td>${d.distancia}</td>
                <td>${d.iluminacion ? 'Encendido' : 'Apagado'}</td>
                <td>${d.bomba ? 'Encendido' : 'Apagado'}</td>
                <td>${d.dispositivo_id}</td>
            </tr>`).join('');
    }

    // Función para crear o actualizar un gráfico
    function createChart(context, label, data, color) {
        return new Chart(context, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: label,
                    data: data.values,
                    backgroundColor: `${color}33`, // Transparent background
                    borderColor: color,
                    borderWidth: 1,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Función para actualizar los gráficos
    function updateCharts(data) {
        const labels = data.map(d => `Nodo ${d.nodo_id}`);
        const tempData = data.map(d => d.temperatura);
        const humData = data.map(d => d.humedad);
        const luzData = data.map(d => d.luz_ambiente);

        // Crear o actualizar gráficos
        createChart(
            document.getElementById('tempChart').getContext('2d'),
            'Temperatura (°C)',
            { labels, values: tempData },
            'rgba(255, 99, 132, 1)'
        );

        createChart(
            document.getElementById('humChart').getContext('2d'),
            'Humedad (%)',
            { labels, values: humData },
            'rgba(54, 162, 235, 1)'
        );

        createChart(
            document.getElementById('luzChart').getContext('2d'),
            'Luz Ambiente',
            { labels, values: luzData },
            'rgba(255, 206, 86, 1)'
        );
    }

    // Función para cargar datos desde la API
    async function fetchData() {
        try {
            const response = await fetch('/api/datos');
            if (!response.ok) {
                throw new Error('Error en la respuesta de la API');
            }
            const data = await response.json();

            // Actualizar tabla y gráficos
            updateTable(data);
            updateCharts(data);
        } catch (error) {
            console.error('Error al cargar datos:', error);
            tableBody.innerHTML = '<tr><td colspan="11">Error al cargar los datos</td></tr>';
        }
    }

    // Llamar a la función para cargar datos al cargar la página
    fetchData();
});
