<?php
session_start();
require 'backend/functions.php';
handlePagePermission("low");

$title = "Classify";
require "template/head.php";

$images_per_page = 20;

///////////////////////////////////////////////////////
// get all image files in the unclassified directory //
///////////////////////////////////////////////////////
$images = glob("$unclassified_dir*$IMG_TYPE");

// order images by date descending
usort($images, function($a, $b) {
    return filemtime($a) < filemtime($b);
});

$page = $_GET['page'] ?? '1';

$num_pages = ceil(count($images) / $images_per_page);

if($page + 1 <= $num_pages){
    $next_page = $page + 1;
}
if($page - 1 > 0){
    $prev_page = $page - 1;
}

$images = array_slice($images, ($page - 1) * $images_per_page, $images_per_page);

?>

<p class="info">
    Manually classify images that the system was not able to.
    <hr>
    First, you should <strong>delete (<span class="material-icons">remove_circle_outline</span>) all images that do not show a face.</strong><br>
    Then classify each image image by <strong>entering the name of the <a href="/members">member</a></strong> below the image and, if not already, <strong>selecting the area of the face</strong>.<br>
    <div align="center">
        <a class="modal-trigger question material-icons" style="font-size: 2em;" href="#infotrain">help_outline</a>
    </div>
</p>

<!-- Modal Train Structure -->
<div id="infotrain" class="modal">
    <div class="modal-content">
        <h4>Tips</h4>
        You can use the cmd (⌘) key and click between the <span class="material-icons">panorama_fish_eye</span> at the top left corner of the images to select individually.<br>
        Or you can use the shift (⇧) key and click between the <span class="material-icons">panorama_fish_eye</span> at the top left corner of the images to select images between.

        <hr>

        <div class="box" style="border-color: #2BA9B1">&nbsp;</div> indicates the face has been detected by the ID My Team server.<br>
        <div class="box" style="border-color: #bc2122">&nbsp;</div> indicates the face has been manually selected by a team member.
    </div>
</div>

<script src="/js/libraries/multiselector.js"></script>
<script src="/js/libraries/jquery.redirect.js"></script>
<script>
    $(document).ready(function(){
        /* INPUT STUFF */
        $(document).mousedown(function(e) {
            if (!$(e.target).parents("#classifiers").length && !$(e.target).is("span")) {
                selector.multiSelector('deselect');
            }else if($(this).attr("class") == "autocomplete"){
                alert("input");
            }
        });

        var selector = $("#classifiers");
        selector.multiSelector({
            selector: '.col',
            onSelectionStart: function (list, parent, e) {
                return !$(e).find(".autocomplete").is(":focus");
            }
        });

        /* get name data */
        var names = {
            '<?php echo $unknown_member_string?>': null,
            <?php
            $query = mysqli_query($con,"SELECT name FROM `Members`");
            while($row = mysqli_fetch_assoc($query)){
                echo '"'.$row["name"].'": null,';
            }
            ?>
        };

        $("input").bind('keyup change', function() {
            if($(this).parent().hasClass('ms-selected')){ // check if this input is selected
                // update all the selected values
                var val = $(this).val();
                $(".ms-selected").each(function () {
                    var input = $(this).find("input");
                    input.val(val);
					window.inputValidation(input);
                });
            }else{
				window.inputValidation($(this)); // single input edit
            }
        });

        $('input.autocomplete').autocomplete({
            data: names,
            limit: 5, /* only show 5 names */
            minLength: 1
        });

        window.inputValidation = function(input){
            // check if the value of input is in the names list
            var match = false;
            var v = input.val();
            for (var name in names) {
                if (name === v) {
                    match = true;
                }
            }

            console.log(input.closest("span").attr("has_coords"));
            // set underline colour of input
            input.removeClass("valid").removeClass("invalid");
            if(v !== "") {
                if(match && input.closest("span").attr("has_coords") == "1") {
                    input.addClass("valid");
                }else{
                    input.addClass("invalid");
                }
            }

            var class_btn = $("#sub");
            class_btn.addClass("disabled");
            if($(".valid").length> 0 && $(".invalid").length === 0) class_btn.removeClass("disabled");
        }

        /* DELETE image */
        $(".delete").click(function(){
            var to_delete_images = [];
            to_delete_images.push($(this).closest("span").attr("image-path")); /* add the one clicked */

            if($(this).parent().hasClass('ms-selected')) {
                /* add all the selected items as well */
                $(".ms-selected").each(function () {
                    to_delete_images.push($(this).closest("span").attr("image-path"));
                    // alert($(this).closest("span").attr("image-path"));
                });
            }

            to_delete_images = $.unique(to_delete_images); /* make sure all the ids are unique */
            if (confirm('Are you sure you want to delete the '+to_delete_images.length+' classes?')) {
                to_delete_images = JSON.stringify(to_delete_images); /* convert to json */
                $.redirect("backend/classify/delete.php", {delete_array: to_delete_images});
                // alert(to_delete_images);
            }
        });

        /* CLASSIFY STUFF */
        $("#sub").click(function(){
            var classify_array = {};
            $(".valid").each(function () {
                classify_array[$(this).closest("span").attr("image-path")] = $(this).val();
            });

            if (confirm('Are you sure you want to classify?')) {
                $.redirect("backend/classify/make.php", {classify_array: JSON.stringify(classify_array)});
            }
        });
    });
</script>


<div id="classifiers" class="row">
    <?php

    if(count($images) == 0){
        echo "<p>&nbsp</p><div align='center'><h5 class='success'> <i class='material-icons'>done_all</i> 
<br>No images to classify</h5></div>";
    }else {
        $col_classes = "s12 m6 l4";
        $classifyImage = true;
        require 'template/user-image-classification.php';
    }
    ?>
</div>


    <!-- classify button -->
    <button id="sub" type="submit" class="btn-floating btn-large <?php if(!$has_classified) echo 'disabled'?>"><i class="material-icons">done</i></button>


<div align="center">
<?php
if($num_pages > 1){
    echo "<p>Page $page/$num_pages</p>";

    echo '<p>';
    if(isset($prev_page)){
        echo "<a href='/classify?page=$prev_page'>PREV PAGE</a> | ";
    }

    if(isset($next_page)){
        echo "<a href='classify?page=$next_page'>NEXT PAGE</a>";
    }
}
echo '</p>';
?>
</div>
<p>&nbsp;</p>
<?php require "template/foot.php" ?>