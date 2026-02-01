from django import forms

from .models import EarnPreset, Quest, UserSettings


class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "New quest name"}),
        }


class PresetForm(forms.ModelForm):
    class Meta:
        model = EarnPreset
        fields = ("label", "category", "ap", "icon_key")
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": "Preset label"}),
            "icon_key": forms.TextInput(attrs={"placeholder": "icon filename (optional)"}),
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = (
            "saturday_lock_enabled",
            "saturday_unlock_time",
            "daily_earn_cap",
            "unlock_net_ap_today",
        )
        widgets = {
            "saturday_unlock_time": forms.TimeInput(attrs={"type": "time"}),
        }
