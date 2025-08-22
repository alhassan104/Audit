from django.urls import path, include
from . import views

app_name = "core"

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('', views.dashboard, name="dashboard"),
    path('manager/', views.manager_dashboard, name="manager_dashboard"),
    path('auditor/', views.auditor_dashboard, name="auditor_dashboard"),
    path('department/', views.department_dashboard, name="department_dashboard"),

    # Projects
    path('projects/', views.projects_list, name="projects_list"),
    path('projects/create/', views.project_create, name="project_create"),
    path('projects/<int:pk>/', views.project_detail, name="project_detail"),

    # Plans
    path('plans/create/<int:project_id>/', views.plan_create, name="plan_create"),
    path('plans/<int:pk>/', views.plan_detail, name="plan_detail"),
    path('plans/<int:pk>/review/', views.plan_review, name="plan_review"),
    path('plans/', views.plans_list, name="plans_list"),

    # Issues
    path('issues/create/<int:project_id>/', views.issue_create, name="issue_create"),
    path('issues/<int:pk>/', views.issue_detail, name="issue_detail"),
    path('issues/<int:pk>/review/', views.issue_review, name="issue_review"),
    path('issues/', views.issues_list, name="issues_list"),

    # Reports
    path('reports/create/<int:project_id>/', views.report_create, name="report_create"),
    path('reports/<int:pk>/', views.report_detail, name="report_detail"),
    path('reports/<int:pk>/review/', views.report_review, name="report_review"),
    path('reports/<int:pk>/send-to-department/', views.report_send_to_department, name="report_send_to_department"),
    path('reports/<int:pk>/department-review/', views.department_report_review, name="department_report_review"),
    path('reports/<int:pk>/auditor-final-review/', views.auditor_final_review, name="auditor_final_review"),
    path('reports/<int:pk>/final-manager-review/', views.final_manager_review, name="final_manager_review"),
    path('reports/', views.reports_list, name="reports_list"),
]
