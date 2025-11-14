import time
import serial
import random
from .forms import FPSRegistrationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Users.forms import BeneficiaryProfileForm, Ration_admin
from django.contrib.auth.decorators import login_required
from .forms import FPSLoginForm  # Create this form


#  Create your views here.
def home(request) : 
    return render(request , 'home.html')


@login_required
def dbt_dashboard(request) : 
    return render(request , 'dbt.html')


@login_required
def fps_shop(request) : 
    return render(request , 'fairps.html')

def signup_view(request):
    if request.method == 'POST':  # Handle POST requests for form submission
        name = request.POST.get("beneficiary_name")
        email = request.POST.get("beneficiary_email")
        phone = request.POST.get("beneficiary_phone")
        password = request.POST.get("beneficiary_password")
        card_no = request.POST.get("beneficiary_card_no")
        aadhaar = request.POST.get("beneficiary_aadhaar")
        

        # Check if the user is already registered using the correct field name
        check_user = Beneficiaries.objects.filter(beneficiary_phone=phone).first()
        if check_user:
            context = {
                "message": "Mobile number already registered",
                "class": "danger"
            }
            return render(request, 'signup.html', context)

        # Fetch the corresponding Ration card data based on the provided card number
        ration_card = Ration_Card.objects.filter(beneficiary_card_no=card_no).first()

        if not ration_card:
            context = {
                "message": "Ration card not found. Please verify your details.",
                "class": "danger"
            }
            return render(request, 'signup.html', context)
        
        user, created = User.objects.get_or_create(username=email, defaults={"email": email, "password": password})

        # Generate OTP before saving
        otp = str(random.randint(1000, 9999))
        print(otp)
        

        # Create and save a new beneficiary
        beneficiaries = Beneficiaries(
            bene=user,
            beneficiary_name=name,
            beneficiary_email=email,
            beneficiary_phone=phone,
            beneficiary_password=password,
            beneficiary_card_no=card_no,
            beneficiary_aadhaar=aadhaar,
            beneficiary_address=ration_card.b_ration_address,
            beneficiary_state=ration_card.b_ration_state,
            beneficiary_pincode=ration_card.b_ration_pincode,
            beneficiary_family_size=ration_card.b_ration_family_size,
            beneficiary_family=ration_card.b_ration_family,
            ration_card=ration_card,
            beneficiary_otp=otp,  # Assign the OTP here
        )
        beneficiaries.save()
        


        # Send OTP
        # send_otp(request, phone, otp)

        # Store OTP and phone in session
        request.session['phone'] = phone
        request.session['otp'] = otp

        return redirect('Users:otp')

    # Render signup page for GET requests
    return render(request, 'signup.html')
    

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            # Manually check email and password against the database
            try:
                user = User.objects.get(email=email)
                if user.password == password:  # Directly compare the plain password
                    # Log the user in manually
                    login(request, user)
                    messages.success(request, f"{email}, you have been successfully logged in!")
                    return redirect('Users:home')
                else:
                    messages.error(request, "Invalid password. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")
        else:
            messages.error(request, "Email and password are required")

    return render(request, 'login.html')


def logout_view(request):
    if request.method == "POST":
        username = request.user.username
        logout(request)
        messages.success(
            request,
            "{}, you have been successfully logged out!".format(username)
        )
        return redirect("Users:home")
    return render(request, "logout.html")
#adding ration details 
@login_required
def ration_card_view(request):
    if request.method == "POST":
        form = Ration_admin(request.POST)
        if form.is_valid():
            ration_card = form.save(commit=False)  
            ration_card.ration = request.user  # Assign the logged-in user
            ration_card.save()  
            messages.success(request, "Ration detail successfully added!")
            return redirect("Users:home")
        else:
            messages.error(request, "Unable to add ration details. Try again.")
    else:
        form = Ration_admin()

    return render(request, "ration_card_details.html", {"form": form})


def forgot_p(request):
    return render(request, 'forgot_p.html')

def create_pass(request):
    return render(request, 'create_pass.html')

# def otp_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         entered_otp = request.POST.get('otp')
#         print(entered_otp)

#         try:
#             beneficiary = Beneficiaries.objects.get(beneficiary_email=email)
#             if beneficiary.beneficiary_otp == entered_otp:
#                 print("OTP Verified Successfully")
#                 # You can log them in or redirect to dashboard
#                 return redirect('Users:login')  # Replace with your actual view
#             else:
#                 print("Invalid OTP")
#                 return render(request, 'otp.html', {'email': email, 'error': 'Invalid OTP'})
#         except Beneficiaries.DoesNotExist:
#             return render(request, 'otp.html', {'error': 'Beneficiary not found'})
    
#     return render(request, 'otp.html')



def otp_new_view(request):
    phone = request.session.get('phone')  # Retrieve phone from session
    if not phone:
        context = {
                "message": "Session expired. Please sign up again.",
                "class": "danger"
            }
        
        return redirect('Users:signup')
    

    context = {'mobile': phone}

    if request.method == 'POST':
        otp_entered = request.POST.get("otp")
        user = Beneficiaries.objects.filter(beneficiary_phone=phone).first()
        

        if user and str(otp_entered) == str(user.beneficiary_otp):
            context = {
                "message": "OTP verified successfully! Please log in.",
                "class": "danger"
            }
            return redirect('Users:login')  # Redirect to login page after verification
        else:
            # Delete user if OTP is incorrect
            user = Beneficiaries.objects.filter(beneficiary_phone=phone).first()
            if user:
                user.delete()
            
            context = {
                "message": "Invalid OTP. Please sign up again.",
                "class": "danger"
            }
            return redirect('Users:signup')  # Redirect to signup page

    return render(request, 'otp.html', context)


@login_required
def profile_view(request):
    try:
        # Fetch the current logged-in user's beneficiary profile
        beneficiary = Beneficiaries.objects.get(bene=request.user)
    except Beneficiaries.DoesNotExist:
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('Users:home')

    if request.method == 'POST':
        # Update the beneficiary profile with submitted data
        form = BeneficiaryProfileForm(request.POST, instance=beneficiary)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('Users:profile')
        else:
            messages.error(request, "Error updating profile. Please check your input.")
    else:
        # Prepopulate the form with the user's data
        form = BeneficiaryProfileForm(instance=beneficiary)

    return render(request, 'profile.html', {'form': form, 'beneficiary': beneficiary})

# real 
# def scan_rfid(request):
#     if request.method == 'POST':
#         SERIAL_PORT = "COM7"  # Change for Linux/Mac (e.g., "/dev/ttyUSB0")
#         BAUD_RATE = 9600

#         try:
#             # Open serial connection
#             ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)  
#             print("Waiting for RFID tag...")

#             start_time = time.time()
#             while time.time() - start_time < 20:  # Wait for 2 minutes (120 sec)
#                 if ser.in_waiting > 0:
#                     rfid_data = ser.readline().decode("utf-8").strip()
#                     if rfid_data.startswith("Card UID:"):
#                         rfid_card_id = rfid_data.replace("Card UID:", "").strip()
#                         print("RFID Detected:", rfid_card_id)

#                         # Store RFID in session
#                         request.session['rfid_card_id'] = rfid_card_id
                        
#                         # Redirect to the "Give Ration" page
#                         return redirect('Users:give_ration')

#             messages.error(request, "RFID not scanned within 2 minutes. Try again.")

#         except serial.SerialException as e:
#             messages.error(request, "Error: Could not open serial port!")
#             print("Error:", e)

#         finally:
#             if 'ser' in locals() and ser.is_open:
#                 ser.close()

#     return render(request, "scan_rfid.html")



@login_required
def ration_distribution_static_view(request):
    return render(request, 'ration_dis.html')
    

@login_required
def citizen(request):
    return render(request, 'citizen.html')

def scan_rfid(request):
    if request.method == 'POST':
        SERIAL_PORT = "COM7"  
        BAUD_RATE = 9600

        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=10)
            print("Waiting for RFID tag...")

            start_time = time.time()
            while time.time() - start_time < 20:  # Wait for 2 minutes
                if ser.in_waiting > 0:
                    rfid_data = ser.readline().decode("utf-8").strip()
                    print(f"Raw RFID Data: {rfid_data}")  # Debugging line

                    # Check for the correct RFID tag format
                    if "RFID Tag UID:" in rfid_data:
                        rfid_card_id = rfid_data.replace("RFID Tag UID:", "").strip()
                        print("RFID Detected:", rfid_card_id)
                        # Store RFID in session
                        request.session['rfid_card_id'] = rfid_card_id
                        return redirect('Users:give_ration')

            messages.error(request, "RFID not scanned within 2 minutes. Try again.")

        except serial.SerialException as e:
            messages.error(request, "Error: Could not open serial port!")
            print("Serial Port Error:", e)

        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()

    return render(request, "scan_rfid.html")


# def give_ration(request):
    
#     rfid_card_id = request.session.get('rfid_card_id', None)
    
#     if not rfid_card_id:
#         messages.error(request, "No RFID tag detected. Scan your card first.")
#         return redirect("Users:home")  # Redirect to home if RFID is missing
    
#     try:
#         # Check if the RFID tag matches any Ration_Card record
#         ration_card = Ration_Card.objects.get(beneficiary_card_no=rfid_card_id)

#         # Define ration details
#         if Beneficiaries.beneficiary_card
#         ration_details = {
#             "wheat": "5kg",
#             "rice": "5kg",
#             "sugar": "5kg"
#         }

#         return render(request, "give_ration.html", {"ration_card": ration_card, "ration_details": ration_details})
    
#     except Ration_Card.DoesNotExist:
#         messages.error(request, "Invalid ration number. Please register first.")
#         return redirect("Users:home") 





# real

# def give_ration(request):
#     rfid_card_id = request.session.get('rfid_card_id', None)
    
#     if not rfid_card_id:
#         messages.error(request, "No RFID tag detected. Scan your card first.")
#         return redirect("Users:home")  # Redirect to home if RFID is missing
    
#     try:
#         # Fetch Ration_Card linked to this RFID
#         ration_card = Ration_Card.objects.get(beneficiary_card_no=rfid_card_id)
        
#         # Fetch Beneficiary linked to this Ration Card
#         beneficiary = Beneficiaries.objects.get(ration_card=ration_card)

#         # Define ration details based on beneficiary card type
#         ration_distribution = {
#             "saffron": {"wheat": "5kg", "rice": "5kg", "sugar": "5kg"},
#             "yellow": {"wheat": "8kg", "rice": "8kg", "sugar": "8kg"},
#             "green": {"wheat": "10kg", "rice": "10kg", "sugar": "10kg"},
#         }

#         # Get the beneficiary card type
#         beneficiary_card_type = beneficiary.beneficiary_card.lower()

#         # Check if the card type exists in the dictionary
#         ration_details = ration_distribution.get(beneficiary_card_type)

#         if not ration_details:
#             messages.error(request, "Invalid card type. Contact admin.")
#             return redirect("Users:home")

#         return render(request, "give_ration.html", {
#             "ration_card": ration_card,
#             "beneficiary": beneficiary,
#             "ration_details": ration_details,
#         })
    
#     except Ration_Card.DoesNotExist:
#         messages.error(request, "Invalid ration number. Please register first.")
#     except Beneficiaries.DoesNotExist:
#         messages.error(request, "No beneficiary linked to this ration card.")
    
#     return redirect("Users:home")  # Redirect in case of error

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Ration_Card, Beneficiaries, FPSInventory
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Ration_Card, Beneficiaries, FPSInventory
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Ration_Card, Beneficiaries, FPSInventory, FPSTransaction
def give_ration(request):
    rfid_card_id = request.session.get('rfid_card_id', None)
    
    if not rfid_card_id:
        messages.error(request, "No RFID tag detected. Scan your card first.")
        return redirect("Users:home")  # Redirect to home if RFID is missing
    
    try:
        # Fetch Ration_Card linked to this RFID
        ration_card = Ration_Card.objects.get(beneficiary_card_no=rfid_card_id)
        
        # Fetch Beneficiary linked to this Ration Card
        beneficiary = Beneficiaries.objects.get(ration_card=ration_card)

        # Define ration details based on beneficiary card type
        ration_distribution = {
            "saffron": {"wheat": 5, "rice": 5, "sugar": 5},
            "yellow": {"wheat": 8, "rice": 8, "sugar": 8},
            "green": {"wheat": 10, "rice": 10, "sugar": 10},
        }

        # Get the beneficiary card type
        beneficiary_card_type = beneficiary.beneficiary_card.lower()

        # Check if the card type exists in the dictionary
        ration_details = ration_distribution.get(beneficiary_card_type)

        if not ration_details:
            messages.error(request, "Invalid card type. Contact admin.")
            return redirect("Users:home")

        # Get FPS inventory (Assuming only one FPS handles all)
        fps_inventory = FPSInventory.objects.first()  # Modify this to select correct FPS if needed

        if fps_inventory:
            # Check stock availability
            if (fps_inventory.wheat_current >= ration_details["wheat"] and
                fps_inventory.rice_current >= ration_details["rice"] and
                fps_inventory.sugar_current >= ration_details["sugar"]):
                
                # Deduct stock
                fps_inventory.wheat_current -= ration_details["wheat"]
                fps_inventory.rice_current -= ration_details["rice"]
                fps_inventory.sugar_current -= ration_details["sugar"]
                fps_inventory.save()

                # Log the transaction
                FPSTransaction.objects.create(
                    fps=fps_inventory.fps,  # Link to FPS
                    user=beneficiary.bene,  # ✅ Use 'bene' instead of 'user'
                    wheat_issued=ration_details["wheat"],
                    rice_issued=ration_details["rice"],
                    sugar_issued=ration_details["sugar"],
                    timestamp=now()
                )

                messages.success(request, f"Ration successfully distributed to {beneficiary.bene.username}.")
            else:
                messages.error(request, "Insufficient stock available.")    
        
        return render(request, "give_ration.html", {
            "ration_card": ration_card,
            "beneficiary": beneficiary,
            "ration_details": ration_details,
        })
    
    except Ration_Card.DoesNotExist:
        messages.error(request, "Invalid ration number. Please register first.")
    except Beneficiaries.DoesNotExist:
        messages.error(request, "No beneficiary linked to this ration card.")
    
    return redirect("Users:home")  # Redirect in case of error


def register_fps(request):
    if request.method == "POST":
        form = FPSRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("Users:fps_login")
    else:
        form = FPSRegistrationForm()

    return render(request, "fps_register.html", {"form": form})

def yojana1(request) : 
    return render(request , "yojana1.html")

def yojana2(request) : 
    return render(request , "yojana2.html")

def yojana3(request) : 
    return render(request , "yojana3.html")
# def fps_login(request) : 
#     return render(request , "fps_login.html")


def fps_login(request):
    if request.method == "POST":
        form = FPSLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                try:
                    fps_profile = FPSProfile.objects.get(user=user)
                    login(request, user)
                    return redirect("Users:fps_dashboard")  # Redirect to FPS dashboard
                except FPSProfile.DoesNotExist:
                    form.add_error(None, "No FPS account linked to this user.")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = FPSLoginForm()
    
    return render(request, "fps_login.html", {"form": form})


@login_required
def fps_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("Users:fps_login")  # Redirect to FPS login after logout
    return render(request, "fps_logout.html")  # Show confirmation page
from django.shortcuts import render
from .models import FPSInventory, FPSTransaction

@login_required
def fps_dashboard(request):
    try:
        # Get the FPSProfile for the logged-in user
        fps_profile = FPSProfile.objects.get(user=request.user)
        fps = fps_profile.fps  # This is the actual FPS object

        # Now get the inventory and transactions related to this FPS
        fps_inventory = FPSInventory.objects.get(fps=fps)
        transactions = FPSTransaction.objects.filter(fps=fps).order_by('-timestamp')[:10]

        return render(request, "fps_dashboard.html", {
            "fps": fps,
            "inventory": fps_inventory,
            "transactions": transactions,
        })

    except FPSProfile.DoesNotExist:
        return render(request, "error.html", {"message": "FPS profile not found for this user."})
    except FPSInventory.DoesNotExist:
        return render(request, "error.html", {"message": "Inventory not found for this FPS."})


def chatbot(request):
    if request.method == "POST":
        email = request.POST.get("email")
        ration_number = request.POST.get("ration_number")
        issue = request.POST.get("issue")

        try:
            # Get the beneficiary details
            beneficiary = Beneficiaries.objects.get(beneficiary_email=email, beneficiary_card_no=ration_number)

            # Find the last FPS that issued ration to the user
            last_transaction = FPSTransaction.objects.filter(user=beneficiary.bene).order_by("-timestamp").first()

            if last_transaction:
                fps_id = last_transaction.fps.fps_code
                fps_in_charge = FPS.objects.get(fps_code=fps_id).name
            else:
                fps_id = "Not Found"
                fps_in_charge = "Not Found"

            # Save the complaint (without modifying the models, we just store in JSON for now)
            complaint_data = {
                "email": email,
                "ration_number": ration_number,
                "issue": issue,
                "fps_id": fps_id,
                "fps_in_charge": fps_in_charge
            }

            # Here, you can store the complaint in a database or log file (For now, sending response)
            return JsonResponse({"status": "success", "message": "Complaint submitted successfully!", "data": complaint_data})

        except Beneficiaries.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Invalid Ration Number or Email!"})

    return render(request, "chatbot.html")
