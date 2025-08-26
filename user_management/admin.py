
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserRole

class UserAdmin(BaseUserAdmin):
    # This is for the fields shown when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    # This is for the fields shown when editing an existing user
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)
    
    
    
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display role id and name
    search_fields = ('name',)  # Allow searching by role name
    ordering = ('id',)  # Order by role id
    
class UserRoleAdmin(admin.ModelAdmin):
    # Display id, user's first_name, and role name
    list_display = ('id', 'get_user_first_name', 'role')
    search_fields = ('user__first_name', 'role__name')  # Allows searching by user's first_name and role name
    ordering = ('id',)

    # Custom method to get the first name of the related user
    def get_user_first_name(self, obj):
        return obj.user.first_name
    get_user_first_name.short_description = 'User First Name'

admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(UserRole, UserRoleAdmin)
