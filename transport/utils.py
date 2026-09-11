import datetime
from django.utils import timezone
from django.db.models import Count, Q
from .models import Parcel, Party, Vehicle, DeliveryAssignment


def get_dashboard_metrics():
    """
    Calculates summary numbers and KPIs for the staff/admin dashboard.
    """
    today = timezone.now().date()
    
    total_parcels = Parcel.objects.count()
    today_received = Parcel.objects.filter(receiving_date=today).count()
    pending_deliveries = Parcel.objects.exclude(status__in=['DELIVERED', 'CANCELLED']).count()
    delivered_parcels = Parcel.objects.filter(status='DELIVERED').count()
    total_parties = Party.objects.count()
    total_vehicles = Vehicle.objects.count()
    active_distributions = DeliveryAssignment.objects.filter(delivery_status__in=['ASSIGNED', 'LOADED', 'OUT_FOR_DELIVERY']).count()

    return {
        'total_parcels': total_parcels,
        'today_received': today_received,
        'pending_deliveries': pending_deliveries,
        'delivered_parcels': delivered_parcels,
        'total_parties': total_parties,
        'total_vehicles': total_vehicles,
        'active_distributions': active_distributions,
    }


def get_chart_data():
    """
    Generates structured analytics datasets for pure Vanilla JS / SVG charts.
    """
    today = timezone.now().date()
    
    # 1. Parcels received over last 7 days
    daily_labels = []
    daily_counts = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        count = Parcel.objects.filter(receiving_date=day).count()
        daily_labels.append(day.strftime('%d %b'))
        daily_counts.append(count)

    # 2. Status distribution
    status_order = [
        ('RECEIVED', 'Received', '#3b82f6'),
        ('SORTED', 'Sorted', '#8b5cf6'),
        ('VEHICLE_ASSIGNED', 'Assigned', '#06b6d4'),
        ('IN_TRANSIT', 'In Transit', '#f59e0b'),
        ('OUT_FOR_DELIVERY', 'Out for Del.', '#ec4899'),
        ('DELIVERED', 'Delivered', '#10b981'),
        ('CANCELLED', 'Cancelled', '#ef4444'),
    ]
    status_labels = []
    status_counts = []
    status_colors = []
    for code, label, color in status_order:
        cnt = Parcel.objects.filter(status=code).count()
        if cnt > 0 or code in ['RECEIVED', 'IN_TRANSIT', 'DELIVERED']:
            status_labels.append(label)
            status_counts.append(cnt)
            status_colors.append(color)

    # 3. Top destination hubs
    destinations = (
        Parcel.objects.values('destination')
        .annotate(count=Count('id'))
        .order_by('-count')[:6]
    )
    dest_labels = [d['destination'] for d in destinations] or ['Ahmedabad (Maskati)', 'Ahmedabad (Kalupur)', 'Ahmedabad (Sarangpur)', 'Ahmedabad (Narol)']
    dest_counts = [d['count'] for d in destinations] or [0, 0, 0, 0]

    return {
        'daily': {
            'labels': daily_labels,
            'counts': daily_counts,
        },
        'status': {
            'labels': status_labels,
            'counts': status_counts,
            'colors': status_colors,
        },
        'destinations': {
            'labels': dest_labels,
            'counts': dest_counts,
        }
    }
