from customers.exceptions import FormInvalidException
from customers.forms import CustomerForm
from elasticsearch_client import es as elasticsearch


class CustomerManagement:
    _form = None
    _instance = None
    _request = None

    def __init__(self, request):
        self._request = request

    def validate_form(self):
        self._form = CustomerForm(self._request.POST, self._request.FILES)
        if self._form.is_valid():
            customer = self._form.save()
            # save to elasticsearch
            extra_data = {}
            if customer.phone_number is not None:
                extra_data.update({"phone_number": customer.phone_number})
            if customer.address is not None:
                extra_data.update({"address": customer.address})
            if customer.email is not None:
                extra_data.update({"email": customer.email})
            elasticsearch.index_customer(customer_id=customer.id,
                                         customer_code=customer.customer_code,
                                         customer_name=customer.customer_name,
                                         group_type=customer.group_type,
                                         **extra_data)
            self._instance = customer
            return self._instance
        else:
            raise FormInvalidException()

    def get_errors(self):
        errors = []
        for field in self._form:
            for error in field.errors:
                errors.append({'id': field.auto_id, 'error': error})
        return errors

    @classmethod
    def search_customer_by_key(cls, key):
        es_result = elasticsearch.search_customer(key)
        return {
            "num_of_results": es_result["hits"]["total"]["value"],
            "list_customers": [hit["_source"] for hit in es_result["hits"]["hits"]]
        }
