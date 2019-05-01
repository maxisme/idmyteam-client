<?php
session_start();
require 'backend/functions.php';
handlePagePermission("medium");

$title = "Script";
require "template/head.php";
?>

<script src="/js/libraries/codemirror.js"></script>
<link rel="stylesheet" href="/css/codemirror.css">
<script src="/js/libraries/codemirror-shell.js"></script>

<p class="info">
    Custom <a href="http://www.tldp.org/LDP/Bash-Beginners-Guide/html/" target="_blank">bash</a> script to be executed on a recognition.
    <hr>
</p>

<p>
    <strong>$1</strong> - Holds the name of the recognised person. Returns <i><?php echo $unknown_member_string?></i> if detected a person but unable to recognise them.
    <br>
    <strong>$2</strong> - Holds a value between a minimum of 0.5 to a maximum of 1 representing the confidence of the member.
</p>

<form method="post" action="backend/script/edit.php">
    <textarea id="t" name="bash"><?php echo file_get_contents($script_path)?></textarea>
    Last Execution Speed (seconds): <?php echo selectStat($con, "Custom Script Speed")?>
    <p>
        <div class="center-align">
            <button class="btn-floating btn-large disabled" type="submit"><i class="material-icons">code</i></button>
        </div>
    </p>
</form>
<script>
    $(document).ready(function(){
		var myCodeMirror = CodeMirror.fromTextArea(document.getElementById("t"),{
			lineNumbers: true,
            indentUnit: 4
        });
		myCodeMirror.on("keydown", function() {
			console.log("change");
			$("button").removeClass("disabled");
			$("button").addClass("pulse");
			setTimeout(function() {
				$("button").removeClass("pulse");
			}, 1000);
		});
    });
</script>
<?php require "template/foot.php" ?>