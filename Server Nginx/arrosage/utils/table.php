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
                echo "<th>" . $row["pin_sensor"] . "</th>";
                echo "<th>" . $row["pin_solenoid"] . "</th>";
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