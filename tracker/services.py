from datetime import datetime, time, timedelta

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import Entry, Quest

SPEND_COSTS = {10: 30, 18: 60, 30: 120}


def get_today_range(tz):
    now = timezone.localtime(timezone.now(), tz)
    start = datetime.combine(now.date(), time.min)
    end = start + timedelta(days=1)
    return timezone.make_aware(start, tz), timezone.make_aware(end, tz)


def get_week_range(tz, monday_start=True):
    now = timezone.localtime(timezone.now(), tz)
    weekday = now.weekday() if monday_start else (now.weekday() + 1) % 7
    start_date = now.date() - timedelta(days=weekday)
    start = datetime.combine(start_date, time.min)
    end = start + timedelta(days=7)
    return timezone.make_aware(start, tz), timezone.make_aware(end, tz)


def _sum_entries(entries, kind):
    return entries.filter(kind=kind).aggregate(total=Sum("ap"))["total"] or 0


def today_totals(user):
    tz = timezone.get_current_timezone()
    start, end = get_today_range(tz)
    entries = Entry.objects.filter(user=user, timestamp__gte=start, timestamp__lt=end)
    earned = _sum_entries(entries, Entry.Kind.EARN)
    spent = _sum_entries(entries, Entry.Kind.SPEND)
    return {"earned": earned, "spent": spent, "net": earned - spent}


def week_totals(user):
    tz = timezone.get_current_timezone()
    start, end = get_week_range(tz)
    entries = Entry.objects.filter(user=user, timestamp__gte=start, timestamp__lt=end)
    earned = _sum_entries(entries, Entry.Kind.EARN)
    spent = _sum_entries(entries, Entry.Kind.SPEND)
    return {"earned": earned, "spent": spent, "net": earned - spent}


def balance(user):
    earned = Entry.objects.filter(user=user, kind=Entry.Kind.EARN).aggregate(total=Sum("ap"))["total"] or 0
    spent = Entry.objects.filter(user=user, kind=Entry.Kind.SPEND).aggregate(total=Sum("ap"))["total"] or 0
    return earned - spent


def get_active_quest(user):
    return Quest.objects.filter(user=user, status=Quest.Status.ACTIVE).first()


def set_active_quest(user, quest_id):
    quest = Quest.objects.filter(user=user, id=quest_id).first()
    if not quest:
        raise ValueError("Quest not found.")
    if quest.status == Quest.Status.COMPLETED:
        raise ValueError("Completed quests cannot be set active.")
    Quest.objects.filter(user=user, status=Quest.Status.ACTIVE).update(status=Quest.Status.NOT_STARTED)
    quest.status = Quest.Status.ACTIVE
    quest.save(update_fields=["status", "updated_at"])
    return quest


def can_earn(user, ap_to_add):
    settings = user.usersettings
    totals = today_totals(user)
    return totals["earned"] + ap_to_add <= settings.daily_earn_cap


def is_osrs_unlocked_today(user):
    settings = user.usersettings
    totals = today_totals(user)
    return totals["net"] >= settings.unlock_net_ap_today


def is_saturday_locked_now(user, now=None):
    settings = user.usersettings
    if not settings.saturday_lock_enabled:
        return False
    now = now or timezone.localtime()
    if now.weekday() != 5:
        return False
    unlock_time = settings.saturday_unlock_time
    return now.time() < unlock_time


def spend_ap(user, cost):
    if cost not in SPEND_COSTS:
        raise ValueError("Spend amount must be 10, 18, or 30 AP.")
    quest = get_active_quest(user)
    if not quest:
        raise ValueError("Select an active quest before spending AP.")
    if not is_osrs_unlocked_today(user):
        raise ValueError("OSRS spending locked until your net AP today meets the unlock threshold.")
    if is_saturday_locked_now(user):
        raise ValueError("OSRS spending is locked until the Saturday unlock time.")
    if balance(user) < cost:
        raise ValueError("Insufficient AP balance.")
    minutes = SPEND_COSTS[cost]
    with transaction.atomic():
        Entry.objects.create(
            user=user,
            kind=Entry.Kind.SPEND,
            label="Quest session",
            category=Entry.Category.OSRS,
            ap=cost,
            quest=quest,
            minutes=minutes,
        )
        quest.minutes_logged += minutes
        quest.save(update_fields=["minutes_logged", "updated_at"])
    return quest


def earn_from_preset(user, preset_id):
    preset = user.earnpreset_set.filter(id=preset_id).first()
    if not preset:
        raise ValueError("Preset not found.")
    if not can_earn(user, preset.ap):
        raise ValueError("Daily AP cap reached.")
    Entry.objects.create(
        user=user,
        kind=Entry.Kind.EARN,
        label=preset.label,
        category=preset.category,
        ap=preset.ap,
    )


def create_custom_earn(user, label, category, ap):
    if not can_earn(user, ap):
        raise ValueError("Daily AP cap reached.")
    Entry.objects.create(
        user=user,
        kind=Entry.Kind.EARN,
        label=label,
        category=category,
        ap=ap,
    )


def undo_last_spend(user):
    last_spend = Entry.objects.filter(user=user, kind=Entry.Kind.SPEND).order_by("-timestamp").first()
    if not last_spend:
        raise ValueError("No spend entries to undo.")
    quest = last_spend.quest
    minutes = last_spend.minutes
    with transaction.atomic():
        last_spend.delete()
        if quest:
            quest.minutes_logged = max(0, quest.minutes_logged - minutes)
            quest.save(update_fields=["minutes_logged", "updated_at"])


def mark_quest_complete(user, quest_id):
    quest = Quest.objects.filter(user=user, id=quest_id).first()
    if not quest:
        raise ValueError("Quest not found.")
    quest.status = Quest.Status.COMPLETED
    quest.save(update_fields=["status", "updated_at"])
    Entry.objects.create(
        user=user,
        kind=Entry.Kind.QUEST_COMPLETE,
        label="Quest completed",
        category=Entry.Category.OSRS,
        ap=0,
        quest=quest,
        minutes=0,
    )
    return quest
