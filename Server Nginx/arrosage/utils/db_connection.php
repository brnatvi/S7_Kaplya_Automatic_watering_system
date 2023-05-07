<?php
include '../vars.php';

try {
    $link = mysqli_connect("localhost", $login, $password, "arrosage");

    if (!$link) {
        throw new Exception('Failed');
    }
} catch (Exception $e) {
    echo 'Wrong database username or password';
    die;
}
?>