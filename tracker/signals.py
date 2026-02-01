from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EarnPreset, UserSettings

User = get_user_model()

DEFAULT_PRESETS = [
    ("Dog walk before phone", "Base", 5, "dog.svg", 10),
    ("Morning routine complete", "Base", 3, "default.svg", 20),
    ("No scrolling first 60 min", "Base", 5, "default.svg", 30),
    ("Workout (30–45 min)", "Health", 12, "workout.svg", 40),
    ("Workout (60+ min)", "Health", 15, "workout.svg", 50),
    ("Focus block", "Career", 10, "focus.svg", 60),
    ("Job application submitted", "Career", 15, "job.svg", 70),
    ("Website work", "Career", 10, "default.svg", 80),
    ("Log spending", "Budget", 5, "budget.svg", 90),
    ("No impulse spending", "Budget", 5, "budget.svg", 100),
    ("Budget review", "Budget", 10, "budget.svg", 110),
    ("Savings transfer", "Budget", 15, "budget.svg", 120),
]


@receiver(post_save, sender=User)
def create_user_defaults(sender, instance, created, **kwargs):
    if not created:
        return
    UserSettings.objects.get_or_create(user=instance)
    if not EarnPreset.objects.filter(user=instance).exists():
        presets = [
            EarnPreset(
                user=instance,
                label=label,
                category=category,
                ap=ap,
                icon_key=icon_key,
                sort_order=sort_order,
            )
            for label, category, ap, icon_key, sort_order in DEFAULT_PRESETS
        ]
        EarnPreset.objects.bulk_create(presets)
