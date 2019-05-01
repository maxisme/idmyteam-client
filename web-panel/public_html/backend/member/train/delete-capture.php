<?php
session_start();
require '../../functions.php';
handlePagePermission("medium");

$image_path = trim($_POST["image_path"]);
unlink(trim($image_path)); // delete image
unset($_SESSION['coords'][$image_path]); // remove session
//;
ESC("/member/train#train", false, "Success removing image from classified.");