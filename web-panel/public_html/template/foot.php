
</div>
<p>&nbsp;</p>
<?php
if(allowed("high")) {
    ?>
    <script>
		$(document).ready(function () {
			setInterval(function () {
				$.get("/backend/logs/ajax.php", function (data) {
					if (data.length > 0) {
						data = JSON.parse(data);
						data.forEach(function (d) {
							var t = $('<span>' + d + '</span>').add($("<a href='/logs' class='btn-flat toast-action'>View Logs</a>"));
							Materialize.toast(t, 15000, '');
						});
					}
				});
			}, 1000); // every 2 seconds
		});
    </script>
    <?php
}
?>
</body>
</html>
