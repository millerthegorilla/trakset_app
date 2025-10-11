from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.core.validators import RegexValidator
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_softdelete.models import SoftDeleteManager
from django_softdelete.models import SoftDeleteModel


class CustomUserManager(UserManager, SoftDeleteManager):
    pass


class User(SoftDeleteModel, AbstractUser):
    """
    Default custom user model for trakset_app.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. \
                 Up to 15 digits allowed.",
    )
    phone_number = CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
    )  # Validators should be a list

    objects = CustomUserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self) -> str:
        """String representation of the user."""
        return self.username
