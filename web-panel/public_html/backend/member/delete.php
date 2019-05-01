<?php
/* delete a member */
session_start();
require '../functions.php';
handlePagePermission("high");

/* input */
$member_name = $_POST['member'];

/* default return messages */
$page = "../../members";
$success_msg = "Successfully deleted '$member_name'";

/* make sure not deleting themselves */
if($_SESSION['name'] == $member_name) ESC($page, "You cannot delete yourself!");

$con = connect();

/* validate input */
if(!memberExists($con, $member_name)) ESC($page, "Member doesn't exist!");

/* remove member files and directories */
$class = "${classified_dir}".getMemberID($con, $member_name)."/";
$tmp_class = "${tmp_classified_dir}".getMemberID($con, $member_name)."/";
$profile_img = "${member_images}${member_name}*";
system("rm -rf $class $tmp_class $profile_img");

/* remove user from database */
$query = mysqli_query($con, "DELETE FROM `Members`
WHERE name = '$member_name'");

if(!$query) ESC($page, "Unable to delete from db!");
ESC($page, false, $success_msg);