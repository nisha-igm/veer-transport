from django.contrib import admin
from .models import Party, Vehicle, Parcel, ParcelStatusHistory, DeliveryAssignment


class ParcelStatusHistoryInline(admin.TabularInline):
    model = ParcelStatusHistory
    extra = 0
    readonly_fields = ('timestamp',)


class DeliveryAssignmentInline(admin.StackedInline):
    model = DeliveryAssignment
    extra = 0


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'private_mark', 'contact_person', 'phone', 'city', 'gst_number', 'total_parcels')
    search_fields = ('name', 'private_mark', 'contact_person', 'phone', 'city', 'gst_number')
    list_filter = ('city',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'vehicle_type', 'driver_name', 'driver_contact', 'capacity', 'current_location', 'status')
    search_fields = ('vehicle_number', 'driver_name', 'driver_contact', 'current_location')
    list_filter = ('vehicle_type', 'status')


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        'consignment_number', 'party', 'private_mark', 'source', 'destination',
        'package_count', 'weight', 'status', 'receiving_date'
    )
    search_fields = (
        'consignment_number', 'private_mark', 'party_name_text',
        'sender_name', 'receiver_name', 'receiver_phone', 'destination', 'vehicle_number_text'
    )
    list_filter = ('status', 'source', 'destination', 'receiving_date')
    inlines = [ParcelStatusHistoryInline, DeliveryAssignmentInline]


@admin.register(ParcelStatusHistory)
class ParcelStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('parcel', 'status', 'location', 'timestamp', 'updated_by')
    search_fields = ('parcel__consignment_number', 'status', 'location', 'remarks')
    list_filter = ('status', 'timestamp')


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('parcel', 'tempo', 'driver_name', 'destination_area', 'assigned_date', 'delivery_status')
    search_fields = ('parcel__consignment_number', 'driver_name', 'destination_area', 'tempo__vehicle_number')
    list_filter = ('delivery_status', 'assigned_date')
