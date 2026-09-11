# Veer Transport - Surat to Ahmedabad Parcel Management System

A complete, production-ready, full-stack **Transport & Parcel Management System** built with **Python Django**, **HTML5/CSS3/Vanilla JavaScript**, and **SQLite**.

Designed specifically for **Veer Transport**, managing daily dedicated freight operations exclusively on the **Surat (Saroli Godown) ➔ Ahmedabad** commercial corridor and local tempo distributions across Ahmedabad wholesale markets (Maskati Cloth Market, Kalupur, New Cloth Market, Sarangpur, Narol GIDC).

---

## 📍 Business & Operational Details

- **Company Name**: **Veer Transport**
- **Operating Corridor**: **Surat ➔ Ahmedabad ONLY**
- **Booking Office & Godown**: **Godown No 14 15, Kewal Estate, Saroli, Surat, Gujarat**
- **Working Hours**: **Mon – Sat: 8:00 AM – 9:00 PM (Sunday Closed)**
- **Key Distribution Hubs**:
  - Maskati Cloth Market, Ahmedabad
  - New Cloth Market, Sarangpur, Ahmedabad
  - Kalupur Wholesale Market, Ahmedabad
  - Narol GIDC / Odhav Industrial Hub

---

## Key Features

1. **Public Consignment Tracking Portal (`/track/`)**:
   - Clean milestone stepper: `Received -> Sorted -> Vehicle Assigned -> In Transit -> Out for Delivery -> Delivered`
   - Real-time sanitized tracking without exposing internal billing or confidential logs.
2. **Staff Dashboard (`/dashboard/`)**:
   - Real-time KPI summary cards: Total Parcels, Today's Received, Pending, Delivered, Active Parties, Fleet.
   - Interactive zero-dependency SVG charts: Daily Intake Trends, Status Distribution Donut, Top Ahmedabad Hubs.
3. **Goods & Consignment Entry (`/parcels/new/`)**:
   - Automated sequential Consignment / Lorry Receipt (LR) number generation (`TRN20260001`).
   - Distinct **Party Name** and **Private Mark** fields (e.g. *ABC Traders* with Private Mark *ABC-458*).
   - Dynamic Vanilla JS auto-fill for private marks and driver contacts.
4. **Local Delivery & Distribution Hub (`/distribution/`)**:
   - Dedicated module for last-mile delivery: `Surat Line Truck -> Unload/Sorted -> Local Tempo -> Ahmedabad Destination Market`.
5. **Printable Lorry Receipt / Bilti (`/parcels/<id>/receipt/`)**:
   - Formatted for clean A4 and receipt slip printing via `@media print` CSS.
6. **Party & Fleet Management (`/parties/`, `/vehicles/`)**:
   - 360-degree views with associated parcel manifests.

---

## Quick Start Guide

### 1. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Seed Veer Transport Demo Data
Run the custom seed command to populate realistic Surat ➔ Ahmedabad transport records, line trucks, and create the default admin account:
```bash
python manage.py seed_data
```

* **Default Admin Username**: `admin`
* **Default Admin Password**: `admin123`

### 3. Start the Server
```bash
python manage.py runserver
```

Open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 4. Run Automated Tests
```bash
python manage.py test
```
