<?php
session_start();
require '../functions.php';
handlePagePermission("medium");

$bash_script = $_POST['bash'];

// store temp content of file in case of error.
$tmp_file_contents = file_get_contents("$script_path");
// write to script file
file_put_contents ("$script_path", $bash_script);
// run syntax check on shell script
$error_msg = shell_exec("bash '$validate_script' '$script_path'");
$e = $s = false;
if(strlen($error_msg)> 0){
    $error_msg = str_replace($script_path." ","",$error_msg);
    // store error message in session
    $e = "Error found so script not changed<pre class='error'>\n--------- UPLOADED SCRIPT ------\n\n$bash_script\n\n--------- ERROR REPORT ------".$error_msg."</pre>";
    // revert to original file
    file_put_contents ("$script_path", $tmp_file_contents);
}else {
    // syntax of script is okay.
    $s = "Successfully updated bash script.";
}

writeStat(connect(),"Custom Script Speed", "N/A"); // reset script speed

ESC("/script", $e, $s);