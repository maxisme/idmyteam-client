<?php
session_start();
require '../functions.php';
handlePagePermission("high");

mysqli_query(connect(), "TRUNCATE `Logs`;");
header("Location: /logs?page=1");