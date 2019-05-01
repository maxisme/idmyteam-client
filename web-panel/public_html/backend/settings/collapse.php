<?php
/* stores settings tabs in session so that if they are opened in the session they stay open on return */
session_start();
require '../functions.php';
$id = $_GET['id'];
$open = $_GET['open'];

storeCollapse($id, $open);