"""
Data Anonymization Engine
डेटा गुमनामीकरण इंजन

Real-world example: Ola's data anonymization for ride data
Advanced anonymization techniques for Indian context data
"""

import re
import random
import string
import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import math

class AnonymizationTechnique(Enum):
    """Anonymization techniques - गुमनामीकरण तकनीक"""
    SUPPRESSION = "suppression"  # Remove data completely
    GENERALIZATION = "generalization"  # Make data less specific
    PERTURBATION = "perturbation"  # Add noise to data
    SUBSTITUTION = "substitution"  # Replace with fake data
    MASKING = "masking"  # Partially hide data
    PSEUDONYMIZATION = "pseudonymization"  # Replace with pseudonyms
    K_ANONYMITY = "k_anonymity"  # Group similar records
    DIFFERENTIAL_PRIVACY = "differential_privacy"  # Add statistical noise

@dataclass
class AnonymizationConfig:
    """Anonymization configuration - गुमनामीकरण कॉन्फ़िगरेशन"""
    field_name: str
    technique: AnonymizationTechnique
    parameters: Dict[str, Any]
    preserve_format: bool = False
    preserve_distribution: bool = False

class OlaDataAnonymizer:
    """
    Ola-style Data Anonymization Engine
    ओला-स्टाइल डेटा गुमनामीकरण इंजन
    
    Specialized for Indian context data like phone numbers, addresses, names
    """
    
    def __init__(self):
        self.indian_cities = [
            "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad",
            "Pune", "Ahmedabad", "Surat", "Jaipur", "Lucknow", "Kanpur",
            "Nagpur", "Visakhapatnam", "Bhopal", "Patna", "Vadodara", "Ghaziabad"
        ]
        
        self.indian_names = {
            "first": [
                "Arjun", "Aarav", "Vivaan", "Aditya", "Vihaan", "Sai", "Krishna",
                "Ishaan", "Shaurya", "Atharv", "Priya", "Ananya", "Kavya",
                "Aanya", "Diya", "Saanvi", "Aadhya", "Pari", "Avni", "Myra"
            ],
            "last": [
                "Sharma", "Verma", "Gupta", "Kumar", "Singh", "Patel", "Jain",
                "Agarwal", "Pandey", "Shah", "Mehta", "Reddy", "Iyer", "Nair",
                "Pillai", "Srinivasan", "Choudhary", "Malhotra", "Kapoor"
            ]
        }
        
        self.area_codes = ["11", "22", "33", "40", "44", "79", "80", "124", "120"]
        
        # Pseudonym mapping for consistent anonymization
        self.pseudonym_map = {}
        
    def anonymize_dataset(self, dataset: List[Dict], config: List[AnonymizationConfig]) -> List[Dict]:
        """
        Anonymize complete dataset
        पूरे डेटासेट को गुमनाम करें
        """
        print(f"🎭 Starting anonymization of {len(dataset)} records")
        
        anonymized_data = []
        
        for record in dataset:
            anonymized_record = self.anonymize_record(record, config)
            anonymized_data.append(anonymized_record)
            
        print(f"✅ Anonymization completed: {len(anonymized_data)} records processed")
        return anonymized_data
    
    def anonymize_record(self, record: Dict, config: List[AnonymizationConfig]) -> Dict:
        """
        Anonymize single record
        एकल रिकॉर्ड को गुमनाम करें
        """
        anonymized = record.copy()
        
        for field_config in config:
            if field_config.field_name in anonymized:
                original_value = anonymized[field_config.field_name]
                
                if original_value is not None:
                    anonymized_value = self.apply_anonymization(
                        original_value, field_config
                    )
                    anonymized[field_config.field_name] = anonymized_value
                    
        return anonymized
    
    def apply_anonymization(self, value: Any, config: AnonymizationConfig) -> Any:
        """
        Apply anonymization technique
        गुमनामीकरण तकनीक लागू करें
        """
        technique = config.technique
        
        if technique == AnonymizationTechnique.SUPPRESSION:
            return self.suppress_data(value, config)
            
        elif technique == AnonymizationTechnique.GENERALIZATION:
            return self.generalize_data(value, config)
            
        elif technique == AnonymizationTechnique.PERTURBATION:
            return self.perturb_data(value, config)
            
        elif technique == AnonymizationTechnique.SUBSTITUTION:
            return self.substitute_data(value, config)
            
        elif technique == AnonymizationTechnique.MASKING:
            return self.mask_data(value, config)
            
        elif technique == AnonymizationTechnique.PSEUDONYMIZATION:
            return self.pseudonymize_data(value, config)
            
        else:
            return value
    
    def suppress_data(self, value: Any, config: AnonymizationConfig) -> Any:
        """Complete data suppression - पूर्ण डेटा दमन"""
        return None
    
    def generalize_data(self, value: Any, config: AnonymizationConfig) -> Any:
        """Data generalization - डेटा सामान्यीकरण"""
        field_name = config.field_name
        
        if field_name == "age":
            age = int(value)
            if age < 18:
                return "Under 18"
            elif age < 30:
                return "18-29"
            elif age < 50:
                return "30-49"
            else:
                return "50+"
                
        elif field_name == "salary":
            salary = float(value)
            if salary < 300000:
                return "Below 3L"
            elif salary < 1000000:
                return "3L-10L"
            elif salary < 2500000:
                return "10L-25L"
            else:
                return "Above 25L"
                
        elif field_name == "pincode":
            # Generalize to city level
            pincode = str(value)
            if pincode.startswith("110"):
                return "Delhi Region"
            elif pincode.startswith("400"):
                return "Mumbai Region"
            elif pincode.startswith("560"):
                return "Bangalore Region"
            elif pincode.startswith("600"):
                return "Chennai Region"
            else:
                return "Other Region"
                
        elif field_name == "pickup_location" or field_name == "drop_location":
            # Generalize to area/locality level
            location = str(value)
            # Extract area from full address
            parts = location.split(",")
            if len(parts) >= 2:
                return f"{parts[1].strip()}, {parts[-1].strip()}"  # Area, City
            return location
            
        return value
    
    def perturb_data(self, value: Any, config: AnonymizationConfig) -> Any:
        """Add noise to numerical data - संख्यात्मक डेटा में शोर जोड़ें"""
        if isinstance(value, (int, float)):
            noise_factor = config.parameters.get("noise_factor", 0.1)
            noise = random.uniform(-noise_factor, noise_factor) * value
            
            if isinstance(value, int):
                return int(value + noise)
            else:
                return round(value + noise, 2)
                
        elif field_name == "trip_distance":
            # Add small random variation to distance
            distance = float(value)
            variation = random.uniform(-0.5, 0.5)  # +/- 500m variation
            return round(max(0.1, distance + variation), 2)
            
        elif field_name == "trip_duration":
            # Add random variation to trip duration
            duration = int(value)
            variation = random.randint(-2, 2)  # +/- 2 minutes
            return max(1, duration + variation)
            
        return value
    
    def substitute_data(self, value: Any, config: AnonymizationConfig) -> Any:
        """Replace with synthetic data - सिंथेटिक डेटा के साथ बदलें"""
        field_name = config.field_name
        
        if field_name == "name" or field_name == "customer_name":
            return self.generate_indian_name()
            
        elif field_name == "phone" or field_name == "mobile_number":
            return self.generate_indian_phone()
            
        elif field_name == "email":
            return self.generate_email()
            
        elif field_name == "vehicle_number":
            return self.generate_vehicle_number()
            
        elif field_name == "driver_name":
            return self.generate_indian_name()
            
        elif field_name == "pickup_address" or field_name == "drop_address":
            return self.generate_indian_address()
            
        return value
    
    def mask_data(self, value: Any, config: AnonymizationConfig) -> Any:
        """Partial data masking - आंशिक डेटा मास्किंग"""
        value_str = str(value)
        mask_char = config.parameters.get("mask_char", "*")
        preserve_start = config.parameters.get("preserve_start", 2)
        preserve_end = config.parameters.get("preserve_end", 2)
        
        if len(value_str) <= preserve_start + preserve_end:
            return mask_char * len(value_str)
            
        start_part = value_str[:preserve_start]
        end_part = value_str[-preserve_end:] if preserve_end > 0 else ""
        middle_length = len(value_str) - preserve_start - preserve_end
        middle_part = mask_char * middle_length
        
        return start_part + middle_part + end_part
    
    def pseudonymize_data(self, value: Any, config: AnonymizationConfig) -> Any:
        """Replace with consistent pseudonyms - स्थिर छद्मनाम के साथ बदलें"""
        value_str = str(value)
        
        # Check if we already have a pseudonym for this value
        if value_str in self.pseudonym_map:
            return self.pseudonym_map[value_str]
            
        # Generate new pseudonym
        field_name = config.field_name
        
        if field_name in ["user_id", "customer_id", "driver_id"]:
            # Generate consistent hash-based ID
            hash_obj = hashlib.md5(value_str.encode())
            pseudonym = f"USER_{hash_obj.hexdigest()[:8].upper()}"
            
        elif field_name in ["trip_id", "booking_id"]:
            # Generate trip-like ID
            hash_obj = hashlib.md5(value_str.encode())
            pseudonym = f"TRIP_{hash_obj.hexdigest()[:10].upper()}"
            
        else:
            # Generic hash-based pseudonym
            hash_obj = hashlib.md5(value_str.encode())
            pseudonym = f"ANON_{hash_obj.hexdigest()[:6].upper()}"
            
        self.pseudonym_map[value_str] = pseudonym
        return pseudonym
    
    def generate_indian_name(self) -> str:
        """Generate realistic Indian name - वास्तविक भारतीय नाम जेनरेट करें"""
        first_name = random.choice(self.indian_names["first"])
        last_name = random.choice(self.indian_names["last"])
        return f"{first_name} {last_name}"
    
    def generate_indian_phone(self) -> str:
        """Generate Indian mobile number - भारतीय मोबाइल नंबर जेनरेट करें"""
        # Indian mobile numbers start with 6, 7, 8, or 9
        first_digit = random.choice(['6', '7', '8', '9'])
        remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        return f"+91{first_digit}{remaining_digits}"
    
    def generate_email(self) -> str:
        """Generate synthetic email - सिंथेटिक ईमेल जेनरेट करें"""
        domains = ["gmail.com", "yahoo.co.in", "hotmail.com", "rediffmail.com", "outlook.com"]
        username_length = random.randint(6, 12)
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def generate_vehicle_number(self) -> str:
        """Generate Indian vehicle registration number"""
        state_codes = ["MH", "DL", "KA", "TN", "WB", "AP", "UP", "GJ", "RJ", "MP"]
        state_code = random.choice(state_codes)
        city_code = f"{random.randint(1, 99):02d}"
        series = random.choice(string.ascii_uppercase)
        series += random.choice(string.ascii_uppercase)
        number = f"{random.randint(1000, 9999)}"
        
        return f"{state_code}{city_code}{series}{number}"
    
    def generate_indian_address(self) -> str:
        """Generate synthetic Indian address"""
        building_no = random.randint(1, 999)
        street_names = ["MG Road", "Gandhi Nagar", "Park Street", "Main Road", "Station Road"]
        area_names = ["Sector 21", "Block A", "Phase 2", "Extension", "Colony"]
        
        street = random.choice(street_names)
        area = random.choice(area_names)
        city = random.choice(self.indian_cities)
        pincode = f"{random.randint(100000, 999999)}"
        
        return f"{building_no}, {street}, {area}, {city}, {pincode}"
    
    def apply_k_anonymity(self, dataset: List[Dict], k: int, quasi_identifiers: List[str]) -> List[Dict]:
        """
        Apply k-anonymity to dataset
        डेटासेट पर k-गुमनामता लागू करें
        """
        print(f"🔒 Applying {k}-anonymity on {len(quasi_identifiers)} quasi-identifiers")
        
        # Group records by quasi-identifier combinations
        groups = {}
        
        for record in dataset:
            # Create key from quasi-identifiers
            key_parts = []
            for qi in quasi_identifiers:
                if qi in record:
                    key_parts.append(str(record[qi]))
                else:
                    key_parts.append("NULL")
            
            key = "|".join(key_parts)
            
            if key not in groups:
                groups[key] = []
            groups[key].append(record)
        
        # Process groups that don't meet k-anonymity
        k_anonymous_data = []
        
        for key, records in groups.items():
            if len(records) >= k:
                # Group already satisfies k-anonymity
                k_anonymous_data.extend(records)
            else:
                # Need to generalize or suppress this group
                print(f"⚠️ Group {key} has only {len(records)} records (< {k})")
                
                # Apply generalization to quasi-identifiers
                for record in records:
                    generalized_record = record.copy()
                    
                    for qi in quasi_identifiers:
                        if qi in generalized_record:
                            # Apply generalization based on field type
                            if qi == "age":
                                age = int(generalized_record[qi])
                                generalized_record[qi] = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
                            elif qi == "pincode":
                                pincode = str(generalized_record[qi])
                                generalized_record[qi] = pincode[:3] + "XXX"
                            elif qi == "salary":
                                salary = float(generalized_record[qi])
                                generalized_record[qi] = f"{(salary // 100000) * 100000}-{(salary // 100000 + 1) * 100000}"
                    
                    k_anonymous_data.append(generalized_record)
        
        print(f"✅ K-anonymity applied: {len(k_anonymous_data)} records")
        return k_anonymous_data
    
    def add_differential_privacy_noise(self, value: float, epsilon: float = 1.0, sensitivity: float = 1.0) -> float:
        """
        Add Laplacian noise for differential privacy
        डिफरेंशियल प्राइवेसी के लिए लैप्लासियन शोर जोड़ें
        """
        # Laplacian noise with scale = sensitivity / epsilon
        scale = sensitivity / epsilon
        noise = random.laplace(0, scale)
        
        return value + noise
    
    def calculate_anonymization_metrics(self, original_data: List[Dict], anonymized_data: List[Dict]) -> Dict:
        """
        Calculate anonymization quality metrics
        गुमनामीकरण गुणवत्ता मेट्रिक्स की गणना करें
        """
        metrics = {
            "data_loss": 0.0,
            "information_loss": 0.0,
            "re_identification_risk": 0.0,
            "utility_preservation": 0.0
        }
        
        if not original_data or not anonymized_data:
            return metrics
        
        # Calculate data loss (fields completely removed)
        original_fields = set(original_data[0].keys()) if original_data else set()
        anonymized_fields = set(anonymized_data[0].keys()) if anonymized_data else set()
        
        removed_fields = original_fields - anonymized_fields
        metrics["data_loss"] = len(removed_fields) / len(original_fields) if original_fields else 0
        
        # Calculate information loss (simplified)
        total_changes = 0
        total_fields = 0
        
        for orig, anon in zip(original_data, anonymized_data):
            for field in original_fields & anonymized_fields:
                total_fields += 1
                if str(orig.get(field)) != str(anon.get(field)):
                    total_changes += 1
        
        metrics["information_loss"] = total_changes / total_fields if total_fields > 0 else 0
        
        # Simplified utility preservation (inverse of information loss)
        metrics["utility_preservation"] = 1.0 - metrics["information_loss"]
        
        # Simplified re-identification risk (based on unique combinations)
        unique_combinations = len(set(tuple(record.items()) for record in anonymized_data))
        total_records = len(anonymized_data)
        metrics["re_identification_risk"] = 1.0 - (unique_combinations / total_records) if total_records > 0 else 0
        
        return metrics

def main():
    """
    Main demonstration function
    मुख्य प्रदर्शन फ़ंक्शन
    """
    print("🚗 Ola Data Anonymization Engine Demo")
    print("=" * 50)
    
    anonymizer = OlaDataAnonymizer()
    
    # Sample Ola ride data
    sample_data = [
        {
            "trip_id": "OLA123456",
            "customer_name": "Rajesh Kumar",
            "phone": "+919876543210",
            "email": "rajesh.kumar@gmail.com",
            "age": 32,
            "pickup_location": "123, MG Road, Koramangala, Bangalore, 560095",
            "drop_location": "456, Brigade Road, Commercial Street, Bangalore, 560001",
            "driver_name": "Suresh Sharma",
            "driver_phone": "+918765432109",
            "vehicle_number": "KA03AB1234",
            "trip_distance": 8.5,
            "trip_duration": 25,
            "fare": 180.50,
            "rating": 4.2
        },
        {
            "trip_id": "OLA789012",
            "customer_name": "Priya Patel",
            "phone": "+919123456789",
            "email": "priya.patel@yahoo.co.in",
            "age": 28,
            "pickup_location": "789, Park Street, Ballygunge, Kolkata, 700019",
            "drop_location": "321, Salt Lake, Sector V, Kolkata, 700091",
            "driver_name": "Amit Das",
            "driver_phone": "+917654321098",
            "vehicle_number": "WB02CD5678",
            "trip_distance": 12.3,
            "trip_duration": 35,
            "fare": 245.00,
            "rating": 4.8
        },
        {
            "trip_id": "OLA345678",
            "customer_name": "Mohammed Ahmed",
            "phone": "+918901234567",
            "email": "m.ahmed@hotmail.com",
            "age": 45,
            "pickup_location": "567, Connaught Place, Central Delhi, Delhi, 110001",
            "drop_location": "890, Nehru Place, South Delhi, Delhi, 110019",
            "driver_name": "Vikram Singh",
            "driver_phone": "+916543210987",
            "vehicle_number": "DL01EF9012",
            "trip_distance": 15.7,
            "trip_duration": 42,
            "fare": 320.75,
            "rating": 3.9
        }
    ]
    
    # Define anonymization configuration
    anonymization_config = [
        AnonymizationConfig("customer_name", AnonymizationTechnique.SUBSTITUTION, {}),
        AnonymizationConfig("phone", AnonymizationTechnique.MASKING, {
            "preserve_start": 3, "preserve_end": 2, "mask_char": "X"
        }),
        AnonymizationConfig("email", AnonymizationTechnique.SUBSTITUTION, {}),
        AnonymizationConfig("age", AnonymizationTechnique.GENERALIZATION, {}),
        AnonymizationConfig("pickup_location", AnonymizationTechnique.GENERALIZATION, {}),
        AnonymizationConfig("drop_location", AnonymizationTechnique.GENERALIZATION, {}),
        AnonymizationConfig("driver_name", AnonymizationTechnique.PSEUDONYMIZATION, {}),
        AnonymizationConfig("driver_phone", AnonymizationTechnique.SUPPRESSION, {}),
        AnonymizationConfig("vehicle_number", AnonymizationTechnique.SUBSTITUTION, {}),
        AnonymizationConfig("trip_distance", AnonymizationTechnique.PERTURBATION, {"noise_factor": 0.1}),
        AnonymizationConfig("trip_duration", AnonymizationTechnique.PERTURBATION, {"noise_factor": 0.05}),
        AnonymizationConfig("fare", AnonymizationTechnique.PERTURBATION, {"noise_factor": 0.05})
    ]
    
    print("\n📊 Original Data:")
    for i, record in enumerate(sample_data, 1):
        print(f"  Record {i}: {json.dumps(record, indent=4)}")
    
    # Apply anonymization
    print("\n🎭 Applying Anonymization...")
    anonymized_data = anonymizer.anonymize_dataset(sample_data, anonymization_config)
    
    print("\n🔒 Anonymized Data:")
    for i, record in enumerate(anonymized_data, 1):
        print(f"  Record {i}: {json.dumps(record, indent=4)}")
    
    # Apply k-anonymity
    print("\n🔐 Applying 2-Anonymity on quasi-identifiers...")
    quasi_identifiers = ["age", "pickup_location", "drop_location"]
    k_anonymous_data = anonymizer.apply_k_anonymity(anonymized_data, 2, quasi_identifiers)
    
    print("\n📊 K-Anonymous Data (k=2):")
    for i, record in enumerate(k_anonymous_data, 1):
        print(f"  Record {i}: {json.dumps(record, indent=4)}")
    
    # Calculate metrics
    print("\n📈 Anonymization Quality Metrics:")
    metrics = anonymizer.calculate_anonymization_metrics(sample_data, k_anonymous_data)
    print(f"  Data Loss: {metrics['data_loss']:.1%}")
    print(f"  Information Loss: {metrics['information_loss']:.1%}")
    print(f"  Utility Preservation: {metrics['utility_preservation']:.1%}")
    print(f"  Re-identification Risk: {metrics['re_identification_risk']:.1%}")
    
    # Demonstrate differential privacy
    print("\n🔬 Differential Privacy Example:")
    original_avg_fare = sum(record["fare"] for record in sample_data) / len(sample_data)
    private_avg_fare = anonymizer.add_differential_privacy_noise(original_avg_fare, epsilon=1.0)
    
    print(f"  Original Average Fare: ₹{original_avg_fare:.2f}")
    print(f"  Private Average Fare: ₹{private_avg_fare:.2f}")
    print(f"  Noise Added: ₹{abs(private_avg_fare - original_avg_fare):.2f}")

if __name__ == "__main__":
    main()