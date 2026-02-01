from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("earn/<int:preset_id>/", views.earn_preset, name="earn_preset"),
    path("spend/<int:cost>/", views.spend, name="spend"),
    path("entries/undo-last-spend/", views.undo_spend, name="undo_spend"),
    path("quests/", views.quests, name="quests"),
    path("quests/set-active/<int:quest_id>/", views.set_active, name="set_active"),
    path("quests/complete/<int:quest_id>/", views.complete_quest, name="complete_quest"),
    path("quests/update-notes/<int:quest_id>/", views.update_notes, name="update_notes"),
    path("presets/", views.presets, name="presets"),
    path("presets/<int:preset_id>/toggle/", views.toggle_preset, name="toggle_preset"),
    path("presets/<int:preset_id>/delete/", views.delete_preset, name="delete_preset"),
    path("presets/<int:preset_id>/move-<str:direction>/", views.move_preset, name="move_preset"),
    path("settings/", views.settings_view, name="settings"),
]
