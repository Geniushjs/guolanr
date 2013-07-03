function checkform(form)
{
	if (form.total.value == "") { 
		form.total.focus();
		alert("请输入实收价格");
		return false;
	}
	
	for (var i = 0; i < form.total.value.length; i++)
		if ((form.total.value.charAt(i) < '0' || form.total.value.charAt(i) > '9') &&
				form.total.value.charAt(i) != '.')
		{
			form.total.focus();
			alert("请输入正确的实收价格");
			return false;
		}

	if (form.general.value != "1" && form.remark.value == "")
	{
		form.remark.focus();
		alert("请您反馈相关的不满意信息，帮助我们改善服务质量");
		return false;
	}
		
	return true;  
}