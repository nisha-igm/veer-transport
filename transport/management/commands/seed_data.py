import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from transport.models import Party, Vehicle, Parcel, ParcelStatusHistory, DeliveryAssignment


class Command(BaseCommand):
    help = "Populate the database with realistic Veer Transport sample data (Surat to Ahmedabad corridor)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Veer Transport database (Surat ➔ Ahmedabad line)..."))

        # 1. Ensure Superuser exists
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@veertransport.local",
                "first_name": "Veer",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created with password 'admin123'."))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 2. Seed Parties / Customers (Surat Mills & Ahmedabad Traders)
        parties_data = [
            {
                "name": "ABC Traders",
                "contact_person": "Ramesh Patel",
                "phone": "+91 98250 11223",
                "address": "Shop 104, New Textile Market, Ring Road",
                "city": "Surat",
                "gst_number": "24AAACG1234F1Z5",
                "private_mark": "ABC-458",
            },
            {
                "name": "Shree Ganesh Synthetics",
                "contact_person": "Sanjay Shah",
                "phone": "+91 98795 44332",
                "address": "Plot 42, GIDC Pandesara",
                "city": "Surat",
                "gst_number": "24AABCS5678K1Z2",
                "private_mark": "SGS-902",
            },
            {
                "name": "Radhe Krishna Textile Mills",
                "contact_person": "Ghanshyam Agarwal",
                "phone": "+91 94260 88990",
                "address": "B-12 Millennium Textile Market, Ring Road",
                "city": "Surat",
                "gst_number": "24AAECR7788P1Z8",
                "private_mark": "RKM-101",
            },
            {
                "name": "Ahmedabad Saree Niketan",
                "contact_person": "Kishore Bhai",
                "phone": "+91 98980 33221",
                "address": "22 Maskati Cloth Market, Kalupur",
                "city": "Ahmedabad",
                "gst_number": "24AAHCA4455L1Z3",
                "private_mark": "ASN-330",
            },
            {
                "name": "Karnavati Cloth Store",
                "contact_person": "Mahesh Prajapati",
                "phone": "+91 98240 66554",
                "address": "108 New Cloth Market, Sarangpur",
                "city": "Ahmedabad",
                "gst_number": "24AAACK7788J1Z6",
                "private_mark": "KCS-712",
            },
            {
                "name": "Royal Diamond Tools & Machinery",
                "contact_person": "Paresh Savani",
                "phone": "+91 97270 55441",
                "address": "Mini Bazaar, Varachha Road",
                "city": "Surat",
                "gst_number": "24AARPD2233N1Z7",
                "private_mark": "RDT-555",
            },
            {
                "name": "Narol Dyeing & Processing Fabrics",
                "contact_person": "Vikram Desai",
                "phone": "+91 98790 12345",
                "address": "Phase 2, GIDC Narol",
                "city": "Ahmedabad",
                "gst_number": "24AABCN9922K1Z0",
                "private_mark": "NDF-440",
            },
            {
                "name": "Mahalaxmi Handloom & Sarees",
                "contact_person": "Dinesh Gupta",
                "phone": "+91 94280 44556",
                "address": "15 Revdi Bazaar, Kalupur",
                "city": "Ahmedabad",
                "gst_number": "24AAECM3344P1Z4",
                "private_mark": "MHS-880",
            },
        ]

        party_objs = {}
        for pdata in parties_data:
            party, _ = Party.objects.get_or_create(
                name=pdata["name"],
                defaults=pdata
            )
            party_objs[party.name] = party

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(party_objs)} trading parties."))

        # 3. Seed Vehicles (Surat ➔ Ahmedabad Line Trucks & Ahmedabad Local Tempos)
        vehicles_data = [
            {
                "vehicle_number": "GJ05BX1234",
                "vehicle_type": "HEAVY_TRUCK",
                "driver_name": "Jagdish Bhai Patel",
                "driver_contact": "+91 98251 10001",
                "capacity": "12 Tons / 450 Bales",
                "current_location": "Saroli Godown, Surat",
                "status": "IN_TRANSIT",
            },
            {
                "vehicle_number": "GJ05TR8899",
                "vehicle_type": "HEAVY_TRUCK",
                "driver_name": "Iqbal Khan",
                "driver_contact": "+91 98252 20002",
                "capacity": "10 Tons / 380 Packages",
                "current_location": "Ahmedabad Ring Road Hub",
                "status": "LOADED",
            },
            {
                "vehicle_number": "GJ01TM4512",
                "vehicle_type": "TEMPO",
                "driver_name": "Raju Parmar",
                "driver_contact": "+91 98790 40004",
                "capacity": "1.5 Tons / 50 Boxes",
                "current_location": "Ahmedabad Maskati Hub",
                "status": "IN_TRANSIT",
            },
            {
                "vehicle_number": "GJ01TT8900",
                "vehicle_type": "MINI_TRUCK",
                "driver_name": "Haresh Solanki",
                "driver_contact": "+91 98791 50005",
                "capacity": "2.5 Tons / 90 Boxes",
                "current_location": "Ahmedabad Kalupur",
                "status": "AVAILABLE",
            },
            {
                "vehicle_number": "GJ01NX3344",
                "vehicle_type": "TEMPO",
                "driver_name": "Bhavesh Vaghela",
                "driver_contact": "+91 98793 70007",
                "capacity": "1.8 Tons / 60 Bales",
                "current_location": "Ahmedabad Narol Hub",
                "status": "AVAILABLE",
            },
            {
                "vehicle_number": "GJ06EL1001",
                "vehicle_type": "E_LOADER",
                "driver_name": "Nilesh Barot",
                "driver_contact": "+91 98792 60006",
                "capacity": "800 kg / 25 Packages",
                "current_location": "Godown No 14 15, Saroli, Surat",
                "status": "AVAILABLE",
            },
        ]

        vehicle_objs = {}
        for vdata in vehicles_data:
            veh, _ = Vehicle.objects.get_or_create(
                vehicle_number=vdata["vehicle_number"],
                defaults=vdata
            )
            vehicle_objs[veh.vehicle_number] = veh

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(vehicle_objs)} line trucks & local delivery tempos."))

        # 4. Seed Realistic Parcels (Surat to Ahmedabad ONLY)
        now = timezone.now()

        parcels_seed = [
            {
                "consignment_number": "TRN20260001",
                "party": party_objs["ABC Traders"],
                "private_mark": "ABC-458",
                "sender_name": "ABC Traders (Mill Div)",
                "sender_city": "Surat",
                "receiver_name": "Ahmedabad Saree Niketan",
                "receiver_phone": "+91 98980 33221",
                "source": "Surat (Saroli)",
                "destination": "Ahmedabad (Maskati Market)",
                "package_count": 25,
                "goods_description": "Textile Material - Cotton Printed Sarees",
                "weight": Decimal("380.50"),
                "vehicle": vehicle_objs["GJ05BX1234"],
                "receiving_date": (now - datetime.timedelta(days=2)).date(),
                "expected_delivery_date": (now + datetime.timedelta(days=1)).date(),
                "status": "IN_TRANSIT",
                "remarks": "Received at Godown 14-15 Saroli. Priority delivery to Maskati Cloth Market.",
                "history": [
                    ("RECEIVED", "Godown 14 15, Kewal Estate, Saroli, Surat", "Goods received from mill with 25 bales.", now - datetime.timedelta(days=2, hours=4)),
                    ("SORTED", "Saroli Godown Bay 2", "Inspected, private mark ABC-458 verified.", now - datetime.timedelta(days=1, hours=20)),
                    ("VEHICLE_ASSIGNED", "Surat Saroli Yard", "Loaded into line truck GJ05BX1234 under driver Jagdish Bhai.", now - datetime.timedelta(days=1, hours=10)),
                    ("IN_TRANSIT", "NH-48 Express Highway", "Line truck in transit Surat to Ahmedabad.", now - datetime.timedelta(hours=6)),
                ]
            },
            {
                "consignment_number": "TRN20260002",
                "party": party_objs["Shree Ganesh Synthetics"],
                "private_mark": "SGS-902",
                "sender_name": "Shree Ganesh Synthetics",
                "sender_city": "Surat",
                "receiver_name": "Karnavati Cloth Store",
                "receiver_phone": "+91 98240 66554",
                "source": "Surat (Saroli)",
                "destination": "Ahmedabad (Sarangpur New Cloth Market)",
                "package_count": 40,
                "goods_description": "Polyester Georgette & Chiffon Dress Materials",
                "weight": Decimal("620.00"),
                "vehicle": vehicle_objs["GJ05TR8899"],
                "receiving_date": (now - datetime.timedelta(days=3)).date(),
                "expected_delivery_date": (now - datetime.timedelta(days=1)).date(),
                "status": "DELIVERED",
                "remarks": "Delivered to Sarangpur New Cloth Market against signed LR copy.",
                "history": [
                    ("RECEIVED", "Godown 14 15, Kewal Estate, Saroli, Surat", "Received 40 packages from Pandesara factory.", now - datetime.timedelta(days=3)),
                    ("SORTED", "Saroli Godown", "Sorted for Ahmedabad direct night dispatch.", now - datetime.timedelta(days=2, hours=18)),
                    ("VEHICLE_ASSIGNED", "Surat Saroli Yard", "Loaded on GJ05TR8899.", now - datetime.timedelta(days=2, hours=12)),
                    ("IN_TRANSIT", "Ahmedabad Ring Road Toll", "Vehicle arrived at Ahmedabad hub.", now - datetime.timedelta(days=1, hours=14)),
                    ("OUT_FOR_DELIVERY", "Ahmedabad Central Hub", "Loaded in tempo for Sarangpur market.", now - datetime.timedelta(days=1, hours=4)),
                    ("DELIVERED", "Sarangpur New Cloth Market", "Delivered to Mahesh Prajapati with signature and stamp.", now - datetime.timedelta(days=1)),
                ]
            },
            {
                "consignment_number": "TRN20260003",
                "party": party_objs["Radhe Krishna Textile Mills"],
                "private_mark": "RKM-101",
                "sender_name": "Radhe Krishna Textile Mills",
                "sender_city": "Surat",
                "receiver_name": "Mahalaxmi Handloom & Sarees",
                "receiver_phone": "+91 94280 44556",
                "source": "Surat (Saroli)",
                "destination": "Ahmedabad (Kalupur Market)",
                "package_count": 50,
                "goods_description": "Jacquard Silk Weaving Rolls & Raw Grey Fabric",
                "weight": Decimal("980.00"),
                "vehicle": vehicle_objs["GJ05TR8899"],
                "receiving_date": (now - datetime.timedelta(days=1)).date(),
                "expected_delivery_date": (now + datetime.timedelta(days=1)).date(),
                "status": "SORTED",
                "remarks": "Heavy consignment for Kalupur wholesale merchant.",
                "history": [
                    ("RECEIVED", "Godown 14 15, Kewal Estate, Saroli, Surat", "Consignment booked at Saroli desk.", now - datetime.timedelta(days=1, hours=8)),
                    ("SORTED", "Saroli Godown Bay 1", "Sorted and staged for Ahmedabad night truck.", now - datetime.timedelta(hours=14)),
                ]
            },
            {
                "consignment_number": "TRN20260004",
                "party": party_objs["Royal Diamond Tools & Machinery"],
                "private_mark": "RDT-555",
                "sender_name": "Royal Diamond Tools",
                "sender_city": "Surat",
                "receiver_name": "Narol Dyeing & Processing Fabrics",
                "receiver_phone": "+91 98790 12345",
                "source": "Surat (Saroli)",
                "destination": "Ahmedabad (Narol GIDC)",
                "package_count": 12,
                "goods_description": "Textile Machinery Parts & Diamond Cutting Tools",
                "weight": Decimal("145.00"),
                "vehicle": vehicle_objs["GJ01TM4512"],
                "receiving_date": now.date(),
                "expected_delivery_date": now.date(),
                "status": "OUT_FOR_DELIVERY",
                "remarks": "Express machinery delivery for Narol GIDC unit.",
                "history": [
                    ("RECEIVED", "Godown 14 15, Kewal Estate, Saroli, Surat", "Booked by Paresh Savani.", now - datetime.timedelta(hours=10)),
                    ("SORTED", "Saroli Godown", "Priority staging for Ahmedabad tempo.", now - datetime.timedelta(hours=8)),
                    ("VEHICLE_ASSIGNED", "Saroli Yard", "Line truck to Ahmedabad Ring Road Hub.", now - datetime.timedelta(hours=6)),
                    ("OUT_FOR_DELIVERY", "Ahmedabad Narol Hub", "Loaded in Tempo GJ01TM4512 with Driver Raju Parmar.", now - datetime.timedelta(hours=2)),
                ]
            },
            {
                "consignment_number": "TRN20260005",
                "party": party_objs["Mahalaxmi Handloom & Sarees"],
                "private_mark": "MHS-880",
                "sender_name": "Shreeji Weaving Mills",
                "sender_city": "Surat",
                "receiver_name": "Mahalaxmi Handloom & Sarees",
                "receiver_phone": "+91 94280 44556",
                "source": "Surat (Saroli)",
                "destination": "Ahmedabad (Revdi Bazaar, Kalupur)",
                "package_count": 35,
                "goods_description": "Pure Cotton Zari Border Sarees & Bales",
                "weight": Decimal("440.00"),
                "vehicle": vehicle_objs["GJ05BX1234"],
                "receiving_date": now.date(),
                "expected_delivery_date": (now + datetime.timedelta(days=1)).date(),
                "status": "RECEIVED",
                "remarks": "Booked at Godown 14 15 Saroli. Staging for Ahmedabad dispatch.",
                "history": [
                    ("RECEIVED", "Godown 14 15, Kewal Estate, Saroli, Surat", "35 bales received and tagged with MHS-880 mark.", now - datetime.timedelta(hours=3)),
                ]
            },
        ]

        for pdata in parcels_seed:
            history_list = pdata.pop("history", [])
            parcel, created = Parcel.objects.get_or_create(
                consignment_number=pdata["consignment_number"],
                defaults=pdata
            )
            if created or parcel.status_history.count() <= 1:
                parcel.status_history.all().delete()
                for st, loc, rem, tstamp in history_list:
                    ParcelStatusHistory.objects.create(
                        parcel=parcel,
                        status=st,
                        location=loc,
                        remarks=rem,
                        timestamp=tstamp,
                        updated_by=admin_user
                    )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(parcels_seed)} consignments on Surat ➔ Ahmedabad route."))

        # 5. Seed Local Distribution Assignments (Ahmedabad delivery markets)
        p_narol = Parcel.objects.filter(consignment_number="TRN20260004").first()
        if p_narol:
            DeliveryAssignment.objects.get_or_create(
                parcel=p_narol,
                defaults={
                    "tempo": vehicle_objs["GJ01TM4512"],
                    "driver_name": "Raju Parmar",
                    "driver_contact": "+91 98790 40004",
                    "destination_area": "Narol GIDC Phase 2, Ahmedabad",
                    "delivery_status": "OUT_FOR_DELIVERY",
                    "notes": "Gate Pass #AHM-9021. Delivery to Vikram Desai.",
                }
            )

        p_sarangpur = Parcel.objects.filter(consignment_number="TRN20260002").first()
        if p_sarangpur:
            DeliveryAssignment.objects.get_or_create(
                parcel=p_sarangpur,
                defaults={
                    "tempo": vehicle_objs["GJ01TT8900"],
                    "driver_name": "Haresh Solanki",
                    "driver_contact": "+91 98791 50005",
                    "destination_area": "New Cloth Market, Sarangpur, Ahmedabad",
                    "delivery_status": "COMPLETED",
                    "notes": "Delivered successfully. Signed LR copy collected.",
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded local Ahmedabad tempo distribution assignments."))
        self.stdout.write(self.style.SUCCESS("[OK] All Veer Transport seed data successfully generated!"))
