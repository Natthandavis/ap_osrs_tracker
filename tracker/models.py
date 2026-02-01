from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    saturday_lock_enabled = models.BooleanField(default=False)
    saturday_unlock_time = models.TimeField(default="10:30")
    daily_earn_cap = models.PositiveIntegerField(default=65)
    unlock_net_ap_today = models.PositiveIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"


class EarnPreset(models.Model):
    class Category(models.TextChoices):
        BASE = "Base", "Base"
        CAREER = "Career", "Career"
        HEALTH = "Health", "Health"
        BUDGET = "Budget", "Budget"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    label = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices)
    ap = models.PositiveIntegerField()
    icon_key = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "label")
        ordering = ["sort_order", "label"]

    def __str__(self):
        return f"{self.label} ({self.ap} AP)"


class Quest(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    minutes_logged = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class Entry(models.Model):
    class Kind(models.TextChoices):
        EARN = "earn", "Earn"
        SPEND = "spend", "Spend"
        QUEST_COMPLETE = "quest_complete", "Quest complete"

    class Category(models.TextChoices):
        BASE = "Base", "Base"
        CAREER = "Career", "Career"
        HEALTH = "Health", "Health"
        BUDGET = "Budget", "Budget"
        OSRS = "OSRS", "OSRS"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    label = models.CharField(max_length=140)
    category = models.CharField(max_length=20, choices=Category.choices)
    ap = models.PositiveIntegerField()
    quest = models.ForeignKey(Quest, on_delete=models.SET_NULL, null=True, blank=True)
    minutes = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["user", "timestamp"])]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.label} ({self.ap} AP)"
