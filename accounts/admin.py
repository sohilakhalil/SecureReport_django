from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'role', 'status', 'is_staff', 'is_active')  # شيلنا username
    list_filter = ('role', 'status', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('role', 'status')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'status', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)  # البحث يبقى بالإيميل
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
