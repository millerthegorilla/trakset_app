from celery import shared_task
from django.core.mail import send_mail

from trakset.models import AssetTransfer


@shared_task()
def email_users_on_asset_transfer(asset_transfer_id):
    """Email the list of users that are subscribed to this assset transfer."""
    asset_transfer = AssetTransfer.objects.filter(id=asset_transfer_id).first()
    send_mail(
        "An asset that you are subscribed to has been transferred...",
        "Hey from trakset!",
        "from@webmaster@mindq.co.uk",
        list(asset_transfer.asset.send_user_email_on_transfer.all()),
        html_message=(
            f"<html>Asset Transfer of {asset_transfer.asset.name} has occurred. \
             The current holder is {asset_transfer.to_user.username} \
             whose email address is {asset_transfer.to_user.email}</html>"
        ),
    )
    return "Email sent to users on asset transfer."
