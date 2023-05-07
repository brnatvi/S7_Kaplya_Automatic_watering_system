<?php

$sql_pants = "SELECT name, id_flowerpot, pin_sensor, pin_solenoid, mode, id_category, is_irrigated 
FROM Plant JOIN Flowerpot on Plant.id_plant=Flowerpot.id_plant
            JOIN Solenoide on Flowerpot.id_solenoid=Solenoide.id_solenoid
            JOIN Sensor on Flowerpot.id_sensor=Sensor.id_sensor";
$result_plants = $link->query($sql_pants);

$sql_pants = "SELECT name, id_flowerpot FROM Plant JOIN Flowerpot on Plant.id_plant=Flowerpot.id_plant";
$result_plants2 = $link->query($sql_pants);

$sql_flowerpot = "SELECT id_flowerpot FROM Flowerpot";
$result_flowerpot = $link->query($sql_flowerpot);

$sql_categories = "SELECT * FROM Categories";
$result_categories = $link->query($sql_categories);

$sql_pin_sensors = "SELECT * FROM PinSensor 
                    EXCEPT 
                    SELECT pin_sensor from Flowerpot
                    JOIN Sensor on Flowerpot.id_sensor=Sensor.id_sensor";
$result_pin_sensors = $link->query($sql_pin_sensors);
$result_pin_sensors2 = $link->query($sql_pin_sensors);

$sql_pin_solenoid = "SELECT * FROM PinSolenoid 
                        EXCEPT 
                        SELECT pin_solenoid from Flowerpot
                        JOIN Solenoide on Flowerpot.id_solenoid=Solenoide.id_solenoid";
$result_pin_solenoid = $link->query($sql_pin_solenoid);
$result_pin_solenoid2 = $link->query($sql_pin_solenoid);

?>