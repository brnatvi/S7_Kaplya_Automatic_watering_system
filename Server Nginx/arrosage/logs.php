<!DOCTYPE html>
<html>

<head>
    <title>Watering panel</title>
    <meta charset="utf-8" />
    <link href="style.css" rel="stylesheet" type="text/css">
</head>

<?php
if (isset($_GET['dateFrom'])) {
    $dateFrom = $_GET['dateFrom'];
}
if (isset($_GET['dateTo'])) {
    $dateTo = $_GET['dateTo'];
}
if (isset($_GET['logLevel'])) {
    $getlevel = $_GET['logLevel'];
}
?>

<body>
    <?php include 'utils/navbar.php'; ?>

    <form name="Filter" method="get">
        From:
        <input type="date" name="dateFrom" value="<?php echo $dateFrom; ?>"/>
        To:
        <input type="date" name="dateTo" value="<?php echo $dateTo; ?>" />
        Log level:
        <select name="logLevel">
            <option></option>
            <option>info</option>
            <option>warning</option>
            <option>error</option>
        </select>
        <input type="submit" name="show" value="Show" />
    </form>
    <br>

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
                $test = true;

                if (!empty($dateFrom) && $date < $_GET['dateFrom']) {
                    $test = false;
                }

                if (!empty($dateTo) && $date > $_GET['dateTo']) {
                    $test = false;
                }

                if (!empty($getlevel) && $level != $getlevel) {
                    $test = false;
                }

                if ($test) {
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

    <br>
    <div class="line"></div>
</body>

<?php
$link->close();
?>

</html>
