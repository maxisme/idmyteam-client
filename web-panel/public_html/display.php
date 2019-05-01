<?php
/* displays content of file in settings */
session_start();
require 'backend/functions.php';
handlePagePermission("high");

require "template/head.php";
?>

<pre>
    <?php echo file_get_contents($_GET['f']); ?>
</pre>

<?php require "template/foot.php" ?>
