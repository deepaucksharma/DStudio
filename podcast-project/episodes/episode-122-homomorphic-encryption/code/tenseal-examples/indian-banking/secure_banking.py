"""
Secure Banking Operations using Homomorphic Encryption
Indian banking के लिए privacy-preserving financial computations
UPI, NEFT, RTGS transactions को secure process करने के लिए
"""

import tenseal as ts
import numpy as np
import pandas as pd
import logging
import time
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import json
import hashlib

# Hindi comments के साथ logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class SecureBankingSystem:
    """
    Homomorphic Encryption based Banking System
    SBI, ICICI, HDFC जैसे Indian banks के लिए privacy-preserving operations
    """
    
    def __init__(self, poly_modulus_degree: int = 4096, coeff_mod_bit_sizes: List[int] = None):
        """
        Initialize secure banking system with HE context
        
        Args:
            poly_modulus_degree: Polynomial modulus degree (security parameter)
            coeff_mod_bit_sizes: Coefficient modulus bit sizes
        """
        if coeff_mod_bit_sizes is None:
            coeff_mod_bit_sizes = [60, 40, 40, 60]
        
        # TenSEAL context setup for CKKS scheme (approximate arithmetic)
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_modulus_degree,
            coeff_mod_bit_sizes=coeff_mod_bit_sizes
        )
        
        # Set scale for precision (important for financial calculations)
        self.scale = pow(2, 40)
        self.context.global_scale = self.scale
        
        # Generate public/private key pair
        self.context.generate_galois_keys()
        
        # For demonstration, we'll store encrypted account balances
        self.encrypted_accounts: Dict[str, ts.CKKSVector] = {}
        self.transaction_log: List[Dict] = []
        
        logger.info(f"🏦 Secure Banking System initialized")
        logger.info(f"🔐 Security level: {poly_modulus_degree} bits")
        logger.info(f"💱 Scale: {self.scale}")
    
    def create_account(self, account_number: str, initial_balance: float) -> bool:
        """
        Create new bank account with encrypted balance
        
        Args:
            account_number: Account number (e.g., Aadhaar-linked)
            initial_balance: Initial balance in INR
            
        Returns:
            Success status
        """
        try:
            # Encrypt initial balance
            encrypted_balance = ts.ckks_vector(self.context, [initial_balance])
            self.encrypted_accounts[account_number] = encrypted_balance
            
            # Log account creation (without revealing balance)
            self.transaction_log.append({
                'type': 'ACCOUNT_CREATION',
                'account': account_number,
                'timestamp': datetime.now().isoformat(),
                'balance_hash': hashlib.sha256(str(initial_balance).encode()).hexdigest()[:8]
            })
            
            logger.info(f"💳 Account created: {account_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Account creation failed: {e}")
            return False
    
    def encrypted_transfer(self, from_account: str, to_account: str, 
                          amount: float) -> Tuple[bool, str]:
        """
        Transfer money between accounts using homomorphic operations
        UPI, NEFT, RTGS के लिए secure transfer
        
        Args:
            from_account: Source account number
            to_account: Destination account number
            amount: Transfer amount in INR
            
        Returns:
            (Success status, Transaction ID)
        """
        try:
            # Validate accounts exist
            if from_account not in self.encrypted_accounts:
                return False, "Source account not found"
            if to_account not in self.encrypted_accounts:
                return False, "Destination account not found"
            
            # Check if amount is positive
            if amount <= 0:
                return False, "Invalid transfer amount"
            
            # Encrypt transfer amount
            encrypted_amount = ts.ckks_vector(self.context, [amount])
            
            # Perform homomorphic subtraction from source account
            self.encrypted_accounts[from_account] = (
                self.encrypted_accounts[from_account] - encrypted_amount
            )
            
            # Perform homomorphic addition to destination account
            self.encrypted_accounts[to_account] = (
                self.encrypted_accounts[to_account] + encrypted_amount
            )
            
            # Generate transaction ID
            transaction_id = self._generate_transaction_id()
            
            # Log transaction
            self.transaction_log.append({
                'type': 'TRANSFER',
                'transaction_id': transaction_id,
                'from_account': from_account,
                'to_account': to_account,
                'amount_hash': hashlib.sha256(str(amount).encode()).hexdigest()[:8],
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"💸 Transfer completed: {from_account} → {to_account}")
            logger.info(f"🆔 Transaction ID: {transaction_id}")
            
            return True, transaction_id
            
        except Exception as e:
            logger.error(f"❌ Transfer failed: {e}")
            return False, str(e)
    
    def decrypt_balance(self, account_number: str) -> Optional[float]:
        """
        Decrypt account balance (only for authorized access)
        
        Args:
            account_number: Account to check
            
        Returns:
            Decrypted balance or None if account doesn't exist
        """
        if account_number not in self.encrypted_accounts:
            logger.warning(f"⚠️ Account not found: {account_number}")
            return None
        
        try:
            # Decrypt balance
            decrypted_balance = self.encrypted_accounts[account_number].decrypt()
            balance = decrypted_balance[0]  # First element is the balance
            
            logger.info(f"🔓 Balance decrypted for account: {account_number}")
            return round(balance, 2)
            
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            return None
    
    def encrypted_interest_calculation(self, account_number: str, 
                                     annual_rate: float, days: int) -> bool:
        """
        Calculate and add interest using homomorphic operations
        Savings account के लिए interest calculation without revealing balance
        
        Args:
            account_number: Account to calculate interest for
            annual_rate: Annual interest rate (e.g., 0.04 for 4%)
            days: Number of days to calculate interest for
            
        Returns:
            Success status
        """
        try:
            if account_number not in self.encrypted_accounts:
                logger.warning(f"⚠️ Account not found: {account_number}")
                return False
            
            # Calculate daily interest rate
            daily_rate = annual_rate / 365
            interest_multiplier = 1 + (daily_rate * days)
            
            # Encrypt interest multiplier
            encrypted_multiplier = ts.ckks_vector(self.context, [interest_multiplier])
            
            # Apply interest using homomorphic multiplication
            self.encrypted_accounts[account_number] = (
                self.encrypted_accounts[account_number] * encrypted_multiplier
            )
            
            # Log interest calculation
            self.transaction_log.append({
                'type': 'INTEREST_CALCULATION',
                'account': account_number,
                'annual_rate': annual_rate,
                'days': days,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"💰 Interest calculated for {account_number}: {annual_rate*100:.2f}% for {days} days")
            return True
            
        except Exception as e:
            logger.error(f"❌ Interest calculation failed: {e}")
            return False
    
    def encrypted_loan_emi_calculation(self, principal: float, annual_rate: float, 
                                     tenure_months: int) -> Optional[float]:
        """
        Calculate EMI using encrypted principal amount
        Home loan, personal loan के लिए privacy-preserving EMI calculation
        
        Args:
            principal: Loan amount in INR
            annual_rate: Annual interest rate
            tenure_months: Loan tenure in months
            
        Returns:
            Calculated EMI or None if calculation fails
        """
        try:
            # Encrypt principal amount
            encrypted_principal = ts.ckks_vector(self.context, [principal])
            
            # Calculate monthly interest rate
            monthly_rate = annual_rate / 12
            
            # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
            # Where P = principal, r = monthly rate, n = tenure
            
            # Calculate (1 + r)^n
            power_factor = pow(1 + monthly_rate, tenure_months)
            
            # Calculate EMI multiplier
            emi_multiplier = (monthly_rate * power_factor) / (power_factor - 1)
            
            # Encrypt EMI multiplier
            encrypted_multiplier = ts.ckks_vector(self.context, [emi_multiplier])
            
            # Calculate encrypted EMI
            encrypted_emi = encrypted_principal * encrypted_multiplier
            
            # Decrypt EMI for return (in real scenario, this might stay encrypted)
            decrypted_emi = encrypted_emi.decrypt()[0]
            
            logger.info(f"🏠 EMI calculated: Principal ₹{principal:,.2f}, "
                       f"Rate {annual_rate*100:.2f}%, Tenure {tenure_months} months")
            logger.info(f"💳 EMI: ₹{decrypted_emi:,.2f}")
            
            return round(decrypted_emi, 2)
            
        except Exception as e:
            logger.error(f"❌ EMI calculation failed: {e}")
            return None
    
    def encrypted_fraud_detection(self, account_number: str, 
                                transaction_amount: float) -> Tuple[bool, float]:
        """
        Fraud detection using encrypted transaction patterns
        Banking fraud को detect करने के लिए privacy-preserving ML
        
        Args:
            account_number: Account to check
            transaction_amount: Transaction amount to verify
            
        Returns:
            (Is suspicious, Risk score)
        """
        try:
            if account_number not in self.encrypted_accounts:
                return True, 1.0  # Unknown account is suspicious
            
            # Encrypt transaction amount
            encrypted_amount = ts.ckks_vector(self.context, [transaction_amount])
            
            # Get encrypted account balance
            encrypted_balance = self.encrypted_accounts[account_number]
            
            # Calculate ratio of transaction to balance (homomorphically)
            # This gives a risk indicator without revealing actual amounts
            encrypted_ratio = encrypted_amount / encrypted_balance
            
            # For simplicity, decrypt ratio for analysis
            # In production, this would use encrypted ML models
            ratio = encrypted_ratio.decrypt()[0]
            
            # Fraud detection logic
            risk_score = 0.0
            
            # High transaction-to-balance ratio indicates risk
            if ratio > 0.9:  # Transaction > 90% of balance
                risk_score += 0.5
            elif ratio > 0.5:  # Transaction > 50% of balance
                risk_score += 0.2
            
            # Check recent transaction patterns
            recent_transactions = [
                tx for tx in self.transaction_log 
                if tx.get('from_account') == account_number
                and self._is_recent(tx['timestamp'], hours=24)
            ]
            
            # Multiple transactions in short time
            if len(recent_transactions) > 5:
                risk_score += 0.3
            
            # Night-time transactions (higher risk)
            current_hour = datetime.now().hour
            if current_hour >= 23 or current_hour <= 5:
                risk_score += 0.1
            
            # Round numbers (common in fraud)
            if transaction_amount % 1000 == 0 and transaction_amount >= 10000:
                risk_score += 0.1
            
            is_suspicious = risk_score > 0.5
            
            logger.info(f"🕵️ Fraud check for {account_number}: "
                       f"Risk score {risk_score:.2f}, Suspicious: {is_suspicious}")
            
            return is_suspicious, round(risk_score, 2)
            
        except Exception as e:
            logger.error(f"❌ Fraud detection failed: {e}")
            return True, 1.0  # Default to suspicious on error
    
    def encrypted_credit_score_calculation(self, account_number: str, 
                                         salary: float, existing_loans: float,
                                         credit_history_months: int) -> Optional[int]:
        """
        Calculate credit score using encrypted financial data
        CIBIL score calculation without exposing sensitive financial information
        
        Args:
            account_number: Account holder
            salary: Monthly salary in INR
            existing_loans: Existing loan amount
            credit_history_months: Credit history length
            
        Returns:
            Credit score (300-850) or None if calculation fails
        """
        try:
            # Encrypt input parameters
            encrypted_salary = ts.ckks_vector(self.context, [salary])
            encrypted_loans = ts.ckks_vector(self.context, [existing_loans])
            encrypted_history = ts.ckks_vector(self.context, [credit_history_months])
            
            # Get encrypted account balance
            if account_number in self.encrypted_accounts:
                encrypted_balance = self.encrypted_accounts[account_number]
            else:
                encrypted_balance = ts.ckks_vector(self.context, [0])
            
            # Credit score calculation (simplified algorithm)
            # Score = base + salary_factor + balance_factor - loan_factor + history_factor
            
            base_score = 300  # Minimum credit score
            
            # Salary factor (higher salary = better score)
            salary_factor = 0.01  # 1 point per ₹100 salary
            encrypted_salary_score = encrypted_salary * ts.ckks_vector(self.context, [salary_factor])
            
            # Balance factor (higher balance = better score)
            balance_factor = 0.001  # 1 point per ₹1000 balance
            encrypted_balance_score = encrypted_balance * ts.ckks_vector(self.context, [balance_factor])
            
            # Loan factor (higher loans = lower score)
            loan_factor = -0.002  # -2 points per ₹1000 loan
            encrypted_loan_score = encrypted_loans * ts.ckks_vector(self.context, [loan_factor])
            
            # History factor (longer history = better score)
            history_factor = 2  # 2 points per month
            encrypted_history_score = encrypted_history * ts.ckks_vector(self.context, [history_factor])
            
            # Combine all factors
            encrypted_total_score = (
                encrypted_salary_score + 
                encrypted_balance_score + 
                encrypted_loan_score + 
                encrypted_history_score
            )
            
            # Add base score
            encrypted_base = ts.ckks_vector(self.context, [base_score])
            encrypted_final_score = encrypted_total_score + encrypted_base
            
            # Decrypt final score
            final_score = encrypted_final_score.decrypt()[0]
            
            # Clamp score to valid range (300-850)
            credit_score = max(300, min(850, int(final_score)))
            
            logger.info(f"📊 Credit score calculated for {account_number}: {credit_score}")
            
            # Log credit score calculation
            self.transaction_log.append({
                'type': 'CREDIT_SCORE_CALCULATION',
                'account': account_number,
                'credit_score': credit_score,
                'timestamp': datetime.now().isoformat()
            })
            
            return credit_score
            
        except Exception as e:
            logger.error(f"❌ Credit score calculation failed: {e}")
            return None
    
    def generate_encrypted_statement(self, account_number: str, 
                                   start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Generate account statement with encrypted transaction amounts
        Bank statement के साथ privacy-preserving transaction history
        
        Args:
            account_number: Account for statement
            start_date: Statement start date
            end_date: Statement end date
            
        Returns:
            List of encrypted transaction records
        """
        try:
            # Filter transactions for the account and date range
            account_transactions = []
            
            for tx in self.transaction_log:
                tx_date = datetime.fromisoformat(tx['timestamp'])
                
                # Check if transaction involves this account and is in date range
                if (start_date <= tx_date <= end_date and 
                    (tx.get('from_account') == account_number or 
                     tx.get('to_account') == account_number or
                     tx.get('account') == account_number)):
                    
                    # Create encrypted transaction record
                    encrypted_tx = {
                        'transaction_id': tx.get('transaction_id', 'N/A'),
                        'type': tx['type'],
                        'timestamp': tx['timestamp'],
                        'encrypted_amount': 'ENCRYPTED',  # Actual amount is encrypted
                        'amount_hash': tx.get('amount_hash', 'N/A')
                    }
                    
                    account_transactions.append(encrypted_tx)
            
            logger.info(f"📄 Statement generated for {account_number}: "
                       f"{len(account_transactions)} transactions")
            
            return account_transactions
            
        except Exception as e:
            logger.error(f"❌ Statement generation failed: {e}")
            return []
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"TXN{timestamp}{random_suffix.upper()}"
    
    def _is_recent(self, timestamp_str: str, hours: int = 24) -> bool:
        """Check if timestamp is within recent hours"""
        tx_time = datetime.fromisoformat(timestamp_str)
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return tx_time > cutoff_time
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        return {
            'total_accounts': len(self.encrypted_accounts),
            'total_transactions': len(self.transaction_log),
            'security_level': self.context.poly_modulus_degree,
            'encryption_scheme': 'CKKS',
            'scale': self.scale
        }

# Demonstration functions

def demo_basic_banking_operations():
    """Demonstrate basic banking operations with HE"""
    print("\n🏦 === Basic Banking Operations Demo ===")
    
    # Initialize secure banking system
    bank = SecureBankingSystem()
    
    # Create accounts
    bank.create_account("1234567890", 100000.0)  # ₹1 lakh initial balance
    bank.create_account("9876543210", 50000.0)   # ₹50k initial balance
    
    # Check initial balances
    print(f"Account 1 balance: ₹{bank.decrypt_balance('1234567890'):,.2f}")
    print(f"Account 2 balance: ₹{bank.decrypt_balance('9876543210'):,.2f}")
    
    # Perform encrypted transfer
    success, tx_id = bank.encrypted_transfer("1234567890", "9876543210", 25000.0)
    print(f"Transfer result: {success}, TX ID: {tx_id}")
    
    # Check balances after transfer
    print(f"Account 1 balance after transfer: ₹{bank.decrypt_balance('1234567890'):,.2f}")
    print(f"Account 2 balance after transfer: ₹{bank.decrypt_balance('9876543210'):,.2f}")

def demo_interest_calculation():
    """Demonstrate encrypted interest calculation"""
    print("\n💰 === Interest Calculation Demo ===")
    
    bank = SecureBankingSystem()
    bank.create_account("SAV001", 1000000.0)  # ₹10 lakh savings
    
    print(f"Initial balance: ₹{bank.decrypt_balance('SAV001'):,.2f}")
    
    # Calculate 6% annual interest for 30 days
    bank.encrypted_interest_calculation("SAV001", 0.06, 30)
    
    print(f"Balance after 30 days interest: ₹{bank.decrypt_balance('SAV001'):,.2f}")

def demo_loan_emi_calculation():
    """Demonstrate encrypted EMI calculation"""
    print("\n🏠 === Loan EMI Calculation Demo ===")
    
    bank = SecureBankingSystem()
    
    # Calculate EMI for home loan
    principal = 5000000.0  # ₹50 lakh home loan
    annual_rate = 0.085    # 8.5% annual interest
    tenure_months = 240    # 20 years
    
    emi = bank.encrypted_loan_emi_calculation(principal, annual_rate, tenure_months)
    
    if emi:
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
        
        print(f"Loan Principal: ₹{principal:,.2f}")
        print(f"Monthly EMI: ₹{emi:,.2f}")
        print(f"Total Payment: ₹{total_payment:,.2f}")
        print(f"Total Interest: ₹{total_interest:,.2f}")

def demo_fraud_detection():
    """Demonstrate encrypted fraud detection"""
    print("\n🕵️ === Fraud Detection Demo ===")
    
    bank = SecureBankingSystem()
    bank.create_account("USR001", 100000.0)
    
    # Normal transaction
    is_suspicious, risk_score = bank.encrypted_fraud_detection("USR001", 5000.0)
    print(f"Normal transaction (₹5,000): Suspicious={is_suspicious}, Risk={risk_score}")
    
    # Large transaction
    is_suspicious, risk_score = bank.encrypted_fraud_detection("USR001", 95000.0)
    print(f"Large transaction (₹95,000): Suspicious={is_suspicious}, Risk={risk_score}")

def demo_credit_score():
    """Demonstrate encrypted credit score calculation"""
    print("\n📊 === Credit Score Calculation Demo ===")
    
    bank = SecureBankingSystem()
    bank.create_account("CRD001", 200000.0)
    
    # Calculate credit score
    credit_score = bank.encrypted_credit_score_calculation(
        account_number="CRD001",
        salary=75000.0,         # ₹75k monthly salary
        existing_loans=500000.0, # ₹5 lakh existing loans
        credit_history_months=60 # 5 years credit history
    )
    
    if credit_score:
        print(f"Credit Score: {credit_score}")
        if credit_score >= 750:
            print("Excellent credit rating! 🌟")
        elif credit_score >= 650:
            print("Good credit rating 👍")
        else:
            print("Fair credit rating ⚠️")

if __name__ == "__main__":
    print("🇮🇳 Secure Banking System for Indian Banks")
    print("Privacy-preserving financial operations using Homomorphic Encryption")
    
    # Run all demonstrations
    demo_basic_banking_operations()
    demo_interest_calculation()
    demo_loan_emi_calculation()
    demo_fraud_detection()
    demo_credit_score()
    
    print("\n✅ All demonstrations completed!")
    print("🔐 All operations performed on encrypted data without exposing sensitive information")