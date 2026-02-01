#!/usr/bin/env bash
set -o errexit

DJANGO_SETTINGS_MODULE=ap_osrs_tracker.settings.prod python manage.py migrate
DJANGO_SETTINGS_MODULE=ap_osrs_tracker.settings.prod python manage.py collectstatic --noinput
