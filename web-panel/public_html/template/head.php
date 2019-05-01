<html>
<head>
    <!-- custom meta -->
    <meta name="keywords" content="detect, recognise, facial, detection, detecter, recogniser, detectme, detectme.uk">
    <meta name="description" content="A face recognition API for your team.">
    <meta name="google" content="notranslate" />
    <title>
    <?php echo $title ?? 'Web Panel'; ?>
    </title>
    <link rel="shortcut icon" href="/images/icon.ico">

    <!-- mobile meta -->
    <meta name="viewport" content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0'/>

    <!-- jQuery -->
    <script type="text/javascript" src="/js/libraries/jquery-3.2.1.min.js"></script>

    <!-- Third party JavaScript -->
    <script src="/js/libraries/materialize.min.js"></script>

    <!-- Google Fonts -->
    <link href="/css/google-fonts.css" rel="stylesheet">

    <!-- Third party CSS -->
    <link rel="stylesheet" href="/css/materialize-sass/materialize.css">

    <!-- Custom CSS -->
    <link href="/css/style.css" rel="stylesheet">

    <!-- Custom JS -->
    <script src="/js/script.js"></script>
</head>

<?php
$menu_bar_content = "
<li><a href='/members' class='button'>Members</a></li>
<li><a href='/live-stream' class='button'>Live Stream</a></li>
<li><a href='/script' class='button'>Script</a></li>
<li><a href='/classify' class='button'>Classify</a></li>
<li><a href='/settings' class='button'>Settings</a></li>
<li><a href='/logs' class='button'>Logs</a></li>
<li><a href='/backend/login/logout' class='button'>Log Out</a></li>
";

$con = connect();

if(!isset($_SESSION['permissions'])){
    $menu_bar_content = "<li><a id='login' href='/login' class='button'>Log  In</a></li>";
}


/* check everything is up and running */
$all_good = true;
if(!cameraRunning()) $all_good = false;

$sm = selectStat($con, "Socket");
if($sm != "Connected") $all_good = false;
if($yaml_settings['Camera']['Silent Mode']['val'] == "1") $all_good = false;
?>
<body>
    <nav class="z-depth-0">
        <div class="nav-wrapper">
            <a href="/" class="brand-logo"><img class="svg <?php if(!$all_good) echo 'error'?>" src="/images/logo.svg"/></a>
            <a href="#" data-activates="mobile-demo" class="button-collapse"><i class="material-icons">menu</i></a>
            <ul class="right hide-on-med-and-down">
                <?php echo $menu_bar_content?>
            </ul>
            <ul class="side-nav" id="mobile-demo">
                <?php echo $menu_bar_content?>
            </ul>
        </div>
    </nav>
    <div class="content" align="center">
        <?php
            if(isset($title)) echo "<h2><strong>".$title."</strong></h2>";
        ?>

        <?php echo handleESC();?>

