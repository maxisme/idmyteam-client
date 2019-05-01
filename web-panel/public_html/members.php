<?php
session_start();
require 'backend/functions.php';
handlePagePermission("low");

$title = "Members";
require "template/head.php";

$red = "#bc2122";
$pending_colour = "#db8d2e";

function genSplitFaceCSS($perc, $base_colour, $pending_colour){
    return "
    background: -moz-linear-gradient(bottom, $pending_colour 0%, $pending_colour $perc, $base_colour $perc, $base_colour 100%);
    background: -webkit-linear-gradient(bottom, $pending_colour 0%,$pending_colour $perc,$base_colour $perc,$base_colour 100%);
    background: linear-gradient(to top, $pending_colour 0%,$pending_colour $perc,$base_colour $perc,$base_colour 100%);
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr=$pending_colour, endColorstr=$base_colour,GradientType=0 );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;";
}
?>
<script src="js/libraries/jquery.redirect.js"></script>
<p class="info">
    <?php if($sm == "No Team Model") {
        echo "<strong class='error'>For the system to start recognising you must first add and train at least 2 members!</strong><br>";
    }else {
        echo "The members of your team.";
    }?>
    <hr>
</p>
<?php if(allowed("medium")){?>
    <div align="center"><p><a style="border-bottom: none;" href="member/add"><div class="btn-floating btn-large"><i class="large material-icons">person_add</i></div></a></p></div>
<?php }?>

<table id="members">
    <thead>
        <tr>
            <th><!-- image --></th>
            <th>Name</th>
            <?php if(allowed("medium")) { ?>
                <th>
                    Train <a class="modal-trigger question material-icons" href="#modaltrain">help_outline</a>
                </th>
                <!-- Modal Train Structure -->
                <div id="modaltrain" class="modal">

                    <div class="modal-content">
                        <h4>Trained</h4>
                        <span class="material-icons error">face</span> indicates that 0 faces are ready to be sent for training<br>
                        <span class="material-icons" style="<?php echo genSplitFaceCSS("50%", $red, $pending_colour)?>">face</span> indicates that there are <?php echo ($min_training_images/2)." out of the ".$min_training_images?> faces needed for the initial training<br>
                        <span class="material-icons" style="color: <?php echo $pending_colour?>">face</span> indicates that enough faces are pending training<br>
                        <span class="material-icons flashme">face</span> indicates that the faces are being trained<br>
                        <span class="material-icons success">face</span> indicates that more than <?php echo $min_training_images?> faces have been trained and the user is now able to be recognised<br>
                    </div>
                </div>
                <th>
                    Stats
                </th>
            <?php }?>

            <?php if(allowed("high")) { ?>
                <th>Permissions <a class="question modal-trigger material-icons" href="#modalperm">help_outline</a></th>

                <!-- MODAL FOR PERMISSIONS SAME AS member/add.php-->
                <div id="modalperm" class="modal">
                    <div class="modal-content">
                        <h4>Website Permissions</h4>
                        <p>
                            Choose the permissions for this user.
                        </p>
                        <?php foreach($permission_explanations as $permission => $explanation){ ?>
                            <p>
                                <strong><?php echo ucfirst($permission)?></strong><br><?php echo $explanation?>
                            </p>
                        <?php }?>
                    </div>
                </div>

                <th>Change Password</th>
                <th>Delete <a class=" modal-trigger question material-icons" href="#modaldelete">help_outline</a></th>
                <!-- Modal Delete Structure -->
                <div id="modaldelete" class="modal">
                    <div class="modal-content">
                        <h4>Delete</h4>
                        <p>Deleting a member is <strong>irreversible</strong>. All the users data will be purged and the user will no longer be recognised.</p>
                    </div>
                </div>
            <?php }?>
        </tr>
    </thead>
    <tbody>
        <?php
        $query = mysqli_query($con,"SELECT *
                            FROM `Members`");
        while($row = mysqli_fetch_assoc($query)){
            // get portrait of member
            $portrait_path = "";
            $images = glob("${member_images}".$row['name']."*");
            foreach ($images as $image_path) $portrait_path = $image_path;
        ?>
            <tr>
                <td>
                    <img width="100px"src='<?php echo imgToBase64($portrait_path)?>' alt="" class="materialboxed circle border responsive-img">
                </td>
                <td>
                    <strong><span class="name"><?php echo $row['name'];?></span></strong>
                </td>
                <?php
                if(allowed("medium")){
                    ?>
                    <?php if(isTraining($con, $row['id'])){ ?>
                        <td><div class="icon material-icons flashme">face</div></td>
                    <?php }else if(numTrainedUserImages($con, $row['id']) >= $min_training_images){ ?>
                        <td><a href="member/train?member=<?php echo $row['id']?>" class="icon material-icons success">face</a></td>
                    <?php }else{ $perc = (count(imagesToTrain($row['id'])) / $min_training_images) * 100 . "%"; ?>
                        <td><a href="member/train?member=<?php echo $row['id']?>" class="train icon material-icons" style="<?php echo genSplitFaceCSS($perc, $red, $pending_colour)?>">face</a></td>
                    <?php } ?>

                    <td><a href="member/stats?member=<?php echo $row['id']?>" class="stats icon material-icons">timeline</a></td>
                <?php }?>
                <?php if(allowed("high")){ ?>
                    <td>
                        <select>
                            <?php
                            foreach($member_permissions as $perm => $id){
                                $p = ucwords($perm);
                                if($perm == $row['perm']){
                                    echo "<option value='$id' selected>$p</option>";
                                }else{
                                    echo "<option value='$id'>$p</option>";
                                }
                            }
                            ?>
                        </select>
                    </td>
                    <td><a class="new-pass icon material-icons" href="member/password?name=<?php echo $row['name'];?>">vpn_key</a></td>
                    <td><i class="delete icon material-icons">delete</i></td>
                <?php }?>
            </tr>
    <?php
        }
    ?>
    </tbody>
</table>
    <script>
        $(document).ready(function() {
            $('select').material_select();

            $(".delete").click(function() {
                var name = $(this).parents("tr").find(".name").html();
                if(confirm("Are you sure you want to permanently delete '"+name+"'?")){
                    $.redirect("backend/member/delete.php", { member: name});
                }
            });

            <?php if(allowed("high")){ ?>
                $('select').on('change', function() {
                    var permission = this.value;
                    var name = $(this).parents("tr").find(".name").html();
                    $.redirect("/backend/member/permissions.php",{ perm: permission, name: name});
                });
            <?php } ?>
        });
    </script>
</div>

<?php require "template/foot.php" ?>
