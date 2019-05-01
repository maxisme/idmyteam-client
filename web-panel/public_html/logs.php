<?php
session_start();
require 'backend/functions.php';
handlePagePermission("high");
$title = "Logs";
require "template/head.php";

$logs_per_page = 100;

$page = $_GET['page'] ?? '1';

$result = mysqli_query($con, "SELECT user_message, message, time
FROM `Logs`
ORDER BY `id` DESC;");

$logs = mysqli_fetch_all($result,MYSQLI_ASSOC);

$num_pages = ceil(count($logs) / $logs_per_page);

if($page + 1 <= $num_pages) $next_page = $page + 1;
if($page - 1 > 0) $prev_page = $page - 1;
$logs = array_slice($logs, ($page - 1) * $logs_per_page, $logs_per_page);

?>
<script type="text/javascript" src="/js/libraries/Chart.min.js"></script>

<!-- SYSTEM ACTIVITY -->
<canvas id="activity" width="400" height="150"></canvas>
<?php
$min_interval = 15;
// fetch activity (number of log messages at interval for last day)
$result = mysqli_query($con,"SELECT time, message, count(message) as cnt
FROM Logs
GROUP BY 
UNIX_TIMESTAMP(time) DIV ". 60 * $min_interval);
$activity_array = mysqli_fetch_all($result);

$from_time = strtotime('-24 hours', time());
$from_time = $from_time - $from_time % (60 * $min_interval); // round to interval

$to_time = strtotime("+$min_interval minutes", time());

$labels = "";
$plot_data = array(
    "Error" => "",
    "Invalid Upload" => "",
    "Repeated Recognition" => "",
    "Unknown Member" => "",
);

$colour = array(
    "Error" => "#333",
    "Invalid Upload" => "#bc2122",
    "Repeated Recognition" => "#DCC698",
    "Unknown Member" => "#2B6F75",
);

$finder = array(
    "Invalid Upload" => array("No face was detected"),
    "Unknown Member" => array("Unknown"),
    "Repeated Recognition" => array("Already")
);

$today_range = range($from_time, $to_time,60 * $min_interval);
for($i = 0; $i < count($today_range) - 1; $i++){
    $begin = $today_range[$i];
    $end = $today_range[$i + 1];

    $t = date("D H:i", $end);
    $num = 0;
    $mess = "";
    foreach($activity_array as $index => $activity){
        $ts = strtotime($activity[0]);
        $mess = $activity[1];
        $num = $activity[2];
        if ($ts >= $begin && $ts < $end){
            unset($activity_array[$index]);
            break;
        }
    }
    $d = "'$t'";
    $labels .= "$d, ";
    // find message type

    $type = "Error";
    foreach($finder as $key => $arr){
        foreach($arr as $val){
            if(in($mess, $val)) $type = $key;
        }
    }

    foreach($plot_data as $key => $arr){
        if ($key == $type){
            $plot_data[$key] .= "{x:$d, y:$num}, ";
        }else{
            $plot_data[$key] .= "{x:$d, y:0}, ";
        }
    }
}


$set = "";
foreach($plot_data as $key => $str){
    $set .= "{
            label: '$key',
            data: [$str],
            borderWidth: 1,
            borderColor: '".$colour[$key]."',
            fill: false
        },";
}
printChart("activity", $labels, $set,"# of Logs", $r=2);
?>


<!-- LOG MESSAGES -->
<div align="center"><strong class="error">"With great power comes great responsibility!"</strong></div>
<div align="center">Please do not use these logs to keep 'tabs' these are purely for debugging the system. Be reminded that we have the right to terminate the account on behalf of employees.</div>


<br>
<?php if($num_pages == 0){
    die("<p>&nbsp</p><div align='center'><h5 class='success'> <i class='material-icons'>done_all</i> 
<br>No logs!</h5></div>");
} ?>

Page <?php echo "$page/$num_pages"?><br>
<table class="responsive-table">
    <thead>
    <tr>
        <th>Message</th>
        <th>Time</th>
    </tr>
    </thead>

    <tbody>
    <?php
    foreach($logs as $log){
    ?>
    <tr>
        <td>
            <?php echo "<strong>". $log['user_message'].'</strong><br>'.strip_tags($log['message']) ?>
        </td>
        <td>
            <?php echo $log['time'] ?>
        </td>
    </tr>
    <?php } ?>
    </tbody>
</table>

<?php if ($num_pages > 1){ ?>
    <div align="center">
        <a href="/logs?page=<?php echo $page - 1 ?>">Previous Page</a> |
        <a href="/logs?page=<?php echo $page + 1 ?>">Next Page</a>
    </div>
<?php } ?>

<a href="backend/logs/delete-all.php" style="font-size: 2em" class="material-icons">delete</a>