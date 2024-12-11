from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import Profile
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile automatically when a User is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the associated profile whenever the User is saved."""
    instance.profile.save()
