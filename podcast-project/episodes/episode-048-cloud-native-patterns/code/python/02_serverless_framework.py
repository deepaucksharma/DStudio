#!/usr/bin/env python3
"""
Serverless Framework Implementation - Paytm Style
Cloud Native Serverless Functions for Payment Processing

Paytm ke payment processing system ke liye serverless architecture
AWS Lambda, Azure Functions, aur GCP Cloud Functions compatible
"""

import json
import os
import time
import uuid
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError


# Serverless Function Decorator
def serverless_function(timeout: int = 30, memory: int = 512, 
                       environment: str = 'production'):
    """
    Decorator to mark functions as serverless
    Paytm mein har payment function ko properly configure karna hai
    """
    def decorator(func: Callable) -> Callable:
        func._serverless_config = {
            'timeout': timeout,
            'memory': memory, 
            'environment': environment,
            'function_name': func.__name__
        }
        
        def wrapper(event, context=None):
            # Add serverless context
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            # Setup logging for serverless
            logger = logging.getLogger(func.__name__)
            logger.setLevel(logging.INFO)
            
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    f'[{request_id}] %(asctime)s %(levelname)s: %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            
            try:
                logger.info(f"🚀 Starting {func.__name__} - Request ID: {request_id}")
                
                # Add serverless metadata to event
                if isinstance(event, dict):
                    event['_serverless'] = {
                        'request_id': request_id,
                        'function_name': func.__name__,
                        'start_time': start_time,
                        'memory_limit': memory,
                        'timeout': timeout
                    }
                
                # Execute function
                result = func(event, context)
                
                # Add execution metadata
                execution_time = time.time() - start_time
                logger.info(f"✅ Completed {func.__name__} in {execution_time:.3f}s")
                
                if isinstance(result, dict):
                    result['_metadata'] = {
                        'execution_time_ms': int(execution_time * 1000),
                        'request_id': request_id,
                        'success': True
                    }
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ Error in {func.__name__}: {e}")
                
                return {
                    'error': str(e),
                    'success': False,
                    '_metadata': {
                        'execution_time_ms': int(execution_time * 1000),
                        'request_id': request_id,
                        'success': False
                    }
                }
        
        return wrapper
    return decorator


@dataclass
class PaymentRequest:
    """Paytm payment request data structure"""
    user_id: str
    amount: float
    currency: str = 'INR'
    payment_method: str = 'wallet'
    merchant_id: str = ''
    order_id: str = ''


@dataclass
class PaymentResponse:
    """Paytm payment response data structure"""
    transaction_id: str
    status: str
    amount: float
    currency: str
    timestamp: str
    gateway_response: Dict[str, Any]


# Serverless Payment Processing Functions
class PaytmServerlessPayments:
    """
    Paytm serverless payment functions
    Mumbai se Delhi tak har transaction ko handle karta hai
    """
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        self.sns = boto3.client('sns', region_name='ap-south-1')
        
        # Paytm configuration from environment
        self.paytm_merchant_key = os.environ.get('PAYTM_MERCHANT_KEY', '')
        self.paytm_website = os.environ.get('PAYTM_WEBSITE', 'WEBSTAGING')
        self.paytm_industry_type = os.environ.get('PAYTM_INDUSTRY_TYPE', 'Retail')
    
    @serverless_function(timeout=10, memory=256, environment='production')
    def validate_payment_request(self, event: Dict, context=None) -> Dict:
        """
        Payment validation function - serverless
        Har request ko validate karna zaroori hai, fraud detection ke liye
        """
        try:
            # Extract payment data
            payment_data = event.get('body', {})
            if isinstance(payment_data, str):
                payment_data = json.loads(payment_data)
            
            # Validation rules
            required_fields = ['user_id', 'amount', 'payment_method']
            missing_fields = [field for field in required_fields 
                            if field not in payment_data]
            
            if missing_fields:
                return {
                    'statusCode': 400,
                    'body': {
                        'error': f'Missing required fields: {missing_fields}',
                        'success': False
                    }
                }
            
            # Amount validation
            amount = float(payment_data['amount'])
            if amount <= 0:
                return {
                    'statusCode': 400,
                    'body': {
                        'error': 'Amount must be greater than 0',
                        'success': False
                    }
                }
            
            # Daily limit check (Paytm has daily limits)
            daily_limit = self._check_daily_limit(payment_data['user_id'], amount)
            if not daily_limit['allowed']:
                return {
                    'statusCode': 429,
                    'body': {
                        'error': 'Daily transaction limit exceeded',
                        'limit': daily_limit['limit'],
                        'used': daily_limit['used'],
                        'success': False
                    }
                }
            
            # Fraud detection
            fraud_score = self._calculate_fraud_score(payment_data)
            if fraud_score > 0.8:
                return {
                    'statusCode': 403,
                    'body': {
                        'error': 'Transaction flagged for manual review',
                        'fraud_score': fraud_score,
                        'success': False
                    }
                }
            
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Payment request validated successfully',
                    'fraud_score': fraud_score,
                    'success': True
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': {
                    'error': f'Validation failed: {str(e)}',
                    'success': False
                }
            }
    
    @serverless_function(timeout=15, memory=512, environment='production')
    def process_paytm_payment(self, event: Dict, context=None) -> Dict:
        """
        Main payment processing function - serverless
        Paytm ka core payment processing logic
        """
        try:
            # Extract payment data
            payment_data = event.get('body', {})
            if isinstance(payment_data, str):
                payment_data = json.loads(payment_data)
            
            # Create payment request
            payment_request = PaymentRequest(
                user_id=payment_data['user_id'],
                amount=float(payment_data['amount']),
                currency=payment_data.get('currency', 'INR'),
                payment_method=payment_data['payment_method'],
                merchant_id=payment_data.get('merchant_id', 'PAYTM_MERCHANT'),
                order_id=payment_data.get('order_id', str(uuid.uuid4()))
            )
            
            # Generate transaction ID
            transaction_id = f"PAYTM_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Process payment based on method
            if payment_request.payment_method == 'wallet':
                result = self._process_wallet_payment(payment_request, transaction_id)
            elif payment_request.payment_method == 'upi':
                result = self._process_upi_payment(payment_request, transaction_id)
            elif payment_request.payment_method == 'card':
                result = self._process_card_payment(payment_request, transaction_id)
            else:
                raise ValueError(f"Unsupported payment method: {payment_request.payment_method}")
            
            # Store transaction in DynamoDB
            self._store_transaction(result)
            
            # Send notification
            self._send_payment_notification(result)
            
            return {
                'statusCode': 200,
                'body': {
                    'transaction_id': result.transaction_id,
                    'status': result.status,
                    'amount': result.amount,
                    'currency': result.currency,
                    'message': 'Payment processed successfully',
                    'success': True
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': {
                    'error': f'Payment processing failed: {str(e)}',
                    'success': False
                }
            }
    
    @serverless_function(timeout=5, memory=128, environment='production')
    def payment_status_webhook(self, event: Dict, context=None) -> Dict:
        """
        Payment status webhook handler - serverless
        Bank se payment status update aane par trigger hota hai
        """
        try:
            # Extract webhook data
            webhook_data = event.get('body', {})
            if isinstance(webhook_data, str):
                webhook_data = json.loads(webhook_data)
            
            transaction_id = webhook_data.get('transaction_id')
            status = webhook_data.get('status')
            gateway_response = webhook_data.get('gateway_response', {})
            
            if not transaction_id or not status:
                return {
                    'statusCode': 400,
                    'body': {
                        'error': 'Missing transaction_id or status',
                        'success': False
                    }
                }
            
            # Update transaction status in DynamoDB
            table = self.dynamodb.Table('paytm_transactions')
            table.update_item(
                Key={'transaction_id': transaction_id},
                UpdateExpression='SET #status = :status, gateway_response = :gateway_response, updated_at = :updated_at',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': status,
                    ':gateway_response': gateway_response,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            
            # Send status update notification
            self._send_status_notification(transaction_id, status, gateway_response)
            
            return {
                'statusCode': 200,
                'body': {
                    'message': f'Transaction {transaction_id} status updated to {status}',
                    'success': True
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': {
                    'error': f'Webhook processing failed: {str(e)}',
                    'success': False
                }
            }
    
    @serverless_function(timeout=20, memory=1024, environment='production')
    def generate_payment_analytics(self, event: Dict, context=None) -> Dict:
        """
        Payment analytics generation - serverless
        Daily, weekly, monthly analytics generate karta hai
        """
        try:
            # Get time range from event
            time_range = event.get('time_range', 'daily')
            
            # Calculate date range
            now = datetime.utcnow()
            if time_range == 'daily':
                start_date = now - timedelta(days=1)
            elif time_range == 'weekly':
                start_date = now - timedelta(weeks=1)
            elif time_range == 'monthly':
                start_date = now - timedelta(days=30)
            else:
                start_date = now - timedelta(days=1)
            
            # Query DynamoDB for transactions
            table = self.dynamodb.Table('paytm_transactions')
            
            # Scan for transactions in date range (in production, use proper indexing)
            response = table.scan(
                FilterExpression='created_at BETWEEN :start_date AND :end_date',
                ExpressionAttributeValues={
                    ':start_date': start_date.isoformat(),
                    ':end_date': now.isoformat()
                }
            )
            
            transactions = response['Items']
            
            # Generate analytics
            analytics = {
                'total_transactions': len(transactions),
                'total_amount': sum(float(t['amount']) for t in transactions),
                'success_rate': len([t for t in transactions if t['status'] == 'success']) / len(transactions) * 100 if transactions else 0,
                'payment_methods': {},
                'hourly_distribution': {},
                'currency_breakdown': {},
                'avg_transaction_amount': 0
            }
            
            if transactions:
                # Payment method breakdown
                for transaction in transactions:
                    method = transaction.get('payment_method', 'unknown')
                    analytics['payment_methods'][method] = analytics['payment_methods'].get(method, 0) + 1
                
                # Currency breakdown
                for transaction in transactions:
                    currency = transaction.get('currency', 'INR')
                    analytics['currency_breakdown'][currency] = analytics['currency_breakdown'].get(currency, 0) + float(transaction['amount'])
                
                # Calculate average
                analytics['avg_transaction_amount'] = analytics['total_amount'] / analytics['total_transactions']
            
            # Store analytics in DynamoDB
            analytics_table = self.dynamodb.Table('paytm_analytics')
            analytics_table.put_item(
                Item={
                    'analytics_id': f"{time_range}_{now.strftime('%Y-%m-%d')}",
                    'time_range': time_range,
                    'created_at': now.isoformat(),
                    'analytics': analytics
                }
            )
            
            return {
                'statusCode': 200,
                'body': {
                    'analytics': analytics,
                    'message': f'{time_range.capitalize()} analytics generated successfully',
                    'success': True
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': {
                    'error': f'Analytics generation failed: {str(e)}',
                    'success': False
                }
            }
    
    def _check_daily_limit(self, user_id: str, amount: float) -> Dict:
        """Check user's daily transaction limit"""
        # Simplified daily limit check
        daily_limit = 50000.0  # ₹50,000 daily limit
        
        # In production, query DynamoDB for today's transactions
        # For demo, return mock data
        used_today = 15000.0  # Mock used amount
        
        return {
            'allowed': (used_today + amount) <= daily_limit,
            'limit': daily_limit,
            'used': used_today,
            'remaining': daily_limit - used_today
        }
    
    def _calculate_fraud_score(self, payment_data: Dict) -> float:
        """
        Calculate fraud score for transaction
        Mumbai se late night transaction - thoda suspicious lagta hai
        """
        fraud_score = 0.0
        
        # Amount-based scoring
        amount = float(payment_data['amount'])
        if amount > 10000:
            fraud_score += 0.2
        if amount > 50000:
            fraud_score += 0.3
        
        # Time-based scoring (late night transactions)
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 23:
            fraud_score += 0.1
        
        # User behavior (simplified)
        if payment_data.get('new_user', False):
            fraud_score += 0.1
        
        return min(fraud_score, 1.0)
    
    def _process_wallet_payment(self, request: PaymentRequest, transaction_id: str) -> PaymentResponse:
        """Process Paytm wallet payment"""
        # Simulate wallet payment processing
        time.sleep(0.1)  # Simulate processing delay
        
        return PaymentResponse(
            transaction_id=transaction_id,
            status='success',
            amount=request.amount,
            currency=request.currency,
            timestamp=datetime.utcnow().isoformat(),
            gateway_response={
                'gateway': 'paytm_wallet',
                'wallet_balance': 25000.0,  # Mock balance
                'transaction_fee': 0.0
            }
        )
    
    def _process_upi_payment(self, request: PaymentRequest, transaction_id: str) -> PaymentResponse:
        """Process UPI payment"""
        # Simulate UPI payment processing
        time.sleep(0.2)  # Simulate processing delay
        
        return PaymentResponse(
            transaction_id=transaction_id,
            status='success',
            amount=request.amount,
            currency=request.currency,
            timestamp=datetime.utcnow().isoformat(),
            gateway_response={
                'gateway': 'upi',
                'upi_id': 'user@paytm',
                'bank_ref_id': f"UPI{int(time.time())}"
            }
        )
    
    def _process_card_payment(self, request: PaymentRequest, transaction_id: str) -> PaymentResponse:
        """Process card payment"""
        # Simulate card payment processing
        time.sleep(0.3)  # Simulate processing delay
        
        return PaymentResponse(
            transaction_id=transaction_id,
            status='success',
            amount=request.amount,
            currency=request.currency,
            timestamp=datetime.utcnow().isoformat(),
            gateway_response={
                'gateway': 'card_payment',
                'card_last4': '1234',
                'card_type': 'VISA',
                'bank_ref_id': f"CARD{int(time.time())}"
            }
        )
    
    def _store_transaction(self, response: PaymentResponse):
        """Store transaction in DynamoDB"""
        table = self.dynamodb.Table('paytm_transactions')
        table.put_item(
            Item={
                'transaction_id': response.transaction_id,
                'status': response.status,
                'amount': str(response.amount),  # Store as string for precision
                'currency': response.currency,
                'created_at': response.timestamp,
                'gateway_response': response.gateway_response
            }
        )
    
    def _send_payment_notification(self, response: PaymentResponse):
        """Send payment notification via SNS"""
        message = {
            'transaction_id': response.transaction_id,
            'status': response.status,
            'amount': response.amount,
            'currency': response.currency,
            'timestamp': response.timestamp
        }
        
        self.sns.publish(
            TopicArn=os.environ.get('PAYMENT_NOTIFICATION_TOPIC'),
            Message=json.dumps(message),
            Subject=f'Payment {response.status.upper()}: {response.transaction_id}'
        )
    
    def _send_status_notification(self, transaction_id: str, status: str, gateway_response: Dict):
        """Send status update notification"""
        message = {
            'transaction_id': transaction_id,
            'updated_status': status,
            'gateway_response': gateway_response,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.sns.publish(
            TopicArn=os.environ.get('STATUS_UPDATE_TOPIC'),
            Message=json.dumps(message),
            Subject=f'Status Update: {transaction_id} - {status.upper()}'
        )


# AWS Lambda Handler Functions
def lambda_validate_payment(event, context):
    """AWS Lambda handler for payment validation"""
    paytm_payments = PaytmServerlessPayments()
    return paytm_payments.validate_payment_request(event, context)


def lambda_process_payment(event, context):
    """AWS Lambda handler for payment processing"""
    paytm_payments = PaytmServerlessPayments()
    return paytm_payments.process_paytm_payment(event, context)


def lambda_payment_webhook(event, context):
    """AWS Lambda handler for payment webhooks"""
    paytm_payments = PaytmServerlessPayments()
    return paytm_payments.payment_status_webhook(event, context)


def lambda_generate_analytics(event, context):
    """AWS Lambda handler for analytics generation"""
    paytm_payments = PaytmServerlessPayments()
    return paytm_payments.generate_payment_analytics(event, context)


if __name__ == '__main__':
    # Local testing
    paytm_payments = PaytmServerlessPayments()
    
    # Test payment validation
    test_event = {
        'body': {
            'user_id': 'test_user_mumbai',
            'amount': 1500.0,
            'payment_method': 'wallet'
        }
    }
    
    print("🧪 Testing payment validation...")
    validation_result = paytm_payments.validate_payment_request(test_event)
    print(f"Validation result: {validation_result}")
    
    if validation_result.get('body', {}).get('success'):
        print("🧪 Testing payment processing...")
        processing_result = paytm_payments.process_paytm_payment(test_event)
        print(f"Processing result: {processing_result}")
        
        if processing_result.get('body', {}).get('success'):
            transaction_id = processing_result['body']['transaction_id']
            print(f"✅ Payment processed successfully: {transaction_id}")
    
    print("🧪 Testing analytics generation...")
    analytics_result = paytm_payments.generate_payment_analytics({'time_range': 'daily'})
    print(f"Analytics result: {analytics_result}")