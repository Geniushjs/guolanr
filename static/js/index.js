$(document).ready(
	function () {
		$(window).scroll(
			function () {
				$(".small_cart").css("top", $(window).scrollTop());
			}
		);
	}
);