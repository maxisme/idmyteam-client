<?php
/* this page is used along with an import to display images with selection areas */
if(!isset($images)) die("You must specify images");
if(!isset($col_classes)) die("You must specify col classes (s12, m6)");
?>

<!-- FOR EACH IMAGE -->
<?php
    $area_jquery = "";
    $id = 0;
    foreach ($images as $image){
        $id++;
        /* JQUERY */
        // get feature coordinates either stored in session or in image file comment and display them using $area_jquery
        if(isset($_SESSION['coords'][$image])){
            $coords = $_SESSION['coords'][$image];
        }else{
            $coords = getImageComment($image);
        }
        // jquery to be run on page load to set all the areas stored
        if(validCoords($coords)) $area_jquery .= "$('#portrait-$id').selectAreas('add', toActualArea($('#portrait-$id'), JSON.parse('$coords'), true));\n$('#portrait-$id').closest('span').attr(\"has_coords\", \"1\");\n";

        ?>
        <span image-path="<?php echo $image?>" align="left" style="padding-bottom: 20px" class="col ima <?php echo $col_classes?>">
            <div class="icon material-icons delete">remove_circle_outline</div>

            <?php if(!isset($classifyImage)){ ?>
                <!-- [maybe] show icon showing that the image has already been classified-->
                <div class="icon material-icons face"
                    <?php if(strpos($image, $classified_dir) === false){ ?>
                        style="visibility:hidden"
                    <?php } ?>
                >face</div>
            <?php }else{ ?>
                <!-- Show selection icon so that you can classify the name of multiple image at once-->
                <div class="icon circle material-icons">panorama_fish_eye</div>
            <?php }?>

            <img style="height: 500px; width: 100%" id="portrait-<?php echo $id?>" class="portrait" src='<?php echo imgToBase64($image)?>'>

            <?php if(isset($classifyImage)){
                echo '<input class="autocomplete';

                /* if image file is in format memberid_file.jpg  auto fill input */
                $file = str_replace($unclassified_dir,"", $image);
                $member_id = explode("_", $file)[0];
                $name = getMemberName($con, $member_id);
                if(!empty($name)){
                    $has_classified = true;
                    echo ' valid" value="'.$name;
                }
                echo '" placeholder="Member Name..." type="search">';
            } ?>
        </span>
        <?php
    }
?>

<!-- JAVASCRIPT -->
<script src="/js/libraries/jquery.selectareas.min.js"></script>
<script>
    /* set areas after page load */
	$(document).ready(function() {
		window.setting_init_areas = true;
        <?php echo $area_jquery?>
		window.setting_init_areas = false;
	});

    /* image dimensions by js library are relative to the screen size rather than the actual image size
    * This function converts them*/
	function toActualArea(el, area, inverse=false){
		var arr = new Object();
		if(!area) return arr; // return empty object for empty area

		var nw = el[0].naturalWidth / el.width();
		var nh = el[0].naturalHeight / el.height();
		if(inverse){
			nw = el.width() / el[0].naturalWidth;
			nh = el.height() / el[0].naturalHeight;
		}

		arr.x = area.x * nw;
		arr.y = area.y * nh;
		arr.width = area.width * nw;
		arr.height = area.height * nh;

		if(area.method) arr.method = area.method;
		return arr;
	}

	// HANDLE SELECTION
	$(".portrait").selectAreas({
		minSize: [10, 10],
		maxAreas: 1,
		onChanged: function (e, id, areas) {
			var p_span = $(this).closest(".ima");
			var a = toActualArea($(this), areas[0]);

			var outline = $(this).parent().find('.select-areas-outline');
			if(!window.setting_init_areas){ // don't upload during initial set of areas on images
				outline.css("border", "1px #bc2122 solid"); // during Ajax Upload

				// store changed coord in $_session for use in to-train.php
				$.post( "/backend/member/face-selector/store-coordinates.php", { img_path: p_span.attr("image-path"), coords: JSON.stringify(a) }).done(function(){
					// mark image as having coords for submit button
					if(areas.length >= 1){
						outline.css("border", "4px #bc2122 solid"); // red border
						p_span.attr("has_coords", "1");
					}else{
						p_span.attr("has_coords", "0");
					}

					// SEND ALERT TO CLASSIFY FUNCTION TO VERIFY INPUT IS STILL VALID
                    <?php if(isset($classifyImage)){ ?>
					    window.inputValidation(p_span.find("input"));
                    <?php }?>
				});
			}else if(a.method == "model"){
				outline.css("border", "4px #2BA9B1 solid"); // blue border
			}
		}
	});
</script>