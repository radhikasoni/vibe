from django.db import models
from django.conf import settings
from django.utils import timezone as tz

class Vibe(models.Model):
    MOOD_BUCKETS = [
        ('lighthearted', 'Lighthearted'),
        ('up_for_anything', 'Up for Anything'),
        ('deep', 'Deep Conversation'),
    ]

    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vibes')
    mood_bucket   = models.CharField(max_length=20, choices=MOOD_BUCKETS)
    mood_slider   = models.FloatField(help_text="0.0 → 1.0 position of slider")  # redundant but nice for analytics
    mood_text     = models.CharField(max_length=150)                             # e.g. tooltip message

    latitude = models.DecimalField(max_digits=17, decimal_places=14)
    longitude = models.DecimalField(max_digits=17, decimal_places=14)
    address       = models.CharField(max_length=255, blank=True)

    timer_seconds = models.PositiveIntegerField()                                 # total duration
    start_time    = models.DateTimeField(default=tz.now)
    end_time      = models.DateTimeField()

    created_at    = models.DateTimeField(auto_now_add=True)

    is_active     = models.BooleanField(default=True)

    def __str__(self):
        return f"Vibe({self.user.username}, {self.mood_bucket}, active={self.is_active})"
