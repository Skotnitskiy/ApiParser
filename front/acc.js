$(document).ready(function() {
	$('#accordeon .acc-head').on('click', f_acc);

	//reports include
	$("#newstories").load("newstories.html");
	$("#showstories").load("showstories.html");
    $("#askstories").load("askstories.html");
	$("#jobstories").load("jobstories.html");
	$("#date").load("date.html");
});

function f_acc(){
  $('#accordeon .acc-body').not($(this).next()).slideUp(500);
    $(this).next().slideToggle(500);
}