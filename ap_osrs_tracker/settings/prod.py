from .base import *  # noqa: F403
import dj_database_url

DEBUG = os.environ.get("DEBUG", "False").lower() in {"true", "1", "yes"}

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
