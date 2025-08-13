#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swiggy Microservice Containerization Example
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे Swiggy जैसी food delivery company
अपनी microservices को containers में package करती है।

Real-world scenario: Swiggy का order processing service
"""

import os
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest
import logging
from loguru import logger

# Hindi comments के साथ production-ready code
# यह service Swiggy के order processing को simulate करती है

@dataclass
class SwiggyOrder:
    """Swiggy order data structure - Ghar ka khana style!"""
    order_id: str
    customer_id: str
    restaurant_id: str
    items: List[Dict[str, any]]
    total_amount: float
    delivery_address: str
    order_time: str
    status: str = "placed"  # placed, confirmed, preparing, picked_up, delivered
    
    def to_dict(self) -> Dict:
        """Convert order to dictionary for JSON serialization"""
        return asdict(self)

class SwiggyOrderService:
    """
    Swiggy Order Processing Microservice
    यह service handle करती है order lifecycle को
    """
    
    def __init__(self):
        # Metrics for monitoring - Prometheus style
        self.order_counter = Counter(
            'swiggy_orders_total', 
            'Total orders processed',
            ['restaurant_zone', 'order_status']
        )
        self.order_processing_time = Histogram(
            'swiggy_order_processing_seconds',
            'Time spent processing orders'
        )
        
        # In-memory store for demo (production में database होगा)
        self.orders: Dict[str, SwiggyOrder] = {}
        self.restaurants = {
            "rest_001": {"name": "Rajesh Uncle Ki Dukaan", "zone": "Andheri"},
            "rest_002": {"name": "Sharma Aunty Ka Dhaba", "zone": "Bandra"},
            "rest_003": {"name": "Singh Brother's Kitchen", "zone": "Malad"}
        }
        
        logger.info("Swiggy Order Service initialized - Ready to serve Mumbai!")
    
    async def create_order(self, order_data: Dict) -> SwiggyOrder:
        """
        नया order create करना - Swiggy style!
        """
        with self.order_processing_time.time():
            # Order ID generation - timestamp based
            order_id = f"SWG_{int(time.time() * 1000)}"
            
            # Validate restaurant exists
            if order_data["restaurant_id"] not in self.restaurants:
                raise ValueError(f"Restaurant {order_data['restaurant_id']} not found!")
            
            # Create order object
            order = SwiggyOrder(
                order_id=order_id,
                customer_id=order_data["customer_id"],
                restaurant_id=order_data["restaurant_id"],
                items=order_data["items"],
                total_amount=order_data["total_amount"],
                delivery_address=order_data["delivery_address"],
                order_time=datetime.now().isoformat(),
                status="placed"
            )
            
            # Store order
            self.orders[order_id] = order
            
            # Update metrics
            restaurant = self.restaurants[order_data["restaurant_id"]]
            self.order_counter.labels(
                restaurant_zone=restaurant["zone"],
                order_status="placed"
            ).inc()
            
            logger.info(f"Order {order_id} placed for restaurant {restaurant['name']}")
            return order
    
    async def update_order_status(self, order_id: str, new_status: str) -> SwiggyOrder:
        """
        Order status update करना - Real-time tracking के लिए
        """
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found!")
        
        order = self.orders[order_id]
        old_status = order.status
        order.status = new_status
        
        # Update metrics
        restaurant = self.restaurants[order.restaurant_id]
        self.order_counter.labels(
            restaurant_zone=restaurant["zone"],
            order_status=new_status
        ).inc()
        
        logger.info(f"Order {order_id} status: {old_status} -> {new_status}")
        return order
    
    async def get_order(self, order_id: str) -> Optional[SwiggyOrder]:
        """Order details fetch करना"""
        return self.orders.get(order_id)
    
    async def get_restaurant_orders(self, restaurant_id: str) -> List[SwiggyOrder]:
        """Specific restaurant के सारे orders"""
        return [
            order for order in self.orders.values() 
            if order.restaurant_id == restaurant_id
        ]

# FastAPI app setup
app = FastAPI(
    title="Swiggy Order Service",
    description="Container-ready microservice for food delivery orders",
    version="1.0.0"
)

# CORS middleware - Mumbai se Pune tak access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service instance
order_service = SwiggyOrderService()

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "swiggy-order-service",
        "timestamp": datetime.now().isoformat(),
        "total_orders": len(order_service.orders)
    }

@app.post("/api/v1/orders")
async def create_order(order_data: Dict, background_tasks: BackgroundTasks):
    """
    नया order create करना
    Example payload:
    {
        "customer_id": "cust_001",
        "restaurant_id": "rest_001",
        "items": [{"name": "Butter Chicken", "quantity": 2, "price": 350}],
        "total_amount": 700,
        "delivery_address": "Andheri East, Mumbai"
    }
    """
    try:
        order = await order_service.create_order(order_data)
        
        # Background task for order processing simulation
        background_tasks.add_task(simulate_order_lifecycle, order.order_id)
        
        return {
            "success": True,
            "order": order.to_dict(),
            "message": "Order placed successfully! Ghar pahunch jaayega."
        }
    except Exception as e:
        logger.error(f"Order creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    """Order details fetch करना"""
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found!")
    
    return {
        "success": True,
        "order": order.to_dict()
    }

@app.put("/api/v1/orders/{order_id}/status")
async def update_order_status(order_id: str, status_data: Dict):
    """Order status update करना"""
    try:
        order = await order_service.update_order_status(
            order_id, 
            status_data["status"]
        )
        return {
            "success": True,
            "order": order.to_dict(),
            "message": f"Order status updated to {status_data['status']}"
        }
    except Exception as e:
        logger.error(f"Status update failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/restaurants/{restaurant_id}/orders")
async def get_restaurant_orders(restaurant_id: str):
    """Restaurant के सारे orders"""
    orders = await order_service.get_restaurant_orders(restaurant_id)
    return {
        "success": True,
        "restaurant_id": restaurant_id,
        "orders": [order.to_dict() for order in orders],
        "total_orders": len(orders)
    }

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

async def simulate_order_lifecycle(order_id: str):
    """
    Order lifecycle simulation - Real Swiggy experience!
    Background task जो order को different stages में move करता है
    """
    statuses = ["confirmed", "preparing", "picked_up", "out_for_delivery", "delivered"]
    
    for status in statuses:
        # Random delay between status updates (30 seconds to 5 minutes)
        await asyncio.sleep(30)  # In production, this would be actual events
        
        try:
            await order_service.update_order_status(order_id, status)
            logger.info(f"Order {order_id} moved to {status}")
        except Exception as e:
            logger.error(f"Failed to update order {order_id}: {str(e)}")
            break

if __name__ == "__main__":
    # Container में run करने के लिए configuration
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Swiggy Order Service on {host}:{port}")
    logger.info("Mumbai ke orders ki duniya में welcome!")
    
    uvicorn.run(
        "01_swiggy_microservice_containerization:app",
        host=host,
        port=port,
        reload=False,  # Production में reload=False
        workers=1,  # Container में single worker se start
        log_level="info"
    )

# Dockerfile के लिए commands:
"""
# Build command:
docker build -t swiggy-order-service:latest .

# Run command:
docker run -p 8000:8000 \
  -e PORT=8000 \
  -e HOST=0.0.0.0 \
  swiggy-order-service:latest

# Health check:
curl http://localhost:8000/health

# Create order:
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_mumbai_001",
    "restaurant_id": "rest_001",
    "items": [{"name": "Vada Pav", "quantity": 3, "price": 45}],
    "total_amount": 135,
    "delivery_address": "Andheri Station, Platform 1"
  }'
"""