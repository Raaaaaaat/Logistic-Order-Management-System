function myAlert(info)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>Warning\
				</div>\
				<div class='modal-body'>\
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
				<div class='modal-body'>\
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

function myShowTableInfo(title, info)
{
    var modalHtml = "\
		<div class='modal-dialog modal-lg'>\
			<div class='modal-content'>\
				<div class='modal-header'>"+title+"\
				</div>\
				<div class='modal-body'>\
					"+info+"\
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

function myInputInvoice(call_back_func)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>\
				    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\
				    <h4 class=\"modal-title\">请输入票号</h4>\
				</div>\
				<div class='modal-body'>\
					<p>票号： </p>\
					<input type='text' id='modal_input'>\
					<div class='checkbox'>\
                        <label>\
                            <input type='checkbox' id='modal_checkbox'>\
                        </label> 不出票\
                    </div>\
                    <div class='checkbox'>\
                        <label>\
                            <input type='checkbox' id='modal_clear_checkbox'>\
                        </label> 清空记录\
                    </div>\
				</div>\
				<div class='modal-footer'>\
					<button type='button' class='btn btn-default' data-dismiss='modal'>取消</button>\
					<button type='button' class='btn btn-default' id='modal_click' data-dismiss='modal'>确认</button>\
				</div>\
			</div>\
	    </div>";
    $('#popModal').html(modalHtml);
    $('#modal_checkbox').change(function(){
        if($(this).prop('checked')){
            $("#modal_input").val("不出票");
            $("#modal_input").attr('disabled', true);
        }
        else{
            $("#modal_input").val("");
            $("#modal_input").removeAttr('disabled');
        }
    });
    $('#modal_clear_checkbox').change(function(){
        if($(this).prop('checked')){
            $("#modal_input").val("清空");
            $("#modal_input").attr('disabled', true);
            $('#modal_checkbox').attr('disabled', true);
        }
        else{
            $("#modal_input").val("");
            $("#modal_input").removeAttr('disabled');
            $('#modal_checkbox').removeAttr('disabled');
        }
    });
    $('#modal_click').click(call_back_func);
    $('#popModal').modal();
}

function myInputPaid(call_back_func)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>\
				    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\
				    <h4 class=\"modal-title\">请输入已收金额</h4>\
				</div>\
				<div class='modal-body'>\
				<div class=\"col-sm-12\">\
                    <div class='input-group'>\
                        <div class='radio' style='display: inline-block'>\
                            <label>\
                                <input type=\"radio\" name=\"paid_type\" checked=\"true\" value=0>\
                                现金\
                            </label>\
                        </div>\
                        <div class=\"radio\" style=\"display: inline-block\">\
                            <label>\
                                <input type=\"radio\" name=\"paid_type\" value=1>\
                                油卡\
                            </label>\
                        </div>\
                    </div>\
                </div>\
					<p>金额： </p>\
					<input type='text' id='modal_input'>\
				</div>\
				<div class='modal-footer'>\
					<button type='button' class='btn btn-default' data-dismiss='modal'>取消</button>\
					<button type='button' class='btn btn-default' id='modal_click' data-dismiss='modal'>确认</button>\
				</div>\
			</div>\
	    </div>";
    $('#popModal').html(modalHtml);
    $('#modal_checkbox').change(function(){
        if($(this).prop('checked')){
            $("#modal_input").val("不出票");
            $("#modal_input").attr('disabled', true);
        }
        else{
            $("#modal_input").val("");
            $("#modal_input").removeAttr('disabled');
        }
    });
    $('#modal_click').click(call_back_func);
    $('#popModal').modal();
}

function myInputContent(title, note, call_back_func)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>\
				    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\
				    <h4 class=\"modal-title\">"+title+"</h4>\
				</div>\
				<div class='modal-body'>\
					<p>"+note+"</p>\
					<input type='text' id='modal_input'>\
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

function myInputTwoContent(title, note1, note2, default1, default2, call_back_func)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>\
				    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\
				    <h4 class=\"modal-title\">"+title+"</h4>\
				</div>\
				<div class='modal-body'>\
					<p>"+note1+"</p>\
					<input type='text' id='modal_input1' value='"+default1+"'>\
					<p>"+note2+"</p>\
					<input type='text' id='modal_input2' value='"+default2+"'>\
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

function myInputDateAndContent(title, note1, note2, default1, default2, call_back_func)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>\
				    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\
				    <h4 class=\"modal-title\">"+title+"</h4>\
				</div>\
				<div class='modal-body'>\
					<p>"+note1+"</p>\
					<input type='text' id='modal_input1' value='"+default1+"'>\
					<p>"+note2+"</p>\
					<input type='text' id='modal_input2' value='"+default2+"'>\
				</div>\
				<div class='modal-footer'>\
					<button type='button' class='btn btn-default' data-dismiss='modal'>取消</button>\
					<button type='button' class='btn btn-default' id='modal_click' data-dismiss='modal'>确认</button>\
				</div>\
			</div>\
	    </div>";
    $('#popModal').html(modalHtml);
    $('#modal_input1').datepicker({
                weekStart:1, //1代表从一周周一开始，0代表从周天开始
                autoclose:true,
                clearBtn:true,
                zIndexOffset: 10000,
            });
    $('#modal_click').click(call_back_func);
    $('#popModal').modal();
}

function myInputDate(title, note, default1, call_back_func)
{
    var modalHtml = "\
		<div class='modal-dialog'>\
			<div class='modal-content'>\
				<div class='modal-header'>\
				    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\
				    <h4 class=\"modal-title\">"+title+"</h4>\
				</div>\
				<div class='modal-body'>\
					<p>"+note+"</p>\
					<input type='text' id='modal_input' value='"+default1+"'>\
				</div>\
				<div class='modal-footer'>\
					<button type='button' class='btn btn-default' data-dismiss='modal'>取消</button>\
					<button type='button' class='btn btn-default' id='modal_click' data-dismiss='modal'>确认</button>\
				</div>\
			</div>\
	    </div>";
    $('#popModal').html(modalHtml);
    $('#modal_input').datepicker({
                weekStart:1, //1代表从一周周一开始，0代表从周天开始
                autoclose:true,
                clearBtn:true,
                zIndexOffset: 10000,
                format: 'yyyy-mm-dd',
            });
    $('#modal_click').click(call_back_func);
    $('#popModal').modal();
}