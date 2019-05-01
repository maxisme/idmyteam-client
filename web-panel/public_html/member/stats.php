<?php
session_start();
require '../backend/functions.php';
handlePagePermission("medium");
$return_page = "/members";


$title = "Stats";
require "../template/head.php";

// a $_GET is sent the first time accessing this page. After that a session is created for the member until the
// images are sent to be trained.
if(isset($_GET['member'])){
    $member_id = $_GET['member'];
    $_SESSION['stats_id'] = $member_id;
}else if(isset($_SESSION['stats_id'])){
    $member_id = $_SESSION['stats_id'];
}

$name = getMemberName($con, $member_id);

if($name == "root"){
    ESC($return_page,"You cannot view stats of root user. Should be deleted.");
}

if(!memberExists($con, $name)){
    ESC($return_page, "Not a valid member id '".$_GET['member']."'", false);
}
?>
    <script type="text/javascript" src="/js/libraries/Chart.min.js"></script>
<?php
    $query = mysqli_query($con,"SELECT `score`
    FROM Activity 
    WHERE `member_id` = '".$member_id."'
    AND `type` = 'RECOGNISED'");
    if($query){
        echo '<h5>Recognition scores of '.$name.'</h5><canvas id="rec" width="400" height="100"></canvas>';
        $arr = mysqli_fetch_all($query);
        $num_recognitions = count($arr);

        $data = implode(',', array_map(function ($entry) {
            return $entry[0];
        }, array_filter($arr)));

        $set = "{
            label: 'Score',
            data: [$data],
            borderWidth: 1,
            borderColor: '#333',
            fill: false
        }";
        $sum = 0;
        foreach( $arr as $val){
            $sum += $val[0];
        }
        $avg_score = $sum / $num_recognitions;
        echo "Recognised <strong>$num_recognitions</strong> times. At an average score of $avg_score.";

        printChart("rec", $num_recognitions, $set,"Score", $r=2);
    }else if(numTrainedUserImages($con, $member_id) < $min_training_images) {
        echo "<span class='error'>$name cannot be recognised! Not enough images trained.</span>";
        if(isTraining($con, $member_id)) echo "<br><span class='error'>Currently training!</span>";
    }else{
        echo "<span class='error'>$name has not been recognised yet!</span>";
    }
?>


<?php require "../template/foot.php" ?>