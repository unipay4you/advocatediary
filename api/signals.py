from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

# Optional: models to ignore
IGNORED_MODELS = [
    "django.contrib.sessions.models.Session",
    "django.contrib.contenttypes.models.ContentType"
]

@receiver(post_save)
@receiver(post_delete)
def mark_model_changed(sender, **kwargs):
    model_path = f"{sender.__module__}.{sender.__name__}"
    if model_path in IGNORED_MODELS:
        return

    cache_key = f"model_changed:{sender.__name__}"
    cache.set(cache_key, True)
