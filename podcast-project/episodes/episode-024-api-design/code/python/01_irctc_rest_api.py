#!/usr/bin/env python3
"""
IRCTC Train Booking REST API - Indian Railway Booking System
इस API में हम Indian Railways के real booking flow को simulate करेंगे

Key Features:
- Train search API endpoint
- PNR status checking
- Tatkal booking endpoint
- Cancellation handling
- Mumbai local train integration

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 24 - API Design Patterns
"""

from flask import Flask, request, jsonify, abort
from datetime import datetime, timedelta
import uuid
import json
from dataclasses import dataclass, asdict
from typing import List, Optional
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# डेटा स्ट्रक्चर्स - Data structures for IRCTC system
@dataclass
class Train:
    train_number: str
    train_name: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    available_seats: dict  # class_name: available_count
    price: dict  # class_name: price_in_rupees

@dataclass
class Passenger:
    name: str
    age: int
    gender: str
    aadhar_number: str
    mobile: str

@dataclass
class BookingRequest:
    train_number: str
    journey_date: str
    passengers: List[Passenger]
    class_type: str
    quota: str  # GENERAL, TATKAL, PREMIUM_TATKAL

@dataclass
class PNR:
    pnr_number: str
    train_number: str
    journey_date: str
    passengers: List[Passenger]
    status: str  # CONFIRMED, RAC, WL
    booking_time: str
    total_fare: float

# In-memory database - Production में यह Redis/PostgreSQL होगा
TRAINS_DB = {
    "12137": Train("12137", "Punjab Mail", "Mumbai Central", "New Delhi", "20:05", "08:35", 
                  {"3AC": 45, "2AC": 12, "1AC": 8}, {"3AC": 1850, "2AC": 2650, "1AC": 4200}),
    "12951": Train("12951", "Mumbai Rajdhani", "Mumbai Central", "New Delhi", "17:00", "08:35",
                  {"3AC": 62, "2AC": 28, "1AC": 15}, {"3AC": 2100, "2AC": 2950, "1AC": 4850}),
    "19019": Train("19019", "Dehradun Express", "Mumbai Central", "Dehradun", "21:45", "13:50",
                  {"Sleeper": 180, "3AC": 85, "2AC": 35}, {"Sleeper": 485, "3AC": 1250, "2AC": 1850})
}

BOOKINGS_DB = {}  # PNR -> BookingDetails
USER_SESSIONS = {}  # session_id -> user_info

# API Endpoints - Mumbai style error messages के साथ

@app.route('/api/v1/trains/search', methods=['GET'])
def search_trains():
    """
    Train search API - यात्री trains search कर सकते हैं
    
    Query Parameters:
    - source: शुरुआती station (required)
    - destination: अंतिम station (required) 
    - journey_date: यात्रा की date (YYYY-MM-DD format)
    - class_type: preferred class (optional)
    """
    try:
        source = request.args.get('source')
        destination = request.args.get('destination')
        journey_date = request.args.get('journey_date')
        
        # Validation - Mumbai tapori style
        if not source:
            return jsonify({"error": "Bhai source station batana padega na!"}), 400
        if not destination:
            return jsonify({"error": "Destination toh batao yaar!"}), 400
        if not journey_date:
            return jsonify({"error": "Kab jaana hai? Date toh dalo!"}), 400
            
        # Date validation
        try:
            journey_dt = datetime.strptime(journey_date, "%Y-%m-%d")
            if journey_dt.date() <= datetime.now().date():
                return jsonify({"error": "Aaj ya kal ki booking nahi kar sakte! Future date dalo"}), 400
        except ValueError:
            return jsonify({"error": "Date format galat hai! YYYY-MM-DD use karo"}), 400
            
        # Filter trains based on source and destination
        matching_trains = []
        for train_num, train in TRAINS_DB.items():
            if source.lower() in train.source.lower() and destination.lower() in train.destination.lower():
                matching_trains.append({
                    "train_number": train.train_number,
                    "train_name": train.train_name,
                    "source": train.source,
                    "destination": train.destination,
                    "departure_time": train.departure_time,
                    "arrival_time": train.arrival_time,
                    "available_seats": train.available_seats,
                    "price": train.price,
                    "journey_duration": "12h 30m"  # Calculated duration
                })
                
        logger.info(f"Train search: {source} to {destination} on {journey_date} - Found {len(matching_trains)} trains")
        
        return jsonify({
            "success": True,
            "search_query": {
                "source": source,
                "destination": destination, 
                "journey_date": journey_date
            },
            "trains_found": len(matching_trains),
            "trains": matching_trains,
            "message": f"Mumbai से {destination} के लिए {len(matching_trains)} trains मिली हैं!"
        })
        
    except Exception as e:
        logger.error(f"Train search error: {str(e)}")
        return jsonify({"error": "कुछ technical problem है! Please try again"}), 500

@app.route('/api/v1/booking/create', methods=['POST'])
def create_booking():
    """
    Train booking API - Tatkal और regular booking के लिए
    
    JSON Body:
    {
        "train_number": "12137",
        "journey_date": "2025-01-15", 
        "passengers": [...],
        "class_type": "3AC",
        "quota": "GENERAL"
    }
    """
    try:
        booking_data = request.get_json()
        
        # Input validation
        required_fields = ['train_number', 'journey_date', 'passengers', 'class_type']
        for field in required_fields:
            if field not in booking_data:
                return jsonify({"error": f"{field} missing hai bhai!"}), 400
                
        train_number = booking_data['train_number']
        if train_number not in TRAINS_DB:
            return jsonify({"error": "Ye train number exist nahi karta!"}), 404
            
        train = TRAINS_DB[train_number]
        class_type = booking_data['class_type']
        
        if class_type not in train.available_seats:
            return jsonify({"error": f"Is train mein {class_type} class available nahi hai!"}), 400
            
        passengers = booking_data['passengers']
        if len(passengers) > 6:
            return jsonify({"error": "Maximum 6 passengers book kar sakte ho!"}), 400
            
        # Seat availability check
        if train.available_seats[class_type] < len(passengers):
            return jsonify({
                "error": f"Sirf {train.available_seats[class_type]} seats available hain! Aap {len(passengers)} passengers ke liye book kar rahe ho"
            }), 409
            
        # Tatkal booking time validation - only between 10 AM to 12 PM
        quota = booking_data.get('quota', 'GENERAL')
        current_time = datetime.now().time()
        if quota == 'TATKAL' and not (10 <= current_time.hour < 12):
            return jsonify({
                "error": "Tatkal booking sirf 10 AM se 12 PM tak kar sakte hain!"
            }), 400
            
        # Generate PNR number - Real IRCTC style 10 digit
        pnr_number = str(uuid.uuid4().int)[:10]
        
        # Calculate total fare
        base_fare = train.price[class_type] * len(passengers)
        gst = base_fare * 0.05
        tatkal_charges = 300 if quota == 'TATKAL' else 0
        total_fare = base_fare + gst + tatkal_charges
        
        # Create booking record
        booking = PNR(
            pnr_number=pnr_number,
            train_number=train_number,
            journey_date=booking_data['journey_date'],
            passengers=[Passenger(**p) for p in passengers],
            status="CONFIRMED",
            booking_time=datetime.now().isoformat(),
            total_fare=total_fare
        )
        
        BOOKINGS_DB[pnr_number] = booking
        
        # Update seat availability
        TRAINS_DB[train_number].available_seats[class_type] -= len(passengers)
        
        logger.info(f"Booking created: PNR {pnr_number} for train {train_number}")
        
        return jsonify({
            "success": True,
            "message": f"Congratulations! Aapki booking confirm ho gayi hai!",
            "pnr_number": pnr_number,
            "booking_details": {
                "train_name": train.train_name,
                "journey_date": booking_data['journey_date'],
                "class_type": class_type,
                "total_passengers": len(passengers),
                "total_fare": f"₹{total_fare:.2f}",
                "status": "CONFIRMED",
                "quota": quota
            },
            "next_steps": [
                "SMS aur Email confirmation aayega",
                "Journey pe photo ID लेकर आना",
                "Platform number departure se 30 min pehle check करना"
            ]
        }), 201
        
    except Exception as e:
        logger.error(f"Booking creation error: {str(e)}")
        return jsonify({"error": "Booking process mein problem! Please try again"}), 500

@app.route('/api/v1/pnr/<pnr_number>', methods=['GET'])
def check_pnr_status(pnr_number):
    """
    PNR Status Check API - Real IRCTC जैसा status checking
    
    Path Parameter:
    - pnr_number: 10 digit PNR number
    """
    try:
        if pnr_number not in BOOKINGS_DB:
            return jsonify({
                "error": "Invalid PNR number! Check करके फिर से enter करो"
            }), 404
            
        booking = BOOKINGS_DB[pnr_number]
        train = TRAINS_DB[booking.train_number]
        
        # Mumbai local train status messages
        status_messages = {
            "CONFIRMED": "Ticket confirm hai! Enjoy your journey",
            "RAC": "RAC में हो, chances hain seat confirm होने के",  
            "WL": "Waiting list mein ho, cancel kar do ya wait karo"
        }
        
        return jsonify({
            "pnr_number": pnr_number,
            "train_details": {
                "train_number": booking.train_number,
                "train_name": train.train_name,
                "source": train.source,
                "destination": train.destination,
                "departure_time": train.departure_time,
                "journey_date": booking.journey_date
            },
            "booking_status": booking.status,
            "status_message": status_messages.get(booking.status, "Status unclear hai"),
            "passengers": [
                {
                    "name": p.name,
                    "age": p.age,
                    "status": booking.status,
                    "coach": "B1" if booking.status == "CONFIRMED" else "NOT_ALLOTTED",
                    "berth": f"{i+1}" if booking.status == "CONFIRMED" else "NOT_ALLOTTED"
                }
                for i, p in enumerate(booking.passengers)
            ],
            "total_fare": f"₹{booking.total_fare:.2f}",
            "booking_time": booking.booking_time,
            "chart_preparation": "Will be prepared 4 hours before departure"
        })
        
    except Exception as e:
        logger.error(f"PNR status check error: {str(e)}")
        return jsonify({"error": "PNR check karne mein problem!"})

@app.route('/api/v1/booking/<pnr_number>/cancel', methods=['DELETE']) 
def cancel_booking(pnr_number):
    """
    Booking Cancellation API - Indian Railways cancellation charges के साथ
    """
    try:
        if pnr_number not in BOOKINGS_DB:
            return jsonify({"error": "Invalid PNR number!"}), 404
            
        booking = BOOKINGS_DB[pnr_number]
        
        # Check if cancellation is allowed
        journey_date = datetime.strptime(booking.journey_date, "%Y-%m-%d")
        hours_until_journey = (journey_date - datetime.now()).total_seconds() / 3600
        
        if hours_until_journey < 4:
            return jsonify({
                "error": "Cancellation not allowed! Journey se 4 hours पहले cancel करना padta hai"
            }), 400
            
        # Calculate refund amount - Indian Railways formula
        cancellation_charges = 60  # Base cancellation charges
        if hours_until_journey < 24:
            cancellation_charges += booking.total_fare * 0.25  # 25% deduction
        elif hours_until_journey < 48:
            cancellation_charges += booking.total_fare * 0.10  # 10% deduction
            
        refund_amount = booking.total_fare - cancellation_charges
        
        # Process cancellation
        train = TRAINS_DB[booking.train_number]
        class_type = None
        for cls in train.price.keys():
            if cls in ['1AC', '2AC', '3AC', 'Sleeper']:
                class_type = cls
                break
                
        if class_type:
            TRAINS_DB[booking.train_number].available_seats[class_type] += len(booking.passengers)
            
        # Update booking status
        booking.status = "CANCELLED"
        
        logger.info(f"Booking cancelled: PNR {pnr_number}, Refund: ₹{refund_amount:.2f}")
        
        return jsonify({
            "success": True,
            "message": "Booking successfully cancel ho gayi!",
            "cancellation_details": {
                "pnr_number": pnr_number,
                "original_fare": f"₹{booking.total_fare:.2f}",
                "cancellation_charges": f"₹{cancellation_charges:.2f}",
                "refund_amount": f"₹{refund_amount:.2f}",
                "refund_timeline": "5-7 working days mein aapke account mein refund aayega"
            }
        })
        
    except Exception as e:
        logger.error(f"Booking cancellation error: {str(e)}")
        return jsonify({"error": "Cancellation process mein problem!"})

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """API Health check - Load balancer के लिए"""
    return jsonify({
        "status": "healthy",
        "service": "IRCTC Booking API",
        "timestamp": datetime.now().isoformat(),
        "message": "Sab kuch running smoothly! Train time pe aayegi 😄"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint nahi mila! Check your URL",
        "available_endpoints": [
            "/api/v1/trains/search",
            "/api/v1/booking/create", 
            "/api/v1/pnr/<pnr_number>",
            "/api/v1/booking/<pnr_number>/cancel"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Server mein कुछ technical problem! Please try after some time",
        "support": "Contact IRCTC helpline: 139"
    }), 500

if __name__ == '__main__':
    print("🚂 IRCTC REST API Server starting...")
    print("📍 Mumbai Central se Delhi tak - सभी trains available!")
    print("🎫 Tatkal booking: 10 AM - 12 PM only")
    app.run(host='0.0.0.0', port=8000, debug=True)