<!DOCTYPE html>
<html>

<head>
    <title>Watering panel</title>
    <meta charset="utf-8" />
    <link href="style.css" rel="stylesheet" type="text/css">
</head>

<!-- sql connection -->
<?php

try {
    $link = mysqli_connect("localhost", "admin", "admin", "arrosage");

    if (!$link) {
        throw new Exception('Failed');
    }
} catch (Exception $e) {
    echo 'Wrong database username or password';
    die;
}

$sql_pants = "SELECT name, id_flowerpot, id_sensor, id_solenoid, mode, id_category, is_irrigated FROM Plant JOIN Flowerpot on Plant.id_plant=Flowerpot.id_plant";
$result_plants = $link->query($sql_pants);

$sql_flowerpot = "SELECT id_flowerpot FROM Flowerpot";
$result_flowerpot = $link->query($sql_flowerpot);

$sql_categories = "SELECT * FROM Categories";
$result_categories = $link->query($sql_categories);

$sql_pin_sensors = "SELECT * FROM PinSensor";
$result_pin_sensors = $link->query($sql_pin_sensors);

$sql_pin_solenoid = "SELECT * FROM PinSolenoid";
$result_pin_solenoid = $link->query($sql_pin_solenoid);

?>

<body>
    <ul class="navbar">
        <li><a href="index.php">Home</a></li>
        <li><a href="">Modify plants</a></li>
        <li><a href="manual_control.php">Manual control</a></li>
        <li><a href="logs.php">Logs</a></li>
    </ul>

    <br>
    <div class="line"></div>

    <!-- table -->
    <br>
    <table id="table" border="0" cellspacing="0" cellpadding="4">
        <tr>
            <th>Plant</th>
            <th>Flowerpot</th>
            <th>Sensor</th>
            <th>Solenoid</th>
            <th>Mode</th>
            <th>Category</th>
            <th>Irrigated</th>
        </tr>

        <!-- adding plants from database -->
        <?php
        if ($result_plants->num_rows > 0) {
            while ($row = $result_plants->fetch_assoc()) {
                echo "<tr>";
                echo "<th>" . $row["name"] . "</th>";
                echo "<th>" . $row["id_flowerpot"] . "</th>";
                echo "<th>" . $row["id_sensor"] . "</th>";
                echo "<th>" . $row["id_solenoid"] . "</th>";
                echo "<th>" . $row["mode"] . "</th>";
                echo "<th>" . $row["id_category"] . "</th>";
                echo "<th>" . $row["is_irrigated"] . "</th>";
                echo "</tr>";
            }
        } else {
            echo "<tr>";
            echo "<th colspan=\"6\">List is empty</th>";
            echo "</tr>";
        }
        ?>
    </table>

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

    </br>
    <div class="line"></div>
    </br>
</body>

<?php
if (array_key_exists('add', $_POST)) {
    $name = "\"" . $_POST['name'] . "\"";
    $id_category = "\"" . explode(' ', $_POST['id_category'], 2)[0] . "\"";
    $pin_sensor = "\"" . $_POST['pin_sensor'] . "\"";
    $min_humidity = "\"" . $_POST['min_humidity'] . "\"";
    $max_humidity = "\"" . $_POST['max_humidity'] . "\"";
    $pin_solenoid = "\"" . $_POST['pin_solenoid'] . "\"";
    $capacity = "\"" . $_POST['capacity'] . "\"";
    $sql = "INSERT INTO Sensor (pin_sensor, min_humidity, max_humidity) VALUES ($pin_sensor, $min_humidity,$max_humidity)";
    $id_sensor = sql_query($sql);
    $sql = "INSERT INTO Solenoide (pin_solenoid, capacity) VALUES ($pin_solenoid, $capacity)";
    $id_solenoid = sql_query($sql);
    $sql = "INSERT INTO Plant (name, id_category) VALUES ($name, $id_category)";
    $id_plant = sql_query($sql);
    $sql = "INSERT INTO Flowerpot (id_plant, id_sensor, id_solenoid) VALUES ($id_plant, $id_sensor, $id_solenoid)";
    sql_query($sql);

    $txt = "Sensor " . $pin_sensor . ", solenoid " . $pin_solenoid . ", plant connected" . "\n";
    writeLog($txt);
} else if (array_key_exists('delete', $_POST)) {
    $id_flowerpot = $_POST['id_flowerpot'];
    $sql_pants = "SELECT id_plant, id_sensor, id_solenoid FROM Flowerpot WHERE id_flowerpot=$id_flowerpot";
    $result_plants = $link->query($sql_pants);
    if ($result_plants->num_rows > 0) {
        $row = $result_plants->fetch_assoc();
        $id_plant = $row["id_plant"];
        $id_sensor = $row["id_sensor"];
        $id_solenoid = $row["id_solenoid"];
        $sql = "DELETE FROM Flowerpot WHERE id_flowerpot = $id_flowerpot";
        sql_query($sql);
        $sql = "DELETE FROM Plant WHERE id_plant = $id_plant";
        sql_query($sql);
        $sql = "DELETE FROM Sensor WHERE id_sensor = $id_sensor";
        sql_query($sql);
        $sql = "DELETE FROM Solenoide WHERE id_solenoid = $id_solenoid";
        sql_query($sql);
        
        //$txt = "Sensor " . $pin_sensor . ", solenoid " . $pin_solenoid . ", plant desconnected" . "\n";
        $txt = "Plant desconnected" . "\n";
        writeLog($txt);
    }
}

function sql_query($sql)
{
    $link = mysqli_connect("localhost", "admin", "admin", "arrosage");

    if ($link->connect_error) {
        die("Connection failed : " . $link->connect_error . "</br></br>");
    }

    if ($link->query($sql) === TRUE) {
        header("Refresh:0");
        $last_id = $link->insert_id;
    } else {
        echo "Error : " . $sql . "<br>" . $link->error;
    }
    return $last_id;
}

function writeLog($txt){
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