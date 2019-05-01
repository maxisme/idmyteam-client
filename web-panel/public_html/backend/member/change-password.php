<?php
session_start();
require '../functions.php';
handlePagePermission("high");

/* post variables */
$name = $_POST['name'];
$pw = myHash($_POST['password']);
$cpw = myHash($_POST['c_password']);

if($pw != $cpw) ESC("/member/password?name=$name","Passwords do not match!");

/* update db */
mysqli_query(connect(), "UPDATE `Members`
SET `password` = '".$pw."'
WHERE `name` = '".$name."'");

ESC("/members",false,"Success Updating $name's password");