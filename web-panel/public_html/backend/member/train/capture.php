<?php
session_start();
require '../../functions.php';
handlePagePermission("medium");

$page = "/members";
if(!isset($_SESSION['training_member_id'])){
    ESC($page, "No specified member in capture.php", false);
}else{
    $member_id = $_SESSION['training_member_id'];
}

$ran_string = generateRandomString(30);
$save_dir = "${tmp_classified_dir}${member_id}/";
$save_path = "${save_dir}${ran_string}${IMG_TYPE}";

mdir($save_dir);

copy($live_image_path, $save_path);
exit(header("Location: /member/train#livestream"));