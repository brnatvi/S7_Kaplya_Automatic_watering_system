<!DOCTYPE html>
<html>

<head>
    <title>Watering panel</title>
    <meta charset="utf-8" />
    <link href="style.css" rel="stylesheet" type="text/css">
</head>

<!-- sql connection -->
<?php
include 'utils/db_connection.php';

include 'utils/db_queries.php';

?>

<body>
    <?php include 'utils/navbar.php'; ?>

    <?php include 'utils/table.php'; ?>

    <form method="post">
        <fieldset>
            <legend>Add a plant</legend>
            Name :
            <input type="text" name="name" required="required" /><br>
            Humidity category :
            <select name="id_category">
                <!-- required="required" -->
                <?php
                if ($result_categories->num_rows > 0) {
                    while ($row = $result_categories->fetch_assoc()) {
                        $str = $row["id_category"] . " : " . $row["lower_limit"] . " - " . $row["upper_limit"];
                        echo "<option>" . $str . "</option>";
                    }
                }
                ?>
            </select><br>
            Sensor :
            <select name="pin_sensor">
                <?php
                if ($result_pin_sensors->num_rows > 0) {
                    while ($row = $result_pin_sensors->fetch_assoc()) {
                        echo "<option>" . $row["Number"] . "</option>";
                    }
                }
                ?>
            </select>
            Minimum humidity
            <input type="text" size="4" name="min_humidity" required="required" />
            Maximum humidity
            <input type="text" size=4 name="max_humidity" required="required" />
            <br>
            Solenoid :
            <select name="pin_solenoid">
                <?php
                if ($result_pin_solenoid->num_rows > 0) {
                    while ($row = $result_pin_solenoid->fetch_assoc()) {
                        echo "<option>" . $row["Number"] . "</option>";
                    }
                }
                ?>
            </select>
            Capacity
            <input type="text" size=4 name="capacity" required="required" />
            <br>
            Pot volume in liters : 
            <input type="text" size=4 name="volume" required="required" />
            <br>
            Pot diameter : 
            <input type="text" size=4 name="diameter" required="required" />
            <br>
            <input type="submit" name="add" class="button" value="Add" />
        </fieldset>
    </form>

    <form method="post">
        <fieldset>
            <legend>Delete a plant</legend>
            Flowerpot :
            <select name="id_flowerpot">
                <!-- required="required" -->
                <?php
                if ($result_flowerpot->num_rows > 0) {
                    while ($row = $result_flowerpot->fetch_assoc()) {
                        $str = $row["id_flowerpot"];
                        echo "<option>" . $str . "</option>";
                    }
                }
                ?>
            </select><br>
            <input type="submit" name="delete" class="button" value="Delete" />
        </fieldset>
    </form>

    <form method="post">
        <fieldset>
            <legend>Check sensors</legend>
            Sensor :
            <select name="pin_sensor">
                <?php
                if ($result_pin_sensors2->num_rows > 0) {
                    while ($row = $result_pin_sensors2->fetch_assoc()) {
                        echo "<option>" . $row["Number"] . "</option>";
                    }
                }
                ?>
            </select>
            <input type="submit" name="testSensor" class="button" value="Test humidity" />
            <br>
            Solenoid :
            <select name="pin_solenoid">
                <?php
                if ($result_pin_solenoid2->num_rows > 0) {
                    while ($row = $result_pin_solenoid2->fetch_assoc()) {
                        echo "<option>" . $row["Number"] . "</option>";
                    }
                }
                ?>
            </select>
            <input type="submit" name="testSolenoid" class="button" value="Test capacity" />
            <br>
        </fieldset>
    </form>

    </br>
    <div class="line"></div>
    </br>
</body>

<?php

include 'utils/db_connection.php';

if (array_key_exists('add', $_POST)) {

    $link->begin_transaction();
    try {
        $name = "\"" . $_POST['name'] . "\"";
        $id_category = "\"" . explode(' ', $_POST['id_category'], 2)[0] . "\"";
        $pin_sensor = "\"" . $_POST['pin_sensor'] . "\"";
        $min_humidity = "\"" . $_POST['min_humidity'] . "\"";
        $max_humidity = "\"" . $_POST['max_humidity'] . "\"";
        $pin_solenoid = "\"" . $_POST['pin_solenoid'] . "\"";
        $capacity = "\"" . $_POST['capacity'] . "\"";
        $volume = "\"" . floatval($_POST['volume']) * 1000 . "\"";
        $diameter = floatval($_POST['diameter']);
        $area = "\"" . (1 / 4 * M_PI * $diameter * $diameter) . "\"";
        $sql = "INSERT INTO Sensor (pin_sensor, min_humidity, max_humidity) VALUES ($pin_sensor, $min_humidity,$max_humidity)";
        $id_sensor = sql_query($sql, $link);
        $sql = "INSERT INTO Solenoide (pin_solenoid, capacity) VALUES ($pin_solenoid, $capacity)";
        $id_solenoid = sql_query($sql, $link);
        $sql = "INSERT INTO Plant (name, id_category) VALUES ($name, $id_category)";
        $id_plant = sql_query($sql, $link);
        $sql = "INSERT INTO Flowerpot (id_plant, id_sensor, id_solenoid, volume, area) VALUES ($id_plant, $id_sensor, $id_solenoid, $volume, $area)";
        sql_query($sql, $link);

        $txt = "Sensor " . $pin_sensor . ", solenoid " . $pin_solenoid . ", plant connected" . "\n";
        writeLog($txt);

        $link->commit();
        
        header("Refresh:0");
    } catch (Exception $e) {
      $link->rollback();
      echo "Error: " . $e->getMessage();
    }

    $link->close();
} else if (array_key_exists('delete', $_POST)) {
    $id_flowerpot = $_POST['id_flowerpot'];
    $sql_pants = "SELECT id_plant, id_sensor, id_solenoid FROM Flowerpot WHERE id_flowerpot=$id_flowerpot";
    $result_plants = $link->query($sql_pants);
    if ($result_plants->num_rows > 0) {
        $link->begin_transaction();
        try {
            $row = $result_plants->fetch_assoc();
            $id_plant = $row["id_plant"];
            $id_sensor = $row["id_sensor"];
            $id_solenoid = $row["id_solenoid"];
            $sql = "DELETE FROM Flowerpot WHERE id_flowerpot = $id_flowerpot";
            sql_query($sql, $link);
            $sql = "DELETE FROM Plant WHERE id_plant = $id_plant";
            sql_query($sql, $link);
            $sql = "DELETE FROM Sensor WHERE id_sensor = $id_sensor";
            sql_query($sql, $link);
            $sql = "DELETE FROM Solenoide WHERE id_solenoid = $id_solenoid";
            sql_query($sql, $link);

            $txt = "Plant desconnected" . "\n";
            writeLog($txt);

            $link->commit();

            header("Refresh:0");
        } catch (Exception $e) {
            $link->rollback();
            echo "Error: " . $e->getMessage();
        }
      
        $link->close();
    }
} else if (array_key_exists('testSensor', $_POST)) {
    $command = "python3 test.py testSensor " . $_POST['pin_sensor'];

    //only for test
    $output = exec($command);
    echo $output;

    //Uncommit after adding a valide python file
    //header("Refresh: 0");
} else if (array_key_exists('testSolenoid', $_POST)) {
    $command = "python3 test.py testSolenoid " . $_POST['pin_solenoid'];

    //only for test
    $output = exec($command);
    echo $output;

    //Uncommit after adding a valide python file
    //header("Refresh: 0");
}

function sql_query($sql, $link)
{
    if ($link->query($sql) === TRUE) {
        $last_id = $link->insert_id;
    } else {
        echo "Error : " . $sql . "<br>" . $link->error;
    }
    return $last_id;
}

function writeLog($txt)
{
    $current_datetime = date('Y-m-d H:i:s');
    $myfile = fopen("logs.txt", "a") or die("Unable to open file!");
    $txt = $current_datetime . " info " . $txt;
    fwrite($myfile, $txt);
    fclose($myfile);
}
?>

<?php
$link->close();
?>

</html>