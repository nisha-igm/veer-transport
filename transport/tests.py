import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Party, Vehicle, Parcel, ParcelStatusHistory, DeliveryAssignment


class TransportSystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create staff user
        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True,
            is_superuser=True
        )

        # Create sample Party
        self.party = Party.objects.create(
            name="ABC Traders",
            contact_person="Ramesh Patel",
            phone="+91 98250 11223",
            address="Shop 104, New Textile Market, Ring Road",
            city="Surat",
            gst_number="24AAACG1234F1Z5",
            private_mark="ABC-458"
        )

        # Create sample Vehicle
        self.vehicle = Vehicle.objects.create(
            vehicle_number="GJ05BX1234",
            vehicle_type="HEAVY_TRUCK",
            driver_name="Jagdish Bhai Patel",
            driver_contact="+91 98251 10001",
            capacity="12 Tons",
            current_location="Surat Main Hub",
            status="AVAILABLE"
        )

        # Create sample Tempo
        self.tempo = Vehicle.objects.create(
            vehicle_number="GJ01TM4512",
            vehicle_type="TEMPO",
            driver_name="Raju Parmar",
            driver_contact="+91 98790 40004",
            capacity="1.5 Tons",
            current_location="Ahmedabad Hub",
            status="AVAILABLE"
        )

        # Create sample Parcel
        self.parcel = Parcel.objects.create(
            party=self.party,
            private_mark="ABC-458",
            sender_name="ABC Traders (Mill Div)",
            sender_city="Surat",
            receiver_name="Ahmedabad Saree Niketan",
            receiver_phone="+91 98980 33221",
            source="Surat",
            destination="Ahmedabad",
            package_count=25,
            goods_description="Cotton Printed Sarees",
            weight=Decimal("380.50"),
            vehicle=self.vehicle,
            receiving_date=timezone.now().date(),
            status="RECEIVED",
            remarks="Handle with care"
        )

    def test_consignment_number_generation(self):
        """Test that consignment number is generated automatically with TRN prefix."""
        self.assertTrue(self.parcel.consignment_number.startswith("TRN"))
        self.assertEqual(len(self.parcel.consignment_number), 11)  # TRN20260001

        # Create another parcel to verify sequence
        p2 = Parcel.objects.create(
            party=self.party,
            private_mark="ABC-458",
            sender_name="Sender",
            receiver_name="Receiver",
            receiver_phone="1234567890",
            source="Surat",
            destination="Mumbai",
            package_count=5,
            goods_description="Silk Bales",
            weight=Decimal("100.00"),
        )
        self.assertTrue(p2.consignment_number.startswith("TRN"))
        self.assertNotEqual(self.parcel.consignment_number, p2.consignment_number)

    def test_party_and_private_mark_separation(self):
        """Verify Party Name and Private Mark are separate fields."""
        self.assertEqual(self.party.name, "ABC Traders")
        self.assertEqual(self.party.private_mark, "ABC-458")
        self.assertEqual(self.parcel.private_mark, "ABC-458")

    def test_initial_status_history_creation(self):
        """Test that creating a parcel automatically creates initial history entry."""
        histories = self.parcel.status_history.all()
        self.assertEqual(histories.count(), 1)
        self.assertEqual(histories.first().status, "RECEIVED")

    def test_public_homepage(self):
        """Verify public homepage loads successfully."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VEER TRANSPORT", html=False)
        self.assertContains(response, "Kewal Estate, Saroli, Surat", html=False)

    def test_public_tracking(self):
        """Verify public tracking search finds consignment and displays journey steps."""
        response = self.client.get(reverse('public_tracking') + f"?q={self.parcel.consignment_number}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.parcel.consignment_number)
        self.assertContains(response, "ABC-458")
        self.assertContains(response, "Surat")
        self.assertContains(response, "Ahmedabad")

    def test_public_tracking_invalid(self):
        """Verify public tracking handles unknown consignment numbers gracefully."""
        response = self.client.get(reverse('public_tracking') + "?q=INVALID123")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No consignment found with tracking number")

    def test_protected_views_require_login(self):
        """Verify dashboard and management views redirect unauthenticated users."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_login'), response.url)

    def test_staff_login_and_dashboard(self):
        """Verify staff login works and dashboard metrics are computed."""
        logged_in = self.client.login(username="admin", password="admin123")
        self.assertTrue(logged_in)

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Parcels")
        self.assertContains(response, "Status Distribution")

    def test_parcel_creation_form(self):
        """Test staff creating a new parcel via form."""
        self.client.login(username="admin", password="admin123")
        data = {
            'party': self.party.pk,
            'party_name_text': 'ABC Traders',
            'private_mark': 'ABC-458',
            'sender_name': 'Surat Textile Mill',
            'sender_city': 'Surat',
            'receiver_name': 'Delhi Merchant',
            'receiver_phone': '+91 98110 55443',
            'source': 'Surat (Saroli)',
            'destination': 'Ahmedabad (Maskati Market)',
            'package_count': 15,
            'goods_description': 'Synthetic Sarees',
            'weight': '220.00',
            'vehicle': self.vehicle.pk,
            'receiving_date': timezone.now().date().strftime('%Y-%m-%d'),
            'status': 'RECEIVED',
            'remarks': 'Express delivery requested'
        }
        response = self.client.post(reverse('parcel_create'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Parcel.objects.filter(destination='Ahmedabad (Maskati Market)').exists())

    def test_status_update_and_history_logging(self):
        """Test transitioning parcel status and verifying audit history record."""
        self.client.login(username="admin", password="admin123")
        data = {
            'status': 'IN_TRANSIT',
            'location': 'Bharuch Toll Station',
            'remarks': 'Truck cleared Gujarat border checkpoint.'
        }
        response = self.client.post(reverse('update_parcel_status', kwargs={'pk': self.parcel.pk}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.parcel.refresh_from_db()
        self.assertEqual(self.parcel.status, 'IN_TRANSIT')
        self.assertEqual(self.parcel.status_history.count(), 2)
        latest_hist = self.parcel.status_history.first()
        self.assertEqual(latest_hist.status, 'IN_TRANSIT')
        self.assertEqual(latest_hist.location, 'Bharuch Toll Station')

    def test_local_distribution_assignment(self):
        """Test assigning parcel to a local distribution tempo."""
        self.client.login(username="admin", password="admin123")
        data = {
            'parcel': self.parcel.pk,
            'tempo': self.tempo.pk,
            'driver_name': 'Raju Parmar',
            'driver_contact': '+91 98790 40004',
            'destination_area': 'Maskati Cloth Market, Kalupur',
            'delivery_status': 'OUT_FOR_DELIVERY',
            'notes': 'Doorstep handoff'
        }
        response = self.client.post(reverse('distribution_list'), data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.parcel.refresh_from_db()
        self.assertEqual(self.parcel.status, 'OUT_FOR_DELIVERY')
        self.assertTrue(DeliveryAssignment.objects.filter(parcel=self.parcel).exists())

    def test_printable_receipt(self):
        """Test printable consignment receipt view."""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse('parcel_receipt', kwargs={'pk': self.parcel.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.parcel.consignment_number)
        self.assertContains(response, "CONSIGNMENT NOTE / BILTI")
        self.assertContains(response, "TERMS &amp; CONDITIONS")

    def test_party_crud(self):
        """Test party creation, update, and detail view."""
        self.client.login(username="admin", password="admin123")
        # Create
        response = self.client.post(reverse('party_create'), {
            'name': 'New Gujarat Silks',
            'contact_person': 'Pravin Bhai',
            'phone': '+91 98980 99887',
            'address': 'Ring Road, Surat',
            'city': 'Surat',
            'gst_number': '24AABCN1234K1Z9',
            'private_mark': 'NGS-100',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        party = Party.objects.get(name='New Gujarat Silks')
        self.assertEqual(party.private_mark, 'NGS-100')

        # Detail
        detail_res = self.client.get(reverse('party_detail', kwargs={'pk': party.pk}))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, 'New Gujarat Silks')

    def test_vehicle_crud(self):
        """Test vehicle creation and detail view."""
        self.client.login(username="admin", password="admin123")
        response = self.client.post(reverse('vehicle_create'), {
            'vehicle_number': 'GJ05ZZ9988',
            'vehicle_type': 'TEMPO',
            'driver_name': 'Mohan Lal',
            'driver_contact': '+91 98250 99887',
            'capacity': '2 Tons',
            'current_location': 'Surat Yard',
            'status': 'AVAILABLE',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vehicle.objects.filter(vehicle_number='GJ05ZZ9988').exists())
