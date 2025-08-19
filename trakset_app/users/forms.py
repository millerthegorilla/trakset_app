from allauth.account.forms import SignupForm
from allauth.account.models import EmailAddress
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    def clean(self):
        """
        Override the clean method to ensure that the email field is not saved.
        """
        email = self["email"].value()
        username = self["username"].value()
        if email:
            user = User.global_objects.filter(username=username).first()
            if email != user.email:
                user.email = email
                user.save(update_fields=["email"])
            # Ensure the email address is created or updated
            emailaddress = user.emailaddress_set.first()
            if not emailaddress:
                emailaddress = EmailAddress.objects.create(
                    user=user,
                    email=user.email,
                    primary=True,
                    verified=True,
                )
            if emailaddress.email != user.email:
                emailaddress.email = user.email
                emailaddress.save()
        else:
            # If email is not provided, we raise a validation error
            raise ValidationError(_("Email field cannot be empty."))

    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            raise ValidationError(_("This field is required."))
        try:
            user = User.global_objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            if user.is_deleted:
                # If the user exists, we raise a validation error
                # to prevent duplicate usernames.
                raise ValidationError(
                    _(
                        "This username has already been taken but \
                    the user has been deleted. Please use a different username. \
                    This allows us to retain data about asset transfers",
                    ),
                )
            # If the user exists and is not deleted, we raise a validation error
            raise ValidationError(_("This username has already been taken."))
        return username

    def save(self):
        user = super().save(commit=False)
        user.save()
        return user

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
