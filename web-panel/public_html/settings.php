<?php
session_start();

/* do not remove incase problems with yaml*/
error_reporting(E_ALL);
ini_set("display_errors", 1);

require 'backend/functions.php';
handlePagePermission("high");
$title = "Settings";
require "template/head.php";
?>
<form method="post" action="backend/settings/edit.php">
<ul class="collapsible content" data-collapsible="expandable">
    <li id="Stats">
        <div class="collapsible-header">
            <i class="material-icons">show_chart</i> Statistics
        </div>
        <div class="collapsible-body">
            <div id="time_since"></div>
            <?php
            $result = mysqli_query($con,"SELECT *
            FROM `Stats`");
            while ($row = mysqli_fetch_array($result)){
                ?>
                <div class="row valign-wrapper">
                    <div class="col valign s12 m6 l8">
                        <h5><?php echo $row['stat']?></h5>
                        <?php echo $row['info']?>
                    </div>
                    <div align="center" class="col s12 m6 l4">
                        <h5><?php echo $row['value'] ?? '0'?></h5>
                    </div>
                </div>
            <?php }?>
        </div>
    </li>
    <li id="Settings">
        <div class="collapsible-header">
            <i class="material-icons">tune</i> Settings
        </div>
        <div class="collapsible-body">
        <?php foreach ($yaml_settings as $type_header => $type_array) { if($type_header == "Global") continue ?>
            <ul class="collapsible" data-collapsible="expandable">
                <li id="<?php echo $type_header ?>">
                    <div class="collapsible-header">
                        <i class="material-icons"><?php echo $type_array['icon']?></i> <?php echo $type_header ?>
                    </div>
                    <div class="collapsible-body">
                        <?php if(isset($type_array['info'])) echo '<div class="info">'.$type_array['info'].'</div>';?>

                        <?php foreach ($type_array as $type => $arr) { if (count($arr) <= 1) continue; $name = strtolower(str_replace(" ", "-","${type_header}_${type}")); ?>
                            <div class="row valign-wrapper">
                                <div class="col s12 m6 l8">
                                    <!-- info -->
                                    <h5 id='<?php echo $type ?>'><?php echo $type ?></h5>
                                    <?php echo $arr['info']; ?>
                                </div>
                                <div align="center" class="in valign valign-wrapper col s12 m6 l4">
                                    <!-- HANDLE ALL THE DIFFERENT FORM INPUTS -->
                                    <?php if ($arr['type'] == "switch") { ?>
                                        <?php
                                            /* check if the camera script is running manually */
                                            if($type == "Run"){
                                                if(cameraRunning()) $arr['val'] = '1';
                                            }
                                        ?>
                                        <span class="switch">
                                            <label>
                                                <input type='hidden' value='0' name="<?php echo $name?>">
                                                <input type="checkbox" name="<?php echo $name?>" <?php if($arr['val'] == '1'){ echo ' checked '; }?> <?php if(isset($arr['disabled'])) echo "disabled";?>>
                                                <span class="lever"></span>
                                            </label>
                                        </span>

                                    <?php } else if($arr['type'] == "select"){ ?>
                                        <select name="<?php echo $name?>" <?php if(isset($arr['disabled'])) echo "disabled";?>>
                                            <?php
                                                $options = $arr["options"];
                                                /* handle default value of options */
                                                echo str_replace($arr["val"].'"', $arr["val"].'" selected="selected"', $options);
                                            ?>
                                        </select>

                                    <?php } else if($arr['type'] == "range"){ ?>
                                        <div class="range-field"><input type="range" name="<?php echo $name?>" value="<?php echo $arr["val"]?>" min="<?php echo $arr["min"]?>" max="<?php echo $arr["max"]?>" step="<?php echo $arr["step"]?>" <?php if(isset($arr['disabled'])) echo "disabled";?>></div>

                                    <?php } else if($arr['type'] == "text"){ ?>
                                        <?php if(isset($arr["icon"])) { ?>
                                            <label style="padding-right: 10px" class="valign material-icons"><?php echo $arr["icon"]?></label>
                                        <?php }?>
                                        <input style="margin: 0;" type="text" name="<?php echo $name?>" value="<?php echo $arr["val"]?>" <?php if(isset($arr['disabled'])) echo "disabled";?>>

                                    <?php } else if($arr['type'] == "time"){ ?>
                                        <label style="padding-right: 10px" class="material-icons">timer</label>
                                        <input style="margin: 0;" type="text" name="<?php echo $name?>" class="timepicker" value="<?php echo $arr["val"]?>" <?php if(isset($arr['disabled'])) echo "disabled";?>>

                                    <?php } ?>

                                </div>
                            </div>
                        <?php } ?>
                    </div>
                </li>
            </ul>
        <?php } ?>
        </div>
    </li>
</ul>
<button id="sub" type="submit" class="btn-floating btn-large disabled"><i class="material-icons">done</i></button>
</form>

<script>
    // https://stackoverflow.com/a/3177838/2768038
    function timeSince(date) {
        var seconds = Math.floor((new Date() - date) / 1000);

        var interval = Math.floor(seconds / 31536000);

        if (interval> 1) {
            return interval + " years";
        }
        interval = Math.floor(seconds / 2592000);
        if (interval> 1) {
            return interval + " months";
        }
        interval = Math.floor(seconds / 86400);
        if (interval> 1) {
            return interval + " days";
        }
        interval = Math.floor(seconds / 3600);
        if (interval> 1) {
            return interval + " hours";
        }
        interval = Math.floor(seconds / 60);
        if (interval> 1) {
            return interval + " minutes";
        }
        return Math.floor(seconds) + " seconds";
    }

    var should_prevent = false;
    function onChange(){
        should_prevent = true;
		$("#sub").removeClass("disabled");
		$("#sub").addClass("pulse");
        setTimeout(function() {
            $("#sub").removeClass("pulse");
        }, 1000);
    }

    $(document).ready(function () {
        // update "time since" in settings every second
        <?php if (isset($time_since)){ ?>
            var time_since = new Date();
            time_since.setTime(<?php echo $time_since?> * 1000);

            setInterval(function(){
                $("#time_since").html("Last updated "+timeSince(time_since)+" ago. <a href='/settings'>Refresh</a>")
            },1000);
        <?php } ?>

		/* set all stored collapsible settings */
        <?php
        if(isset($_SESSION['collapse'])){
            foreach($_SESSION['collapse'] as $id=>$open) {
                if($open == 0) continue;
                echo '$("#'.$id.'").find(".collapsible-header").first().addClass("active");';
            }
        }
        ?>

        function collapse(id, open){
			$.get("/backend/settings/collapse.php?id="+id+"&open="+open);
        }

		$('.collapsible').collapsible({
			onOpen: function(el){
				collapse($(el).attr("id"), 1);
            },
            onClose: function(el){
				collapse($(el).attr("id"), 0);
            }
		});

        $('select').material_select();

        $('.timepicker').pickatime({
            fromnow: 0,       // set default time to * milliseconds from now (using with default = 'now')
            twelvehour: false, // Use AM/PM or 24-hour format
            donetext: 'OK', // text for done-button
            cleartext: 'Clear', // text for clear-button
            canceltext: 'Cancel', // Text for cancel-button
            autoclose: true, // automatic close timepicker
            ampmclickable: true, // make AM PM clickable
            afterDone: function () {
                onChange();
            }
        });

        $("form").on('change keyup', function() {
            onChange();
        });
    });
</script>

<?php require "template/foot.php" ?>