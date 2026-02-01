from .base import *  # noqa: F403
import dj_database_url

DEBUG = os.environ.get("DEBUG", "False").lower() in {"true", "1", "yes"}

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        ssl_require=True,
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # noqa: F405
    )
}

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host.strip()
] or [".onrender.com"]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
] or ["https://*.onrender.com"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
