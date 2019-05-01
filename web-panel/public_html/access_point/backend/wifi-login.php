<pre>
<?php
session_start();
include '../../backend/functions.php';

$name = trim($_POST['name']);
$pass = trim($_POST['password']);

if(empty($name)) ESC("../", "You have not specified your wifi network name / SSID");
if(empty($pass)) ESC("../", "You have not specified your wifi network password");

$cmd = escapeshellcmd("sudo '$wifi_connector' '$name' '$pass'");
$output = shell_exec($cmd);
ESC("../", "Unable to connect: $output");
?>
</pre>
