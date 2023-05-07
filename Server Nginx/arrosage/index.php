<!DOCTYPE html>
<html>

<head>
    <title>Panneau d'arrosage</title>
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

    <!-- mode, TODO : change -->
    <b>Current mode : Automatic</b>
    <div class="line"></div>

    <!-- table -->
    <?php include 'utils/table.php'; ?>

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
