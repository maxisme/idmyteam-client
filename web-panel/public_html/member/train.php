<?php
session_start();
require '../backend/functions.php';
handlePagePermission("medium");

$return_page = "/members";
// a $_GET is sent the first time accessing this page. After that a session is created for the member until the
// images are sent to be trained.
if(isset($_GET['member'])){
    $member_id = $_GET['member'];
    $_SESSION['training_member_id'] = $member_id;
}else if(isset($_SESSION['training_member_id'])){
    $member_id = $_SESSION['training_member_id'];
}

$title = "Train";
require "../template/head.php";

$name = getMemberName($con, $member_id);

if($name == "root") ESC($return_page,"You cannot train root user. Should be deleted.");
if(!memberExists($con, $name)) ESC($return_page, "Not a valid member id '$member_id'", false);
if(isTraining($con, $member_id)) ESC($return_page, "Currently Training '$name'", false);

//get pending images
$images = imagesToTrain($member_id);

//get number of already classified images
$num_actually_trained = numTrainedUserImages($con, $member_id) ?? 0;
$num_trained = $num_actually_trained + count($images);
$perc_trained = ($num_trained / $min_training_images) * 100;

?>
<h5>How to train</h5>
<ol>
    <li class="info">
        Take as many photos of <strong><?php echo $name?></strong> as possible. The more images, the better the system will perform.
    </li>
    <li class="info">
        After taking the photos <strong>select the facial areas</strong>.
    </li>
    <li class="info">
        Submit.
    </li>
</ol>
<p class="info">
    You are required to take <strong>at least <?php echo $min_training_images?> images</strong> of <strong><?php echo $name?></strong> for the recognition system to start.
</p>
<?php if($num_actually_trained >= $min_training_images){?>
    <p class="info">
        Due to the member already being trained. On submitting the images they will be moved to <strong><?php echo $name?>'s</strong> training folder for training at <?php echo $yaml_settings["Training"]["Recurring Time"]["val"];?> hours.
    </p>
<?php }else{ ?>
    <p class="info">
        As <?php echo $name?> has not been trained. On submitting the images they will be immediately uploaded for training.
    </p>
<?php }?>
<hr>

<?php
// CHECK IF TRAINING MODE IS TURNED OFF
// IF IT IS OFF ASK FOR IT TO BE TURNED ON
if($yaml_settings['Camera']['Silent Mode']['val'] != "1" || $yaml_settings['Camera']['Mask']['val'] == "1"){
    ?>
    <div align="center">
        Switch on <strong>Silent Mode</strong> to prevent unnecessary recognition attempts.<br><br>
        <span class="switch">
            <label>
                <input type="checkbox">
                <span class="lever"></span>
            </label>
        </span>
    </div>
    <br>

    <script>
        $(document).ready(function(){
            // Turn on camera and live stream
            $("input").on("change", function(){
                $.redirect("/backend/settings/edit.php", {'camera_silent-mode': "1", 'camera_mask': "0"});
            });
        })
    </script>
    <?php
}
require "../template/live-stream.php"; ?>
<div id="train">
    <?php
        if($running){
    ?>
    <div align="center"><div id="capture-btn" class="btn-floating btn-large"><i class="material-icons">photo_camera</i></div></div>
    <?php }?>
    <?php echo count($images)." / ".$min_training_images ?> images to be sent for training.
    <div class="progress">
        <div class="determinate" style="width: <?php echo $perc_trained?>%"></div>
    </div>
    <h4>Training Images of <?php echo $name?></h4>
    <p class="valign-wrapper">
        <span class="material-icons">face</span> the image has already been manually classified.
    </p>
    <div class="row">
        <?php
            $col_classes = "s12 l6";
        require '../template/user-image-classification.php'
        ?>
    </div>
    <div align="center">
        <div id="train-btn" class="btn-floating btn-large <?php if($num_trained < $min_training_images) echo "disabled" ?>"><i class="material-icons"><?php echo $yaml_settings["Training"]["icon"]?></i></div>
    </div>
    <script>
        $(document).ready(function(){
            window.init_areas = true;
            <?php echo $area_jquery?>
            window.init_areas = false;

			$("#capture-btn").click(function(){
                $(this).addClass('disabled');
                $(this).val("more_horiz");
                $.redirect("/backend/member/train/capture.php");
            });

            $("#train-btn").click(function(){
                if(!allImagesHaveAreas()){
                    alert("Not all images have detection coordinates set.")
                } else {
                    // send images to be trained
                    $.redirect("/backend/member/train/to-train.php");
                }
            });

            $(".delete").click(function(){
                var path = $(this).parent().attr("image-path");
                $.redirect("/backend/member/train/delete-capture.php", {image_path: path});
            });

			/* used along with a submit button to make sure all images have manually assigned areas */
			function allImagesHaveAreas() {
				$("*[image-path]").each(function () {
					if ($(this).attr("has_coords") == "") return false;
				});
				return true;
			}
        });
    </script>
</div>
<?php require "../template/foot.php" ?>