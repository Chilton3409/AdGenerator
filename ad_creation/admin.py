from django.contrib import admin
from .models import Advertisement

from django.contrib.auth.admin import UserAdmin
from .models import User
UserAdmin.fieldsets = (
    (None, {'fields': ('username', 'password')}),
    ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
    ('Permissions', {'fields': ('subscription_status','stripe_subscription_id','stripe_customer_id','is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    ('Important dates', {'fields': ('last_login',)}),
)
admin.site.register(User, UserAdmin)
admin.site.register(Advertisement)