function productFormSetUp() {
    // $(".datepicker" ).datepicker({
    //     dateFormat: "yy-mm-dd",
    // });

    $('[data-toggle="tooltip"]').tooltip();

    $("#product-form").validate({
        rules: {
            product_name: {
                required: true,
            },
            category: {
                required: true,
            },
            unit: {
                required: true,
            },
            sell_price: {
                required: true,
            },
            available: {
                required: true,
                min: 0,
            }
        },
        messages: {
            product_name: {
                required: "Cần nhập tên sản phẩm",
            },
            category: {
                required: "Cần lựa chọn nhóm sản phẩm",
            },
            unit: {
                required: "Cần lựa chọn đơn vị bán",
            },
            sell_price: {
                required: "Cần nhập giá bán",
            },
            available: {
                required: "Cần nhập số lượng",
                min: "Số lượng không thể âm",
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
}

function categoryFormSetUp() {
    $("#category-form").validate({
        rules: {
            category_name: {
                required: true,
            }
        },
        messages: {
            category_name: {
                required: "Cần nhập tên nhóm",
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
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function(e) {
            var imgUpload = $(input).parent().children()[1];
            $(imgUpload).attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]); // convert to base64 string
    }
}

function formCallAjax(formId, url, successCallBack, failCallBack) {

    $(formId).submit(function(e) {
        e.preventDefault();
        var form = $(this);

        if (!form.valid()) return false;

        var formData = new FormData(form[0]);
        var url = form.attr('action');

        $.ajax({
            type: 'POST',
            url: url,
            enctype: 'multipart/form-data',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data['status'] == "success") {
                    successCallBack();
                } else {
                    failCallBack(data);
                }
            }
        })
    })
}
