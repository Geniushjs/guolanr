$(document).ready(
	function () {
		setTimeout('$(".small_cart_body").slideUp()', 1000);
		  
		$(".getone").click(
			function () {
				$.get("/cart/add", {fruit_id:$(this).attr("fruit_id"), render_to:$(this).attr("render_to")},
					function (data) {
						handleCartData(data);
						setTimeout('$(".small_cart_body").slideUp()', 1000);
						//$(".small_cart_body").hide();
					}
				);
			}
		);
			
		bindEvent();
	}
);

function bindEvent() {
	$(".coupon").change(
		function (){
			$.get("/cart/coupon", {coupon_id:$(this).val(), render_to:"checkout_cart.html"},
				function (data) {
					handleCartData(data);
				}
			);
		}
	);
		
	$(".small_cart").mouseenter(
		function () {
			$(".small_cart_body").slideDown("fast");
		}
	);
	$(".small_cart").mouseleave(
		function () {
			$(".small_cart_body").slideUp("fast");
//			setTimeout('$(".small_cart_body").slideUp("fast")', 1000);
		}
	);
		
	$(".count").change(
		function () {
			$.get("/cart/update", 
				{fruit_id:$(this).attr("fruit_id"), count:$(this).val(), render_to:$(this).attr("render_to")},
				function (data) {
					handleCartData(data);
				}
			);
		}
	);
	
	$(".add").click(
		function () {
			$.get("/cart/add", {fruit_id:$(this).attr("fruit_id"), render_to:$(this).attr("render_to")},
				function (data) {
					handleCartData(data);
				}
			);
		}
	);
	
	$(".del").click(
		function () {
			$.get("/cart/del", {fruit_id:$(this).attr("fruit_id"), render_to:$(this).attr("render_to")},
				function (data) {
					handleCartData(data);
				}
			);
		}
	);

	$(".remove").click(
		function () {
			$.get("/cart/remove", {fruit_id:$(this).attr("fruit_id"), render_to:$(this).attr("render_to")},
				function (data) {
					handleCartData(data);
				}
			);
		}
	);
	
	$(".checkout_remove").click(
		function () {
			$.get("/cart/remove", {fruit_id:$(this).attr("fruit_id"), render_to:$(this).attr("render_to")},
				function (data) {
					handleCartData(data);
				}
			);
		}
	);
	
	$(".clear").click(
		function () {
			$.get("/cart/clear", {render_to:$(this).attr("render_to")},
				function (data) {
					$(".cart").html(data);
					$(".small_cart").css("top", $(window).scrollTop());
					setTimeout('$(".small_cart_body").slideUp()', 1000);
					bindEvent();
				});
		}
	);
}

function handleCartData(data)
{
	$(".cart").html(data);
	$(".cart").show();
	
	$(".small_cart").css("top", $(window).scrollTop());
	//$("#checkout_cart").html(data);
	//$("#checkout_cart").show();
	
	bindEvent();
}