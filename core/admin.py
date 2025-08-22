from django.contrib import admin
from .models import (
    Department, AuditProject, AuditAssignment,
    AuditPlan, AuditIssue, AuditReport, FinalReport
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'manager__username', 'manager__first_name', 'manager__last_name']
    ordering = ['name']


@admin.register(AuditProject)
class AuditProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'department', 'created_at']
    search_fields = ['title', 'description', 'department__name', 'created_by__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(AuditAssignment)
class AuditAssignmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'auditor', 'assigned_by', 'assigned_at']
    list_filter = ['assigned_at', 'project__department']
    search_fields = ['project__title', 'auditor__username', 'assigned_by__username']
    ordering = ['-assigned_at']
    readonly_fields = ['assigned_at']


@admin.register(AuditPlan)
class AuditPlanAdmin(admin.ModelAdmin):
    list_display = ['project', 'created_by', 'status', 'created_at', 'manager_reviewed_at']
    list_filter = ['status', 'created_at', 'manager_reviewed_at', 'project__department']
    search_fields = ['project__title', 'description', 'created_by__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'manager_reviewed_at']


@admin.register(AuditIssue)
class AuditIssueAdmin(admin.ModelAdmin):
    list_display = ['project', 'created_by', 'status', 'created_at', 'manager_reviewed_at']
    list_filter = ['status', 'created_at', 'manager_reviewed_at', 'project__department']
    search_fields = ['project__title', 'description', 'created_by__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'manager_reviewed_at']


@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    list_display = ['project', 'created_by', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'project__department']
    search_fields = ['project__title', 'description', 'created_by__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(FinalReport)
class FinalReportAdmin(admin.ModelAdmin):
    list_display = ['project', 'created_at']
    list_filter = ['created_at', 'project__department']
    search_fields = ['project__title', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
