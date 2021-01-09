import logging

from django.contrib.auth.models import Group, Permission

LOGGER = logging.getLogger(__name__)


def setup():
    LOGGER.info("Setting group permissions")
    create_group_manager()
    create_group_staff()
    LOGGER.info("Created default group and permissions.")


def create_group_manager():
    LOGGER.info("Setting manager group permissions")
    PERMISSIONS = ["Can add coupon", "Can change coupon", "Can delete coupon", "Can view coupon",
                   "Can add customer", "Can change customer", "Can delete customer", "Can view customer",
                   "Can add category", "Can change category", "Can delete category", "Can view category",
                   "Can add product", "Can change product", "Can delete product", "Can view product",
                   "Can add invoice", "Can change invoice", "Can delete invoice", "Can view invoice",
                   "Can add order", "Can change order", "Can delete order", "Can view order",
                   "Can add product item", "Can change product item", "Can delete product item",
                   "Can view product item", "Can add user", "Can change user", "Can delete user", "Can view user"]
    manager_group, created = Group.objects.get_or_create(name='manager')
    for permission_name in PERMISSIONS:
        try:
            model_add_perm = Permission.objects.get(name=permission_name)
        except Permission.DoesNotExist:
            logging.warning("Permission not found with name '{}'.".format(permission_name))
            continue
        manager_group.permissions.add(model_add_perm)
    LOGGER.info("Done setting manager group permissions")


def create_group_staff():
    LOGGER.info("Setting staff group permissions")
    PERMISSIONS = ["Can add customer", "Can change customer", "Can delete customer", "Can view customer",
                   "Can add category", "Can change category", "Can delete category", "Can view category",
                   "Can add product", "Can change product", "Can delete product", "Can view product",
                   "Can add invoice", "Can view invoice", "Can add order", "Can change order", "Can view order",
                   "Can add product item", "Can change product item", "Can delete product item",
                   "Can view product item"]
    staff_group, created = Group.objects.get_or_create(name='staff')
    for permission_name in PERMISSIONS:
        try:
            model_add_perm = Permission.objects.get(name=permission_name)
        except Permission.DoesNotExist:
            logging.warning("Permission not found with name '{}'.".format(permission_name))
            continue
        staff_group.permissions.add(model_add_perm)
    LOGGER.info("Done setting staff group permissions")

