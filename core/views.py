from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from .models import (
    AuditProject, Department, AuditAssignment,
    AuditPlan, AuditIssue, AuditReport, FinalReport
)
import os


# ---- Helper Functions ----
def is_audit_manager(user):
    return user.groups.filter(name="Audit Managers").exists()

def is_auditor(user):
    return user.groups.filter(name="Auditors").exists()

def is_department_manager(user):
    return user.groups.filter(name="Department Managers").exists()

def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


# ---- Dashboard Views ----
@login_required
def dashboard(request):
    if is_audit_manager(request.user):
        return redirect('core:manager_dashboard')
    elif is_auditor(request.user):
        return redirect('core:auditor_dashboard')
    elif is_department_manager(request.user):
        return redirect('core:department_dashboard')
    else:
        return render(request, 'core/dashboard.html')


@login_required
@user_passes_test(is_audit_manager)
def manager_dashboard(request):
    projects = AuditProject.objects.all().order_by('-created_at')
    pending_plans = AuditPlan.objects.filter(status='submitted')
    pending_issues = AuditIssue.objects.filter(status='submitted')
    pending_reports = AuditReport.objects.filter(status='submitted')
    
    context = {
        'projects': projects,
        'pending_plans': pending_plans,
        'pending_issues': pending_issues,
        'pending_reports': pending_reports,
    }
    return render(request, 'core/manager_dashboard.html', context)


@login_required
@user_passes_test(is_auditor)
def auditor_dashboard(request):
    assignments = AuditAssignment.objects.filter(auditor=request.user)
    projects = [assignment.project for assignment in assignments]
    
    context = {
        'projects': projects,
        'assignments': assignments,
    }
    return render(request, 'core/auditor_dashboard.html', context)


@login_required
@user_passes_test(is_department_manager)
def department_dashboard(request):
    department = Department.objects.filter(manager=request.user).first()
    if department:
        pending_reports = AuditReport.objects.filter(
            project__department=department,
            status='sent_to_department'
        )
    else:
        pending_reports = []
    
    context = {
        'department': department,
        'pending_reports': pending_reports,
    }
    return render(request, 'core/department_dashboard.html', context)


# ---- Project Management ----
@login_required
@user_passes_test(is_audit_manager)
def project_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        dept_id = request.POST.get('department')
        auditors_ids = request.POST.getlist('auditors')
        manager_notes = request.POST.get('manager_notes', '')

        dept = Department.objects.get(id=dept_id)
        project = AuditProject.objects.create(
            department=dept,
            title=title,
            description=description,
            manager_notes=manager_notes,
            created_by=request.user
        )

        for aid in auditors_ids:
            auditor = User.objects.get(id=aid)
            AuditAssignment.objects.create(
                project=project,
                auditor=auditor,
                assigned_by=request.user
            )

        if is_htmx(request):
            return render(request, 'core/partials/project_row.html', {'project': project})
        messages.success(request, 'Project created successfully!')
        return redirect('core:manager_dashboard')

    departments = Department.objects.all()
    auditors = User.objects.filter(groups__name='Auditors')
    return render(request, 'core/projects/create.html', {
        'departments': departments,
        'auditors': auditors
    })


@login_required
def project_detail(request, pk):
    project = get_object_or_404(AuditProject, pk=pk)
    is_assigned_auditor = (
        is_auditor(request.user) and
        AuditAssignment.objects.filter(project=project, auditor=request.user).exists()
    )
    
    context = {
        'project': project,
        'is_assigned_auditor': is_assigned_auditor,
    }
    return render(request, 'core/projects/detail.html', context)


@login_required
def projects_list(request):
    if is_audit_manager(request.user):
        projects = AuditProject.objects.all().order_by('-created_at')
    elif is_auditor(request.user):
        assignments = AuditAssignment.objects.filter(auditor=request.user)
        projects = [assignment.project for assignment in assignments]
    elif is_department_manager(request.user):
        department = Department.objects.filter(manager=request.user).first()
        if department:
            projects = AuditProject.objects.filter(department=department).order_by('-created_at')
        else:
            projects = []
    else:
        projects = []
    
    return render(request, 'core/projects/list.html', {'projects': projects})


# ---- Audit Plan Management ----
@login_required
@user_passes_test(is_auditor)
def plan_create(request, project_id):
    project = get_object_or_404(AuditProject, id=project_id)
    
    # Check if auditor is assigned to this project
    if not AuditAssignment.objects.filter(project=project, auditor=request.user).exists():
        messages.error(request, 'You are not assigned to this project.')
        return redirect('core:auditor_dashboard')
    
    if request.method == "POST":
        description = request.POST.get("description")
        attachment = request.FILES.get("attachment")
        
        plan = AuditPlan.objects.create(
            project=project,
            created_by=request.user,
            description=description,
            attachment=attachment,
            status="submitted"
        )
        
        project.status = "plan_pending"
        project.save()
        
        if is_htmx(request):
            return HttpResponse("Plan submitted successfully!")
        messages.success(request, 'Plan submitted successfully!')
        return redirect('core:project_detail', pk=project.id)
    
    return render(request, 'core/plans/create.html', {'project': project})


@login_required
@user_passes_test(is_audit_manager)
def plan_review(request, pk):
    plan = get_object_or_404(AuditPlan, pk=pk)
    
    if request.method == "POST":
        action = request.POST.get('action')
        manager_notes = request.POST.get('manager_notes', '')
        attachment = request.FILES.get('attachment')
        
        if action == 'approve':
            plan.status = 'approved'
            plan.project.status = 'audit_in_progress'
            plan.project.save()
        elif action == 'reject':
            plan.status = 'rejected'
            plan.project.status = 'created'
            plan.project.save()
        
        plan.manager_notes = manager_notes
        if attachment:
            plan.attachment = attachment
        plan.manager_reviewed_at = timezone.now()
        plan.save()
        
        if is_htmx(request):
            return HttpResponse("Plan reviewed successfully!")
        messages.success(request, 'Plan reviewed successfully!')
        return redirect('core:manager_dashboard')
    
    return render(request, 'core/plans/review.html', {'plan': plan})


@login_required
def plan_detail(request, pk):
    plan = get_object_or_404(AuditPlan, pk=pk)
    return render(request, 'core/plans/detail.html', {'plan': plan})


# ---- Issue Management ----
@login_required
@user_passes_test(is_auditor)
def issue_create(request, project_id):
    project = get_object_or_404(AuditProject, id=project_id)
    
    # Check if auditor is assigned and plan is approved
    if not AuditAssignment.objects.filter(project=project, auditor=request.user).exists():
        messages.error(request, 'You are not assigned to this project.')
        return redirect('core:auditor_dashboard')
    
    if project.status != 'audit_in_progress':
        messages.error(request, 'Project must be in audit progress to create issues.')
        return redirect('core:project_detail', pk=project.id)
    
    if request.method == "POST":
        description = request.POST.get("description")
        attachment = request.FILES.get("attachment")
        
        issue = AuditIssue.objects.create(
            project=project,
            created_by=request.user,
            description=description,
            attachment=attachment,
            status="submitted"
        )
        
        if is_htmx(request):
            return HttpResponse("Issue submitted successfully!")
        messages.success(request, 'Issue submitted successfully!')
        return redirect('core:project_detail', pk=project.id)
    
    return render(request, 'core/issues/create.html', {'project': project})


@login_required
@user_passes_test(is_audit_manager)
def issue_review(request, pk):
    issue = get_object_or_404(AuditIssue, pk=pk)
    
    if request.method == "POST":
        action = request.POST.get('action')
        manager_notes = request.POST.get('manager_notes', '')
        attachment = request.FILES.get('attachment')
        
        if action == 'approve':
            issue.status = 'approved'
        elif action == 'reject':
            issue.status = 'rejected'
        
        issue.manager_notes = manager_notes
        if attachment:
            issue.attachment = attachment
        issue.manager_reviewed_at = timezone.now()
        issue.save()
        
        if is_htmx(request):
            return HttpResponse("Issue reviewed successfully!")
        messages.success(request, 'Issue reviewed successfully!')
        return redirect('core:manager_dashboard')
    
    return render(request, 'core/issues/review.html', {'issue': issue})


@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(AuditIssue, pk=pk)
    return render(request, 'core/issues/detail.html', {'issue': issue})


# ---- Report Management ----
@login_required
@user_passes_test(is_auditor)
def report_create(request, project_id):
    project = get_object_or_404(AuditProject, id=project_id)
    
    # Check if auditor is assigned and issues are approved
    if not AuditAssignment.objects.filter(project=project, auditor=request.user).exists():
        messages.error(request, 'You are not assigned to this project.')
        return redirect('core:auditor_dashboard')
    
    approved_issues = AuditIssue.objects.filter(project=project, status='approved')
    if not approved_issues.exists():
        messages.error(request, 'You must have approved issues before creating a report.')
        return redirect('core:project_detail', pk=project.id)
    
    if request.method == "POST":
        description = request.POST.get("description")
        attachment = request.FILES.get("attachment")
        
        report = AuditReport.objects.create(
            project=project,
            created_by=request.user,
            description=description,
            attachment=attachment,
            status="submitted"
        )
        
        if is_htmx(request):
            return HttpResponse("Report submitted successfully!")
        messages.success(request, 'Report submitted successfully!')
        return redirect('core:project_detail', pk=project.id)
    
    return render(request, 'core/reports/create.html', {'project': project})


@login_required
@user_passes_test(is_audit_manager)
def report_review(request, pk):
    report = get_object_or_404(AuditReport, pk=pk)
    
    if request.method == "POST":
        action = request.POST.get('action')
        manager_notes = request.POST.get('manager_notes', '')
        attachment = request.FILES.get('attachment')
        
        if action == 'approve':
            report.status = 'approved_by_manager'
            report.project.status = 'report_pending_manager'
            report.project.save()
        elif action == 'reject':
            report.status = 'rejected'
            report.project.status = 'audit_in_progress'
            report.project.save()
        
        report.manager_notes = manager_notes
        if attachment:
            report.attachment = attachment
        report.save()
        
        if is_htmx(request):
            return HttpResponse("Report reviewed successfully!")
        messages.success(request, 'Report reviewed successfully!')
        return redirect('core:manager_dashboard')
    
    return render(request, 'core/reports/review.html', {'report': report})


@login_required
@user_passes_test(is_audit_manager)
def report_send_to_department(request, pk):
    report = get_object_or_404(AuditReport, pk=pk)
    report.status = 'sent_to_department'
    report.project.status = 'report_pending_department'
    report.save()
    report.project.save()
    
    messages.success(request, 'Report sent to department successfully!')
    return redirect('core:manager_dashboard')


@login_required
@user_passes_test(is_department_manager)
def department_report_review(request, pk):
    report = get_object_or_404(AuditReport, pk=pk)
    
    # Check if department manager is assigned to the project's department
    if report.project.department.manager != request.user:
        messages.error(request, 'You are not authorized to review this report.')
        return redirect('core:department_dashboard')
    
    if request.method == "POST":
        department_notes = request.POST.get('department_notes', '')
        attachment = request.FILES.get('attachment')
        
        report.department_notes = department_notes
        if attachment:
            report.attachment = attachment
        report.status = 'dept_replied'
        report.save()
        
        if is_htmx(request):
            return HttpResponse("Department response submitted successfully!")
        messages.success(request, 'Department response submitted successfully!')
        return redirect('core:department_dashboard')
    
    return render(request, 'core/reports/department_review.html', {'report': report})


@login_required
@user_passes_test(is_auditor)
def auditor_final_review(request, pk):
    report = get_object_or_404(AuditReport, pk=pk)
    
    # Check if auditor is assigned to this project
    if not AuditAssignment.objects.filter(project=report.project, auditor=request.user).exists():
        messages.error(request, 'You are not assigned to this project.')
        return redirect('core:auditor_dashboard')
    
    if request.method == "POST":
        action = request.POST.get('action')
        auditor_notes = request.POST.get('auditor_notes', '')
        
        if action == 'approve':
            report.status = 'auditor_approved'
            report.project.status = 'final_review'
            report.project.save()
        elif action == 'reject':
            report.status = 'sent_to_department'
            report.project.status = 'report_pending_department'
            report.project.save()
        
        report.auditor_final_notes = auditor_notes
        report.save()
        
        if is_htmx(request):
            return HttpResponse("Final review submitted successfully!")
        messages.success(request, 'Final review submitted successfully!')
        return redirect('core:auditor_dashboard')
    
    return render(request, 'core/reports/auditor_final_review.html', {'report': report})


@login_required
@user_passes_test(is_audit_manager)
def final_manager_review(request, pk):
    report = get_object_or_404(AuditReport, pk=pk)
    
    if request.method == "POST":
        action = request.POST.get('action')
        final_notes = request.POST.get('final_notes', '')
        attachment = request.FILES.get('attachment')
        
        if action == 'approve':
            report.status = 'final_approved'
            report.project.status = 'finalized'
            report.project.save()
            
            # Generate final report
            final_content = f"""
            Final Audit Report for {report.project.title}
            
            Project Description: {report.project.description}
            Department: {report.project.department.name}
            
            Audit Plan: {report.project.plans.first().description if report.project.plans.exists() else 'No plan'}
            
            Issues Found:
            {chr(10).join([f'- {issue.description}' for issue in report.project.issues.filter(status='approved')])}
            
            Department Response: {report.department_notes}
            
            Final Manager Notes: {final_notes}
            """
            
            FinalReport.objects.create(
                project=report.project,
                content=final_content,
                attachment=attachment
            )
            
        elif action == 'reject':
            report.status = 'auditor_approved'
            report.project.status = 'final_review'
            report.project.save()
        
        report.final_manager_notes = final_notes
        report.save()
        
        if is_htmx(request):
            return HttpResponse("Final review completed successfully!")
        messages.success(request, 'Final review completed successfully!')
        return redirect('core:manager_dashboard')
    
    return render(request, 'core/reports/final_manager_review.html', {'report': report})


@login_required
def report_detail(request, pk):
    report = get_object_or_404(AuditReport, pk=pk)
    return render(request, 'core/reports/detail.html', {'report': report})


# ---- List Views ----
@login_required
def plans_list(request):
    if is_audit_manager(request.user):
        plans = AuditPlan.objects.all().order_by('-created_at')
    elif is_auditor(request.user):
        assignments = AuditAssignment.objects.filter(auditor=request.user)
        project_ids = [assignment.project.id for assignment in assignments]
        plans = AuditPlan.objects.filter(project_id__in=project_ids).order_by('-created_at')
    else:
        plans = []
    
    return render(request, 'core/plans/list.html', {'plans': plans})


@login_required
def issues_list(request):
    if is_audit_manager(request.user):
        issues = AuditIssue.objects.all().order_by('-created_at')
    elif is_auditor(request.user):
        assignments = AuditAssignment.objects.filter(auditor=request.user)
        project_ids = [assignment.project.id for assignment in assignments]
        issues = AuditIssue.objects.filter(project_id__in=project_ids).order_by('-created_at')
    else:
        issues = []
    
    return render(request, 'core/issues/list.html', {'issues': issues})


@login_required
def reports_list(request):
    if is_audit_manager(request.user):
        reports = AuditReport.objects.all().order_by('-created_at')
    elif is_auditor(request.user):
        assignments = AuditAssignment.objects.filter(auditor=request.user)
        project_ids = [assignment.project.id for assignment in assignments]
        reports = AuditReport.objects.filter(project_id__in=project_ids).order_by('-created_at')
    elif is_department_manager(request.user):
        department = Department.objects.filter(manager=request.user).first()
        if department:
            reports = AuditReport.objects.filter(project__department=department).order_by('-created_at')
        else:
            reports = []
    else:
        reports = []
    
    return render(request, 'core/reports/list.html', {'reports': reports})


# ---- Utility Views ----
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

