function validateCustomerForm() {
	$.validator.addMethod("checkEmpty", function(value, element) {
        return !(value.replaceAll(" ", "") == "");
    });

	$("#customer-form").validate({
		rules: {
			customer_name: {
				required: true,
				checkEmpty: true
			}
		},
		messages: {
			customer_name: {
				required: "Cần nhập tên khách hàng",
				checkEmpty: "Tên không hợp lệ"
			}
		},
		errorElement: 'span',
        errorPlacement: function (error, element) {
            error.addClass('invalid-feedback');
            element.closest('.form-group .col-md-8').append(error);
        },
        highlight: function (element, errorClass, validClass) {
            $(element).addClass('is-invalid');
        },
        unhighlight: function (element, errorClass, validClass) {
            $(element).removeClass('is-invalid');
        }
	});

	$("#customer-form").submit(function(e) {
		e.preventDefault();
		var form = $(this);

		if (!form.valid()) return false;

		var formData = new FormData(form[0]);
		var url = form.attr("action");

		$.ajax({
			url: url,
			type: "POST",
			enctype: 'multipart/form-data',
			data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data['status'] == "success") {
                    successNotification({
                        title: "Thêm thành công"
                    });
                    $("#add-customer-modal").modal('hide');
                    form[0].reset();
                    showCustomer(data.data);
                } else {
                    data.data.forEach(item => {
                        $(`#${item.id}`).addClass("is-invalid");
                        errorNotification({
                            title: "Lỗi!",
                            message: item.error,
                        });
                    });
                }
            }
		})
	});
}

function showCustomer(customer) {
	$(".customer-show #customer-name").html(customer.name);
	$(".customer-show #customer-name").attr("cid", customer.id);
	$(".sell-right .header-search").fadeOut(0);
	$(".customer-show").fadeIn(0);
}

function hideCustomer() {
	$(".sell-right .header-search input").val("");
	$(".sell-right .header-search").fadeIn(0);
	$(".customer-show").fadeOut(0);
	$(".customer-show #customer-name").html("");
	$(".customer-show #customer-name").attr("cid", "");
}