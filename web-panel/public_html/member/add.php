<?php
session_start();
require '../backend/functions.php';
handlePagePermission("medium");
$title = "Add Member";
require "../template/head.php";
?>

<div align="left">
    <form method="post" action="/backend/member/add.php" enctype="multipart/form-data">
        <div class="row">
            <div class="input-field col s12">
                <input name="name" id="name" type="text">
                <label for="name">Name</label>
            </div>
        </div>
        <!-- PASSWORD -->
        <div class="row">
            <div class="input-field col s6">
                <input name="password" id="password" type="password">
                <label for="password">Password</label>
            </div>
            <div class="input-field col s6">
                <input name="c_password" id="password-confirm" type="password">
                <label for="password-confirm">Confirm Password</label>
            </div>
        </div>

        <div class="row">
            <div class="file-field input-field col s12">
                <div class="btn btn-small">
                    <span>Profile Image</span>
                    <input name="file" type="file"> <!-- actual $_FILES -->
                </div>
                <div class="file-path-wrapper">
                    <input class="file-path" type="text">
                </div>
            </div>
        </div>
        <div class="row">
            <div class="input-field col s12">
                <a class="modal-trigger question" href = "#modalperm">Permissions<span style="font-size: inherit;display: inline-block; vertical-align: middle" class="material-icons">help_outline</span> </a>
                <select name="permission">
                    <?php
                    foreach($member_permissions as $perm => $id){
                        echo "<option value='$perm'>".ucfirst($perm)."</option>";
                    }
                    ?>
                </select>
            </div>
        </div>

        <!-- MODAL FOR PERMISSIONS SAME AS members.php-->
        <div id="modalperm" class="modal">
            <div class="modal-content">
                <h4>Website Permissions</h4>
                <p>
                    Choose the permissions for this user.
                </p>
                <?php foreach($permission_explanations as $permission => $explanation){ ?>
                    <p>
                        <strong><?php echo ucfirst($permission)?></strong>: <?php echo $explanation?>
                    </p>
                <?php }?>
            </div>
        </div>


        <div align="center">
            <button class="btn material-icons" type="submit">navigate_next</button>
        </div>
    </form>
    <script>
        $(document).ready(function() {
			$('.modal').modal();
            $('select').material_select();
        });
    </script>
</div>
<?php require "../template/foot.php" ?>
