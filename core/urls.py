from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('map/', views.map_view, name='map'),
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Containers
    path('containers/', views.containers_list, name='containers_list'),
    path('containers/<int:container_id>/', views.container_detail, name='container_detail'),
    
    # Routes
    path('routes/', views.routes_list, name='routes_list'),
    
    # Alerts
    path('alerts/', views.alerts_list, name='alerts_list'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    
    # API Endpoints
    path('api/containers/', views.api_containers_json, name='api_containers'),
    path('api/stats/', views.api_stats_json, name='api_stats'),
    path('report-issue-api/', views.report_issue_api, name='report_issue_api'),

    path('report-issue/', views.report_issue, name='report_issue'),
]