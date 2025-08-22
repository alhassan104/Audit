from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class AuditProject(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('plan_pending', 'Plan Pending'),
        ('audit_in_progress', 'Audit In Progress'),
        ('report_pending_manager', 'Report Pending Manager'),
        ('report_pending_department', 'Report Pending Department'),
        ('final_review', 'Final Review'),
        ('finalized', 'Finalized'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(default="")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='audit_projects')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='created')
    manager_notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.title


class AuditAssignment(models.Model):
    project = models.ForeignKey(AuditProject, on_delete=models.CASCADE, related_name='assignments')
    auditor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_audits')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'auditor']
    
    def __str__(self):
        return f"{self.auditor.username} - {self.project.title}"


class AuditPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.ForeignKey(AuditProject, on_delete=models.CASCADE, related_name='plans')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    description = models.TextField(default="")
    attachment = models.FileField(upload_to='audit/plans/', blank=True, null=True)
    manager_notes = models.TextField(blank=True)
    manager_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Plan for {self.project.title}"


class AuditIssue(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.ForeignKey(AuditProject, on_delete=models.CASCADE, related_name='issues')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_issues')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    description = models.TextField(default="")
    attachment = models.FileField(upload_to='audit/issues/', blank=True, null=True)
    manager_notes = models.TextField(blank=True)
    manager_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Issue for {self.project.title}"


class AuditReport(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved_by_manager', 'Approved by Manager'),
        ('sent_to_department', 'Sent to Department'),
        ('dept_replied', 'Department Replied'),
        ('auditor_approved', 'Auditor Approved'),
        ('final_manager_review', 'Final Manager Review'),
        ('final_approved', 'Final Approved'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.ForeignKey(AuditProject, on_delete=models.CASCADE, related_name='reports')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    description = models.TextField(default="")
    attachment = models.FileField(upload_to='audit/reports/', blank=True, null=True)
    manager_notes = models.TextField(blank=True)
    department_notes = models.TextField(blank=True)
    auditor_final_notes = models.TextField(blank=True)
    final_manager_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Report for {self.project.title}"


class FinalReport(models.Model):
    project = models.OneToOneField(AuditProject, on_delete=models.CASCADE, related_name='final_report')
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(default="")
    attachment = models.FileField(upload_to='audit/final_reports/', blank=True, null=True)
    
    def __str__(self):
        return f"Final Report for {self.project.title}"

