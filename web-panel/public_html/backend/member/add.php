<?php
/* delete a member */
session_start();
require '../functions.php';
handlePagePermission("medium");

$page = "/member/add";
$image_name = "file";

/* input */
$name = ucwords($_POST['name']);
$pass = $_POST['password'];
$permission = $_POST['permission'];

$con = connect();

/* validate input */
if(!validName($name)) ESC($page, "Member name can only be characters and spaces");
if(strlen($name)>= 50) ESC($page, "Member name must be less than 50 characters.");

if($pass != $_POST['c_password']) ESC($page, "Passwords do not match.");
if(strlen($pass) <= 8) ESC($page, "Password must have more than 8 characters.");

if(memberExists($con, $name)) ESC($page, "Member name already taken");

if(!key_exists($permission, $member_permissions)) ESC($page, "Not a valid permission $permission");

if($member_permissions[$_SESSION['permissions']] < $member_permissions[$permission]) ESC($page, "You cannot add a member with higher permissions than yourself!");

if(!getimagesize($_FILES['file']["tmp_name"])) ESC($page, "Invalid image");

/* crop to profile picture */
$image_ext = strtolower(pathinfo($_FILES[$image_name]["name"],PATHINFO_EXTENSION));
$im = new imagick( $_FILES['file']["tmp_name"]);
if(!$im->cropThumbnailImage( 300, 300)) ESC($page, "Error cropping image");
if(!$im->writeImage( "${member_images}${name}.${image_ext}")) ESC($page, "Error writing image");

/* insert name and pass into db */
$hash_pass = myHash($pass);
$query = mysqli_query($con,"INSERT INTO `Members` (name, password, perm)
VALUES ('$name','$hash_pass', '$permission')");

// TODO get ID
$last_id = mysqli_insert_id($conn);
header("Location: /member/train?member=$name");
