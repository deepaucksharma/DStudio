# Episode 091: WebSocket Protocols - Research Notes

## Core Concepts

### What are WebSockets?
- Full-duplex communication protocol
- Persistent connection between client and server
- Real-time bidirectional data transfer
- Upgrade from HTTP to WebSocket protocol
- Lower latency than polling or long-polling

### WebSocket vs Traditional HTTP
- HTTP: Request-Response, stateless, half-duplex
- WebSocket: Full-duplex, stateful, persistent
- HTTP overhead: Headers on every request
- WebSocket: Single handshake, minimal overhead

### Protocol Details
- Starts with HTTP handshake
- Upgrade header to switch protocols
- Uses frames for data transfer
- Supports text and binary data
- Built-in ping/pong for keep-alive

## Indian Company Case Studies

### Zerodha Kite - Stock Market Updates
- 3M+ active traders
- Real-time stock quotes
- 50,000+ concurrent WebSocket connections
- Sub-100ms latency for price updates
- Saves ₹2 crores/month vs polling

### Dream11 - Live Match Updates
- 140M+ users
- Live score streaming during IPL
- 10M concurrent connections during finals
- WebSocket for real-time points calculation
- 90% reduction in server load vs HTTP polling

### Ola - Driver Location Tracking
- 2.5M drivers
- Real-time location updates
- WebSocket for continuous GPS streaming
- 15-second update intervals
- Reduced battery consumption by 40%

### Swiggy - Order Tracking
- Live delivery tracking
- 500K+ concurrent orders
- WebSocket for rider location
- Customer notifications
- 60% reduction in API calls

### Groww - Stock Trading
- Real-time portfolio updates
- Market depth streaming
- Order status notifications
- Price alerts via WebSocket
- Handles 1M+ concurrent users

## Technical Architecture

### Connection Lifecycle
1. HTTP handshake
2. Protocol upgrade
3. Connection establishment
4. Data frames exchange
5. Keep-alive with ping/pong
6. Connection closure

### Scaling Challenges
- Connection limits per server
- Memory consumption per connection
- Load balancing sticky sessions
- Horizontal scaling complexity
- Connection recovery strategies

### Security Considerations
- WSS (WebSocket Secure) over TLS
- Origin validation
- Authentication tokens
- Rate limiting
- XSS and CSRF protection

## Implementation Frameworks

### Server-Side
- Node.js: Socket.io, ws
- Python: websockets, Django Channels
- Java: Spring WebSocket, Netty
- Go: Gorilla WebSocket
- .NET: SignalR

### Client-Side
- JavaScript: Native WebSocket API
- React: react-use-websocket
- Angular: RxJS WebSocketSubject
- Mobile: iOS (URLSessionWebSocketTask), Android (OkHttp)

## Production Metrics

### Performance Benchmarks
- Connection establishment: 50-200ms
- Message latency: 5-50ms
- Throughput: 10K-100K messages/sec per server
- Memory: 10-50KB per connection
- CPU: 1 core handles 10K connections

### Cost Analysis (Indian Context)
- AWS India pricing: ₹0.015 per million messages
- Server costs: ₹50K/month for 100K concurrent
- Bandwidth: ₹5-10 per GB
- Comparison: 70% cheaper than HTTP polling
- ROI: Break-even at 10K users

## Real Production Issues

### Common Problems
1. Connection drops in mobile networks
2. Proxy/firewall blocking
3. Memory leaks in long connections
4. Reconnection storms
5. Message ordering issues

### Solutions
1. Automatic reconnection with exponential backoff
2. Fallback to long-polling
3. Connection pooling and recycling
4. Jitter in reconnection timing
5. Message queuing and sequencing