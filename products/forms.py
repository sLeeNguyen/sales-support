from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from products.models import Product, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["category_name", "description"]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_category_name(self):
        category_name = self.cleaned_data["category_name"].strip()
        while category_name.find("  ") != -1:
            category_name = category_name.replace("  ", " ")
        if category_name == "":
            raise ValidationError(
                _("Tên nhóm phải chứa ít nhát một chữ cái.")
            )
        if not self.instance.pk:
            if Category.objects.filter(category_name=category_name).exists():
                raise ValidationError(
                    _("Nhóm hàng đã tồn tại")
                )
        return category_name


class ProductForm(forms.ModelForm):
    product_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'title': 'Mã hàng là thông tin duy nhất.',
            'placeholder': 'Mã tự động',
        }),
        required=False,
    )

    class Meta:
        model = Product
        fields = ('product_code', 'barcode', 'product_name', 'description',
                  'cost_price', 'sell_price', 'available', 'unit',
                  'mfg', 'exp', 'category', 'image1', 'image2', 'image3', 'image4', 'image5')
        widgets = {
            'barcode': forms.TextInput(attrs={
                'title': 'Mã vạch thường được cung cấp bởi nhà sản xuất.'
            }),
            'product_name': forms.TextInput(attrs={
                'title': 'Tên hàng là tên của sản phẩm.'
            }),
            'mfg': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
            'exp': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'unit': forms.Select(attrs={
                'title': 'Đơn vị bán của sản phẩm'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        available = cleaned_data.get('available')
        unit = cleaned_data.get('unit')

        # check product's unit and product's available
        # if unit is INT, product's available must be integer
        if unit == Product.UNIT_INT:
            if abs(available - round(available)) > 0.00001:
                msg = _('Số lượng không phù hợp với đơn vị')
                self.add_error('available', msg)
                self.add_error('unit', msg)

        mfg = cleaned_data.get('mfg')
        exp = cleaned_data.get('exp')

        if mfg and exp:
            if mfg > exp:
                msg = _('Ngày sản xuất không thể lớn hơn ngày hết hạn.')
                self.add_error('mfg', msg)
                self.add_error('exp', msg)

        return cleaned_data

    def clean_available(self):
        available = self.cleaned_data['available']
        if available < 0:
            raise ValidationError(
                _('Số lượng không thể âm.')
            )
        return available

    def clean_product_code(self):
        """
        Check product_code exists or not.
        If form action is update then ignore check it
        """
        product_code = self.cleaned_data['product_code']
        if not self.instance.pk:
            if product_code:
                if Product.objects.find_by_code(product_code=product_code).exists():
                    error_msg = "Mã sản phẩm '{}' đã tồn tại".format(product_code)
                    raise ValidationError(_(error_msg))

        return product_code

    def clean_product_name(self):
        """
        Check product_name exists or not.
        If form action is update then ignore check it
        """
        product_name = self.cleaned_data['product_name']
        if not self.instance.pk:
            if product_name:
                if Product.objects.find_by_name(product_name=product_name).exists():
                    error_msg = "Tên sản phẩm '{}' đã tồn tại".format(product_name)
                    raise ValidationError(_(error_msg))

        return product_name

    def save(self, commit=True):
        if not self.instance.product_code:
            self.instance.product_code = Product.objects.gen_default_code()
        super(ProductForm, self).save()
