from django.conf import settings
from django.db import models as m
from django.utils.timezone import now

from django.contrib.auth.models import User  
from django.core.validators import EmailValidator, RegexValidator

# Create your m here.
class Beneficiaries(m.Model):
    ration_card = m.OneToOneField('Ration_Card', on_delete=m.CASCADE, null=True, blank=True)
    bene = m.OneToOneField(User , on_delete=m.CASCADE)
    beneficiary_card_no = m.CharField(max_length=15, default=str , null=False)
    beneficiary_name = m.CharField(max_length=20, blank=False, null=False)
    beneficiary_email = m.EmailField(
        max_length=50,
        blank=False,
        null=False,
        validators=[EmailValidator(message="Enter a valid email address.")]
    )
    beneficiary_phone = m.CharField(
        max_length=13,
        blank=False,
        null=False,
        validators=[RegexValidator(r'^\d{10,13}$', message="Enter a valid phone number.")]
    )
    beneficiary_address = m.CharField(max_length=100,default=str, blank=False, null=False)
    beneficiary_aadhaar = m.CharField(max_length=10, blank=False,default=str, null=False)
    beneficiary_state = m.CharField(max_length=20, blank=False,default=str, null=False)
    beneficiary_pincode = m.CharField(max_length=6, blank=False, default=str,null=False)
    beneficiary_family_size = m.IntegerField(blank=False, null=False , default=int)
    beneficiary_family = m.JSONField(blank=False, null=False, default=list)  # Store family as a list
    beneficiary_otp = m.CharField(max_length=6, blank=False, null=False, default=None)
    beneficiary_password = m.CharField(max_length=128, blank=False, default=str)  # Plain text password


    def __str__(self):
        return f"Beneficiary({self.bene.username}, {self.beneficiary_name})"


    

    class BeneficiaryCardChoices(m.TextChoices):
        SELECT = "select", "Select"
        YELLOW = "yellow", "Yellow"
        WHITE = "white", "White"
        SAFFRON = "saffron", "Saffron"
        GREEN = "green", "Green"

    beneficiary_card = m.CharField(
        max_length=20,
        choices=BeneficiaryCardChoices.choices,
        default=BeneficiaryCardChoices.SELECT
    )

    class BeneficiaryTypeChoices(m.TextChoices):
        SELECT = "select", "Select"
        SUPERUSER = "superuser", "Superuser"
        FPS = "fps", "Fair Price Shop"
        USER = "user", "User"

    beneficiary_type = m.CharField(
        max_length=20,
        choices=BeneficiaryTypeChoices.choices,
        default=BeneficiaryTypeChoices.SELECT,
        null=True,
    )

    




#Ration Card Model : 

class Ration_Card(m.Model):

    r_id = m.AutoField(primary_key=True)
    ration = m.OneToOneField(settings.AUTH_USER_MODEL, on_delete=m.CASCADE, null=False)    
    email = m.EmailField(
        max_length=50,
        blank=False,
        null=False,
        validators=[EmailValidator(message="Enter a valid email address.")]
    )
    beneficiary_card_no = m.CharField(max_length=15, null=False, default=str)
    ration_card_beneficiary_name = m.CharField(max_length=20, blank=False, null=False, default=str)
    b_ration_address = m.CharField(max_length=100, blank=False, null=False, default=str)
    b_ration_aadhaar = m.CharField(max_length=10, blank=False, null=False, default=str)
    b_ration_state = m.CharField(max_length=20, blank=False, null=False, default=str)
    b_ration_pincode = m.CharField(max_length=6, blank=False, null=False, default=str)
    b_ration_family_size = m.IntegerField(blank=False, null=False, default=1)
    b_ration_family = m.JSONField(blank=False, null=False, default=list)  # Default to an empty list
    rfid_tag = m.CharField(blank=False ,max_length= 15,default='default_rfid_tag', null=False)

    def _str_(self):
        return f"RationCard({self.ration_card_beneficiary_name})"




class FPS(m.Model):
    name = m.CharField(max_length=255)  # FPS Owner's Name
    fps_code = m.CharField(max_length=50, unique=True)  # Unique FPS Code
    contact_number = m.CharField(max_length=15)
    address = m.TextField()
    state = m.CharField(max_length=100)
    district = m.CharField(max_length=100)
    pincode = m.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} - {self.fps_code}"
    


class FPSInventory(m.Model):
    fps = m.OneToOneField(FPS, on_delete=m.CASCADE)  # Link to FPS
    wheat_initial = m.IntegerField(default=1000)  # Initial stock
    rice_initial = m.IntegerField(default=1000)
    sugar_initial = m.IntegerField(default=1000)

    wheat_current = m.IntegerField(default=1000)  # Current stock
    rice_current = m.IntegerField(default=1000)
    sugar_current = m.IntegerField(default=1000)

    last_reset = m.DateField(default=now)  # Track last reset date

    def reset_stock(self):
        """Resets the stock to the initial quantity every 30 days."""
        self.wheat_current = self.wheat_initial
        self.rice_current = self.rice_initial
        self.sugar_current = self.sugar_initial
        self.last_reset = now().date()
        self.save()

    def __str__(self):
        return f"FPS Inventory ({self.fps.fps_code})"
class FPSProfile(m.Model):
    user = m.OneToOneField(User, on_delete=m.CASCADE)  # Django User Model
    fps = m.OneToOneField(FPS, on_delete=m.CASCADE)  # Link to FPS
    profile_picture = m.ImageField(upload_to='fps_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.fps.fps_code}"
    


class FPSTransaction(m.Model):
    fps = m.ForeignKey('FPS', on_delete=m.CASCADE)  # Link to FPS
    user = m.ForeignKey(User, on_delete=m.CASCADE)  # Beneficiary/User
    wheat_issued = m.IntegerField(default=0)
    rice_issued = m.IntegerField(default=0)
    sugar_issued = m.IntegerField(default=0)
    timestamp = m.DateTimeField(default=now)  # Transaction Date & Time

    def __str__(self):
        return f"Transaction at {self.fps.fps_code} by {self.user.username} on {self.timestamp}"
