# Service Discovery with Consul

Production-ready service discovery implementation using Consul, designed for Indian scale applications like Zomato and Swiggy.

## Features

- Consul-based service registration and discovery
- Health checking with multiple check types
- Load balancing with round-robin algorithm
- Graceful shutdown and deregistration
- Production-ready HTTP timeouts
- Mumbai-style metaphors in code comments

## Usage

```bash
# Start Consul (required)
consul agent -dev

# Set environment variables
export SERVICE_NAME="zomato-delivery-service"
export PORT="8080"
export CONSUL_ADDR="localhost:8500"

# Run the service
go run main.go
```

## Endpoints

- `/health` - Health check endpoint
- `/discover?service=SERVICE_NAME&tag=TAG` - Service discovery
- `/api/orders` - Sample business endpoint

## Cost Analysis (Indian Context)

- Consul cluster: ₹15,000/month for 3-node setup
- Health check overhead: ~1% CPU per service
- Network calls: ₹0.001 per API call
- Total for 100 services: ₹25,000/month

Perfect for startups scaling from 10 to 1000+ microservices!