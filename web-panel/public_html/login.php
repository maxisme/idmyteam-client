<?php
session_start();
require 'backend/functions.php';
$title = "Log In";
require "template/head.php";
if(isset($_SESSION['permissions'])) ESC("/members",false, "Already logged in!");
?>

<form method="post" action="/backend/login/login" enctype="multipart/form-data">
    <div class="row">
        <div class="input-field col s12">
            <input name="name" id="name" type="text">
            <label for="name">Name</label>
        </div>
        <div class="input-field col s12">
            <input name="password" id="password" type="password">
            <label for="password">Password</label>
        </div>
    </div>

    <div align="center">
        <button class="btn" type="submit">Log In</button>
    </div>
</form>
<?php require "template/foot.php" ?>

