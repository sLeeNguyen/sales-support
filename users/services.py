from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate

from users.models import User


class AccountAlreadyExistsError(Exception):
    pass


class AccountNotExistsError(Exception):
    pass


class AccountIsBlockedError(Exception):
    pass


class RegisterUserAccount:
    def __int__(self, username, password, display_name,
                first_name=None,
                last_name=None,
                gender=0,
                birthday=None,
                phone_number=None,
               ):
        self._username = username
        self._password = password
        self._display_name = display_name
        self._first_name = first_name
        self._last_name = last_name
        self._gender = gender
        self._birthday = birthday
        self._phone_number = phone_number

    def execute(self, is_manager=False):
        """
        Check username exists? If not, create new user and grant permissions
        via add user to a group.
        If user's role is manager, add to group named Managers, Employees
        otherwise.
        """
        self.valid_data()
        user = User.objects.create_user(
            username=self._username,
            password=self._password,
            **{
                'display_name': self._display_name,
                'first_name': self._first_name,
                'last_name': self._last_name,
                'gender': self._gender,
                'birthday': self._birthday,
                'phone_number': self._phone_number
            }
        )
        if is_manager:
            group = Group.objects.get(name='Managers')
        else:
            group = Group.objects.get(name='Employees')
        group.user_set.add(user)
        return user

    def valid_data(self):
        # It is a public method to allow clients of this object to validate
        # the data even before to execute the use case.
        user_qs = User.objects.find_by_username(username=self._username)
        if user_qs.exists():
            # Raise a meaningful error to be catched by the client
            error_msg = (
                "Tên tài khoản '{}' đã tồn tại. "
                "Hãy thử một tài khoản khác."
            ).format(self._username)
            raise AccountAlreadyExistsError(_(error_msg))

        return True


def user_authentication(username, password, store):
    user = authenticate(username=username, password=password)
    if user is None:
        raise AccountNotExistsError(
            _("Tài khoản '{}' không tồn tại. Hãy thử lại.".format(username))
        )
    if not user.is_active:
        raise AccountIsBlockedError(
            _("Tài khoản của bạn đang bị khoá.")
        )
    if not user.store or user.store.id != store.id:
        raise AccountNotExistsError(
            _("Tài khoản không chính xác.")
        )
    return user
