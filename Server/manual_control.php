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
?>

<body>
    <ul class="navbar">
        <li><a href="index.php">Home</a></li>
        <li><a href="modify_plants.php">Modify plants</a></li>
        <li><a href="">Manual control</a></li>
        <li><a href="logs.php">Logs</a></li>
    </ul>

    <br>
    <div class="line"></div>
</body>

<?php
$link->close();
?>

</html>