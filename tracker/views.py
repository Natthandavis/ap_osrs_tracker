from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PresetForm, QuestForm, SettingsForm, SignupForm
from .models import EarnPreset, Entry, Quest
from .services import (
    SPEND_COSTS,
    balance,
    earn_from_preset,
    get_active_quest,
    is_osrs_unlocked_today,
    is_saturday_locked_now,
    mark_quest_complete,
    set_active_quest,
    spend_ap,
    today_totals,
    undo_last_spend,
)


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to AP → OSRS Tracker.")
            return redirect("dashboard")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    active_quest = get_active_quest(user)
    presets = EarnPreset.objects.filter(user=user, is_active=True).order_by("sort_order", "label")
    entries = Entry.objects.filter(user=user).select_related("quest")[:50]

    totals = today_totals(user)
    current_balance = balance(user)
    unlocked_today = is_osrs_unlocked_today(user)
    saturday_locked = is_saturday_locked_now(user)

    quests = Quest.objects.filter(user=user)
    total_quests = quests.count()
    completed_quests = quests.filter(status=Quest.Status.COMPLETED).count()

    spend_options = []
    for cost, minutes in SPEND_COSTS.items():
        enabled = True
        reason = ""
        if not active_quest:
            enabled = False
            reason = "Select an active quest"
        elif saturday_locked:
            enabled = False
            unlock_time = user.usersettings.saturday_unlock_time.strftime("%H:%M")
            reason = f"Locked until {unlock_time}"
        elif not unlocked_today:
            enabled = False
            reason = "Net AP today below unlock"
        elif current_balance < cost:
            enabled = False
            reason = "Insufficient balance"
        spend_options.append({"cost": cost, "minutes": minutes, "enabled": enabled, "reason": reason})

    context = {
        "active_quest": active_quest,
        "presets": presets,
        "entries": entries,
        "today_earned": totals["earned"],
        "today_spent": totals["spent"],
        "today_net": totals["net"],
        "balance": current_balance,
        "unlocked_today": unlocked_today and not saturday_locked,
        "saturday_locked": saturday_locked,
        "quests": quests,
        "total_quests": total_quests,
        "completed_quests": completed_quests,
        "spend_options": spend_options,
        "now": timezone.localtime(),
    }
    return render(request, "tracker/dashboard.html", context)


@login_required
def earn_preset(request, preset_id):
    if request.method != "POST":
        return redirect("dashboard")
    try:
        earn_from_preset(request.user, preset_id)
        messages.success(request, "AP earned.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("dashboard")


@login_required
def spend(request, cost):
    if request.method != "POST":
        return redirect("dashboard")
    try:
        spend_ap(request.user, int(cost))
        messages.success(request, "Quest session logged.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("dashboard")


@login_required
def undo_spend(request):
    if request.method != "POST":
        return redirect("dashboard")
    try:
        undo_last_spend(request.user)
        messages.success(request, "Last spend entry removed.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("dashboard")


@login_required
def quests(request):
    quests_qs = Quest.objects.filter(user=request.user).order_by("name")
    if request.method == "POST":
        form = QuestForm(request.POST)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.user = request.user
            try:
                quest.save()
                messages.success(request, "Quest added.")
                return redirect("quests")
            except Exception:
                messages.error(request, "Quest name must be unique.")
    else:
        form = QuestForm()
    return render(request, "tracker/quests.html", {"quests": quests_qs, "form": form})


@login_required
def set_active(request, quest_id):
    if request.method != "POST":
        return redirect("dashboard")
    try:
        set_active_quest(request.user, quest_id)
        messages.success(request, "Active quest updated.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("dashboard")


@login_required
def complete_quest(request, quest_id):
    if request.method != "POST":
        return redirect("dashboard")
    try:
        mark_quest_complete(request.user, quest_id)
        messages.success(request, "Quest marked complete.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("dashboard")


@login_required
def update_notes(request, quest_id):
    if request.method != "POST":
        return redirect("dashboard")
    quest = get_object_or_404(Quest, user=request.user, id=quest_id)
    quest.notes = request.POST.get("notes", "")
    quest.save(update_fields=["notes", "updated_at"])
    messages.success(request, "Quest notes updated.")
    return redirect("dashboard")


@login_required
def presets(request):
    presets_qs = EarnPreset.objects.filter(user=request.user).order_by("sort_order", "label")
    if request.method == "POST":
        form = PresetForm(request.POST)
        if form.is_valid():
            preset = form.save(commit=False)
            preset.user = request.user
            preset.save()
            messages.success(request, "Preset created.")
            return redirect("presets")
    else:
        form = PresetForm()
    return render(request, "tracker/presets.html", {"presets": presets_qs, "form": form})


@login_required
def toggle_preset(request, preset_id):
    if request.method != "POST":
        return redirect("presets")
    preset = get_object_or_404(EarnPreset, user=request.user, id=preset_id)
    preset.is_active = not preset.is_active
    preset.save(update_fields=["is_active", "updated_at"])
    messages.success(request, "Preset updated.")
    return redirect("presets")


@login_required
def delete_preset(request, preset_id):
    if request.method != "POST":
        return redirect("presets")
    preset = get_object_or_404(EarnPreset, user=request.user, id=preset_id)
    preset.delete()
    messages.success(request, "Preset deleted.")
    return redirect("presets")


@login_required
def move_preset(request, preset_id, direction):
    if request.method != "POST":
        return redirect("presets")
    preset = get_object_or_404(EarnPreset, user=request.user, id=preset_id)
    offset = -1 if direction == "up" else 1
    swap = (
        EarnPreset.objects.filter(user=request.user, sort_order=preset.sort_order + offset)
        .order_by("sort_order")
        .first()
    )
    if swap:
        preset.sort_order, swap.sort_order = swap.sort_order, preset.sort_order
        preset.save(update_fields=["sort_order", "updated_at"])
        swap.save(update_fields=["sort_order", "updated_at"])
    return redirect("presets")


@login_required
def settings_view(request):
    settings_obj = request.user.usersettings
    if request.method == "POST":
        form = SettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated.")
            return redirect("settings")
    else:
        form = SettingsForm(instance=settings_obj)
    return render(request, "tracker/settings.html", {"form": form})
