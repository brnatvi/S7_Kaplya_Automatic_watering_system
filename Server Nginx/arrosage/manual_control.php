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

    <form method="post" action="">

        <label><input type="checkbox" id="checkAll"> Check/uncheck all </label><br>

        <?php
        if ($result_plants2->num_rows > 0) {
            while ($row = $result_plants2->fetch_assoc()) {
                echo '<label>
                <input type="checkbox" class="checkbox" name="plants[]" value="' . $row["id_flowerpot"] . '">' .
                    " id_flowerpot - " . $row["id_flowerpot"] . ", plant " . $row["name"] . "</label><br>";
            }
        }
        ?>
        <input type="submit" name="checkHumidity" class="button" value="Check humidity" />
        <input type="submit" name="switchToReal" class="button" value="Switch to real mode" />
        <input type="submit" name="runIrrigation" class="button" value="Run one manual irrigation" />
        <input type="submit" name="excludeIrrigation" class="button" value="Exclude from irrigation" />
        <input type="submit" name="includeIrrigation" class="button" value="Include to irrigation" />
    </form>

</body>

<script>

    var checkAll = document.getElementById("checkAll");

    var checkboxes = document.getElementsByClassName("checkbox");

    checkAll.addEventListener("click", function () {
        for (var i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = checkAll.checked;
        }
    });
</script>


<?php
if (isset($_POST['plants'])) {
    if (array_key_exists('checkHumidity', $_POST)) {

        $command = "python3 test.py arg1 arg2";

        //only for test
        $output = exec($command);
        echo $output;

        //Uncommit after adding a valide python file
        //header("Refresh: 0");
    }

    if (array_key_exists('switchToReal', $_POST)) {
        foreach ($_POST['plants'] as $value) {
            $sql = "UPDATE Flowerpot SET mode = \"real\" WHERE Flowerpot.id_flowerpot = $value";
            sql_query($sql);
        }
        //write to logs
    }

    if (array_key_exists('runIrrigation', $_POST)) {
        $command = "python3 test.py arg1 arg2";

        //only for test
        $output = exec($command);
        echo $output;

        //Uncommit after adding a valide python file
        //header("Refresh: 0");
    }

    if (array_key_exists('excludeIrrigation', $_POST)) {
        foreach ($_POST['plants'] as $value) {
            $sql = "UPDATE Flowerpot SET is_irrigated = 0 WHERE Flowerpot.id_flowerpot = $value";
            sql_query($sql);
        }
        //write to logs
    }

    if (array_key_exists('includeIrrigation', $_POST)) {
        foreach ($_POST['plants'] as $value) {
            $sql = "UPDATE Flowerpot SET is_irrigated = 1 WHERE Flowerpot.id_flowerpot = $value";
            sql_query($sql);
        }
        //write to logs
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
?>

<?php
$link->close();
?>

</html>