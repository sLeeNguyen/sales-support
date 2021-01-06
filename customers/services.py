from customers.exceptions import FormInvalidException
from customers.forms import CustomerForm


class CustomerManagement:
    _form = None
    _instance = None
    _request = None

    def __init__(self, request):
        self._request = request

    def validate_form(self):
        self._form = CustomerForm(self._request.POST, self._request.FILES)
        if self._form.is_valid():
            self._instance = self._form.save()
            return self._instance
        else:
            raise FormInvalidException()

    def get_errors(self):
        errors = []
        for field in self._form:
            for error in field.errors:
                errors.append({'id': field.auto_id, 'error': error})
        return errors

    def search_customer_by_key_name(self, key):
        pass
