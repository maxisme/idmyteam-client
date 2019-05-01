<?php
session_start();
require '../backend/functions.php';

$title = "Access Point";
?>

<script src="http://192.168.1.1/js/libraries/jquery-3.2.1.min.js"></script>
<script src="http://192.168.1.1/js/libraries/materialize.min.js"></script>
<script src="http://192.168.1.1/js/script.js"></script>

<link rel="stylesheet" href="http://192.168.1.1/css/materialize-sass/materialize.css">
<link href="http://192.168.1.1/css/google-fonts.css" rel="stylesheet">
<link href="http://192.168.1.1/css/style.css" rel="stylesheet">

<body>
<nav class="z-depth-0">
    <div class="nav-wrapper">
        <a href="/" class="brand-logo"><img class="svg" src="/logo.svg"/></a>
        <a href="#" data-activates="mobile-demo" class="button-collapse"><i class="material-icons">menu</i></a>
    </div>
</nav>
<?php echo handleESC();?>

Enter your Networks Name and Password to connect the Raspberry Pi to the internet.
<form method="post" action="backend/wifi-login.php" enctype="multipart/form-data">
    <div class="row">
        <div class="input-field col s12">
            <input name="name" id="name" type="text">
            <label for="name">Name (SSID)</label>
        </div>
        <div class="input-field col s12">
            <input name="password" id="password" type="password">
            <label for="password">Password</label>
        </div>
    </div>

    <div align="center">
        <button class="btn" type="submit">Connect</button>
    </div>
</form>
