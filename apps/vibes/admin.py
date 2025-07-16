from django.contrib import admin
from .models import Vibe


@admin.register(Vibe)
class VibeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "mood_bucket",
        "mood_slider",
        "is_active",
        'status',
        "start_time",
        "end_time",
        "created_at",
    )
    list_filter = (
        "mood_bucket",
        "is_active",
        'status',
        ("start_time", admin.DateFieldListFilter),
        ("end_time", admin.DateFieldListFilter),
    )
    search_fields = (
        "user__username",
        "mood_text",
        "address",
    )
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "start_time", "end_time")

    fieldsets = (
        ("Vibe Details", {
            "fields": (
                "user",
                "mood_bucket",
                "mood_slider",
                "mood_text",
            )
        }),
        ("Location", {
            "fields": (
                ("latitude", "longitude"),
                "address",
            )
        }),
        ("Timer", {
            "fields": (
                "timer_seconds",
                ("start_time", "end_time"),
            )
        }),
        ("Meta", {
            "fields": (
                "status",
                "is_active",
                "created_at",
            )
        }),
    )

    # for performance – avoids  N + 1 queries in admin list view
    list_select_related = ("user",)
