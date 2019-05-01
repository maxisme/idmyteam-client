<?php
session_start();
require "../functions.php";
if(!isset($_SESSION['permissions'])) ESC("/login", "You must login to logout!");

unset($_SESSION['permissions']);
unset($_SESSION['name']);

// return to login page
ESC("/",false, "Successfully logged out");