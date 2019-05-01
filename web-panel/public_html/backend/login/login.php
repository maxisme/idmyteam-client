<?php
/* from index */
session_start();
require "../functions.php";

$name = ucwords($_POST['name']);
$password = myHash($_POST['password']);

/* validate name input */
if(!validName($name)) ESC("/login", "Invalid name");

$con = connect();
$query = mysqli_query($con, "SELECT perm
FROM `Members`
WHERE name = '$name'
AND password = '$password'");

if(mysqli_num_rows($query) == 1){
    $_SESSION['name'] = $name;
    $_SESSION['permissions'] = mysqli_fetch_array($query)["perm"];

    // get redirect
    $redirect = $_SESSION['redirect'] ?? '/';
    unset($_SESSION['redirect']);

    ESC($redirect,false,"Welcome $name");
}

ESC("/login", "Invalid login credentials");
