from rest_framework import serializers
from django.utils import timezone as tz
from .models import Vibe

class CreateVibeSerializer(serializers.ModelSerializer):
    # client will send these as integers
    hours   = serializers.IntegerField(write_only=True, required=True, min_value=0, max_value=23)
    minutes = serializers.IntegerField(write_only=True, required=True, min_value=0, max_value=59)
    seconds = serializers.IntegerField(write_only=True, required=True, min_value=0, max_value=59)

    class Meta:
        model  = Vibe
        fields = [
            'mood_bucket', 'mood_slider', 'mood_text',
            'latitude', 'longitude', 'address',
            'hours', 'minutes', 'seconds',
        ]

    def validate_mood_slider(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("mood_slider must be between 0 and 1.")
        return value

    def create(self, validated):
        # pop timer fields
        h = validated.pop('hours')
        m = validated.pop('minutes')
        s = validated.pop('seconds')
        total_sec = h * 3600 + m * 60 + s
        if total_sec == 0:
            raise serializers.ValidationError("Timer duration cannot be zero.")

        start = tz.now()
        end   = start + tz.timedelta(seconds=total_sec)

        vibe = Vibe.objects.create(
            user          = self.context['request'].user,
            timer_seconds = total_sec,
            start_time    = start,
            end_time      = end,
            **validated
        )
        return vibe
