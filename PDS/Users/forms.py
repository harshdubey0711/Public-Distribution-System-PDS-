from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from .models import FPS, FPSProfile, FPSInventory
from django import forms
from django.contrib.auth.models import User
from .models import FPS, FPSInventory, FPSProfile

class FPSRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, help_text="Enter a unique username.")
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = FPS
        fields = ['name', 'fps_code', 'contact_number', 'address', 'state', 'district', 'pincode']

    def clean(self):
        """Check if passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        fps = super().save(commit=False)

        # Create user account
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        if commit:
            fps.save()

            # Create FPS Inventory
            FPSInventory.objects.create(fps_id=fps.id)

            # Create FPS Profile
            FPSProfile.objects.create(
                user=user,
                fps=fps,
                profile_picture=self.cleaned_data.get('profile_picture')
            )

        return fps




class Registration(forms.ModelForm):
    class Meta:
        model = Beneficiaries
        fields = [
            "beneficiary_name",
            "beneficiary_phone",
            "beneficiary_card_no",
            "beneficiary_email",
            "beneficiary_aadhaar",
        ]

class Ration_admin(forms.ModelForm):
    class Meta:
        model = Ration_Card
        fields = [
            "beneficiary_card_no",
            "ration_card_beneficiary_name",
            "b_ration_address",
            "b_ration_state",
            "b_ration_pincode",
            "b_ration_family_size",
            "b_ration_family",
        ]

# class Admin_registration(UserCreationForm):
#     class Meta:
#         model = Admin_model
#         fields = [
#             "admin_name",
#             "admin_email",
#             "admin_password",
#         ]


class BeneficiaryProfileForm(forms.ModelForm):
    class Meta:
        model = Beneficiaries
        fields = [
            'beneficiary_name',
            'beneficiary_email',
            'beneficiary_phone',
            'beneficiary_address',
            'beneficiary_state',
            'beneficiary_pincode',
        ]
        

class FPSLoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
