import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Party(models.Model):
    """
    Represents a client / trading party / customer consignor or consignee.
    """
    name = models.CharField(max_length=150, verbose_name="Party Name")
    contact_person = models.CharField(max_length=100, verbose_name="Contact Person")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    address = models.TextField(verbose_name="Address")
    city = models.CharField(max_length=100, verbose_name="City")
    gst_number = models.CharField(max_length=20, blank=True, verbose_name="GST Number")
    private_mark = models.CharField(
        max_length=100,
        verbose_name="Private Mark",
        help_text="Standard private identification mark used for this party's parcels (e.g. ABC-458)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Party / Customer"
        verbose_name_plural = "Parties / Customers"

    def __str__(self):
        return f"{self.name} ({self.private_mark})"

    @property
    def total_parcels(self):
        return self.parcels.count()

    @property
    def active_parcels(self):
        return self.parcels.exclude(status__in=['DELIVERED', 'CANCELLED']).count()


class Vehicle(models.Model):
    """
    Represents heavy line transport trucks (Surat line) and local delivery tempos.
    """
    TYPE_CHOICES = [
        ('HEAVY_TRUCK', 'Heavy Line Truck (Surat Main Line)'),
        ('TEMPO', 'Local Distribution Tempo'),
        ('MINI_TRUCK', 'Mini Truck / Pickup'),
        ('CONTAINER', 'Container Trailer'),
        ('E_LOADER', 'Electric Mini Loader'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available / Ready'),
        ('LOADED', 'Loaded'),
        ('IN_TRANSIT', 'In Transit'),
        ('UNDER_MAINTENANCE', 'Under Maintenance'),
    ]

    vehicle_number = models.CharField(max_length=30, unique=True, verbose_name="Vehicle Number")
    vehicle_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='TEMPO', verbose_name="Vehicle Type")
    driver_name = models.CharField(max_length=100, verbose_name="Driver Name")
    driver_contact = models.CharField(max_length=20, verbose_name="Driver Contact")
    capacity = models.CharField(max_length=50, verbose_name="Load Capacity", help_text="e.g. 9.5 Tons / 400 Boxes")
    current_location = models.CharField(max_length=100, default="Saroli Godown, Surat", verbose_name="Current Location")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='AVAILABLE', verbose_name="Availability Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['vehicle_number']
        verbose_name = "Vehicle / Tempo"
        verbose_name_plural = "Vehicles / Fleet"

    def __str__(self):
        return f"{self.vehicle_number} - {self.driver_name} ({self.get_vehicle_type_display()})"

    @property
    def active_parcels_count(self):
        return self.assigned_parcels.exclude(status__in=['DELIVERED', 'CANCELLED']).count()


class Parcel(models.Model):
    """
    Main consignment / parcel record tracking goods from arrival (Surat Saroli godown) to Ahmedabad.
    """
    STATUS_CHOICES = [
        ('RECEIVED', 'Goods Received'),
        ('SORTED', 'Sorted & Staged'),
        ('VEHICLE_ASSIGNED', 'Vehicle Assigned'),
        ('IN_TRANSIT', 'In Transit'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    consignment_number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Consignment / LR Number",
        help_text="Unique transport identification number, e.g. TRN20260001"
    )
    party = models.ForeignKey(
        Party,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parcels",
        verbose_name="Party / Client"
    )
    # Party Name & Private Mark are explicitly distinct fields as required
    party_name_text = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Party Name",
        help_text="Direct party name if not selecting an existing party"
    )
    private_mark = models.CharField(
        max_length=100,
        verbose_name="Private Mark",
        help_text="Crucial private mark on cartons/bales (e.g. ABC-458, SGT-991)"
    )
    sender_name = models.CharField(max_length=150, verbose_name="Sender Name (Consignor)")
    sender_city = models.CharField(max_length=100, default="Surat", verbose_name="Sender City")
    receiver_name = models.CharField(max_length=150, verbose_name="Receiver Name (Consignee)")
    receiver_phone = models.CharField(max_length=20, verbose_name="Receiver Contact Number")
    source = models.CharField(max_length=100, default="Surat", verbose_name="Source / Origin")
    destination = models.CharField(max_length=100, default="Ahmedabad", verbose_name="Destination Hub / City")
    package_count = models.PositiveIntegerField(default=1, verbose_name="Number of Packages / Bales")
    goods_description = models.CharField(
        max_length=255,
        verbose_name="Goods Description",
        help_text="e.g. Textile Sarees, Yarn spools, Diamond machinery parts"
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Weight (kg)")
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_parcels",
        verbose_name="Assigned Vehicle"
    )
    vehicle_number_text = models.CharField(max_length=30, blank=True, verbose_name="Vehicle Number (Manual / External)")
    driver_name_text = models.CharField(max_length=100, blank=True, verbose_name="Driver Name")
    driver_contact_text = models.CharField(max_length=20, blank=True, verbose_name="Driver Contact")
    receiving_date = models.DateField(default=timezone.now, verbose_name="Receiving Date")
    expected_delivery_date = models.DateField(null=True, blank=True, verbose_name="Expected Delivery Date")
    actual_delivery_date = models.DateTimeField(null=True, blank=True, verbose_name="Actual Delivery Date")
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='RECEIVED',
        verbose_name="Current Status"
    )
    remarks = models.TextField(blank=True, verbose_name="Remarks / Special Handling Instructions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-receiving_date', '-created_at']
        verbose_name = "Parcel / Consignment"
        verbose_name_plural = "Parcels / Consignments"

    def __str__(self):
        return f"{self.consignment_number} - {self.get_party_display()} ({self.private_mark})"

    def get_party_display(self):
        if self.party:
            return self.party.name
        return self.party_name_text or "General Consignment"

    def get_effective_vehicle_number(self):
        if self.vehicle:
            return self.vehicle.vehicle_number
        return self.vehicle_number_text or "Not Assigned"

    def get_effective_driver(self):
        if self.vehicle:
            return f"{self.vehicle.driver_name} ({self.vehicle.driver_contact})"
        if self.driver_name_text:
            return f"{self.driver_name_text} ({self.driver_contact_text})"
        return "Not Assigned"

    @classmethod
    def generate_next_consignment_number(cls):
        """
        Generates sequential unique consignment number: TRN<YEAR><0001>
        Example: TRN20260001, TRN20260002
        """
        current_year = timezone.now().year
        prefix = f"TRN{current_year}"
        latest = cls.objects.filter(consignment_number__startswith=prefix).order_by('-consignment_number').first()

        if latest:
            try:
                # Extract numerical suffix
                suffix = int(latest.consignment_number[len(prefix):])
                next_seq = suffix + 1
            except (ValueError, IndexError):
                next_seq = cls.objects.filter(consignment_number__startswith=prefix).count() + 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:04d}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.consignment_number:
            self.consignment_number = self.generate_next_consignment_number()
        
        # If party is assigned, sync party name if blank
        if self.party and not self.party_name_text:
            self.party_name_text = self.party.name
        if self.party and not self.private_mark:
            self.private_mark = self.party.private_mark

        # If vehicle is assigned, sync vehicle text
        if self.vehicle:
            self.vehicle_number_text = self.vehicle.vehicle_number
            self.driver_name_text = self.vehicle.driver_name
            self.driver_contact_text = self.vehicle.driver_contact

        if self.status == 'DELIVERED' and not self.actual_delivery_date:
            self.actual_delivery_date = timezone.now()

        super().save(*args, **kwargs)

        # Log initial history if newly created
        if is_new:
            ParcelStatusHistory.objects.create(
                parcel=self,
                status=self.status,
                location=self.source,
                remarks=self.remarks or "Goods received at transport booking office."
            )


class ParcelStatusHistory(models.Model):
    """
    Maintains a full audit trail of parcel movements and milestones.
    """
    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Parcel"
    )
    status = models.CharField(max_length=50, verbose_name="Status")
    location = models.CharField(max_length=150, blank=True, verbose_name="Location / Depot")
    remarks = models.TextField(blank=True, verbose_name="Remarks / Update Notes")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Timestamp")
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Updated By"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Parcel Status History"
        verbose_name_plural = "Parcel Status Histories"

    def __str__(self):
        return f"{self.parcel.consignment_number} -> {self.status} at {self.timestamp.strftime('%d-%m-%Y %H:%M')}"


class DeliveryAssignment(models.Model):
    """
    Local distribution module:
    Maps goods arriving on line trucks (e.g. from Surat) to local tempos for door/destination delivery.
    """
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned to Tempo'),
        ('LOADED', 'Loaded into Tempo'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('COMPLETED', 'Delivered to Party'),
        ('FAILED', 'Delivery Failed / Rescheduled'),
    ]

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name="delivery_assignments",
        verbose_name="Consignment / Parcel"
    )
    tempo = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tempo_assignments",
        verbose_name="Local Tempo / Vehicle"
    )
    driver_name = models.CharField(max_length=100, verbose_name="Local Driver Name")
    driver_contact = models.CharField(max_length=20, verbose_name="Driver Phone")
    destination_area = models.CharField(max_length=150, verbose_name="Local Delivery Area / Market")
    assigned_date = models.DateTimeField(default=timezone.now, verbose_name="Assignment Date & Time")
    delivery_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='ASSIGNED',
        verbose_name="Distribution Status"
    )
    notes = models.TextField(blank=True, verbose_name="Distribution Notes / Gate Pass Info")

    class Meta:
        ordering = ['-assigned_date']
        verbose_name = "Delivery / Distribution Assignment"
        verbose_name_plural = "Delivery / Distribution Assignments"

    def __str__(self):
        return f"Distribution: {self.parcel.consignment_number} -> Tempo {self.tempo} ({self.delivery_status})"
