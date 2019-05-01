<?php
session_start();
require '../functions.php';
handlePagePermission("high");

$con = connect();
// check for log in database
$result = mysqli_query($con, "SELECT DISTINCT user_message
    FROM `Logs`
    WHERE `read` = 0
    AND user_message != ''
    ORDER BY `id` DESC");

$arr = mysqli_fetch_all($result);
if ($arr) echo json_encode($arr);

// set all messages to read
mysqli_query($con,"UPDATE `Logs` SET `read` = 1;");