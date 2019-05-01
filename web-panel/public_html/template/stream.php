<?php
session_start();
require '../backend/functions.php';
handlePagePermission("medium");

header("Content-Type: image/jpeg");

readfile($live_image_path);