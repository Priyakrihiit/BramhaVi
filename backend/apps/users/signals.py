"""
User Accounts Event Signals - BrahmaVidya Galaxy
Purpose: Handles systemic hooks such as auto-provisioning wallets and logging registration milestones.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def on_user_registered(sender, instance, created, **kwargs) -> None:
    """
    Triggers automatically when a new User record is written.
    - Creates a digital payment wallet for tracking ledgers.
    - Dispatches verification email background task queue elements.
    """
    if created:
        # TODO: Trigger wallet initialization service (apps.wallets.services)
        # TODO: Queue async verification email dispatcher (apps.users.tasks)
        pass
