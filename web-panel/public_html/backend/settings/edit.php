<?php
session_start();
/* do not remove problems with yaml*/
error_reporting(E_ALL);
ini_set("display_errors", 1);

require '../functions.php';
handlePagePermission("high");

$camera_cmd = "restart";
$restart_camera = false;
$restart_socket = false;
// iterate all the settings and get the matching post input
foreach ($yaml_settings as $settings_group => &$settings) {
    if ($settings_group == "Global") continue; /* skip global variables */
    foreach ($settings as $setting => &$params) {
        if ($setting == "icon") continue; /* skip the icons */
        if ($setting == "info") continue; /* skip the info */
        if (isset($params['disabled'])) continue; /* skip disabled entries */

        /* set post value */
        $post_name = strtolower(str_replace(" ", "-", "${settings_group}_${setting}"));
        $p_val = @$_POST[$post_name];

        /* change switch values to '1' if on */
        if($params['type'] == "switch" && $p_val == 'on') $p_val = "1";

        /* switch on or off the camera */
        echo "$post_name = ".$p_val."<br>";
        if ($settings_group == "Camera" && $setting == "Run") {
            if (!cameraRunning() && $p_val == "1") {
                // turn on
                $camera_cmd = "start";
                $restart_camera = true;
            } else if (cameraRunning() && $p_val == '0') {
                // turn off
                $camera_cmd = "stop";
                $restart_camera = true;
            }
        }

        if (isset($p_val)) {
            $change_in_val = ($params['val'] != $p_val);

            /* if there is a change in the camera settings restart the python script using the camera */
            if ($settings_group == "Camera" && $change_in_val) $restart_camera = true;

            /* if there is a change in the rpi credentials restart the python script to start the socket */
            if (($setting == "Id My Team Username" || $setting == "Id My Team Credentials") && $change_in_val) {
                $_SESSION['invalid_credentials'] = true;
                $restart_socket = true;
            }
            
            /* if change in Recognition group restart camera and socket */
            if ($settings_group == "Recognition" && $change_in_val) {
                $restart_camera = true;
                $restart_socket = true;
            }

            $params['val'] = trim($p_val);
        }
    }
}

$temp = tmpfile();
$tmp_path = stream_get_meta_data($temp)['uri'];
if(yaml_emit_file($tmp_path, $yaml_settings)) {
    rename($tmp_path, $SETTINGS_FILE);

    if ($restart_camera) {
        $cmd = escapeshellcmd("sudo '$control_camera_script' $camera_cmd");
        $output = shell_exec($cmd);
        if ($output != "1") $error_message = $output;
        $message = "<br>${camera_cmd}ing the camera.";
    }

    if ($restart_socket) {
        $cmd = escapeshellcmd("sudo '$restart_socket_script'");
        $output = shell_exec($cmd);
        $message = "$message<br>Restarting Socket.";
    }
    ESC($_SERVER["HTTP_REFERER"], $error_message, "Successfully updated system settings!$message");
}else{
    ESC($_SERVER["HTTP_REFERER"], "Problem writing yaml file");
}
