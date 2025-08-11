"""
IRCTC Tatkal Booking Workflow DAG
Episode 12: Real-world Indian Railway Context

यह DAG हर दिन सुबह ठीक 10:00 AM पर चलता है - Tatkal booking time!
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import pytz
import requests
import json

IST = pytz.timezone('Asia/Kolkata')

default_args = {
    'owner': 'railway-booking-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,  # Tatkal में 3 बार कोशिश करेंगे
    'retry_delay': timedelta(seconds=30),  # 30 सेकंड बाद retry
    'email': ['booking-alerts@railways.co.in']
}

# हर दिन सुबह 10:00 AM IST पर चलेगा - exact Tatkal time!
dag = DAG(
    dag_id='irctc_tatkal_booking_workflow',
    default_args=default_args,
    description='IRCTC Tatkal Booking - हर दिन 10 AM शार्प!',
    schedule_interval='0 10 * * *',  # Cron: 10:00 AM daily
    catchup=False,
    max_active_runs=1,  # Multiple bookings prevent करने के लिए
    tags=['irctc', 'tatkal', 'booking', 'railway'],
)

def check_tatkal_availability():
    """Tatkal ticket की availability check करना"""
    print("🚂 IRCTC Tatkal Availability Check शुरू...")
    
    # Mock data - real में IRCTC API का इस्तेमाल करेंगे
    trains = [
        {'train_no': '12301', 'name': 'Rajdhani Express', 'available': True, 'price': 1840},
        {'train_no': '12951', 'name': 'Mumbai Rajdhani', 'available': False, 'price': 2650},
        {'train_no': '12009', 'name': 'Shatabdi Express', 'available': True, 'price': 1200},
        {'train_no': '12627', 'name': 'Karnataka Express', 'available': True, 'price': 950}
    ]
    
    available_trains = [train for train in trains if train['available']]
    
    print(f"✅ कुल available trains: {len(available_trains)}")
    for train in available_trains:
        print(f"🎫 {train['name']} ({train['train_no']}) - ₹{train['price']}")
    
    # Airflow Variable में store करेंगे
    Variable.set("available_trains", json.dumps(available_trains))
    
    if not available_trains:
        raise Exception("❌ कोई भी Tatkal ticket available नहीं है!")
        
    return len(available_trains)

def validate_passenger_details():
    """यात्री की details validate करना"""
    print("👤 Passenger Details Validation...")
    
    # Mock passenger data
    passengers = [
        {
            'name': 'राम कुमार शर्मा',
            'age': 35,
            'gender': 'M',
            'id_proof': 'Aadhaar',
            'id_number': '1234-5678-9012'
        },
        {
            'name': 'सीता देवी',
            'age': 32,
            'gender': 'F', 
            'id_proof': 'Aadhaar',
            'id_number': '9876-5432-1098'
        }
    ]
    
    # Validation rules
    for passenger in passengers:
        if not passenger['name'] or len(passenger['name']) < 3:
            raise Exception(f"❌ Invalid name: {passenger['name']}")
        if passenger['age'] < 5 or passenger['age'] > 120:
            raise Exception(f"❌ Invalid age: {passenger['age']}")
        if passenger['gender'] not in ['M', 'F']:
            raise Exception(f"❌ Invalid gender: {passenger['gender']}")
    
    print("✅ सभी passenger details valid हैं!")
    Variable.set("passenger_details", json.dumps(passengers))
    return len(passengers)

def attempt_booking():
    """Actual booking attempt - यहाँ magic होता है!"""
    print("🎯 Tatkal Booking Attempt शुरू...")
    
    # Available trains get करना
    available_trains = json.loads(Variable.get("available_trains", "[]"))
    passengers = json.loads(Variable.get("passenger_details", "[]"))
    
    if not available_trains:
        raise Exception("कोई train available नहीं है!")
    
    # सबसे सस्ती train choose करना (Indian mentality!)
    cheapest_train = min(available_trains, key=lambda x: x['price'])
    
    print(f"🚂 Selected Train: {cheapest_train['name']}")
    print(f"💰 Price: ₹{cheapest_train['price']}")
    print(f"👥 Passengers: {len(passengers)}")
    
    # Mock booking process
    import random
    booking_success = random.choice([True, True, True, False])  # 75% success rate
    
    if booking_success:
        pnr = f"PNR{random.randint(1000000000, 9999999999)}"
        booking_data = {
            'pnr': pnr,
            'train': cheapest_train,
            'passengers': passengers,
            'total_amount': cheapest_train['price'] * len(passengers),
            'booking_time': datetime.now(IST).isoformat()
        }
        Variable.set("booking_result", json.dumps(booking_data))
        print(f"🎉 Booking Successful! PNR: {pnr}")
        return pnr
    else:
        raise Exception("❌ Booking Failed - Server busy या कोई technical issue!")

def send_confirmation_sms():
    """SMS भेजना (mock implementation)"""
    booking_data = json.loads(Variable.get("booking_result", "{}"))
    
    if not booking_data:
        print("कोई booking data नहीं मिला!")
        return
    
    sms_message = f"""
    🎊 IRCTC Tatkal Booking Confirmed!
    
    PNR: {booking_data['pnr']}
    Train: {booking_data['train']['name']}
    Amount: ₹{booking_data['total_amount']}
    
    Happy Journey! 🚂
    """
    
    print("📱 SMS Sent:")
    print(sms_message)
    return "SMS_SENT"

def handle_booking_failure():
    """Booking fail होने पर क्या करना है"""
    print("😞 Booking Failed - Alternative actions...")
    
    alternatives = [
        "General ticket book करें",
        "दूसरी train try करें", 
        "Next day का wait करें",
        "Bus ticket देखें",
        "Flight check करें (महंगा but fast!)"
    ]
    
    print("Alternative options:")
    for i, option in enumerate(alternatives, 1):
        print(f"{i}. {option}")
    
    # Email alert भेजना
    return "ALTERNATIVES_SUGGESTED"

# Tasks definition
availability_check = PythonOperator(
    task_id='check_tatkal_availability',
    python_callable=check_tatkal_availability,
    dag=dag
)

passenger_validation = PythonOperator(
    task_id='validate_passenger_details', 
    python_callable=validate_passenger_details,
    dag=dag
)

booking_attempt = PythonOperator(
    task_id='attempt_booking',
    python_callable=attempt_booking,
    dag=dag
)

sms_confirmation = PythonOperator(
    task_id='send_confirmation_sms',
    python_callable=send_confirmation_sms,
    dag=dag
)

failure_handler = PythonOperator(
    task_id='handle_booking_failure',
    python_callable=handle_booking_failure,
    trigger_rule='one_failed',  # किसी भी task के fail होने पर चलेगा
    dag=dag
)

# Success email
success_email = EmailOperator(
    task_id='send_success_email',
    to=['passenger@gmail.com'],
    subject='🎉 Tatkal Booking Confirmed - IRCTC',
    html_content="""
    <h2>बधाई हो! आपकी Tatkal booking confirm हो गई!</h2>
    <p>PNR और details के लिए SMS check करें।</p>
    <p>Happy Journey! 🚂</p>
    """,
    dag=dag
)

# Task dependencies - booking workflow
availability_check >> passenger_validation >> booking_attempt

# Success path
booking_attempt >> sms_confirmation >> success_email

# Failure path  
[availability_check, passenger_validation, booking_attempt] >> failure_handler

"""
Production Deployment Notes:

1. Environment Variables:
   - IRCTC_API_KEY: IRCTC API access key
   - SMS_GATEWAY_URL: SMS service endpoint
   - NOTIFICATION_EMAIL: Alert email address

2. Monitoring:
   - Setup CloudWatch/Grafana dashboards
   - Alert on booking failures
   - Track success rates

3. Security:
   - Encrypt passenger data
   - Use secure credential storage
   - Rate limiting for API calls

4. Scale Considerations:
   - Multiple booking attempts
   - Load balancing
   - Database for booking history

Real-world Usage:
- Travel agents use similar workflows
- Corporate booking systems
- Personal automation scripts
- Railway booking aggregators
"""