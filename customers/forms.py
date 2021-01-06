from django import forms

from customers.models import Customer


class CustomerForm(forms.ModelForm):
    customer_code = forms.CharField(
        label="Mã khách hàng",
        widget=forms.TextInput(attrs={
            'title': 'Mã khách hàng là thông tin duy nhất.',
            'placeholder': 'Mã tự động',
        }),
        required=False,
    )

    class Meta:
        model = Customer
        fields = "__all__"
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
            'note': forms.Textarea(attrs={"rows": 4})
        }

