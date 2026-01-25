from django.contrib import admin
from .models import Scamtype, Scamreports, ReportAbuse, ReportFollow, ReportComment


@admin.register(Scamreports)
class ScamreportsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_or_number', 'social_media', 'is_verified', 'is_hidden', 'encounter_count', 'is_resolved', 'date_reported')
    list_filter = ('is_verified', 'is_hidden', 'is_resolved', 'date_reported')
    search_fields = ('name_or_number', 'social_media', 'description')


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
