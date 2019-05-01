<?php
session_start();
require 'backend/functions.php';

if (isset($_SESSION['permissions'])) $title = "Status";
require "template/head.php";
?>


<?php if(!isset($_SESSION['permissions'])){?>
    <div id="welcome" align="center">
        <h1>
            Web Panel
        </h1>
        <p style="font-weight: 200">Welcome to the ID My Team panel.</p>
    </div>

    <script>
        $(document).ready(function(){
			fadeInOut($("#login"));
        });
    </script>
<?php }else {
    echo "<p>&nbsp</p>";
    // force to enter credentials if not set
    if (empty(trim($yaml_settings['Credentials']['Id My Team Username']['val'])) || empty(trim($yaml_settings['Credentials']['Id My Team Credentials']['val']))) {
        if (@$_SESSION['invalid_credentials'] == true) {
            echo "<div align='center'><strong class='error'>You may have entered invalid credentials</strong></div>";
        }
        ?>
        <div align="center">
            <strong>Before using ID My Team you must set your username and credentials from your <a target="_blank"
                                                                                                    href='https://idmy.team/profile'>ID
                    My Team - Profile</a></strong>
        </div>
        <br><br>
        <span class="material-icons">face</span><input id="username" type="text" placeholder="Username">
        <br>
        <span class="material-icons">vpn_key</span> <input id="credentials" type="text" placeholder="Credentials">
        <div align="center"><button id="takeaway" class="btn">Submit</button></div>

        <script src="/js/libraries/jquery.redirect.js"></script>
        <script>
            $("#takeaway").on("click", function () {
                var username = $("#username").val().trim();
                var cred = $("#credentials").val().trim();
                if (username.length > 0 && cred.length >= 40) {
                    $.redirect("/backend/settings/edit.php", {
                        'credentials_id-my-team-username': username,
                        'credentials_id-my-team-credentials': cred
                    });
                }
            });
        </script>
    <?php } else {
        ////////////////
        // SHOW STATS //
        ////////////////
        ?>
        <table class="responsive-table centered">
            <thead>
                <tr>
                    <th><span style="font-size: 2em" class="material-icons tooltipped" data-position="top" data-tooltip="Live Stream">photo_camera</span></th>
                    <th><span style="font-size: 2em" class="material-icons tooltipped" data-position="top" data-tooltip="idmy.team Connection">settings_ethernet</span></th>
                    <th><span style="font-size: 2em" class="material-icons tooltipped" data-position="top" data-tooltip="Recognitions are running">face</span></th>
                    <th><span style="font-size: 2em" class="material-icons tooltipped" data-position="top" data-tooltip="Average time it takes from the snap of the camera to the returned recognition.">av_timer</span></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
                        <?php
                        $recognising = true;
                        if (cameraRunning()) {
                            echo "Running";
                        } else {
                            $recognising = false;
                            echo "<a class='error' href='/settings'>Off</a>";
                        }
                        ?>
                    </td>
                    <td>
                        <?php
                        if($sm == "No Team Model"){
                            echo "<span class='error'>No Recognition Model. You must train two <a href='members'>members</a> for the system to start recognising!</span>";
                        }else if($sm != "Connected"){
                            echo "<span class='error'>Unable to connect to the <a href='mailto:help@idmy.team'>idmy.team</a> server - see <a href='logs'>Logs</a> !</span>";
                            $recognising = false;
                        }else{
                            echo $sm;
                        }
                        ?>
                    </td>
                    <td>
                        <?php
                        if ($yaml_settings['Camera']['Silent Mode']['val'] == "1") {
                            echo "<a class='error' href='/settings'>Silent Mode On</a><br>Turn off for recognitions.";
                        } else if($recognising) {
                            echo "Recognising";
                        }else{
                            echo "<span class='error'>Not recognising!</span>";
                        }
                        ?>
                    </td>
                    <td>
                        <?php
                        // average recognition speed
                        $query = mysqli_query($con, "SELECT AVG(speed) AS avg_speed 
        FROM Activity;");
                        $a_speed = round(mysqli_fetch_array($query)['avg_speed'], 3);
                        if ($a_speed > 0) {
                            echo $a_speed;
                        }else{
                            echo "No recognitions yet!";
                        }
                        ?>

                    </td>
                </tr>
            </tbody>
        </table>
    <?php }
}
require "template/foot.php" ?>
