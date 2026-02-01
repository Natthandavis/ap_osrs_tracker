# Generated manually for initial schema
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Quest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not started"),
                            ("active", "Active"),
                            ("completed", "Completed"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                ("minutes_logged", models.IntegerField(default=0)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "unique_together": {("user", "name")},
            },
        ),
        migrations.CreateModel(
            name="UserSettings",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("saturday_lock_enabled", models.BooleanField(default=False)),
                ("saturday_unlock_time", models.TimeField(default="10:30")),
                ("daily_earn_cap", models.PositiveIntegerField(default=65)),
                ("unlock_net_ap_today", models.PositiveIntegerField(default=15)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="EarnPreset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=120)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Base", "Base"),
                            ("Career", "Career"),
                            ("Health", "Health"),
                            ("Budget", "Budget"),
                        ],
                        max_length=20,
                    ),
                ),
                ("ap", models.PositiveIntegerField()),
                ("icon_key", models.CharField(blank=True, max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["sort_order", "label"],
                "unique_together": {("user", "label")},
            },
        ),
        migrations.CreateModel(
            name="Entry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("earn", "Earn"),
                            ("spend", "Spend"),
                            ("quest_complete", "Quest complete"),
                        ],
                        max_length=20,
                    ),
                ),
                ("label", models.CharField(max_length=140)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Base", "Base"),
                            ("Career", "Career"),
                            ("Health", "Health"),
                            ("Budget", "Budget"),
                            ("OSRS", "OSRS"),
                        ],
                        max_length=20,
                    ),
                ),
                ("ap", models.PositiveIntegerField()),
                ("minutes", models.PositiveIntegerField(default=0)),
                (
                    "quest",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="tracker.quest",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.AddIndex(
            model_name="entry",
            index=models.Index(fields=["user", "timestamp"], name="tracker_ent_user_id_9a53d6_idx"),
        ),
    ]
