from django.contrib import admin
from .models import (
    Scamtype,
    Scamreports,
    ReportAbuse,
    ReportFollow,
    ReportComment,
    ReportEditLog,
    WatchlistItem,
    DigestSubscription,
)


@admin.register(Scamreports)
class ScamreportsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_or_number', 'social_media', 'is_verified', 'is_hidden', 'encounter_count', 'is_resolved', 'date_reported')
    list_filter = ('is_verified', 'is_hidden', 'is_resolved', 'date_reported')
    search_fields = ('name_or_number', 'social_media', 'description')
    actions = ['approve_reports', 'hide_reports']

    def approve_reports(self, request, queryset):
        queryset.update(is_hidden=False, is_verified=True)

    def hide_reports(self, request, queryset):
        queryset.update(is_hidden=True)

    approve_reports.short_description = "Approve selected reports"
    hide_reports.short_description = "Hide selected reports"


@admin.register(Scamtype)
class ScamtypeAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(ReportAbuse)
class ReportAbuseAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('report__name_or_number', 'report__social_media', 'details', 'email')


@admin.register(ReportFollow)
class ReportFollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'email', 'created_at')
    search_fields = ('report__name_or_number', 'report__social_media', 'email')


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'name', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('report__name_or_number', 'report__social_media', 'message', 'name')


@admin.register(ReportEditLog)
class ReportEditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'user', 'created_at')
    search_fields = ('report__name_or_number', 'report__social_media')


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name_or_number', 'social_media', 'created_at')
    search_fields = ('name_or_number', 'social_media', 'user__username')


@admin.register(DigestSubscription)
class DigestSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
