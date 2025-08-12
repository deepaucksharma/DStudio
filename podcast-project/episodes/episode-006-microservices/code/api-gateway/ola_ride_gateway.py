#!/usr/bin/env python3
"""
Ola-style Ride Matching API Gateway
Dynamic routing based on ride types, geography, and driver availability

जैसे Mumbai में different routes Andheri se Bandra jaane ke लिए,
वैसे ही ride types के अनुसार different services को route करते हैं
"""

import asyncio
import json
import logging
import time
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import geopy.distance
import redis
import aiohttp
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from enum import Enum
import random

# Ola-style logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OlaRideGateway")

class RideType(Enum):
    """Different ride categories like Ola"""
    MINI = "mini"           # Economy rides - like sharing auto in Mumbai
    PRIME = "prime"         # Premium sedan - like AC taxi
    SUV = "suv"            # Large vehicles - like Mahindra Scorpio
    AUTO = "auto"          # Auto rickshaw - Mumbai special
    BIKE = "bike"          # Two wheeler - for traffic jams
    OUTSTATION = "outstation"  # Long distance - Mumbai to Pune

class ServiceZone(Enum):
    """Mumbai zones for service routing"""
    SOUTH_MUMBAI = "south_mumbai"     # Fort, Colaba, Churchgate
    CENTRAL_MUMBAI = "central_mumbai" # Dadar, Bandra, Andheri
    WESTERN_SUBURBS = "western_suburbs" # Borivali, Malad, Goregaon
    EASTERN_SUBURBS = "eastern_suburbs" # Thane, Mulund, Vikhroli
    NAVI_MUMBAI = "navi_mumbai"       # Vashi, Nerul, Panvel

@dataclass
class RideRequest:
    """Ride request structure"""
    user_id: str
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    ride_type: RideType
    pickup_address: str
    dropoff_address: str
    estimated_fare: float = 0.0
    distance_km: float = 0.0
    estimated_time_minutes: int = 0

@dataclass
class DriverLocation:
    """Driver location and availability"""
    driver_id: str
    lat: float
    lng: float
    ride_type: RideType
    is_available: bool
    current_zone: ServiceZone
    rating: float
    vehicle_number: str

class GeoLocationService:
    """Geographic calculations for Mumbai"""
    
    # Mumbai zone boundaries (approximate)
    ZONE_BOUNDARIES = {
        ServiceZone.SOUTH_MUMBAI: {
            "center": (18.9220, 72.8342),  # Fort area
            "radius_km": 8
        },
        ServiceZone.CENTRAL_MUMBAI: {
            "center": (19.0760, 72.8777),  # Bandra
            "radius_km": 12
        },
        ServiceZone.WESTERN_SUBURBS: {
            "center": (19.2183, 72.8479),  # Borivali
            "radius_km": 15
        },
        ServiceZone.EASTERN_SUBURBS: {
            "center": (19.2183, 72.9781),  # Thane
            "radius_km": 15
        },
        ServiceZone.NAVI_MUMBAI: {
            "center": (19.0330, 73.0297),  # Vashi
            "radius_km": 20
        }
    }
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        return geopy.distance.geodesic((lat1, lng1), (lat2, lng2)).kilometers
    
    @staticmethod
    def get_zone(lat: float, lng: float) -> ServiceZone:
        """Determine which Mumbai zone the coordinates belong to"""
        min_distance = float('inf')
        closest_zone = ServiceZone.CENTRAL_MUMBAI
        
        for zone, boundary in GeoLocationService.ZONE_BOUNDARIES.items():
            center_lat, center_lng = boundary["center"]
            distance = GeoLocationService.calculate_distance(lat, lng, center_lat, center_lng)
            
            if distance < min_distance:
                min_distance = distance
                closest_zone = zone
        
        return closest_zone
    
    @staticmethod
    def estimate_travel_time(distance_km: float, zone: ServiceZone) -> int:
        """Estimate travel time based on Mumbai traffic patterns"""
        # Mumbai traffic multipliers
        traffic_multipliers = {
            ServiceZone.SOUTH_MUMBAI: 2.5,    # Heavy traffic like Nariman Point
            ServiceZone.CENTRAL_MUMBAI: 2.0,  # Moderate like Bandra
            ServiceZone.WESTERN_SUBURBS: 1.8, # Better roads
            ServiceZone.EASTERN_SUBURBS: 1.7, # Less congested
            ServiceZone.NAVI_MUMBAI: 1.5      # Planned city, better roads
        }
        
        # Base speed assumption: 25 km/h average in Mumbai traffic
        base_time_minutes = (distance_km / 25) * 60
        multiplier = traffic_multipliers.get(zone, 2.0)
        
        return int(base_time_minutes * multiplier)

class RideMatchingEngine:
    """Core ride matching logic - जैसे Ola का brain"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.geo_service = GeoLocationService()
        
    async def find_nearby_drivers(self, ride_request: RideRequest, 
                                radius_km: float = 5.0) -> List[DriverLocation]:
        """
        Find nearby available drivers
        जैसे Mumbai में nearest auto rickshaw ढूंढना
        """
        pickup_zone = self.geo_service.get_zone(ride_request.pickup_lat, ride_request.pickup_lng)
        
        # Get all available drivers from Redis (in production, use geospatial queries)
        driver_keys = self.redis.keys("driver:*")
        nearby_drivers = []
        
        for key in driver_keys:
            driver_data = self.redis.hgetall(key)
            if not driver_data:
                continue
                
            driver = DriverLocation(
                driver_id=driver_data.get(b'driver_id', b'').decode(),
                lat=float(driver_data.get(b'lat', 0)),
                lng=float(driver_data.get(b'lng', 0)),
                ride_type=RideType(driver_data.get(b'ride_type', b'mini').decode()),
                is_available=driver_data.get(b'is_available', b'false').decode().lower() == 'true',
                current_zone=ServiceZone(driver_data.get(b'current_zone', b'central_mumbai').decode()),
                rating=float(driver_data.get(b'rating', 4.0)),
                vehicle_number=driver_data.get(b'vehicle_number', b'').decode()
            )
            
            # Filter by availability and ride type
            if not driver.is_available or driver.ride_type != ride_request.ride_type:
                continue
            
            # Calculate distance from pickup point
            distance = self.geo_service.calculate_distance(
                ride_request.pickup_lat, ride_request.pickup_lng,
                driver.lat, driver.lng
            )
            
            if distance <= radius_km:
                nearby_drivers.append(driver)
        
        # Sort by distance and rating
        nearby_drivers.sort(key=lambda d: (
            self.geo_service.calculate_distance(
                ride_request.pickup_lat, ride_request.pickup_lng, d.lat, d.lng
            ),
            -d.rating  # Higher rating is better
        ))
        
        logger.info(f"Found {len(nearby_drivers)} nearby drivers for {ride_request.ride_type.value}")
        return nearby_drivers[:10]  # Return top 10 drivers
    
    def calculate_fare(self, ride_request: RideRequest) -> float:
        """
        Calculate ride fare based on Ola-style pricing
        Mumbai के अनुसार different zones में different rates
        """
        distance_km = ride_request.distance_km
        zone = self.geo_service.get_zone(ride_request.pickup_lat, ride_request.pickup_lng)
        
        # Base fare structure (in INR)
        base_fares = {
            RideType.MINI: {"base": 25, "per_km": 10, "per_min": 1.5},
            RideType.PRIME: {"base": 50, "per_km": 15, "per_min": 2.0},
            RideType.SUV: {"base": 80, "per_km": 20, "per_min": 2.5},
            RideType.AUTO: {"base": 20, "per_km": 12, "per_min": 1.0},
            RideType.BIKE: {"base": 15, "per_km": 8, "per_min": 1.0},
            RideType.OUTSTATION: {"base": 200, "per_km": 25, "per_min": 0}
        }
        
        # Zone multipliers - South Mumbai is more expensive
        zone_multipliers = {
            ServiceZone.SOUTH_MUMBAI: 1.5,
            ServiceZone.CENTRAL_MUMBAI: 1.2,
            ServiceZone.WESTERN_SUBURBS: 1.0,
            ServiceZone.EASTERN_SUBURBS: 1.0,
            ServiceZone.NAVI_MUMBAI: 0.9
        }
        
        fare_config = base_fares.get(ride_request.ride_type, base_fares[RideType.MINI])
        zone_multiplier = zone_multipliers.get(zone, 1.0)
        
        # Calculate components
        base_fare = fare_config["base"]
        distance_fare = distance_km * fare_config["per_km"]
        time_fare = ride_request.estimated_time_minutes * fare_config["per_min"]
        
        total_fare = (base_fare + distance_fare + time_fare) * zone_multiplier
        
        # Add surge pricing during peak hours (Mumbai office hours)
        current_hour = datetime.now().hour
        if current_hour in [8, 9, 10, 18, 19, 20]:  # Office hours
            surge_multiplier = 1.5
            logger.info(f"Surge pricing applied: {surge_multiplier}x")
            total_fare *= surge_multiplier
        
        return round(total_fare, 2)

class OlaRideGateway:
    """Ola-style API Gateway with intelligent routing"""
    
    def __init__(self):
        self.app = FastAPI(title="Ola Ride Gateway", version="2.0.0")
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.matching_engine = RideMatchingEngine(self.redis)
        
        # Service endpoints for different functionalities
        self.service_endpoints = {
            "user_service": "http://user-service:8001",
            "driver_service": "http://driver-service:8002", 
            "pricing_service": "http://pricing-service:8003",
            "booking_service": "http://booking-service:8004",
            "payment_service": "http://payment-service:8005",
            "notification_service": "http://notification-service:8006",
            "tracking_service": "http://tracking-service:8007"
        }
        
        self._setup_middleware()
        self._setup_routes()
        self._populate_sample_data()
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "ola-ride-gateway",
                "timestamp": datetime.now().isoformat(),
                "message": "Ready for Mumbai traffic! 🚗"
            }
        
        @self.app.post("/api/rides/estimate")
        async def estimate_ride(request: Request, ride_data: dict = Body(...)):
            """Estimate ride fare and time"""
            return await self._handle_ride_estimation(ride_data)
        
        @self.app.post("/api/rides/book")
        async def book_ride(request: Request, booking_data: dict = Body(...)):
            """Book a ride with driver matching"""
            return await self._handle_ride_booking(booking_data)
        
        @self.app.get("/api/rides/{ride_id}")
        async def get_ride_status(ride_id: str):
            """Get ride status and live tracking"""
            return await self._handle_ride_tracking(ride_id)
        
        @self.app.post("/api/rides/{ride_id}/cancel")
        async def cancel_ride(ride_id: str):
            """Cancel booked ride"""
            return await self._handle_ride_cancellation(ride_id)
        
        @self.app.get("/api/drivers/nearby")
        async def get_nearby_drivers(
            lat: float = Query(...), 
            lng: float = Query(...),
            ride_type: str = Query(default="mini")
        ):
            """Get nearby available drivers"""
            return await self._handle_driver_discovery(lat, lng, ride_type)
    
    async def _handle_ride_estimation(self, ride_data: dict) -> dict:
        """
        Handle ride estimation request
        जैसे Ola में price estimate देखना before booking
        """
        try:
            # Parse ride request
            ride_request = RideRequest(
                user_id=ride_data.get("user_id", ""),
                pickup_lat=ride_data["pickup_lat"],
                pickup_lng=ride_data["pickup_lng"],
                dropoff_lat=ride_data["dropoff_lat"],
                dropoff_lng=ride_data["dropoff_lng"],
                ride_type=RideType(ride_data.get("ride_type", "mini")),
                pickup_address=ride_data.get("pickup_address", ""),
                dropoff_address=ride_data.get("dropoff_address", "")
            )
            
            # Calculate distance and time
            distance_km = GeoLocationService.calculate_distance(
                ride_request.pickup_lat, ride_request.pickup_lng,
                ride_request.dropoff_lat, ride_request.dropoff_lng
            )
            
            pickup_zone = GeoLocationService.get_zone(
                ride_request.pickup_lat, ride_request.pickup_lng
            )
            
            estimated_time = GeoLocationService.estimate_travel_time(distance_km, pickup_zone)
            
            # Update ride request with calculations
            ride_request.distance_km = distance_km
            ride_request.estimated_time_minutes = estimated_time
            ride_request.estimated_fare = self.matching_engine.calculate_fare(ride_request)
            
            # Find nearby drivers for availability check
            nearby_drivers = await self.matching_engine.find_nearby_drivers(ride_request)
            
            return {
                "ride_id": hashlib.md5(f"{ride_request.user_id}{time.time()}".encode()).hexdigest()[:12],
                "distance_km": round(distance_km, 2),
                "estimated_time_minutes": estimated_time,
                "estimated_fare": ride_request.estimated_fare,
                "currency": "INR",
                "pickup_zone": pickup_zone.value,
                "available_drivers": len(nearby_drivers),
                "ride_type": ride_request.ride_type.value,
                "surge_active": self._is_surge_time(),
                "estimated_arrival": f"{random.randint(3, 8)} minutes",
                "message": f"Found {len(nearby_drivers)} drivers nearby - Like finding rickshaw in Dadar!"
            }
            
        except Exception as e:
            logger.error(f"Ride estimation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def _handle_ride_booking(self, booking_data: dict) -> dict:
        """Handle actual ride booking with driver assignment"""
        try:
            # Create ride request
            ride_request = RideRequest(
                user_id=booking_data["user_id"],
                pickup_lat=booking_data["pickup_lat"],
                pickup_lng=booking_data["pickup_lng"],
                dropoff_lat=booking_data["dropoff_lat"],
                dropoff_lng=booking_data["dropoff_lng"],
                ride_type=RideType(booking_data.get("ride_type", "mini")),
                pickup_address=booking_data.get("pickup_address", ""),
                dropoff_address=booking_data.get("dropoff_address", "")
            )
            
            # Calculate details
            distance_km = GeoLocationService.calculate_distance(
                ride_request.pickup_lat, ride_request.pickup_lng,
                ride_request.dropoff_lat, ride_request.dropoff_lng
            )
            ride_request.distance_km = distance_km
            ride_request.estimated_fare = self.matching_engine.calculate_fare(ride_request)
            
            # Find and assign driver
            nearby_drivers = await self.matching_engine.find_nearby_drivers(ride_request)
            
            if not nearby_drivers:
                return {
                    "success": False,
                    "error": "No drivers available",
                    "message": "Koi driver nahi mila - Try again in few minutes!"
                }
            
            # Select best driver (first in sorted list)
            assigned_driver = nearby_drivers[0]
            ride_id = hashlib.md5(f"{ride_request.user_id}{time.time()}".encode()).hexdigest()[:12]
            
            # Store booking in Redis
            booking_info = {
                "ride_id": ride_id,
                "user_id": ride_request.user_id,
                "driver_id": assigned_driver.driver_id,
                "pickup_lat": ride_request.pickup_lat,
                "pickup_lng": ride_request.pickup_lng,
                "dropoff_lat": ride_request.dropoff_lat,
                "dropoff_lng": ride_request.dropoff_lng,
                "fare": ride_request.estimated_fare,
                "status": "assigned",
                "created_at": datetime.now().isoformat()
            }
            
            self.redis.hset(f"ride:{ride_id}", mapping=booking_info)
            
            # Mark driver as busy
            self.redis.hset(f"driver:{assigned_driver.driver_id}", "is_available", "false")
            
            # Route to booking service for detailed processing
            await self._route_to_service("booking_service", "/api/bookings", booking_info)
            
            return {
                "success": True,
                "ride_id": ride_id,
                "driver": {
                    "driver_id": assigned_driver.driver_id,
                    "vehicle_number": assigned_driver.vehicle_number,
                    "rating": assigned_driver.rating,
                    "location": {
                        "lat": assigned_driver.lat,
                        "lng": assigned_driver.lng
                    }
                },
                "fare": ride_request.estimated_fare,
                "estimated_arrival": f"{random.randint(3, 8)} minutes",
                "status": "assigned",
                "message": "Driver assigned successfully! Driver aa raha hai like Mumbai local!"
            }
            
        except Exception as e:
            logger.error(f"Ride booking error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def _handle_ride_tracking(self, ride_id: str) -> dict:
        """Handle ride tracking requests"""
        try:
            # Get ride details from Redis
            ride_data = self.redis.hgetall(f"ride:{ride_id}")
            
            if not ride_data:
                raise HTTPException(status_code=404, detail="Ride not found")
            
            # Route to tracking service for real-time updates
            tracking_data = await self._route_to_service(
                "tracking_service", 
                f"/api/tracking/{ride_id}", 
                {}
            )
            
            # Simulate live tracking data
            return {
                "ride_id": ride_id,
                "status": ride_data.get(b"status", b"unknown").decode(),
                "driver_location": {
                    "lat": 19.0760 + random.uniform(-0.01, 0.01),
                    "lng": 72.8777 + random.uniform(-0.01, 0.01),
                    "heading": random.randint(0, 360)
                },
                "estimated_arrival": f"{random.randint(2, 15)} minutes",
                "distance_to_pickup": f"{random.uniform(0.5, 3.0):.1f} km",
                "fare": float(ride_data.get(b"fare", 0)),
                "message": "Tracking active - Driver location updating like Uber!"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ride tracking error: {str(e)}")
            raise HTTPException(status_code=500, detail="Tracking service error")
    
    async def _handle_ride_cancellation(self, ride_id: str) -> dict:
        """Handle ride cancellation"""
        try:
            ride_data = self.redis.hgetall(f"ride:{ride_id}")
            
            if not ride_data:
                raise HTTPException(status_code=404, detail="Ride not found")
            
            # Update ride status
            self.redis.hset(f"ride:{ride_id}", "status", "cancelled")
            
            # Free up the driver
            driver_id = ride_data.get(b"driver_id", b"").decode()
            if driver_id:
                self.redis.hset(f"driver:{driver_id}", "is_available", "true")
            
            # Route to booking service for cancellation processing
            await self._route_to_service(
                "booking_service", 
                f"/api/bookings/{ride_id}/cancel", 
                {}
            )
            
            return {
                "success": True,
                "ride_id": ride_id,
                "status": "cancelled",
                "cancellation_fee": 0,  # Could calculate based on timing
                "refund_amount": float(ride_data.get(b"fare", 0)),
                "message": "Ride cancelled successfully - No worries, Mumbai mein aur options hain!"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ride cancellation error: {str(e)}")
            raise HTTPException(status_code=500, detail="Cancellation service error")
    
    async def _handle_driver_discovery(self, lat: float, lng: float, ride_type: str) -> dict:
        """Handle nearby drivers discovery"""
        try:
            ride_request = RideRequest(
                user_id="temp",
                pickup_lat=lat,
                pickup_lng=lng,
                dropoff_lat=lat,
                dropoff_lng=lng,
                ride_type=RideType(ride_type),
                pickup_address="",
                dropoff_address=""
            )
            
            nearby_drivers = await self.matching_engine.find_nearby_drivers(ride_request, radius_km=10)
            
            drivers_data = []
            for driver in nearby_drivers:
                distance = GeoLocationService.calculate_distance(lat, lng, driver.lat, driver.lng)
                drivers_data.append({
                    "driver_id": driver.driver_id,
                    "location": {"lat": driver.lat, "lng": driver.lng},
                    "distance_km": round(distance, 2),
                    "rating": driver.rating,
                    "vehicle_number": driver.vehicle_number,
                    "ride_type": driver.ride_type.value,
                    "estimated_arrival": f"{max(1, int(distance * 3))} minutes"
                })
            
            return {
                "drivers": drivers_data,
                "count": len(drivers_data),
                "search_radius_km": 10,
                "zone": GeoLocationService.get_zone(lat, lng).value,
                "message": f"Found {len(drivers_data)} drivers - Like spotting yellow-black taxis in Mumbai!"
            }
            
        except Exception as e:
            logger.error(f"Driver discovery error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def _route_to_service(self, service_name: str, endpoint: str, data: dict) -> dict:
        """Route request to appropriate microservice"""
        try:
            service_url = self.service_endpoints.get(service_name)
            if not service_url:
                logger.warning(f"Service {service_name} not configured")
                return {"status": "service_unavailable"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service_url}{endpoint}",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Service {service_name} returned {response.status}")
                        return {"status": "error", "code": response.status}
                        
        except Exception as e:
            logger.error(f"Service routing error for {service_name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _is_surge_time(self) -> bool:
        """Check if it's surge pricing time"""
        current_hour = datetime.now().hour
        return current_hour in [8, 9, 10, 18, 19, 20]  # Rush hours
    
    def _populate_sample_data(self):
        """Populate Redis with sample drivers for testing"""
        sample_drivers = [
            # South Mumbai drivers
            {"driver_id": "driver_001", "lat": 18.9220, "lng": 72.8342, "ride_type": "mini", "zone": "south_mumbai"},
            {"driver_id": "driver_002", "lat": 18.9340, "lng": 72.8250, "ride_type": "prime", "zone": "south_mumbai"},
            {"driver_id": "driver_003", "lat": 18.9180, "lng": 72.8400, "ride_type": "auto", "zone": "south_mumbai"},
            
            # Central Mumbai drivers  
            {"driver_id": "driver_004", "lat": 19.0760, "lng": 72.8777, "ride_type": "mini", "zone": "central_mumbai"},
            {"driver_id": "driver_005", "lat": 19.0650, "lng": 72.8680, "ride_type": "suv", "zone": "central_mumbai"},
            {"driver_id": "driver_006", "lat": 19.0540, "lng": 72.8320, "ride_type": "bike", "zone": "central_mumbai"},
            
            # Western suburbs drivers
            {"driver_id": "driver_007", "lat": 19.2183, "lng": 72.8479, "ride_type": "mini", "zone": "western_suburbs"},
            {"driver_id": "driver_008", "lat": 19.2080, "lng": 72.8380, "ride_type": "prime", "zone": "western_suburbs"},
            
            # Eastern suburbs drivers
            {"driver_id": "driver_009", "lat": 19.2183, "lng": 72.9781, "ride_type": "auto", "zone": "eastern_suburbs"},
            {"driver_id": "driver_010", "lat": 19.1950, "lng": 72.9600, "ride_type": "mini", "zone": "eastern_suburbs"},
        ]
        
        for driver in sample_drivers:
            driver_data = {
                "driver_id": driver["driver_id"],
                "lat": str(driver["lat"]),
                "lng": str(driver["lng"]),
                "ride_type": driver["ride_type"],
                "is_available": "true",
                "current_zone": driver["zone"],
                "rating": str(random.uniform(3.8, 4.9)),
                "vehicle_number": f"MH01{random.randint(1000, 9999)}"
            }
            
            self.redis.hset(f"driver:{driver['driver_id']}", mapping=driver_data)
        
        logger.info(f"Populated {len(sample_drivers)} sample drivers")

def run_gateway():
    """Run the Ola-style gateway"""
    gateway = OlaRideGateway()
    
    logger.info("Starting Ola Ride Gateway - Mumbai traffic ready! 🚗")
    logger.info("Endpoints:")
    logger.info("  - Health: http://localhost:8080/health")
    logger.info("  - Estimate: POST http://localhost:8080/api/rides/estimate")
    logger.info("  - Book: POST http://localhost:8080/api/rides/book")
    logger.info("  - Track: GET http://localhost:8080/api/rides/{ride_id}")
    logger.info("  - Drivers: GET http://localhost:8080/api/drivers/nearby")
    
    uvicorn.run(
        gateway.app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

if __name__ == "__main__":
    run_gateway()