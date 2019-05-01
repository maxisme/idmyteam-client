<?php
/* do not change */
$SETTINGS_FILE = "/var/www/web-panel/settings.yaml";

/* relative variables */
global $yaml_settings;
$yaml_settings = yaml_parse_file($SETTINGS_FILE);
$ROOT = $yaml_settings["Global"]["Root"];
$IMG_TYPE = trim($yaml_settings["Global"]["Image File Type"]);
$unclassified_dir = $yaml_settings["File Location"]["Unclassified Images"]["val"];
$classified_dir = $yaml_settings["File Location"]["Classified Images"]["val"];
$tmp_classified_dir = $yaml_settings["File Location"]["Temporary Classified Images"]["val"];
$invalid_class_dir = "${classified_dir}invalid/"; /* not a person */
$unrecognised_class_dir = "${classified_dir}unknown/"; /* unrecognised person */
$unknown_member_string = "UNKNOWN";
$script_path = $yaml_settings["File Location"]["Bash Script"]["val"];
$member_images = "${ROOT}public_html/images/member/";
$min_training_images = $yaml_settings["Global"]["Training"]["min"];
$live_image_path = $yaml_settings["File Location"]["Live Image"]["val"];

# script locations all added to `sudo visudo`
$validate_script = "${ROOT}scripts/validate-bash.sh";
$control_camera_script = "${ROOT}scripts/control-camera.sh";
$restart_socket_script = "${ROOT}scripts/restart-socket.sh";
$upload_classifications_script = "${ROOT}scripts/upload-classifications.sh";
//$wifi_connector = "${ROOT}scripts/connect-wifi.sh";

$member_permissions = array(
    "low" => 1, //Low: Allowed access to classify team member and view team member",
    "medium" => 2, //"Medium: Allowed access to all the low permissions, adding member, deleting classification images, watching the live stream and editing the script.",
    "high" => 3 // "High: Allowed access to all the medium permissions, choosing member permissions, deleting team member and changing the settings"
);

$permission_explanations = array(
    "low" => "Allowed access to classify team members and view team members",
    "medium" => "Allowed access to all the low permissions, adding members, deleting classification images, watching the live stream and editing the script.",
    "high" => "Allowed access to all the medium permissions, choosing member permissions, deleting team members, viewing the logs and changing the settings"
);

function handlePagePermission($perm){
    global $yaml_settings, $member_permissions;
    if(!key_exists($perm, $member_permissions)) die("Not a valid permission");

    if(!isset($_SESSION['permissions']) || !isset($_SESSION['name'])){
        $_SESSION['redirect'] = $_SERVER['REQUEST_URI'];
        ESC("/login", "You are not logged in!");
    }else if(!allowed($perm)) {
        ESC("/", "You do not have permission to access this page! Please ask a <a href='/members'>member</a> with at least '$perm' permissions.");
    }else if($_SERVER['REQUEST_URI'] != "/index.php" && $_SERVER['REQUEST_URI'] != "/backend/settings/edit.php" && (empty(trim($yaml_settings['Credentials']['Id My Team Username']['val'])) || empty(trim($yaml_settings['Credentials']['Id My Team Credentials']['val'])))){
        ESC("/", "You have not set your Id My Team Credentials!");
    }
}

function storeCollapse($id, $open){
    if(isset($_SESSION['collapse'])){
        $arr = $_SESSION['collapse'];
    }else{
        $arr = array();
    }
    $arr[$id] = $open;
    $_SESSION['collapse'] = $arr;
}

function allowed($perm){
    global $member_permissions;
    return isset($_SESSION['permissions']) && isset($member_permissions[$_SESSION['permissions']]) && $member_permissions[$_SESSION['permissions']] >= $member_permissions[$perm];
}

function connect(){
    global $yaml_settings;
    $con = mysqli_connect("127.0.0.1", $yaml_settings['Credentials']['Database Username']['val'], $yaml_settings['Credentials']['Database Password']['val'], $yaml_settings['Credentials']['Database Name']['val']);
    if(!$con){
        die("Failed to connect to Database");
    }
    return $con;
}

function ESC($redirect, $error_msg=false, $success_msg=false){
    if($error_msg) $_SESSION["error_msg"] = $error_msg;
    if($success_msg) $_SESSION["success_msg"] = $success_msg;
    if($redirect != $_SERVER['REQUEST_URI'] && (!error_get_last() or error_get_last()['type'] == 8)){
        die(header("Location: $redirect"));
    }else{
        die(var_dump(error_get_last()));
    }
}

function handleESC(){
    $html = "";
    if(isset($_SESSION['error_msg'])) {
        $html = "<p class='ESC error'>" . $_SESSION['error_msg'] . "</p>";
    }else if(isset($_SESSION['success_msg'])) {
        $html = "<p class='ESC success'>" . $_SESSION['success_msg'] . "</p>";
    }

    unset($_SESSION['error_msg']);
    unset($_SESSION['success_msg']);
    return $html;
}

/* checks if $name contains only letters and spaces */
function validName($name){
    if(strlen($name) < 3) return false;
    if(ctype_alpha(str_replace(' ', '', $name)) === false) return false;
    return true;
}

/* checks if member exists in database */
function memberExists($con, $name){
    $get_name = mysqli_query($con,"SELECT id
    FROM `Members`
    WHERE name = '$name'");
    if(mysqli_num_rows($get_name) == 1) return true;
    return false;
}

function numTrainedUserImages($con, $id){
    $result = mysqli_query($con,"SELECT SUM(`num`) as sum
    FROM `Activity`
    WHERE `member_id` = '$id' 
    AND type = 'TRAINED'");
    return mysqli_fetch_array($result)['sum'];
}

function cameraRunning(){
    global $yaml_settings;
    $script = $yaml_settings["File Location"]["Camera Script"]["val"];
    exec("ps aux | grep -v grep | grep -i '$script'", $pids);
    return !empty($pids);
}

function myHash($str){
    return hash("sha256", $str); // TODO change to more modern format
}

function generateRandomString($length) {
    $characters = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    $charactersLength = strlen($characters);
    $randomString = '';
    for ($i = 0; $i < $length; $i++) {
        $randomString .= $characters[rand(0, $charactersLength - 1)];
    }
    return $randomString;
}

function imgToBase64($path){
    // Read image path, convert to base64 encoding
    $imageData = base64_encode(file_get_contents($path));
    return 'data: ' . mime_content_type($path).';base64,' . $imageData;
}

function getMemberID($con, $name){
    $result = mysqli_query($con,"SELECT id
    FROM `Members`
    WHERE name = '".$name."'");
    $id = mysqli_fetch_array($result)['id'];
    return $id;
}

function getMemberName($con, $id){
    $result = mysqli_query($con,"SELECT name
    FROM `Members`
    WHERE id = '".$id."'");
    $name = mysqli_fetch_array($result)['name'];
    return $name;
}

function imagesToTrain($member_id){
    global $tmp_classified_dir;
    global $classified_dir;

    $images = glob("${tmp_classified_dir}${member_id}/*");
    $images = array_merge(glob("${classified_dir}${member_id}/*"), $images); // show already classified images of user too.

    // order images by date descending
    usort($images, function($a, $b) {
        return filemtime($a) < filemtime($b);
    });

    return $images;
}

/* makes a directory if it doesn't already exist */
function mdir($d){
    if(!file_exists($d)) mkdir($d, 0777, true);
}

function validCoords($coords_string){
    $coords = json_decode($coords_string);
    if($coords && is_numeric($coords->x) && is_numeric($coords->y) && is_numeric($coords->width) && is_numeric($coords->height)) return $coords;
    return false;
}

function storeImageComment($img_path, $coordinates){
    $im = new imagick($img_path);
    $im->commentImage($coordinates);
    return $im->writeImage($img_path);
}

function getImageComment($img_path){
    $im = new imagick($img_path);
    $comment = $im->getImageProperty("comment");
    return $comment;
}

function writeStat($con, $stat, $value){
    mysqli_query($con,"UPDATE `Stats`
    SET `value` = '".$value."'
    WHERE `stat` = '".$stat."'");
}

function selectStat($con, $stat){
    $result = mysqli_query($con,"SELECT `value`
    FROM `Stats`
    WHERE `stat` = '".$stat."'");
    return mysqli_fetch_array($result)['value'];
}

function isTraining($con, $member_id){
    $result = mysqli_query($con, "SELECT `training`
    FROM `Members`
    WHERE id = '$member_id'");

    return boolval(mysqli_fetch_array($result)['training']);
}

/* SAME FUNCTION IN IDMY.TEAM */
function printChart($id, $labels, $sets, $y_label, $r=0){
    if(is_int($labels)){
        $display_x = 'false';
    }else{
        $display_x = 'true';
    }
    $labels = 'new Array('.$labels.')';
    echo '
    <script>
        $(document).ready(function(){
            new Chart(document.getElementById("'.$id.'"), {
                "type": "line",
                "data": {
                    labels: '.$labels.',
                    datasets: ['.$sets.']
                },
                "options": {
                    scales: {
                        xAxes: [{
                            display: '.$display_x.',
                            gridLines: {
                                display:false
                            }
                        }],
                        yAxes: [{
                            drawBorder: false,
                            scaleLabel: {
                                display: true,
                                labelString: "'.$y_label.'"
                            }
                        }]
                    },
                    elements: { point: { radius: '.$r.' } } // remove data points
                }
            });
        });
    </script>';
}

function in($haystack, $needle){
    return strpos($haystack, $needle) !== false;
}