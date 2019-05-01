<?php
/*  this script is run when a user deletes a classification as it does not have a person in it
*   the script then moves the unclassified image to the invalid folder used to train the model on images with no one in
*/
session_start();
require '../functions.php';
handlePagePermission("medium");

$delete_array = json_decode($_POST['delete_array']);
if(json_last_error() != JSON_ERROR_NONE) die("input not json");
foreach($delete_array as $file_path){
    $file = str_replace("$unclassified_dir", "", $file_path);
    // move the file to the invalid class directory
    rename("$file_path", "${invalid_class_dir}${file}");
}

ESC("../../classify", false, "Success removing image from classified.");
?>