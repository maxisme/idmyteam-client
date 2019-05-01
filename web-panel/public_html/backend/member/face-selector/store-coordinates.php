<?php
/* script stores an images feature coordinates (face) */
session_start();
require '../../functions.php';
handlePagePermission("medium");

//create array of coords if not already
if(!is_array($_SESSION['coords'])) $_SESSION['coords'] = array();

$json_c = validCoords($_POST['coords']);
if($json_c){
    // convert coords from floats to ints
    foreach($json_c as $item=>$value) $json_c->$item = intval($value);

    $json_c->method = "manual";
    //store the img_paths coordinates
    $_SESSION['coords'][$_POST['img_path']] = json_encode($json_c);
}