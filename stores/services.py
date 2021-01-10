from stores.exceptions import UserNotInStoreException
from stores.models import Store


class StoreManagement:
    model = Store

    def __int__(self):
        pass

    @classmethod
    def get_queryset(cls):
        return cls.model.objects.all()

    @classmethod
    def check_store_by_name(cls, store_name):
        stores = cls.get_queryset().filter(store_name=store_name)
        if stores.exists():
            return stores[0]
        return None

    @classmethod
    def valid_store_user(cls, store_name, user):
        # import pdb;pdb.set_trace()
        store = cls.check_store_by_name(store_name)
        if store is None or store.id != user.store.id:
            raise UserNotInStoreException()
        return store
