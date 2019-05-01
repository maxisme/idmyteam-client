<?php
session_start();
require '../backend/functions.php';
handlePagePermission("high");
$title = "New Password";
require "../template/head.php";

/* get parameters */
$name = @mysqli_real_escape_string($con, $_GET['name']);

$result = mysqli_query($con,"SELECT id
FROM `Members`
WHERE name = '".$name."'");
if(mysqli_num_rows($result) == 0) die("No such user!");
?>

Set a new password for <?php echo $name?>

<form action="/backend/member/change-password.php" method="POST">
    <div class="row">
        <div class="input-field col s6">
            <input name="password" id="password" type="password">
            <label for="password">Password</label>
        </div>
        <div class="input-field col s6">
            <input name="c_password" id="password-confirm" type="password">
            <label for="password-confirm">Confirm Password</label>
        </div>
    </div>
    <input type="hidden" name="name" value="<?php echo $name?>"/>
    <div align="center">
        <button class="btn" type="submit">Set</button>
    </div>
</form>
