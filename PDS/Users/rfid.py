from django.shortcuts import render
import serial

import random
from django.http import JsonResponse

from .models import Ration_Card

def read_rfid_tag():
    try:
        serial_port = "COM7"  # Replace with your RFID reader's COM port
        baud_rate = 9600
        timeout = 1

        with serial.Serial(port=serial_port, baudrate=baud_rate, timeout=timeout) as rfid_reader:
            if rfid_reader.in_waiting > 0:
                # Read and decode RFID tag
                rfid_tag = rfid_reader.readline().decode('utf-8').strip()
                return rfid_tag
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None




def calculate_ration_quantity(ration_card):
    # Ration details for different card types
    if ration_card.beneficiary_card == "yellow" or ration_card.beneficiary_card == "saffron":
        # Yellow and Saffron Cards
        wheat_quantity = 35  # kg of wheat per month
        rice_quantity = 35   # kg of rice per month
        return {"wheat": wheat_quantity, "rice": rice_quantity}
    
    elif ration_card.beneficiary_card == "pink":
        # Pink Cards
        wheat_quantity = 35  # kg of wheat per month
        rice_quantity = 35   # kg of rice per month
        return {"wheat": wheat_quantity, "rice": rice_quantity}
    
    elif ration_card.beneficiary_card == "white":
        # White Card - Not eligible for ration
        return {"error": "Not eligible for ration"}
    
    else:
        return {"error": "Invalid card type"}
    



def rfid_ration_view(request):
    if request.method == "GET":
        rfid_tag = read_rfid_tag()  # Your existing function for reading RFID tag

        if not rfid_tag:
            return JsonResponse({"error": "Unable to read RFID tag. Please try again."}, status=400)
        # Render the initial page asking the user to scan their RFID
        return render(request, 'rfid_ration.html')
    
    # If it's a POST request, we attempt to read the RFID tag
    if request.method == "POST":

        try:
            # Fetch the corresponding ration card details
            ration_card = Ration_Card.objects.get(rfid_tag=rfid_tag)
            ration_details = {
                "name": ration_card.ration_card_beneficiary_name,
                "address": ration_card.b_ration_address,
                "state": ration_card.b_ration_state,
                "pincode": ration_card.b_ration_pincode,
                "family_size": ration_card.b_ration_family_size,
            }

            # Get the ration quantity based on the card color
            quantity = calculate_ration_quantity(ration_card)
            
            # If there's an error in the quantity (e.g., "Not eligible for ration")
            if "error" in quantity:
                ration_details["eligibility"] = quantity["error"]
            else:
                ration_details["wheat_quantity"] = quantity["wheat"]
                ration_details["rice_quantity"] = quantity["rice"]
            
            return JsonResponse({"success": True, "ration_details": ration_details}, status=200)
        except Ration_Card.DoesNotExist:
            return JsonResponse({"error": "RFID tag not registered. Please check your details."}, status=404)
