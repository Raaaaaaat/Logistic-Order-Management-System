function myAlert(info)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>Warning\
				</div>\
				<div class='modal-body' id = 'modal_body_multi'>\
					<h1>"+info+"</h1>\
				</div>\
				<div class='modal-footer'>\
					<button type='button' class='btn btn-default' data-dismiss='modal'>确认\
					</button>\
				</div>\
			</div>\
	    </div>";
    $('#popModal').html(modalHtml);
    $('#popModal').modal();
}

function myConfirm(info,call_back_func)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>\
				    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\
				    <h4 class=\"modal-title\">确认</h4>\
				</div>\
				<div class='modal-body' id = 'modal_body_multi'>\
					<p>"+info+"</p>\
				</div>\
				<div class='modal-footer'>\
					<button type='button' class='btn btn-default' data-dismiss='modal'>取消</button>\
					<button type='button' class='btn btn-default' id='modal_click' data-dismiss='modal'>确认</button>\
				</div>\
			</div>\
	    </div>";
    $('#popModal').html(modalHtml);
    $('#modal_click').click(call_back_func);
    $('#popModal').modal();
}
