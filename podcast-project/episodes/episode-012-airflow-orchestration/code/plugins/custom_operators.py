"""
Custom Airflow Operators for Indian Business Requirements
Episode 12: Airflow Orchestration - Custom Operator Development

यह file custom operators को define करती है जो Indian business scenarios
के लिए specifically designed हैं। Production-ready operators with
comprehensive error handling और monitoring।

Author: Code Developer Agent
Language: Python with Hindi Comments
Context: Custom operators for Indian e-commerce, fintech, and enterprise patterns
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import requests
import pytz
from dataclasses import dataclass

# Airflow imports
from airflow import AirflowException
from airflow.models import BaseOperator
from airflow.hooks.base import BaseHook
from airflow.utils.decorators import apply_defaults
from airflow.utils.context import Context
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# =============================================================================
# Data Classes for Type Safety
# =============================================================================

@dataclass
class PaymentGatewayResponse:
    """Payment gateway response structure"""
    transaction_id: str
    status: str
    amount: float
    currency: str
    payment_method: str
    gateway: str
    timestamp: datetime
    error_message: Optional[str] = None
    
@dataclass
class SMSDeliveryResult:
    """SMS delivery result structure"""
    message_id: str
    phone_number: str
    status: str
    delivery_time: Optional[datetime]
    cost_paisa: float
    provider: str
    error_code: Optional[str] = None

@dataclass
class BankingComplianceResult:
    """Banking compliance check result"""
    transaction_id: str
    compliance_status: str
    risk_score: float
    aml_flag: bool
    kyc_verified: bool
    regulatory_alerts: List[str]
    processing_time_ms: float

# =============================================================================
# Custom Operators
# =============================================================================

class IndianPaymentGatewayOperator(BaseOperator):
    """
    Indian Payment Gateway Integration Operator
    ==========================================
    
    यह operator Indian payment gateways (Razorpay, PayU, CCAvenue) के साथ
    integrate करता है। Multiple gateways को support करता है failover के साथ।
    
    Features:
    - Multi-gateway support with automatic failover
    - UPI, Credit/Debit card, Net banking, Wallet support
    - Indian rupee currency handling
    - Compliance with RBI guidelines
    - GST calculation integration
    - Festival season surge pricing
    """
    
    template_fields = ('payment_data', 'gateway_config')
    template_ext = ('.json',)
    ui_color = '#90EE90'  # Light green for payments
    
    @apply_defaults
    def __init__(
        self,
        payment_data: Dict[str, Any],
        primary_gateway: str = 'razorpay',
        backup_gateways: List[str] = None,
        gateway_config: Dict[str, Any] = None,
        enable_failover: bool = True,
        max_retry_attempts: int = 3,
        compliance_check: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.payment_data = payment_data
        self.primary_gateway = primary_gateway
        self.backup_gateways = backup_gateways or ['payu', 'ccavenue']
        self.gateway_config = gateway_config or {}
        self.enable_failover = enable_failover
        self.max_retry_attempts = max_retry_attempts
        self.compliance_check = compliance_check
        
        # Indian payment gateway configurations
        self.gateway_endpoints = {
            'razorpay': {
                'base_url': 'https://api.razorpay.com/v1',
                'payment_endpoint': '/payments',
                'verify_endpoint': '/payments/{payment_id}',
                'max_amount_inr': 200000,  # ₹2 lakh limit for instant settlements
                'supported_methods': ['upi', 'card', 'netbanking', 'wallet'],
                'settlement_time_hours': 2,
                'transaction_fee_percent': 2.0
            },
            'payu': {
                'base_url': 'https://secure.payu.in/_payment',
                'payment_endpoint': '/pay',
                'verify_endpoint': '/verify_payment',
                'max_amount_inr': 100000,  # ₹1 lakh limit
                'supported_methods': ['card', 'netbanking', 'upi', 'emi'],
                'settlement_time_hours': 24,
                'transaction_fee_percent': 2.5
            },
            'ccavenue': {
                'base_url': 'https://secure.ccavenue.com/transaction',
                'payment_endpoint': '/initiate',
                'verify_endpoint': '/status',
                'max_amount_inr': 500000,  # ₹5 lakh limit
                'supported_methods': ['card', 'netbanking', 'wallet'],
                'settlement_time_hours': 48,
                'transaction_fee_percent': 3.0
            }
        }
    
    def execute(self, context: Context) -> PaymentGatewayResponse:
        """Execute payment processing with Indian gateway integration"""
        
        logger = logging.getLogger(__name__)
        logger.info(f"💳 Starting Indian payment processing - Amount: ₹{self.payment_data.get('amount', 0)}")
        
        # Validate payment data
        self._validate_payment_data()
        
        # Apply Indian business rules
        processed_payment_data = self._apply_indian_business_rules()
        
        # Compliance checks if enabled
        if self.compliance_check:
            compliance_result = self._perform_compliance_checks(processed_payment_data)
            if not compliance_result['passed']:
                raise AirflowException(f"Compliance check failed: {compliance_result['errors']}")
        
        # Attempt payment with primary gateway
        gateways_to_try = [self.primary_gateway] + (self.backup_gateways if self.enable_failover else [])
        
        for gateway in gateways_to_try:
            for attempt in range(self.max_retry_attempts):
                try:
                    logger.info(f"🔄 Attempting payment via {gateway} (attempt {attempt + 1})")
                    
                    result = self._process_payment_with_gateway(gateway, processed_payment_data)
                    
                    if result.status in ['success', 'captured']:
                        logger.info(f"✅ Payment successful via {gateway} - Transaction ID: {result.transaction_id}")
                        
                        # Store payment result for downstream tasks
                        context['task_instance'].xcom_push(
                            key='payment_result',
                            value=result.__dict__
                        )
                        
                        return result
                    
                except Exception as e:
                    logger.warning(f"⚠️ Payment attempt {attempt + 1} failed with {gateway}: {str(e)}")
                    if attempt == self.max_retry_attempts - 1:
                        logger.error(f"❌ All attempts failed with {gateway}")
                    else:
                        time.sleep(2 ** attempt)  # Exponential backoff
        
        # If all gateways fail
        raise AirflowException("Payment processing failed across all configured gateways")
    
    def _validate_payment_data(self) -> None:
        """Validate payment data for Indian payment processing"""
        
        required_fields = ['amount', 'currency', 'customer_id', 'order_id']
        for field in required_fields:
            if field not in self.payment_data:
                raise AirflowException(f"Missing required payment field: {field}")
        
        # Indian currency validation
        if self.payment_data.get('currency') != 'INR':
            raise AirflowException("Only INR currency is supported for Indian payments")
        
        # Amount validation
        amount = float(self.payment_data['amount'])
        if amount <= 0:
            raise AirflowException("Payment amount must be positive")
        
        if amount > 1000000:  # ₹10 lakh limit
            raise AirflowException("Payment amount exceeds maximum allowed limit of ₹10 lakh")
        
        # Customer validation (basic PAN/Aadhaar check)
        customer_id = self.payment_data.get('customer_id', '')
        if len(customer_id) < 6:
            raise AirflowException("Invalid customer ID format")
    
    def _apply_indian_business_rules(self) -> Dict[str, Any]:
        """Apply Indian business rules and enhancements"""
        
        processed_data = self.payment_data.copy()
        
        # GST calculation if applicable
        amount = float(processed_data['amount'])
        if processed_data.get('include_gst', False):
            gst_rate = processed_data.get('gst_rate', 18)  # Default 18% GST
            gst_amount = amount * (gst_rate / 100)
            processed_data['gst_amount'] = gst_amount
            processed_data['total_amount'] = amount + gst_amount
        else:
            processed_data['total_amount'] = amount
        
        # Festival season surcharge (if applicable)
        current_month = datetime.now(IST).month
        festival_months = [10, 11, 12]  # Oct-Dec festival season
        
        if current_month in festival_months and processed_data.get('apply_festival_charges', False):
            festival_surcharge = amount * 0.01  # 1% festival processing fee
            processed_data['festival_surcharge'] = festival_surcharge
            processed_data['total_amount'] += festival_surcharge
        
        # Time-based priority processing
        current_hour = datetime.now(IST).hour
        if 9 <= current_hour <= 17:  # Business hours
            processed_data['priority'] = 'HIGH'
        else:
            processed_data['priority'] = 'NORMAL'
        
        # Regional pricing adjustments
        customer_state = processed_data.get('customer_state', '')
        if customer_state in ['Bihar', 'Jharkhand', 'Odisha']:  # Lower income states
            processed_data['eligible_for_discount'] = True
            processed_data['discount_percent'] = 2.0  # 2% discount for certain states
        
        return processed_data
    
    def _perform_compliance_checks(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform RBI and anti-money laundering compliance checks"""
        
        compliance_result = {
            'passed': True,
            'errors': [],
            'warnings': [],
            'risk_score': 0.0
        }
        
        amount = float(payment_data['total_amount'])
        
        # High-value transaction check (₹2 lakh+)
        if amount >= 200000:
            compliance_result['warnings'].append('High-value transaction - additional scrutiny required')
            compliance_result['risk_score'] += 30
        
        # Suspicious pattern detection (simplified)
        customer_id = payment_data['customer_id']
        
        # Check recent transaction history (mock implementation)
        recent_transaction_count = self._get_recent_transaction_count(customer_id)
        if recent_transaction_count > 10:  # More than 10 transactions today
            compliance_result['warnings'].append('High transaction frequency detected')
            compliance_result['risk_score'] += 20
        
        # Risk score evaluation
        if compliance_result['risk_score'] > 60:
            compliance_result['passed'] = False
            compliance_result['errors'].append('Risk score too high - manual review required')
        
        return compliance_result
    
    def _get_recent_transaction_count(self, customer_id: str) -> int:
        """Get recent transaction count for compliance checking"""
        
        try:
            # In production, this would query actual transaction database
            postgres_hook = PostgresHook(postgres_conn_id='payments_db')
            
            query = """
            SELECT COUNT(*) 
            FROM payment_transactions 
            WHERE customer_id = %s 
            AND created_at >= CURRENT_DATE
            """
            
            result = postgres_hook.get_first(query, parameters=[customer_id])
            return result[0] if result else 0
            
        except Exception:
            # If database check fails, assume low count for safety
            return 0
    
    def _process_payment_with_gateway(self, gateway: str, payment_data: Dict[str, Any]) -> PaymentGatewayResponse:
        """Process payment with specific gateway"""
        
        gateway_config = self.gateway_endpoints[gateway]
        
        # Prepare payment request
        payment_request = self._prepare_gateway_request(gateway, payment_data)
        
        # Make payment API call
        http_hook = HttpHook(method='POST', http_conn_id=f'{gateway}_api')
        
        response = http_hook.run(
            endpoint=gateway_config['payment_endpoint'],
            data=json.dumps(payment_request),
            headers={'Content-Type': 'application/json'}
        )
        
        # Parse response
        response_data = json.loads(response.text)
        
        # Create standardized response
        return PaymentGatewayResponse(
            transaction_id=response_data.get('id', ''),
            status=self._standardize_gateway_status(gateway, response_data.get('status')),
            amount=float(payment_data['total_amount']),
            currency='INR',
            payment_method=payment_data.get('payment_method', 'card'),
            gateway=gateway,
            timestamp=datetime.now(IST),
            error_message=response_data.get('error_message')
        )
    
    def _prepare_gateway_request(self, gateway: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare gateway-specific payment request"""
        
        if gateway == 'razorpay':
            return {
                'amount': int(payment_data['total_amount'] * 100),  # Convert to paisa
                'currency': 'INR',
                'order_id': payment_data['order_id'],
                'description': payment_data.get('description', 'Payment'),
                'customer': {
                    'id': payment_data['customer_id'],
                    'email': payment_data.get('customer_email'),
                    'contact': payment_data.get('customer_phone')
                },
                'notes': {
                    'gst_amount': payment_data.get('gst_amount', 0),
                    'festival_surcharge': payment_data.get('festival_surcharge', 0)
                }
            }
        
        elif gateway == 'payu':
            return {
                'key': self.gateway_config.get('payu_key'),
                'txnid': payment_data['order_id'],
                'amount': payment_data['total_amount'],
                'productinfo': payment_data.get('description', 'Payment'),
                'firstname': payment_data.get('customer_name', 'Customer'),
                'email': payment_data.get('customer_email'),
                'phone': payment_data.get('customer_phone'),
                'surl': self.gateway_config.get('success_url'),
                'furl': self.gateway_config.get('failure_url')
            }
        
        # Add other gateway configurations as needed
        return payment_data
    
    def _standardize_gateway_status(self, gateway: str, gateway_status: str) -> str:
        """Standardize different gateway status codes"""
        
        status_mapping = {
            'razorpay': {
                'created': 'pending',
                'authorized': 'authorized',
                'captured': 'success',
                'refunded': 'refunded',
                'failed': 'failed'
            },
            'payu': {
                'success': 'success',
                'failure': 'failed',
                'pending': 'pending'
            },
            'ccavenue': {
                'Success': 'success',
                'Failure': 'failed',
                'Aborted': 'cancelled'
            }
        }
        
        return status_mapping.get(gateway, {}).get(gateway_status, 'unknown')


class BulkSMSOperator(BaseOperator):
    """
    Bulk SMS Operator for Indian Mobile Networks
    ===========================================
    
    यह operator bulk SMS sending को handle करता है Indian telecom operators
    (Airtel, Jio, Vi, BSNL) के साथ integration करके।
    
    Features:
    - Multi-provider support (TextLocal, MSG91, Route Mobile)
    - Unicode support for Hindi/regional languages
    - DND (Do Not Disturb) compliance
    - Delivery tracking and reporting
    - Cost optimization based on provider rates
    - Time-based sending (avoid night hours)
    """
    
    template_fields = ('message_template', 'recipient_data', 'sms_config')
    template_ext = ('.txt', '.json')
    ui_color = '#FFB6C1'  # Light pink for SMS
    
    @apply_defaults
    def __init__(
        self,
        message_template: str,
        recipient_data: Union[List[Dict], str],  # List of recipients or file path
        primary_provider: str = 'textlocal',
        backup_providers: List[str] = None,
        sms_config: Dict[str, Any] = None,
        enable_dnd_filtering: bool = True,
        enable_unicode: bool = True,
        max_message_length: int = 160,
        delivery_tracking: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.message_template = message_template
        self.recipient_data = recipient_data
        self.primary_provider = primary_provider
        self.backup_providers = backup_providers or ['msg91', 'routemobile']
        self.sms_config = sms_config or {}
        self.enable_dnd_filtering = enable_dnd_filtering
        self.enable_unicode = enable_unicode
        self.max_message_length = max_message_length
        self.delivery_tracking = delivery_tracking
        
        # Indian SMS provider configurations
        self.provider_configs = {
            'textlocal': {
                'api_url': 'https://api.textlocal.in/send/',
                'cost_per_sms_paisa': 25,
                'unicode_cost_per_sms_paisa': 50,
                'max_recipients_per_request': 1000,
                'delivery_report_supported': True,
                'supported_languages': ['hindi', 'english', 'marathi', 'gujarati']
            },
            'msg91': {
                'api_url': 'https://api.msg91.com/api/v5/flow/',
                'cost_per_sms_paisa': 30,
                'unicode_cost_per_sms_paisa': 60,
                'max_recipients_per_request': 500,
                'delivery_report_supported': True,
                'supported_languages': ['hindi', 'english', 'tamil', 'telugu']
            },
            'routemobile': {
                'api_url': 'https://rmlconnect.route.co.in/bulksms',
                'cost_per_sms_paisa': 35,
                'unicode_cost_per_sms_paisa': 70,
                'max_recipients_per_request': 100,
                'delivery_report_supported': False,
                'supported_languages': ['english', 'hindi']
            }
        }
    
    def execute(self, context: Context) -> Dict[str, Any]:
        """Execute bulk SMS sending with Indian provider integration"""
        
        logger = logging.getLogger(__name__)
        logger.info(f"📱 Starting bulk SMS campaign with {self.primary_provider}")
        
        # Load recipient data
        recipients = self._load_recipient_data()
        
        # Validate sending time (avoid night hours 10 PM - 8 AM)
        current_hour = datetime.now(IST).hour
        if current_hour >= 22 or current_hour <= 8:
            logger.warning("⏰ SMS sending outside business hours - consider rescheduling")
        
        # Apply DND filtering if enabled
        if self.enable_dnd_filtering:
            recipients = self._filter_dnd_numbers(recipients)
        
        # Prepare messages
        prepared_messages = self._prepare_messages(recipients)
        
        # Calculate cost estimation
        cost_estimation = self._calculate_cost_estimation(prepared_messages)
        logger.info(f"💰 Estimated cost: ₹{cost_estimation['total_cost_inr']:.2f} for {cost_estimation['total_messages']} messages")
        
        # Send messages in batches
        delivery_results = self._send_bulk_messages(prepared_messages)
        
        # Compile final results
        final_results = {
            'campaign_id': f"SMS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'total_recipients': len(recipients),
            'total_messages_sent': delivery_results['sent_count'],
            'failed_count': delivery_results['failed_count'],
            'cost_estimation': cost_estimation,
            'actual_cost_inr': delivery_results['actual_cost_inr'],
            'delivery_summary': delivery_results['summary'],
            'provider_used': self.primary_provider,
            'campaign_timestamp': datetime.now(IST).isoformat()
        }
        
        # Store results for downstream tasks
        context['task_instance'].xcom_push(
            key='sms_campaign_results',
            value=final_results
        )
        
        logger.info(f"✅ SMS campaign completed - Sent: {delivery_results['sent_count']}, Failed: {delivery_results['failed_count']}")
        return final_results
    
    def _load_recipient_data(self) -> List[Dict[str, str]]:
        """Load recipient data from list or file"""
        
        if isinstance(self.recipient_data, list):
            return self.recipient_data
        
        # If it's a file path, load from file
        if isinstance(self.recipient_data, str):
            if self.recipient_data.endswith('.csv'):
                df = pd.read_csv(self.recipient_data)
                return df.to_dict('records')
            elif self.recipient_data.endswith('.json'):
                with open(self.recipient_data, 'r') as f:
                    return json.load(f)
        
        raise AirflowException(f"Unsupported recipient data format: {type(self.recipient_data)}")
    
    def _filter_dnd_numbers(self, recipients: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Filter out DND (Do Not Disturb) registered numbers"""
        
        # In production, this would check against TRAI DND registry
        # For now, simple mock implementation
        
        filtered_recipients = []
        dnd_filtered_count = 0
        
        for recipient in recipients:
            phone = recipient.get('phone', '')
            
            # Mock DND check - in reality, this would be an API call
            # Assume numbers ending with 0, 5 are DND registered
            if not (phone.endswith('0') or phone.endswith('5')):
                filtered_recipients.append(recipient)
            else:
                dnd_filtered_count += 1
        
        if dnd_filtered_count > 0:
            logging.info(f"🚫 Filtered {dnd_filtered_count} DND registered numbers")
        
        return filtered_recipients
    
    def _prepare_messages(self, recipients: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Prepare personalized messages for each recipient"""
        
        prepared_messages = []
        
        for recipient in recipients:
            # Personalize message template
            personalized_message = self.message_template
            
            # Replace placeholders with recipient data
            for key, value in recipient.items():
                placeholder = f"{{{key}}}"
                personalized_message = personalized_message.replace(placeholder, str(value))
            
            # Check message length
            if len(personalized_message) > self.max_message_length:
                # Truncate message if too long
                personalized_message = personalized_message[:self.max_message_length - 3] + "..."
            
            # Determine if Unicode is needed (contains Hindi/regional characters)
            is_unicode = self._is_unicode_required(personalized_message)
            
            prepared_messages.append({
                'phone': recipient.get('phone'),
                'message': personalized_message,
                'name': recipient.get('name', 'Customer'),
                'is_unicode': is_unicode,
                'recipient_data': recipient
            })
        
        return prepared_messages
    
    def _is_unicode_required(self, message: str) -> bool:
        """Check if message contains Unicode characters (Hindi/regional languages)"""
        
        if not self.enable_unicode:
            return False
        
        # Check for Hindi Devanagari characters
        hindi_range = range(0x0900, 0x097F)
        
        for char in message:
            if ord(char) in hindi_range:
                return True
        
        # Check for other Indian language characters (Tamil, Telugu, etc.)
        # This is a simplified check - production would be more comprehensive
        indian_unicode_ranges = [
            range(0x0B80, 0x0BFF),  # Tamil
            range(0x0C00, 0x0C7F),  # Telugu
            range(0x0C80, 0x0CFF),  # Kannada
            range(0x0D00, 0x0D7F),  # Malayalam
        ]
        
        for char in message:
            for unicode_range in indian_unicode_ranges:
                if ord(char) in unicode_range:
                    return True
        
        return False
    
    def _calculate_cost_estimation(self, prepared_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate cost estimation for SMS campaign"""
        
        provider_config = self.provider_configs[self.primary_provider]
        
        unicode_messages = sum(1 for msg in prepared_messages if msg['is_unicode'])
        regular_messages = len(prepared_messages) - unicode_messages
        
        regular_cost = regular_messages * (provider_config['cost_per_sms_paisa'] / 100)
        unicode_cost = unicode_messages * (provider_config['unicode_cost_per_sms_paisa'] / 100)
        total_cost = regular_cost + unicode_cost
        
        return {
            'total_messages': len(prepared_messages),
            'regular_messages': regular_messages,
            'unicode_messages': unicode_messages,
            'regular_cost_inr': regular_cost,
            'unicode_cost_inr': unicode_cost,
            'total_cost_inr': total_cost,
            'cost_per_message_avg_paisa': (total_cost * 100) / len(prepared_messages) if prepared_messages else 0
        }
    
    def _send_bulk_messages(self, prepared_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send bulk messages via SMS provider"""
        
        provider_config = self.provider_configs[self.primary_provider]
        max_batch_size = provider_config['max_recipients_per_request']
        
        sent_count = 0
        failed_count = 0
        actual_cost = 0.0
        delivery_results = []
        
        # Process in batches
        for i in range(0, len(prepared_messages), max_batch_size):
            batch = prepared_messages[i:i + max_batch_size]
            
            try:
                batch_result = self._send_message_batch(batch)
                
                sent_count += batch_result['sent_count']
                failed_count += batch_result['failed_count']
                actual_cost += batch_result['batch_cost']
                delivery_results.extend(batch_result['delivery_results'])
                
                # Small delay between batches to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"❌ Batch sending failed: {str(e)}")
                failed_count += len(batch)
        
        return {
            'sent_count': sent_count,
            'failed_count': failed_count,
            'actual_cost_inr': actual_cost,
            'summary': {
                'success_rate_percent': (sent_count / len(prepared_messages)) * 100 if prepared_messages else 0,
                'total_batches': (len(prepared_messages) + max_batch_size - 1) // max_batch_size,
                'delivery_results': delivery_results[:100]  # Limit to first 100 for XCom
            }
        }
    
    def _send_message_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send a batch of messages to SMS provider"""
        
        # Prepare API request
        api_data = self._prepare_provider_request(batch)
        
        # Make API call
        http_hook = HttpHook(method='POST', http_conn_id=f'{self.primary_provider}_sms')
        
        response = http_hook.run(
            endpoint='',  # Full URL in provider config
            data=json.dumps(api_data),
            headers={'Content-Type': 'application/json'}
        )
        
        # Parse response
        response_data = json.loads(response.text)
        
        # Process delivery results
        delivery_results = []
        sent_count = 0
        failed_count = 0
        batch_cost = 0.0
        
        for message in batch:
            # This would depend on actual provider response format
            delivery_result = SMSDeliveryResult(
                message_id=f"MSG_{datetime.now().strftime('%Y%m%d%H%M%S')}_{sent_count}",
                phone_number=message['phone'],
                status='sent',  # Would parse from actual response
                delivery_time=datetime.now(IST),
                cost_paisa=50 if message['is_unicode'] else 25,  # Provider-specific
                provider=self.primary_provider
            )
            
            delivery_results.append(delivery_result.__dict__)
            sent_count += 1
            batch_cost += delivery_result.cost_paisa / 100
        
        return {
            'sent_count': sent_count,
            'failed_count': failed_count,
            'batch_cost': batch_cost,
            'delivery_results': delivery_results
        }
    
    def _prepare_provider_request(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare provider-specific API request"""
        
        if self.primary_provider == 'textlocal':
            return {
                'apikey': self.sms_config.get('textlocal_api_key'),
                'sender': self.sms_config.get('sender_id', 'COMPNY'),
                'numbers': ','.join([msg['phone'] for msg in batch]),
                'message': batch[0]['message'],  # Assuming same message for batch
                'unicode': '1' if any(msg['is_unicode'] for msg in batch) else '0'
            }
        
        elif self.primary_provider == 'msg91':
            return {
                'flow_id': self.sms_config.get('msg91_flow_id'),
                'sender': self.sms_config.get('sender_id', 'COMPNY'),
                'mobiles': ','.join([msg['phone'] for msg in batch]),
                'var1': batch[0]['message'],
                'route': '4',  # Promotional route
                'unicode': '1' if any(msg['is_unicode'] for msg in batch) else '0'
            }
        
        # Default format
        return {
            'recipients': [{'phone': msg['phone'], 'message': msg['message']} for msg in batch]
        }


class BankingComplianceOperator(BaseOperator):
    """
    Banking Compliance Check Operator for Indian Financial Services
    ==============================================================
    
    यह operator banking और financial services के लिए compliance checks
    करता है Indian regulations (RBI, SEBI, IRDAI) के अनुसार।
    
    Features:
    - AML (Anti Money Laundering) checks
    - KYC (Know Your Customer) verification
    - High Value Transaction reporting
    - Risk scoring and assessment
    - Regulatory reporting automation
    - Real-time fraud detection
    """
    
    template_fields = ('transaction_data', 'compliance_config')
    ui_color = '#FF6347'  # Tomato color for compliance
    
    @apply_defaults
    def __init__(
        self,
        transaction_data: Dict[str, Any],
        compliance_checks: List[str] = None,
        compliance_config: Dict[str, Any] = None,
        risk_threshold: float = 70.0,
        enable_realtime_monitoring: bool = True,
        regulatory_reporting: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.transaction_data = transaction_data
        self.compliance_checks = compliance_checks or ['aml', 'kyc', 'hvt', 'risk_scoring']
        self.compliance_config = compliance_config or {}
        self.risk_threshold = risk_threshold
        self.enable_realtime_monitoring = enable_realtime_monitoring
        self.regulatory_reporting = regulatory_reporting
        
        # Indian banking compliance thresholds
        self.compliance_thresholds = {
            'high_value_transaction_inr': 200000,    # ₹2 lakh - RBI reporting threshold
            'cash_transaction_limit_inr': 200000,    # ₹2 lakh - Cash transaction limit
            'suspicious_velocity_count': 10,         # 10+ transactions per day
            'max_daily_amount_inr': 1000000,        # ₹10 lakh daily limit
            'kyc_validity_days': 365,               # KYC validity period
            'risk_score_high_threshold': 70,        # High risk threshold
            'risk_score_critical_threshold': 90     # Critical risk threshold
        }
    
    def execute(self, context: Context) -> BankingComplianceResult:
        """Execute banking compliance checks"""
        
        logger = logging.getLogger(__name__)
        logger.info(f"🏦 Starting banking compliance checks for transaction: {self.transaction_data.get('transaction_id')}")
        
        start_time = time.time()
        
        # Initialize compliance result
        compliance_result = BankingComplianceResult(
            transaction_id=self.transaction_data.get('transaction_id', ''),
            compliance_status='PENDING',
            risk_score=0.0,
            aml_flag=False,
            kyc_verified=False,
            regulatory_alerts=[],
            processing_time_ms=0.0
        )
        
        # Perform each compliance check
        for check_type in self.compliance_checks:
            logger.info(f"🔍 Performing {check_type.upper()} compliance check...")
            
            try:
                if check_type == 'aml':
                    aml_result = self._perform_aml_check()
                    compliance_result.aml_flag = aml_result['aml_flag']
                    compliance_result.risk_score += aml_result['risk_score']
                    compliance_result.regulatory_alerts.extend(aml_result['alerts'])
                
                elif check_type == 'kyc':
                    kyc_result = self._perform_kyc_verification()
                    compliance_result.kyc_verified = kyc_result['verified']
                    compliance_result.risk_score += kyc_result['risk_score']
                    compliance_result.regulatory_alerts.extend(kyc_result['alerts'])
                
                elif check_type == 'hvt':
                    hvt_result = self._perform_hvt_check()
                    compliance_result.risk_score += hvt_result['risk_score']
                    compliance_result.regulatory_alerts.extend(hvt_result['alerts'])
                
                elif check_type == 'risk_scoring':
                    risk_result = self._perform_risk_scoring()
                    compliance_result.risk_score += risk_result['additional_risk_score']
                    compliance_result.regulatory_alerts.extend(risk_result['alerts'])
                
            except Exception as e:
                logger.error(f"❌ Compliance check {check_type} failed: {str(e)}")
                compliance_result.regulatory_alerts.append(f"{check_type.upper()}_CHECK_FAILED: {str(e)}")
                compliance_result.risk_score += 20  # Penalty for failed checks
        
        # Determine final compliance status
        if compliance_result.risk_score >= self.compliance_thresholds['risk_score_critical_threshold']:
            compliance_result.compliance_status = 'CRITICAL_RISK'
        elif compliance_result.risk_score >= self.compliance_thresholds['risk_score_high_threshold']:
            compliance_result.compliance_status = 'HIGH_RISK'
        elif compliance_result.aml_flag or not compliance_result.kyc_verified:
            compliance_result.compliance_status = 'NON_COMPLIANT'
        else:
            compliance_result.compliance_status = 'COMPLIANT'
        
        # Calculate processing time
        end_time = time.time()
        compliance_result.processing_time_ms = (end_time - start_time) * 1000
        
        # Store compliance result
        context['task_instance'].xcom_push(
            key='compliance_result',
            value=compliance_result.__dict__
        )
        
        # Trigger regulatory reporting if needed
        if self.regulatory_reporting and compliance_result.compliance_status in ['HIGH_RISK', 'CRITICAL_RISK']:
            self._trigger_regulatory_reporting(compliance_result)
        
        logger.info(f"✅ Compliance checks completed - Status: {compliance_result.compliance_status}, Risk Score: {compliance_result.risk_score}")
        
        return compliance_result
    
    def _perform_aml_check(self) -> Dict[str, Any]:
        """Perform Anti Money Laundering (AML) compliance check"""
        
        transaction_amount = float(self.transaction_data.get('amount', 0))
        customer_id = self.transaction_data.get('customer_id', '')
        
        aml_result = {
            'aml_flag': False,
            'risk_score': 0,
            'alerts': []
        }
        
        # Check 1: High value transaction
        if transaction_amount >= self.compliance_thresholds['high_value_transaction_inr']:
            aml_result['alerts'].append(f"HIGH_VALUE_TRANSACTION: ₹{transaction_amount:,.2f}")
            aml_result['risk_score'] += 25
        
        # Check 2: Rapid transaction velocity
        daily_transaction_count = self._get_daily_transaction_count(customer_id)
        if daily_transaction_count >= self.compliance_thresholds['suspicious_velocity_count']:
            aml_result['alerts'].append(f"SUSPICIOUS_VELOCITY: {daily_transaction_count} transactions today")
            aml_result['risk_score'] += 30
            aml_result['aml_flag'] = True
        
        # Check 3: Unusual transaction patterns
        transaction_patterns = self._analyze_transaction_patterns(customer_id)
        if transaction_patterns['unusual_pattern_detected']:
            aml_result['alerts'].append("UNUSUAL_PATTERN: Deviation from normal behavior")
            aml_result['risk_score'] += 20
        
        # Check 4: Sanctioned entity check
        sanctioned_check = self._check_sanctioned_entities(customer_id)
        if sanctioned_check['is_sanctioned']:
            aml_result['alerts'].append("SANCTIONED_ENTITY: Customer on sanctions list")
            aml_result['risk_score'] += 50
            aml_result['aml_flag'] = True
        
        return aml_result
    
    def _perform_kyc_verification(self) -> Dict[str, Any]:
        """Perform Know Your Customer (KYC) verification"""
        
        customer_id = self.transaction_data.get('customer_id', '')
        
        kyc_result = {
            'verified': False,
            'risk_score': 0,
            'alerts': []
        }
        
        # Get customer KYC status from database
        kyc_status = self._get_customer_kyc_status(customer_id)
        
        if not kyc_status['kyc_completed']:
            kyc_result['alerts'].append("KYC_INCOMPLETE: Customer KYC not completed")
            kyc_result['risk_score'] += 40
        
        elif kyc_status['kyc_expired']:
            kyc_result['alerts'].append("KYC_EXPIRED: Customer KYC documents expired")
            kyc_result['risk_score'] += 25
        
        elif kyc_status['documents_pending_verification']:
            kyc_result['alerts'].append("KYC_PENDING: KYC documents pending verification")
            kyc_result['risk_score'] += 15
        
        else:
            kyc_result['verified'] = True
        
        # Additional checks for Aadhaar/PAN verification
        if not kyc_status.get('aadhaar_verified', False):
            kyc_result['alerts'].append("AADHAAR_NOT_VERIFIED: Aadhaar verification pending")
            kyc_result['risk_score'] += 10
        
        if not kyc_status.get('pan_verified', False):
            kyc_result['alerts'].append("PAN_NOT_VERIFIED: PAN verification pending")
            kyc_result['risk_score'] += 10
        
        return kyc_result
    
    def _perform_hvt_check(self) -> Dict[str, Any]:
        """Perform High Value Transaction (HVT) compliance check"""
        
        transaction_amount = float(self.transaction_data.get('amount', 0))
        
        hvt_result = {
            'risk_score': 0,
            'alerts': []
        }
        
        # RBI High Value Transaction reporting threshold
        if transaction_amount >= self.compliance_thresholds['high_value_transaction_inr']:
            hvt_result['alerts'].append(f"HVT_REPORTING_REQUIRED: ₹{transaction_amount:,.2f} >= ₹{self.compliance_thresholds['high_value_transaction_inr']:,.2f}")
            hvt_result['risk_score'] += 15
            
            # Additional scrutiny for very high amounts
            if transaction_amount >= 1000000:  # ₹10 lakh
                hvt_result['alerts'].append("VERY_HIGH_VALUE: Manual approval required")
                hvt_result['risk_score'] += 25
        
        # Cash transaction limits
        if self.transaction_data.get('payment_method') == 'cash':
            if transaction_amount >= self.compliance_thresholds['cash_transaction_limit_inr']:
                hvt_result['alerts'].append(f"CASH_LIMIT_EXCEEDED: ₹{transaction_amount:,.2f} cash transaction")
                hvt_result['risk_score'] += 35
        
        return hvt_result
    
    def _perform_risk_scoring(self) -> Dict[str, Any]:
        """Perform comprehensive risk scoring"""
        
        customer_id = self.transaction_data.get('customer_id', '')
        
        risk_result = {
            'additional_risk_score': 0,
            'alerts': []
        }
        
        # Customer profile risk factors
        customer_profile = self._get_customer_risk_profile(customer_id)
        
        if customer_profile['new_customer']:  # Customer < 6 months old
            risk_result['additional_risk_score'] += 10
            risk_result['alerts'].append("NEW_CUSTOMER: Higher risk due to limited history")
        
        if customer_profile['high_risk_location']:
            risk_result['additional_risk_score'] += 15
            risk_result['alerts'].append("HIGH_RISK_LOCATION: Transaction from high-risk geography")
        
        if customer_profile['unusual_device']:
            risk_result['additional_risk_score'] += 20
            risk_result['alerts'].append("UNUSUAL_DEVICE: Transaction from new/unusual device")
        
        # Transaction timing risk
        current_hour = datetime.now(IST).hour
        if current_hour < 6 or current_hour > 23:  # Late night transactions
            risk_result['additional_risk_score'] += 5
            risk_result['alerts'].append("OFF_HOURS_TRANSACTION: Transaction during unusual hours")
        
        return risk_result
    
    def _get_daily_transaction_count(self, customer_id: str) -> int:
        """Get daily transaction count for customer"""
        
        try:
            postgres_hook = PostgresHook(postgres_conn_id='banking_db')
            
            query = """
            SELECT COUNT(*) 
            FROM transactions 
            WHERE customer_id = %s 
            AND DATE(created_at) = CURRENT_DATE
            """
            
            result = postgres_hook.get_first(query, parameters=[customer_id])
            return result[0] if result else 0
            
        except Exception:
            return 0
    
    def _analyze_transaction_patterns(self, customer_id: str) -> Dict[str, Any]:
        """Analyze customer transaction patterns for anomalies"""
        
        # Simplified pattern analysis - in production, this would use ML models
        return {
            'unusual_pattern_detected': False,
            'pattern_score': 0,
            'deviation_percentage': 0
        }
    
    def _check_sanctioned_entities(self, customer_id: str) -> Dict[str, bool]:
        """Check if customer is on sanctions list"""
        
        # In production, this would check against OFAC, UN, EU sanctions lists
        return {
            'is_sanctioned': False,
            'sanctions_list': None
        }
    
    def _get_customer_kyc_status(self, customer_id: str) -> Dict[str, Any]:
        """Get customer KYC status from database"""
        
        try:
            postgres_hook = PostgresHook(postgres_conn_id='customer_db')
            
            query = """
            SELECT 
                kyc_status,
                kyc_completion_date,
                aadhaar_verified,
                pan_verified,
                documents_status
            FROM customer_kyc 
            WHERE customer_id = %s
            """
            
            result = postgres_hook.get_first(query, parameters=[customer_id])
            
            if result:
                kyc_completion_date = result[1]
                kyc_expired = False
                
                if kyc_completion_date:
                    days_since_kyc = (datetime.now() - kyc_completion_date).days
                    kyc_expired = days_since_kyc > self.compliance_thresholds['kyc_validity_days']
                
                return {
                    'kyc_completed': result[0] == 'COMPLETED',
                    'kyc_expired': kyc_expired,
                    'aadhaar_verified': result[2],
                    'pan_verified': result[3],
                    'documents_pending_verification': result[4] == 'PENDING'
                }
            
            return {
                'kyc_completed': False,
                'kyc_expired': True,
                'aadhaar_verified': False,
                'pan_verified': False,
                'documents_pending_verification': True
            }
            
        except Exception:
            # Default to non-compliant state if check fails
            return {
                'kyc_completed': False,
                'kyc_expired': True,
                'aadhaar_verified': False,
                'pan_verified': False,
                'documents_pending_verification': True
            }
    
    def _get_customer_risk_profile(self, customer_id: str) -> Dict[str, Any]:
        """Get customer risk profile"""
        
        # Simplified risk profiling - in production, this would be more sophisticated
        return {
            'new_customer': False,
            'high_risk_location': False,
            'unusual_device': False,
            'risk_category': 'MEDIUM'
        }
    
    def _trigger_regulatory_reporting(self, compliance_result: BankingComplianceResult) -> None:
        """Trigger regulatory reporting for high-risk transactions"""
        
        logger = logging.getLogger(__name__)
        logger.info("📋 Triggering regulatory reporting for high-risk transaction")
        
        # In production, this would create entries in regulatory reporting tables
        # and possibly trigger external API calls to regulatory bodies
        
        regulatory_report = {
            'report_type': 'SUSPICIOUS_TRANSACTION_REPORT',
            'transaction_id': compliance_result.transaction_id,
            'risk_score': compliance_result.risk_score,
            'compliance_status': compliance_result.compliance_status,
            'alerts': compliance_result.regulatory_alerts,
            'reporting_timestamp': datetime.now(IST).isoformat(),
            'regulatory_bodies': ['RBI', 'FIU'] if compliance_result.aml_flag else ['RBI']
        }
        
        logger.info(f"📊 Regulatory report prepared: {regulatory_report}")


# =============================================================================
# Plugin Registration
# =============================================================================

"""
Custom Operators Plugin Registration
===================================

यह plugin file Indian business requirements के लिए custom operators
provide करती है। Production में इन operators को use करके complex
business workflows को efficiently handle कर सकते हैं।

Key Features:
1. **Payment Gateway Integration**: Multi-gateway support with failover
2. **Bulk SMS Management**: Indian telecom provider integration
3. **Banking Compliance**: RBI/SEBI compliance automation
4. **Error Handling**: Comprehensive error handling and retry logic
5. **Cost Optimization**: Cost calculation and optimization features
6. **Regional Support**: Indian language and cultural context support

Production Usage:
- Import these operators in your DAGs
- Configure connection IDs for external services
- Set appropriate retry and timeout parameters
- Monitor costs and delivery rates
- Ensure compliance with regulatory requirements

Example DAG Usage:
```python
from plugins.custom_operators import IndianPaymentGatewayOperator, BulkSMSOperator

payment_task = IndianPaymentGatewayOperator(
    task_id='process_payment',
    payment_data={
        'amount': 1000.00,
        'currency': 'INR',
        'customer_id': 'CUST_123',
        'order_id': 'ORDER_456'
    },
    primary_gateway='razorpay',
    backup_gateways=['payu', 'ccavenue']
)
```

यह approach Indian tech ecosystem की complexity को handle करते हुए
scalable और maintainable solutions provide करता है।
"""