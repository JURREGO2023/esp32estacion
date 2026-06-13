<?php
    date_default_timezone_set('America/Bogota');
    include_once('esp-database.php');

    // 1. Parámetros de los filtros
    $readings_count = isset($_GET["readingsCount"]) ? $_GET["readingsCount"] : 20;
    $dateStart = isset($_GET['dateStart']) ? $_GET['dateStart'] : null;
    $dateEnd = isset($_GET['dateEnd']) ? $_GET['dateEnd'] : null;

    // 2. Obtener última lectura para indicadores 
    $last_reading = getLastReadings();
    $last_reading_temp = isset($last_reading["value1"]) ? $last_reading["value1"] : 0;
    $last_reading_humi = isset($last_reading["value2"]) ? $last_reading["value2"] : 0;
    $last_reading_time = isset($last_reading["reading_time"]) ? $last_reading["reading_time"] : "Sin datos";

    // 3. Obtener datos según filtro para gráficas y tabla 
    $result = getAllReadings($readings_count, $dateStart, $dateEnd);
    
    $labels = []; 
    $temp_data = []; 
    $humi_data = [];
    $table_rows = "";

    if ($result) {
        while ($row = $result->fetch_assoc()) {
            // Guardamos la hora para el eje X
            $labels[] = date("H:i", strtotime($row["reading_time"]));
            $temp_data[] = $row["value1"];
            $humi_data[] = $row["value2"];
            
            $table_rows .= "<tr>
                <td>".$row["id"]."</td>
                <td>".$row["sensor"]."</td>
                <td>".$row["value1"]." °C</td>
                <td>".$row["value2"]." %</td>
                <td>".$row["reading_time"]."</td>
            </tr>";
        }
        // Invertimos para que el orden cronológico sea de izquierda a derecha
        $labels = array_reverse($labels);
        $temp_data = array_reverse($temp_data);
        $humi_data = array_reverse($humi_data);
    }
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Panel IoT - Bogotá</title>
    <link rel="stylesheet" type="text/css" href="esp-style1.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <style>
        /* Ajuste rápido para separar las gráficas */
        .chart-section { margin-bottom: 30px; }
        .chart-container { position: relative; height: 300px; width: 100%; }
    </style>
</head>
<body>
    <header class="header">
        <h1>📊 PANEL DE CONTROL CLIMÁTICO BOGOTÁ</h1>
        <p>Última actualización: <strong><?php echo $last_reading_time; ?></strong></p>
    </header>

    <div class="container">
        
        <section class="card">
            <h3>🔍 Filtro de Historial</h3>
            <form method="get" class="filter-form">
                <div class="input-group">
                    <label>Desde:</label>
                    <input type="datetime-local" name="dateStart" value="<?php echo $dateStart; ?>">
                </div>
                <div class="input-group">
                    <label>Hasta:</label>
                    <input type="datetime-local" name="dateEnd" value="<?php echo $dateEnd; ?>">
                </div>
                <div class="input-group">
                    <label>Registros:</label>
                    <input type="number" name="readingsCount" value="<?php echo $readings_count; ?>" min="1">
                </div>
                <div class="actions">
                    <button type="submit" class="btn-filter">APLICAR FILTRO</button>
                    <a href="index.php" class="btn-reset">LIMPIAR</a>
                </div>
            </form>
        </section>

        <section class="gauges-container">
            <div class="card gauge-card">
                <h3>TEMPERATURA ACTUAL</h3>
                <div class="gauge-value"><?php echo $last_reading_temp; ?> <small>°C</small></div>
                <div class="gauge-visual">
                    <div class="bar temp-bar" style="width: <?php echo min(($last_reading_temp * 2), 100); ?>%"></div>
                </div>
            </div>
            <div class="card gauge-card">
                <h3>HUMEDAD ACTUAL</h3>
                <div class="gauge-value"><?php echo $last_reading_humi; ?> <small>%</small></div>
                <div class="gauge-visual">
                    <div class="bar humi-bar" style="width: <?php echo $last_reading_humi; ?>%"></div>
                </div>
            </div>
        </section>

        <section class="card chart-section">
            <h3>📈 Tendencia de Temperatura (°C)</h3>
            <div class="chart-container">
                <canvas id="tempChart"></canvas>
            </div>
        </section>

        <section class="card chart-section">
            <h3>💧 Tendencia de Humedad (%)</h3>
            <div class="chart-container">
                <canvas id="humiChart"></canvas>
            </div>
        </section>

        <section class="card table-container">
            <h3>📋 Historial Detallado</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Sensor</th>
                        <th>Temp.</th>
                        <th>Hum.</th>
                        <th>Fecha y Hora</th>
                    </tr>
                </thead>
                <tbody>
                    <?php echo $table_rows; ?>
                </tbody>
            </table>
        </section>
    </div>

    <script>
        // Configuración Global de las Gráficas
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { 
                    beginAtZero: false,
                    grid: { color: '#f0f0f0' }
                },
                x: {
                    grid: { display: false }
                }
            }
        };

        // --- Gráfica Temperatura ---
        const ctxTemp = document.getElementById('tempChart').getContext('2d');
        new Chart(ctxTemp, {
            type: 'line',
            data: {
                labels: <?php echo json_encode($labels); ?>,
                datasets: [{
                    label: 'Temperatura °C',
                    data: <?php echo json_encode($temp_data); ?>,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4
                }]
            },
            options: commonOptions
        });

        // --- Gráfica Humedad ---
        const ctxHumi = document.getElementById('humiChart').getContext('2d');
        new Chart(ctxHumi, {
            type: 'line',
            data: {
                labels: <?php echo json_encode($labels); ?>,
                datasets: [{
                    label: 'Humedad %',
                    data: <?php echo json_encode($humi_data); ?>,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4
                }]
            },
            options: commonOptions
        });

        // Refresco automático cada 30 segundos para mostrar datos nuevos del ESP32
        setTimeout(function(){
            location.reload();
        }, 30000);
    </script>
</body>
</html>