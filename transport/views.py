import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone

from .models import Party, Vehicle, Parcel, ParcelStatusHistory, DeliveryAssignment
from .forms import (
    ParcelForm, PartyForm, VehicleForm,
    ParcelStatusUpdateForm, DeliveryAssignmentForm
)
from .utils import get_dashboard_metrics, get_chart_data


# --------------------------------------------------------------------------
# 1. PUBLIC VIEWS
# --------------------------------------------------------------------------

def home(request):
    """
    Public landing page with hero, quick tracking form, services,
    how it works workflow, dynamic stats, and contact section.
    """
    metrics = get_dashboard_metrics()
    
    # Get recent successful deliveries or active milestones count
    recent_count = Parcel.objects.filter(status='DELIVERED').count()
    
    context = {
        'metrics': metrics,
        'recent_count': recent_count,
        'title': 'Reliable Transport & Parcel Delivery',
    }
    return render(request, 'home.html', context)


def public_tracking(request):
    """
    Public parcel tracking search page.
    Visually showcases the journey: Received -> Sorted -> Vehicle Assigned -> In Transit -> Out for Delivery -> Delivered.
    Does NOT expose sensitive internal accounting details.
    """
    query = request.GET.get('q', '').strip() or request.POST.get('q', '').strip()
    parcel = None
    status_step = 0
    history = []

    # Milestone index mapping
    step_map = {
        'RECEIVED': 1,
        'SORTED': 2,
        'VEHICLE_ASSIGNED': 3,
        'IN_TRANSIT': 4,
        'OUT_FOR_DELIVERY': 5,
        'DELIVERED': 6,
        'CANCELLED': -1,
    }

    if query:
        # Search by exact or case-insensitive consignment number
        parcel = Parcel.objects.filter(consignment_number__iexact=query).first()
        if not parcel:
            # Fallback search by private mark or partial match
            parcel = Parcel.objects.filter(
                Q(consignment_number__icontains=query) | Q(private_mark__iexact=query)
            ).first()

        if parcel:
            status_step = step_map.get(parcel.status, 1)
            history = parcel.status_history.all().order_by('-timestamp')
        else:
            messages.warning(request, f"No consignment found with tracking number '{query}'. Please verify and try again.")

    context = {
        'query': query,
        'parcel': parcel,
        'status_step': status_step,
        'history': history,
        'title': 'Track Parcel Consignment',
    }
    return render(request, 'tracking.html', context)


def about_page(request):
    """Public about page / company background."""
    return render(request, 'home.html', {'scroll_to': 'about', 'title': 'About Us'})


def services_page(request):
    """Public services page / logistics capabilities."""
    return render(request, 'home.html', {'scroll_to': 'services', 'title': 'Our Services'})


def contact_page(request):
    """Public contact section handler."""
    if request.method == 'POST':
        name = request.POST.get('name', 'Valued Customer')
        phone = request.POST.get('phone', '')
        destination = request.POST.get('destination', 'Ahmedabad')
        quotation = request.POST.get('quotation', '')
        quote_info = f" (Est. Quote: {quotation})" if quotation else ""
        messages.success(request, f"Thank you {name}! Your inquiry for {destination}{quote_info} has been logged. Our Saroli transport desk is connecting with you on WhatsApp ({phone}).")
        return redirect('home')
    return render(request, 'home.html', {'scroll_to': 'contact', 'title': 'Contact Transport Desk'})


# --------------------------------------------------------------------------
# 2. AUTHENTICATION VIEWS
# --------------------------------------------------------------------------

def admin_login(request):
    """
    Staff / Admin custom login view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'login.html', {'title': 'Staff Login - Transport Portal'})


def admin_logout(request):
    """
    Staff logout view.
    """
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')


# --------------------------------------------------------------------------
# 3. ADMIN DASHBOARD & CHARTS
# --------------------------------------------------------------------------

@login_required
def dashboard(request):
    """
    Main operations dashboard with summary KPI cards, dynamic SVG charts,
    and recent parcel activities.
    """
    metrics = get_dashboard_metrics()
    chart_data = get_chart_data()
    
    # Recent parcels
    recent_parcels = Parcel.objects.select_related('party', 'vehicle').order_by('-created_at')[:8]
    
    # Recent distribution assignments
    recent_distributions = DeliveryAssignment.objects.select_related('parcel', 'tempo').order_by('-assigned_date')[:5]

    context = {
        'metrics': metrics,
        'chart_data_json': json.dumps(chart_data),
        'recent_parcels': recent_parcels,
        'recent_distributions': recent_distributions,
        'title': 'Operations Dashboard',
    }
    return render(request, 'dashboard.html', context)


# --------------------------------------------------------------------------
# 4. PARCEL MANAGEMENT VIEWS
# --------------------------------------------------------------------------

@login_required
def parcel_list(request):
    """
    List all parcels with advanced search and filters.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    destination_filter = request.GET.get('destination', '').strip()
    date_filter = request.GET.get('date_range', '').strip()

    parcels = Parcel.objects.select_related('party', 'vehicle').all()

    # Search filter
    if query:
        parcels = parcels.filter(
            Q(consignment_number__icontains=query) |
            Q(private_mark__icontains=query) |
            Q(party__name__icontains=query) |
            Q(party_name_text__icontains=query) |
            Q(sender_name__icontains=query) |
            Q(receiver_name__icontains=query) |
            Q(receiver_phone__icontains=query) |
            Q(destination__icontains=query) |
            Q(vehicle__vehicle_number__icontains=query) |
            Q(vehicle_number_text__icontains=query)
        )

    # Status filter
    if status_filter:
        parcels = parcels.filter(status=status_filter)

    # Destination filter
    if destination_filter:
        parcels = parcels.filter(destination__iexact=destination_filter)

    # Date filter
    today = timezone.now().date()
    if date_filter == 'today':
        parcels = parcels.filter(receiving_date=today)
    elif date_filter == 'week':
        week_ago = today - datetime.timedelta(days=7)
        parcels = parcels.filter(receiving_date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = today - datetime.timedelta(days=30)
        parcels = parcels.filter(receiving_date__gte=month_ago)

    # Unique destinations for filter dropdown
    all_destinations = Parcel.objects.values_list('destination', flat=True).distinct().order_by('destination')

    # Pagination
    paginator = Paginator(parcels, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'parcels': page_obj.object_list,
        'query': query,
        'status_filter': status_filter,
        'destination_filter': destination_filter,
        'date_filter': date_filter,
        'all_destinations': all_destinations,
        'status_choices': Parcel.STATUS_CHOICES,
        'total_count': parcels.count(),
        'title': 'Consignment & Parcel Registry',
    }
    return render(request, 'parcel_list.html', context)


@login_required
def parcel_create(request):
    """
    Parcel / Goods entry module.
    Automatically generates unique consignment number (e.g. TRN20260001).
    Party and Private Mark are kept distinct.
    """
    next_consignment = Parcel.generate_next_consignment_number()

    if request.method == 'POST':
        form = ParcelForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            if not parcel.consignment_number:
                parcel.consignment_number = next_consignment
            parcel.save()
            messages.success(request, f"Consignment {parcel.consignment_number} successfully registered into system!")
            return redirect('parcel_detail', pk=parcel.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        # Pre-populate defaults (Surat to Ahmedabad)
        initial_data = {
            'source': 'Surat (Saroli)',
            'destination': 'Ahmedabad',
            'sender_city': 'Surat',
            'receiving_date': timezone.now().date(),
            'status': 'RECEIVED',
        }
        form = ParcelForm(initial=initial_data)

    parties = Party.objects.all().order_by('name')
    vehicles = Vehicle.objects.all().order_by('vehicle_number')

    # Build JSON map of party_id -> {private_mark, contact_person, phone} for vanilla JS auto-fill
    parties_data = {
        p.id: {
            'name': p.name,
            'private_mark': p.private_mark,
            'contact_person': p.contact_person,
            'phone': p.phone,
            'city': p.city,
        }
        for p in parties
    }

    # Build JSON map of vehicle_id -> {driver_name, driver_contact}
    vehicles_data = {
        v.id: {
            'vehicle_number': v.vehicle_number,
            'driver_name': v.driver_name,
            'driver_contact': v.driver_contact,
        }
        for v in vehicles
    }

    context = {
        'form': form,
        'next_consignment': next_consignment,
        'parties_json': json.dumps(parties_data),
        'vehicles_json': json.dumps(vehicles_data),
        'is_edit': False,
        'title': 'New Parcel / Goods Entry',
    }
    return render(request, 'parcel_form.html', context)


@login_required
def parcel_edit(request, pk):
    """
    Edit existing parcel consignment details.
    """
    parcel = get_object_or_404(Parcel, pk=pk)

    if request.method == 'POST':
        form = ParcelForm(request.POST, instance=parcel)
        if form.is_valid():
            parcel = form.save()
            messages.success(request, f"Consignment {parcel.consignment_number} updated successfully.")
            return redirect('parcel_detail', pk=parcel.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ParcelForm(instance=parcel)

    parties = Party.objects.all().order_by('name')
    vehicles = Vehicle.objects.all().order_by('vehicle_number')

    parties_data = {
        p.id: {
            'name': p.name,
            'private_mark': p.private_mark,
            'contact_person': p.contact_person,
            'phone': p.phone,
            'city': p.city,
        }
        for p in parties
    }

    vehicles_data = {
        v.id: {
            'vehicle_number': v.vehicle_number,
            'driver_name': v.driver_name,
            'driver_contact': v.driver_contact,
        }
        for v in vehicles
    }

    context = {
        'form': form,
        'parcel': parcel,
        'next_consignment': parcel.consignment_number,
        'parties_json': json.dumps(parties_data),
        'vehicles_json': json.dumps(vehicles_data),
        'is_edit': True,
        'title': f'Edit Consignment - {parcel.consignment_number}',
    }
    return render(request, 'parcel_form.html', context)


@login_required
def parcel_detail(request, pk):
    """
    Comprehensive 360-degree parcel details view.
    Displays:
    - Parcel Info (Consignment #, Party, Private Mark, Packages, Weight, Goods)
    - Route Info (Source, Destination)
    - Vehicle Info (Vehicle #, Driver)
    - Delivery Info (Status, Expected Delivery, Actual Delivery)
    - Status Movement Timeline
    - Quick Status Update Modal Form
    """
    parcel = get_object_or_404(Parcel.objects.select_related('party', 'vehicle'), pk=pk)
    history = parcel.status_history.all().order_by('-timestamp')
    distributions = parcel.delivery_assignments.all().order_by('-assigned_date')
    status_form = ParcelStatusUpdateForm(initial={'status': parcel.status, 'location': parcel.destination or 'Surat Hub'})

    context = {
        'parcel': parcel,
        'history': history,
        'distributions': distributions,
        'status_form': status_form,
        'status_choices': Parcel.STATUS_CHOICES,
        'title': f'Consignment Details - {parcel.consignment_number}',
    }
    return render(request, 'parcel_detail.html', context)


@login_required
def parcel_delete(request, pk):
    """
    Delete a parcel record.
    """
    parcel = get_object_or_404(Parcel, pk=pk)
    if request.method == 'POST':
        consignment_no = parcel.consignment_number
        parcel.delete()
        messages.success(request, f"Consignment {consignment_no} has been permanently deleted.")
        return redirect('parcel_list')
    return render(request, 'confirm_delete.html', {
        'object': parcel,
        'object_name': f"Consignment {parcel.consignment_number}",
        'cancel_url': 'parcel_detail',
        'cancel_pk': parcel.pk,
    })


@login_required
def update_parcel_status(request, pk):
    """
    POST action to transition parcel status and append an audit history record.
    """
    parcel = get_object_or_404(Parcel, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        location = request.POST.get('location', '').strip() or parcel.destination or 'En Route'
        remarks = request.POST.get('remarks', '').strip()

        if new_status and new_status in dict(Parcel.STATUS_CHOICES):
            parcel.status = new_status
            if new_status == 'DELIVERED':
                parcel.actual_delivery_date = timezone.now()
            parcel.save()

            # Record history
            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status=new_status,
                location=location,
                remarks=remarks or f"Status updated to {parcel.get_status_display()}.",
                updated_by=request.user
            )

            messages.success(request, f"Status for {parcel.consignment_number} updated to '{parcel.get_status_display()}'.")
        else:
            messages.error(request, "Invalid status choice selected.")

    return redirect('parcel_detail', pk=parcel.pk)


@login_required
def parcel_receipt(request, pk):
    """
    Printable Consignment Lorry Receipt (Bilti / LR).
    Styled for pristine A4 / slip printing with print-only media CSS.
    """
    parcel = get_object_or_404(Parcel.objects.select_related('party', 'vehicle'), pk=pk)
    
    context = {
        'parcel': parcel,
        'today': timezone.now(),
        'title': f'Receipt - {parcel.consignment_number}',
    }
    return render(request, 'receipt.html', context)


# --------------------------------------------------------------------------
# 5. PARTY / CUSTOMER MANAGEMENT VIEWS
# --------------------------------------------------------------------------

@login_required
def party_list(request):
    """
    Party management list view with search by name, contact, private mark, city.
    """
    query = request.GET.get('q', '').strip()
    parties = Party.objects.annotate(
        parcels_total=Count('parcels')
    ).all()

    if query:
        parties = parties.filter(
            Q(name__icontains=query) |
            Q(private_mark__icontains=query) |
            Q(contact_person__icontains=query) |
            Q(phone__icontains=query) |
            Q(city__icontains=query) |
            Q(gst_number__icontains=query)
        )

    paginator = Paginator(parties, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'parties': page_obj.object_list,
        'query': query,
        'total_count': parties.count(),
        'title': 'Party / Customer Management',
    }
    return render(request, 'party_list.html', context)


@login_required
def party_create(request):
    """Register new party / customer."""
    if request.method == 'POST':
        form = PartyForm(request.POST)
        if form.is_valid():
            party = form.save()
            messages.success(request, f"Party '{party.name}' with Private Mark '{party.private_mark}' registered successfully.")
            return redirect('party_detail', pk=party.pk)
        else:
            messages.error(request, "Please resolve the errors below.")
    else:
        form = PartyForm()

    return render(request, 'party_form.html', {
        'form': form,
        'is_edit': False,
        'title': 'Register New Party / Customer',
    })


@login_required
def party_edit(request, pk):
    """Edit existing party."""
    party = get_object_or_404(Party, pk=pk)

    if request.method == 'POST':
        form = PartyForm(request.POST, instance=party)
        if form.is_valid():
            party = form.save()
            messages.success(request, f"Party '{party.name}' updated successfully.")
            return redirect('party_detail', pk=party.pk)
        else:
            messages.error(request, "Please resolve the errors below.")
    else:
        form = PartyForm(instance=party)

    return render(request, 'party_form.html', {
        'form': form,
        'party': party,
        'is_edit': True,
        'title': f'Edit Party - {party.name}',
    })


@login_required
def party_detail(request, pk):
    """
    Party 360 view with associated parcels list and shipment statistics.
    """
    party = get_object_or_404(Party, pk=pk)
    parcels = party.parcels.all().order_by('-receiving_date')

    context = {
        'party': party,
        'parcels': parcels,
        'total_parcels': parcels.count(),
        'delivered_parcels': parcels.filter(status='DELIVERED').count(),
        'pending_parcels': parcels.exclude(status__in=['DELIVERED', 'CANCELLED']).count(),
        'title': f'Party Profile - {party.name}',
    }
    return render(request, 'party_detail.html', context)


@login_required
def party_delete(request, pk):
    """Delete party."""
    party = get_object_or_404(Party, pk=pk)
    if request.method == 'POST':
        name = party.name
        party.delete()
        messages.success(request, f"Party '{name}' deleted successfully.")
        return redirect('party_list')
    return render(request, 'confirm_delete.html', {
        'object': party,
        'object_name': f"Party '{party.name}'",
        'cancel_url': 'party_detail',
        'cancel_pk': party.pk,
    })


# --------------------------------------------------------------------------
# 6. VEHICLE & FLEET MANAGEMENT VIEWS
# --------------------------------------------------------------------------

@login_required
def vehicle_list(request):
    """
    Fleet management: Heavy line trucks and local distribution tempos.
    """
    query = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()
    status_filter = request.GET.get('status', '').strip()

    vehicles = Vehicle.objects.all()

    if query:
        vehicles = vehicles.filter(
            Q(vehicle_number__icontains=query) |
            Q(driver_name__icontains=query) |
            Q(driver_contact__icontains=query) |
            Q(current_location__icontains=query)
        )

    if type_filter:
        vehicles = vehicles.filter(vehicle_type=type_filter)

    if status_filter:
        vehicles = vehicles.filter(status=status_filter)

    context = {
        'vehicles': vehicles,
        'query': query,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'type_choices': Vehicle.TYPE_CHOICES,
        'status_choices': Vehicle.STATUS_CHOICES,
        'title': 'Fleet & Vehicle Management',
    }
    return render(request, 'vehicle_list.html', context)


@login_required
def vehicle_create(request):
    """Add new transport vehicle or distribution tempo."""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"Vehicle {vehicle.vehicle_number} ({vehicle.get_vehicle_type_display()}) registered.")
            return redirect('vehicle_detail', pk=vehicle.pk)
        else:
            messages.error(request, "Please resolve the errors below.")
    else:
        form = VehicleForm()

    return render(request, 'vehicle_form.html', {
        'form': form,
        'is_edit': False,
        'title': 'Register New Vehicle / Tempo',
    })


@login_required
def vehicle_edit(request, pk):
    """Edit vehicle specs and driver info."""
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"Vehicle {vehicle.vehicle_number} updated successfully.")
            return redirect('vehicle_detail', pk=vehicle.pk)
        else:
            messages.error(request, "Please resolve the errors below.")
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'vehicle_form.html', {
        'form': form,
        'vehicle': vehicle,
        'is_edit': True,
        'title': f'Edit Vehicle - {vehicle.vehicle_number}',
    })


@login_required
def vehicle_detail(request, pk):
    """
    Vehicle manifest view: specifications, driver contact, and active assigned consignments.
    """
    vehicle = get_object_or_404(Vehicle, pk=pk)
    assigned_parcels = vehicle.assigned_parcels.all().order_by('-receiving_date')
    tempo_assignments = vehicle.tempo_assignments.all().order_by('-assigned_date')

    context = {
        'vehicle': vehicle,
        'assigned_parcels': assigned_parcels,
        'tempo_assignments': tempo_assignments,
        'title': f'Vehicle Manifest - {vehicle.vehicle_number}',
    }
    return render(request, 'vehicle_detail.html', context)


@login_required
def vehicle_delete(request, pk):
    """Delete vehicle."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        no = vehicle.vehicle_number
        vehicle.delete()
        messages.success(request, f"Vehicle {no} deleted from fleet.")
        return redirect('vehicle_list')
    return render(request, 'confirm_delete.html', {
        'object': vehicle,
        'object_name': f"Vehicle '{vehicle.vehicle_number}'",
        'cancel_url': 'vehicle_detail',
        'cancel_pk': vehicle.pk,
    })


# --------------------------------------------------------------------------
# 7. DELIVERY & LOCAL DISTRIBUTION MODULE
# --------------------------------------------------------------------------

@login_required
def distribution_list(request):
    """
    Local Distribution Hub workflow:
    Large vehicle arrives from Surat -> Goods unloaded and sorted ->
    Different parcels assigned to local tempos for last-mile delivery.
    Shows workflow: Main Transport Vehicle -> Local Tempo -> Destination.
    """
    # Unassigned or staged parcels ready for local distribution
    unassigned_parcels = Parcel.objects.filter(
        status__in=['RECEIVED', 'SORTED', 'IN_TRANSIT']
    ).select_related('party', 'vehicle').order_by('-receiving_date')

    # Active distribution assignments
    active_assignments = DeliveryAssignment.objects.select_related(
        'parcel', 'tempo', 'parcel__party'
    ).order_by('-assigned_date')

    # Tempos available
    tempos = Vehicle.objects.filter(
        vehicle_type__in=['TEMPO', 'MINI_TRUCK', 'E_LOADER']
    )

    if request.method == 'POST':
        assignment_form = DeliveryAssignmentForm(request.POST)
        if assignment_form.is_valid():
            assignment = assignment_form.save()
            # Update parcel status to Out for Delivery
            parcel = assignment.parcel
            parcel.status = 'OUT_FOR_DELIVERY'
            parcel.save()

            # Record history
            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status='OUT_FOR_DELIVERY',
                location=assignment.destination_area or 'Local Distribution Route',
                remarks=f"Loaded in Tempo {assignment.tempo.vehicle_number if assignment.tempo else 'Local Tempo'} with Driver {assignment.driver_name}.",
                updated_by=request.user
            )

            messages.success(request, f"Consignment {parcel.consignment_number} assigned to Tempo for {assignment.destination_area}!")
            return redirect('distribution_list')
        else:
            messages.error(request, "Could not create distribution assignment. Please check fields.")
    else:
        assignment_form = DeliveryAssignmentForm()

    all_tempos = Vehicle.objects.filter(
        vehicle_type__in=['TEMPO', 'MINI_TRUCK', 'E_LOADER']
    )
    if not all_tempos.exists():
        all_tempos = Vehicle.objects.all()

    tempos_data = {
        t.id: {
            'vehicle_number': t.vehicle_number,
            'driver_name': t.driver_name,
            'driver_contact': t.driver_contact,
        }
        for t in all_tempos
    }

    context = {
        'unassigned_parcels': unassigned_parcels,
        'active_assignments': active_assignments,
        'tempos': all_tempos,
        'assignment_form': assignment_form,
        'tempos_json': json.dumps(tempos_data),
        'title': 'Local Distribution & Delivery Hub',
    }
    return render(request, 'distribution.html', context)


@login_required
def update_distribution_status(request, pk):
    """
    Update status of a local tempo delivery assignment.
    """
    assignment = get_object_or_404(DeliveryAssignment, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('delivery_status')
        notes = request.POST.get('notes', '').strip()

        if new_status in dict(DeliveryAssignment.STATUS_CHOICES):
            assignment.delivery_status = new_status
            if notes:
                assignment.notes = f"{assignment.notes}\n{notes}".strip()
            assignment.save()

            # If completed, mark parcel as DELIVERED
            if new_status == 'COMPLETED':
                parcel = assignment.parcel
                parcel.status = 'DELIVERED'
                parcel.actual_delivery_date = timezone.now()
                parcel.save()

                ParcelStatusHistory.objects.create(
                    parcel=parcel,
                    status='DELIVERED',
                    location=assignment.destination_area,
                    remarks=f"Successfully delivered to party by driver {assignment.driver_name}. Notes: {notes}",
                    updated_by=request.user
                )
                messages.success(request, f"Consignment {parcel.consignment_number} marked as DELIVERED!")
            else:
                messages.success(request, f"Distribution status updated to {assignment.get_delivery_status_display()}.")

    return redirect('distribution_list')


# --------------------------------------------------------------------------
# 8. DATA API / AJAX HELPERS
# --------------------------------------------------------------------------

@login_required
def api_party_detail(request, pk):
    """JSON endpoint returning party data for form auto-fills."""
    party = get_object_or_404(Party, pk=pk)
    return JsonResponse({
        'id': party.id,
        'name': party.name,
        'private_mark': party.private_mark,
        'contact_person': party.contact_person,
        'phone': party.phone,
        'address': party.address,
        'city': party.city,
        'gst_number': party.gst_number,
    })
