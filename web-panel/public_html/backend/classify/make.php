<?php
/* makes all the uploaded classifications and moves them to the user folders */
session_start();
error_reporting(E_ALL);
ini_set("display_errors", 1);
require '../functions.php';
handlePagePermission("low");

$classify_array = json_decode($_POST['classify_array']);
if(json_last_error() != JSON_ERROR_NONE) die("input not json");

$con = connect();

$classify_cnt = 0;
foreach($classify_array as $file_path => $member){
    $member_id = getMemberID($con, $member);
    $img_coords = $_SESSION['coords'][$file_path] ?? getImageComment($file_path);
    if(!validCoords($img_coords)) ESC("../../classify", "No face coordinates set for image");
    storeImageComment($file_path, $img_coords);

    if($member == $unknown_member_string) {
        $member_dir = $unrecognised_class_dir;
    }else{
        $member_dir = "${classified_dir}${member_id}/";
    }

    mdir($member_dir);

    /* move unclassified file to classified */
    $file = str_replace("$unclassified_dir", "", $file_path);
    if(rename("$file_path", "${member_dir}${file}")) $classify_cnt++;
}
ESC("../../classify",false, "Successfully classified $classify_cnt images");