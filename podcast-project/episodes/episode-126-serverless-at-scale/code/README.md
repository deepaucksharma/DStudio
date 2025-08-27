# Episode 126 Code Examples: Serverless at Scale

## Overview
This directory contains 15+ production-ready serverless code examples demonstrating various platforms and use cases with Indian context.

## Code Examples Structure

### 1. AWS Lambda Examples
- `irctc_booking_api.py` - IRCTC Tatkal booking system
- `paytm_qr_generator.py` - Paytm QR code generation
- `fraud_detection.py` - ML-based fraud detection
- `notification_service.py` - SQS-based notification system

### 2. Azure Functions Examples  
- `flipkart_order_processor.cs` - Flipkart order processing workflow
- `durable_functions_example.cs` - Long-running processes

### 3. Google Cloud Functions Examples
- `zomato_delivery_tracker.py` - Real-time delivery tracking
- `ai_image_processor.py` - Image processing with AI APIs

### 4. CloudFlare Workers Examples
- `edge_cache_worker.js` - Global edge caching
- `paytm_qr_edge.js` - QR generation at edge
- `geo_routing_worker.js` - Geographic request routing

### 5. Deno Deploy Examples
- `upi_payment_processor.ts` - TypeScript UPI processor
- `websocket_chat.ts` - Real-time chat with WebSockets

### 6. Infrastructure and Monitoring
- `cloudwatch_monitoring.py` - Custom metrics and alarms
- `cost_optimization.py` - Cost analysis and optimization
- `multi_cloud_router.js` - Multi-cloud routing strategy

## Running the Examples

### Prerequisites
```bash
# Install required dependencies
pip install -r requirements.txt
npm install
```

### AWS Lambda Setup
```bash
# Configure AWS CLI
aws configure

# Deploy using SAM
sam build
sam deploy --guided
```

### Testing
```bash
# Run unit tests
python -m pytest tests/
npm test
```

## Performance Benchmarks
- Cold start times: <100ms for Node.js/Python
- Throughput: 1000+ requests/second per function
- Cost efficiency: 60-80% savings vs traditional infrastructure

## Security Best Practices
- IAM least privilege policies
- Input validation and sanitization
- Secrets management with AWS Secrets Manager
- VPC configuration for sensitive operations

## Indian Context Integration
- Regional optimization for Indian networks
- Cost calculations in INR
- Local regulations compliance (RBI guidelines)
- Cultural metaphors and examples throughout