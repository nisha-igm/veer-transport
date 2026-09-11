from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('track/', views.public_tracking, name='public_tracking'),
    path('about/', views.about_page, name='about_page'),
    path('services/', views.services_page, name='services_page'),
    path('contact/', views.contact_page, name='contact_page'),

    # Staff Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # Staff Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Parcel / Consignment Management
    path('parcels/', views.parcel_list, name='parcel_list'),
    path('parcels/new/', views.parcel_create, name='parcel_create'),
    path('parcels/<int:pk>/', views.parcel_detail, name='parcel_detail'),
    path('parcels/<int:pk>/edit/', views.parcel_edit, name='parcel_edit'),
    path('parcels/<int:pk>/delete/', views.parcel_delete, name='parcel_delete'),
    path('parcels/<int:pk>/status-update/', views.update_parcel_status, name='update_parcel_status'),
    path('parcels/<int:pk>/receipt/', views.parcel_receipt, name='parcel_receipt'),

    # Party / Customer Management
    path('parties/', views.party_list, name='party_list'),
    path('parties/new/', views.party_create, name='party_create'),
    path('parties/<int:pk>/', views.party_detail, name='party_detail'),
    path('parties/<int:pk>/edit/', views.party_edit, name='party_edit'),
    path('parties/<int:pk>/delete/', views.party_delete, name='party_delete'),

    # Fleet / Vehicle Management
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/new/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),

    # Local Delivery & Distribution Module
    path('distribution/', views.distribution_list, name='distribution_list'),
    path('distribution/<int:pk>/update/', views.update_distribution_status, name='update_distribution_status'),

    # Data API / Dynamic lookups
    path('api/party/<int:pk>/', views.api_party_detail, name='api_party_detail'),
]
