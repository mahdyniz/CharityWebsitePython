from django.contrib import admin
from .models import Category, CharityCase, Donation

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    actions = ['delete_selected']

@admin.register(CharityCase)
class CharityCaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'target_amount', 'current_amount', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('current_amount', 'created_at')
    actions = ['delete_selected', 'deactivate_cases', 'activate_cases']
    
    def deactivate_cases(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_cases.short_description = "Deactivate selected cases"
    
    def activate_cases(self, request, queryset):
        queryset.update(is_active=True)
    activate_cases.short_description = "Activate selected cases"

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'case', 'amount', 'created_at')
    list_filter = ('case', 'created_at')
    search_fields = ('donor_name', 'donor_email', 'message')
    readonly_fields = ('created_at',)
    actions = ['delete_selected']
