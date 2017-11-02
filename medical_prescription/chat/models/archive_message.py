from django.db import models
from user.models import User
# from chat.models import Response
from chat import constants


class ArchiveMessage(models.Model):
    """
    Create a Message model in database.
    """

    archive_user_from = models.ForeignKey(User, related_name="archive_user_from")
    archive_user_to = models.ForeignKey(User, related_name="archive_user_to")

    subject = models.CharField(max_length=constants.MAX_LENGTH_TEXT_SUBJECT)

    date = models.DateField(auto_now=True)

    # List of response in Message.
    # messages = models.ManyToManyField(Response, default=None)
