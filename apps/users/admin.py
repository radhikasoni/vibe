from django.contrib import admin
from apps.users.models import Profile

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_first_name', 'get_last_name', 'get_email', 'role',
        'country', 'state', 'city', 'address', 'avatar', 'apple_id', 'is_apple_user', 'status',
    )
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'user__email',
        'country', 'city'
    )
    list_filter = ('role', 'country', 'city')

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'