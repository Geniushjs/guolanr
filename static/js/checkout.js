function check_mobile( s ){ 
	var regu =/^[1][3,5,8][0-9]{9}$/; 
	var re = new RegExp(regu); 
	if (re.test(s)) { 
		return true; 
	}else{ 
		return false; 
	}	 
}
 
function checkform(userform)
{
	if (check_mobile(userform.mobile.value) == false) {
		userform.mobile.focus();
		alert("请输入正确的手机号");
		return false;
	}
	
	if (userform.address.value == "") {
		userform.address.focus();
		alert("请输入您的地址");
		return false;
	}

	$(".submit").removeClass("submit_order");
	$(".submit").removeClass("submit_userinfo");
	$(".submit").addClass("submitting");
	userform.submit.disabled = true;
	
	return true;
}
