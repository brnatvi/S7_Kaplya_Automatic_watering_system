<!DOCTYPE html>
<html>

<head>
    <title>Panneau d'arrosage</title>
    <meta charset="utf-8" />
    <link href="style.css" rel="stylesheet" type="text/css">
</head>

<!-- sql connection -->
<?php
try {
    $link = mysqli_connect("mariadb", "admin", "admin", "arrosage");

    if (!$link) {
        throw new Exception('Failed');
    }
} catch (Exception $e) {
    echo $e;
    die;
}

$sql_pants = "SELECT name, id_flowerpot, id_sensor, id_solenoid, mode, id_category, is_irrigated FROM Plant JOIN Flowerpot on Plant.id_plant=Flowerpot.id_plant";
$result_plants = $link->query($sql_pants);

?>

<body>

    <ul class="navbar">
      <li><a href="">Home</a></li>
      <li><a href="modify_plants.php">Modify plants</a></li>
      <li><a href="manual_control.php">Manual control</a></li>
      <li><a href="logs.php">Logs</a></li>
    </ul>

    <br><div class="line"></div>

    <!-- mode, TODO : change -->
    <p><b>Current mode : Automatic</b></p>
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
    </br>
    <div class="line"></div>
    </br>

    <table id="table" border="0" cellspacing="0" cellpadding="4">
        <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Log level</th>
            <th>Log details</th>
        </tr>

        <!-- adding logs -->
        <?php
        $array = explode("\n", file_get_contents('logs.txt'));
        if (count($array) > 0) {
            for ($i = 0; $i < count($array); $i++) {
                $str = explode(' ', $array[$i], 2);
                $date = $str[0];
                $str = explode(' ', $str[1], 2);
                $time = $str[0];
                $str = explode(' ', $str[1], 2);
                $level = $str[0];
                $log = $str[1];

                if ($level=="warning" || $level=="error") {
                    echo "<tr>";
                    echo "<th>" . $date . "</th>";
                    echo "<th>" . $time . "</th>";
                    echo "<th>" . $level . "</th>";
                    echo "<th>" . $log . "</th>";
                    echo "</tr>";
                }
            }
        } else {
            showEmpty();
        }

        function showEmpty()
        {
            echo "<tr>";
            echo "<th colspan=\"3\">List is empty</th>";
            echo "</tr>";
        }

        ?>
    </table>

    </br>
    <div class="line"></div>
    </br>
</body>

<?php 
$link->close();
?>

</html>
