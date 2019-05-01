<?php
/* changes a specific member permissions */
session_start();
require '../functions.php';
handlePagePermission("high");

/* input */
$perm = $_POST['perm'];
$member_name = $_POST['name'];

/* default return messages */
$page = "/members";
$error_msg = "Error updating permissions for '$member_name'";

/* make sure not deleting themselves */
if($_SESSION['name'] == $member_name) ESC($page, "You cannot alter the permissions of yourself!");

if($member_name == "root"){
    ESC("/members","You cannot edit the permissions of the root user. Should be deleted.");
}

$con = connect();

/* validate input */
if(!in_array($perm, $member_permissions)) ESC($page, $error_msg, false);
if(!memberExists($con, $member_name)) ESC($page, $error_msg, false);

/* get permission string from array */
while($element = current($member_permissions)) {
    if($element == $perm){
        $key = key($member_permissions);
        break;
    }
    next($member_permissions);
}

/* update permission in database */
$query = mysqli_query($con,"UPDATE `Members`
SET perm = '$key'
WHERE name = '$member_name';");

if(!$query) ESC($page, $error_msg, false);
ESC($page, false, "Successfully set '$key' permissions for '$member_name'");