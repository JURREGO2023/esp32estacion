<?php


// --- CONFIGURACIÓN DE CONEXIÓN ---
$servername = "bd";
$username   = "root";
$password   = "Utipec2025*";
$dbname     = "estacionesp32";

/**
 * Inserta una nueva lectura desde el ESP32
 */
function insertReading($sensor, $location, $value1, $value2, $value3) {
    global $servername, $username, $password, $dbname;

    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $sql = "INSERT INTO SensorData (sensor, location, value1, value2, value3)
            VALUES ('" . $sensor . "', '" . $location . "', '" . $value1 . "', '" . $value2 . "', '" . $value3 . "')";

    if ($conn->query($sql) === TRUE) {
        $result = "New record created successfully";
    } else {
        $result = "Error: " . $sql . "<br>" . $conn->error;
    }
    $conn->close();
    return $result;
}

/**
 * Obtiene las lecturas (Soporta filtros de fecha para el index.php)
 */
function getAllReadings($limit, $start = null, $end = null) {
    global $servername, $username, $password, $dbname;

    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Lógica de filtrado por fecha
    if ($start && $end) {
        $sql = "SELECT id, sensor, location, value1, value2, value3, reading_time 
                FROM SensorData 
                WHERE reading_time BETWEEN '$start' AND '$end' 
                ORDER BY reading_time DESC LIMIT " . (int)$limit;
    } else {
        $sql = "SELECT id, sensor, location, value1, value2, value3, reading_time 
                FROM SensorData 
                ORDER BY reading_time DESC LIMIT " . (int)$limit;
    }

    $result = $conn->query($sql);
    $conn->close();
    return $result;
}

/**
 * Obtiene la última lectura para los indicadores superiores
 */
function getLastReadings() {
    global $servername, $username, $password, $dbname;

    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $sql = "SELECT id, sensor, location, value1, value2, value3, reading_time FROM SensorData ORDER BY reading_time DESC LIMIT 1";
    if ($result = $conn->query($sql)) {
        $row = $result->fetch_assoc();
        $conn->close();
        return $row;
    } else {
        $conn->close();
        return false;
    }
}

/**
 * Estadísticas: Mínimo
 */
function minReading($limit, $value) {
    global $servername, $username, $password, $dbname;
    $conn = new mysqli($servername, $username, $password, $dbname);
    $sql = "SELECT MIN(" . $value . ") AS min_amount FROM (SELECT " . $value . " FROM SensorData ORDER BY reading_time DESC LIMIT " . (int)$limit . ") AS min";
    $result = $conn->query($sql)->fetch_assoc();
    $conn->close();
    return $result;
}

/**
 * Estadísticas: Máximo
 */
function maxReading($limit, $value) {
    global $servername, $username, $password, $dbname;
    $conn = new mysqli($servername, $username, $password, $dbname);
    $sql = "SELECT MAX(" . $value . ") AS max_amount FROM (SELECT " . $value . " FROM SensorData ORDER BY reading_time DESC LIMIT " . (int)$limit . ") AS max";
    $result = $conn->query($sql)->fetch_assoc();
    $conn->close();
    return $result;
}

/**
 * Estadísticas: Promedio
 */
function avgReading($limit, $value) {
    global $servername, $username, $password, $dbname;
    $conn = new mysqli($servername, $username, $password, $dbname);
    $sql = "SELECT AVG(" . $value . ") AS avg_amount FROM (SELECT " . $value . " FROM SensorData ORDER BY reading_time DESC LIMIT " . (int)$limit . ") AS avg";
    $result = $conn->query($sql)->fetch_assoc();
    $conn->close();
    return $result;
}
?>