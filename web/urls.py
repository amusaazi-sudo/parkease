from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('parking-dashboard/', views.parking_dashboard, name='parking_dashboard'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('register-vehicle/', views.register_vehicle, name='register_vehicle'),
    path('active-vehicles/', views.active_vehicles, name='active_vehicles'),
    path('signout/<int:vehicle_id>/', views.signout_vehicle, name='signout_vehicle'),
    path('receipt/<int:receipt_id>/', views.receipt, name='receipt'),
    path('tyre-service/', views.tyre_service, name='tyre_service'),
    path('tyre-transactions/', views.tyre_transactions, name='tyre_transactions'),
    path('manage-tyre-prices/', views.manage_tyre_prices, name='manage_tyre_prices'),
    path('battery-service/', views.battery_service, name='battery_service'),
    path('battery-transactions/', views.battery_transactions, name='battery_transactions'),
    path('manage-battery-prices/', views.manage_battery_prices, name='manage_battery_prices'),
    path('daily-report/', views.daily_report, name='daily_report'),
]