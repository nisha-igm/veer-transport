from django import forms
from .models import Party, Vehicle, Parcel, ParcelStatusHistory, DeliveryAssignment


class ParcelForm(forms.ModelForm):
    """
    Form for registering and editing parcel consignments.
    """
    class Meta:
        model = Parcel
        fields = [
            'party', 'party_name_text', 'private_mark',
            'sender_name', 'sender_city', 'receiver_name', 'receiver_phone',
            'source', 'destination', 'package_count', 'goods_description', 'weight',
            'vehicle', 'vehicle_number_text', 'driver_name_text', 'driver_contact_text',
            'receiving_date', 'expected_delivery_date', 'status', 'remarks'
        ]
        widgets = {
            'party': forms.Select(attrs={'class': 'form-select', 'id': 'id_party'}),
            'party_name_text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. ABC Traders (if not selected from list)'}),
            'private_mark': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_private_mark', 'placeholder': 'e.g. ABC-458 / SURAT-TX'}),
            'sender_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Consignor Name / Mill'}),
            'sender_city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Surat'}),
            'receiver_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Consignee / Shop Name'}),
            'receiver_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'source': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Surat (Saroli)'}),
            'destination': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ahmedabad (Maskati Market / Kalupur / Narol)'}),
            'package_count': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'placeholder': '1'}),
            'goods_description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 10 Bales Synthetic Sarees, Grey Fabric'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.1', 'placeholder': 'Weight in kg'}),
            'vehicle': forms.Select(attrs={'class': 'form-select', 'id': 'id_vehicle'}),
            'vehicle_number_text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. GJ05BX1234'}),
            'driver_name_text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Driver Name'}),
            'driver_contact_text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Driver Phone'}),
            'receiving_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Handling instructions, gate pass info, payment remarks...'}),
        }

    def clean_package_count(self):
        count = self.cleaned_data.get('package_count')
        if count is None or count <= 0:
            raise forms.ValidationError("Package count must be at least 1.")
        return count

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is None or weight <= 0:
            raise forms.ValidationError("Weight must be greater than 0 kg.")
        return weight


class PartyForm(forms.ModelForm):
    """
    Form for registering and modifying parties / customers.
    """
    class Meta:
        model = Party
        fields = ['name', 'contact_person', 'phone', 'address', 'city', 'gst_number', 'private_mark']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Company or Firm Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Proprietor or Manager'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Number'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Full Office/Godown Address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Surat, Ahmedabad'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 24AAACG1234F1Z5 (Optional)'}),
            'private_mark': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. ABC-458'}),
        }


class VehicleForm(forms.ModelForm):
    """
    Form for registering and updating transport vehicles & delivery tempos.
    """
    class Meta:
        model = Vehicle
        fields = ['vehicle_number', 'vehicle_type', 'driver_name', 'driver_contact', 'capacity', 'current_location', 'status']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. GJ05BX1234'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Driver Full Name'}),
            'driver_contact': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mobile Number'}),
            'capacity': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 9.5 Tons / 400 Parcels'}),
            'current_location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Surat Ring Road Hub'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ParcelStatusUpdateForm(forms.ModelForm):
    """
    Quick status transition form with location and remarks history logging.
    """
    class Meta:
        model = ParcelStatusHistory
        fields = ['status', 'location', 'remarks']
        widgets = {
            'status': forms.Select(
                choices=Parcel.STATUS_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Current Hub / Location'}),
            'remarks': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Detailed status remarks (e.g. Unloaded at Ahmedabad Ring Road Hub, passed inspection)'}),
        }


class DeliveryAssignmentForm(forms.ModelForm):
    """
    Form to assign arrived parcels to local distribution tempos for last-mile delivery.
    """
    class Meta:
        model = DeliveryAssignment
        fields = ['parcel', 'tempo', 'driver_name', 'driver_contact', 'destination_area', 'delivery_status', 'notes']
        widgets = {
            'parcel': forms.Select(attrs={'class': 'form-select'}),
            'tempo': forms.Select(attrs={'class': 'form-select', 'id': 'id_distribution_tempo'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_tempo_driver', 'placeholder': 'Driver Name'}),
            'driver_contact': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_tempo_driver_contact', 'placeholder': 'Driver Contact'}),
            'destination_area': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Maskati Cloth Market, Kalupur, Ring Road'}),
            'delivery_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Gate pass details, receiver token number...'}),
        }
