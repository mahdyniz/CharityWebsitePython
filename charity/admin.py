from django.contrib import admin
from .models import Category, CharityCase, Donation, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    actions = ['delete_selected']

@admin.register(CharityCase)
class CharityCaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'target_amount', 'current_amount', 'status', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('current_amount', 'created_at')
    actions = ['delete_selected', 'deactivate_cases', 'activate_cases']
    
    def deactivate_cases(self, request, queryset):
        queryset.update(status=False)
    deactivate_cases.short_description = "Deactivate selected cases"
    
    def activate_cases(self, request, queryset):
        queryset.update(status=True)
    activate_cases.short_description = "Activate selected cases"

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'case', 'amount', 'created_at')
    list_filter = ('case', 'created_at')
    search_fields = ('user__username', 'case__title', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    actions = ['delete_selected']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    date_hierarchy = 'created_at'
