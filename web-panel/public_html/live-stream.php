<?php
session_start();
require 'backend/functions.php';
handlePagePermission("medium");
$title = "Stream";
require "template/head.php";
?>
    <p class="info">
        Live view of the raspberry pi camera.
    </p>
    <hr>
<?php
require "template/live-stream.php";
require "template/foot.php" ?>