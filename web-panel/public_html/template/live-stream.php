<div align="center">
    <?php
    $running = false;
    if (!cameraRunning()) {
        echo '<strong>Camera is off!</strong><br><br>';
    }else if($yaml_settings['Camera']['Live Stream']['val'] == 0){
        echo '<strong>Live Stream is off!</strong><br><br>';
    }else{
        $running = true;
        echo '<canvas id="livestream" width="700px" height="500px"></canvas>';
    }
    if(!$running){ ?>
        <!-- switch to handle turning on the camera and live stream -->
        <span class="switch">
            <label>
                <input type="checkbox">
                <span class="lever"></span>
            </label>
        </span>
    <?php } ?>
</div>

<script src="/js/libraries/jquery.redirect.js"></script>
<script>
    $(document).ready(function(){

    	<?php if ($running){ ?>
            var img = new Image();
            img.onload = function() {
				var w = $(window).width() * 0.6;
				var h = w * (img.height/img.width);
				var c = $("canvas");
				c.attr("width", w);
				c.attr("height", h);

                var canvas = document.getElementById("livestream");
                var context = canvas.getContext("2d");
                context.drawImage(img, 0, 0, img.width, img.height, 0, 0, w, h);

				//update image every 0.1 seconds
                setTimeout(timedRefresh, 100);
            };

            function timedRefresh() {
                img.src = '/template/stream.php?d=' + Date.now();
            }

            timedRefresh();

        <?php }else{?>
            // Turn on camera and live stream
            $("input").on("change", function(){
				$.redirect("/backend/settings/edit.php", { 'camera_run': "1", 'camera_live-stream': "1"});
            });
        <?php }?>
    });
</script>