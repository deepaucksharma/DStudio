---
type: pattern
category: architecture
title: API Design Mastery
description: Comprehensive guide to designing scalable APIs in distributed systems
tags: [api-design, rest, graphql, grpc, scaling, production]
estimated_time: 420
difficulty: advanced
prerequisites: [distributed-systems-basics, http-protocols, service-architecture]
---

# API Design Mastery: Building APIs that Scale to Millions

## Overview

Modern distributed systems are built on APIs. This comprehensive guide explores production-proven API design patterns used by companies serving billions of requests daily. Learn from Stripe, Twilio, GitHub, Slack, and Google to build APIs that scale.

### Learning Objectives (420 minutes)
- Master RESTful API design principles and best practices
- Understand GraphQL vs REST trade-offs and implementation strategies
- Design APIs using gRPC and Protocol Buffers for high-performance scenarios
- Implement robust versioning, authentication, and error handling
- Apply advanced patterns like HATEOAS, event-driven APIs, and batch operations
- Build production-ready API documentation and testing strategies

## Table of Contents

1. [Foundation: API Design Principles](#foundation-api-design-principles) (45 min)
2. [RESTful API Design Mastery](#restful-api-design-mastery) (60 min)
3. [GraphQL vs REST: When and How](#graphql-vs-rest-when-and-how) (45 min)
4. [gRPC and Protocol Buffers](#grpc-and-protocol-buffers) (40 min)
5. [API Versioning and Evolution](#api-versioning-and-evolution) (35 min)
6. [Authentication and Authorization](#authentication-and-authorization) (40 min)
7. [Error Handling and Status Codes](#error-handling-and-status-codes) (25 min)
8. [Advanced API Patterns](#advanced-api-patterns) (50 min)
9. [API Gateways and BFF Pattern](#api-gateways-and-bff-pattern) (30 min)
10. [Documentation and Testing](#documentation-and-testing) (35 min)
11. [Monitoring and Analytics](#monitoring-and-analytics) (25 min)
12. [Hands-on Exercises](#hands-on-exercises) (10 min)

---

## Foundation: API Design Principles

### Production Examples: API Design Excellence

**Stripe's API Design Philosophy:**
```http
# Predictable resource-based URLs
GET /v1/customers/cus_4fdAW5ftNQDxEs
GET /v1/customers/cus_4fdAW5ftNQDxEs/subscriptions

# Consistent error format
{
  "error": {
    "type": "card_error",
    "code": "card_declined",
    "message": "Your card was declined.",
    "param": "number"
  }
}
```

**Twilio's Consistency Approach:**
- All resources follow the same URL pattern: `/2010-04-01/Accounts/{AccountSid}/Resource.json`
- Consistent authentication across all endpoints
- Standard pagination pattern across all list endpoints

### Core Design Principles

#### 1. Consistency Over Cleverness

```yaml
# Good: Consistent resource naming
/api/v1/users/{id}
/api/v1/orders/{id}
/api/v1/products/{id}

# Bad: Inconsistent patterns
/api/v1/user/{id}
/api/v1/order-details/{id}
/api/v1/product_info/{id}
```

#### 2. Discoverability and Self-Documentation

```json
{
  "data": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "links": {
    "self": "/api/v1/users/user_123",
    "orders": "/api/v1/users/user_123/orders",
    "profile": "/api/v1/users/user_123/profile"
  }
}
```

#### 3. Graceful Degradation

```json
{
  "data": {
    "essential_field": "always_present",
    "optional_field": "may_be_null"
  },
  "meta": {
    "version": "2.1",
    "deprecated_fields": ["legacy_field"],
    "warnings": ["Field 'legacy_field' will be removed in v3.0"]
  }
}
```

### Exercise 1: API Design Audit (15 minutes)

Evaluate this API design and identify improvements:

```http
GET /getUserData?userId=123
POST /createOrder
{
  "user": 123,
  "items": [{"product": "abc", "qty": 2}]
}

Response:
{
  "success": true,
  "data": {...},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Improvements needed:**
- Non-RESTful URL structure
- Inconsistent naming conventions
- Missing error handling patterns
- No resource relationships

---

## RESTful API Design Mastery

### GitHub's REST API: A Model Implementation

GitHub's API v3 demonstrates mature REST design:

```http
# Resource-based URLs
GET /repos/octocat/Hello-World
GET /repos/octocat/Hello-World/issues
POST /repos/octocat/Hello-World/issues

# Clear HTTP semantics
GET    /issues           # List issues
POST   /issues           # Create issue
GET    /issues/{id}      # Get specific issue
PATCH  /issues/{id}      # Update issue
DELETE /issues/{id}      # Delete issue
```

### REST Design Patterns

#### 1. Resource Modeling

```http
# Primary resources
GET /api/v1/customers
GET /api/v1/orders
GET /api/v1/products

# Sub-resources (relationships)
GET /api/v1/customers/{id}/orders
GET /api/v1/orders/{id}/items
GET /api/v1/customers/{id}/addresses

# Nested resources (careful with depth)
GET /api/v1/customers/{id}/orders/{order_id}/items/{item_id}
```

#### 2. HTTP Method Usage

```http
# Safe methods (no side effects)
GET    /resources        # Retrieve collection
HEAD   /resources/{id}   # Check existence
OPTIONS /resources       # Discover capabilities

# Idempotent methods
PUT    /resources/{id}   # Create or replace
DELETE /resources/{id}   # Remove resource

# Non-idempotent methods
POST   /resources        # Create (ID assigned by server)
PATCH  /resources/{id}   # Partial update
```

#### 3. Status Code Strategy

```http
# Success responses
200 OK              # GET, PATCH, DELETE success
201 Created         # POST success
202 Accepted        # Async operation started
204 No Content      # DELETE success, no body

# Client errors
400 Bad Request     # Invalid syntax
401 Unauthorized    # Authentication required
403 Forbidden       # Insufficient permissions
404 Not Found       # Resource doesn't exist
409 Conflict        # Resource conflict
422 Unprocessable Entity # Validation failed

# Server errors
500 Internal Server Error
503 Service Unavailable
504 Gateway Timeout
```

### Pagination Patterns

#### Stripe's Cursor-Based Pagination

```http
GET /v1/customers?limit=100

Response:
{
  "data": [...],
  "has_more": true,
  "url": "/v1/customers",
  "object": "list"
}

# Next page
GET /v1/customers?limit=100&starting_after=cus_4fdAW5ftNQDxEs
```

#### GitHub's Link Header Pagination

```http
GET /repos/octocat/Hello-World/issues?per_page=100&page=2

Response Headers:
Link: <https://api.github.com/repos/octocat/Hello-World/issues?per_page=100&page=1>; rel="first",
      <https://api.github.com/repos/octocat/Hello-World/issues?per_page=100&page=3>; rel="next",
      <https://api.github.com/repos/octocat/Hello-World/issues?per_page=100&page=50>; rel="last"
```

#### Implementing Efficient Pagination

```python
# Cursor-based pagination implementation
class CursorPaginator:
    def __init__(self, query, order_field='created_at'):
        self.query = query
        self.order_field = order_field
    
    def paginate(self, limit=100, cursor=None):
        query = self.query.order_by(self.order_field)
        
        if cursor:
            query = query.filter(**{f"{self.order_field}__gt": cursor})
        
        items = list(query[:limit + 1])  # +1 to check if more exist
        
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]
        
        next_cursor = items[-1][self.order_field] if items and has_more else None
        
        return {
            'data': items,
            'has_more': has_more,
            'next_cursor': next_cursor
        }
```

### Rate Limiting Implementation

#### Token Bucket Algorithm

```python
import time
from collections import defaultdict

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = defaultdict(lambda: {'tokens': capacity, 'last_refill': time.time()})
    
    def allow_request(self, key):
        bucket = self.buckets[key]
        now = time.time()
        
        # Refill tokens
        elapsed = now - bucket['last_refill']
        tokens_to_add = elapsed * self.refill_rate
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now
        
        # Check if request allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        return False

# Usage in Flask
from flask import request, jsonify

def rate_limit_decorator(limit=1000, window=3600):
    bucket = TokenBucket(limit, limit/window)
    
    def decorator(f):
        def wrapper(*args, **kwargs):
            key = request.remote_addr  # or user ID
            if not bucket.allow_request(key):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            return f(*args, **kwargs)
        return wrapper
    return decorator
```

### Exercise 2: REST API Design (20 minutes)

Design a REST API for a library management system with the following requirements:
- Books, Authors, Members, Loans
- Search functionality
- Reservation system
- Late fee tracking

**Solution Framework:**
```http
# Core resources
GET /api/v1/books
GET /api/v1/authors
GET /api/v1/members
GET /api/v1/loans

# Relationships
GET /api/v1/authors/{id}/books
GET /api/v1/members/{id}/loans
GET /api/v1/books/{id}/reservations

# Actions (non-CRUD operations)
POST /api/v1/books/{id}/reserve
POST /api/v1/loans/{id}/return
POST /api/v1/loans/{id}/renew

# Search
GET /api/v1/books?q=title:python&author=doe&available=true
```

---

## GraphQL vs REST: When and How

### GitHub's API Evolution: v3 (REST) to v4 (GraphQL)

GitHub's journey from REST to GraphQL demonstrates the trade-offs:

**REST v3 (Multiple requests needed):**
```http
GET /user
GET /user/repos
GET /repos/owner/repo/issues
GET /repos/owner/repo/pulls
```

**GraphQL v4 (Single request):**
```graphql
query {
  viewer {
    login
    repositories(first: 10) {
      nodes {
        name
        issues(first: 5) {
          nodes {
            title
            state
          }
        }
        pullRequests(first: 5) {
          nodes {
            title
            state
          }
        }
      }
    }
  }
}
```

### GraphQL Schema Design

#### Schema-First Approach

```graphql
# User domain
type User {
  id: ID!
  email: String!
  profile: UserProfile
  orders(first: Int, after: String): OrderConnection!
  createdAt: DateTime!
}

type UserProfile {
  firstName: String!
  lastName: String!
  avatar: String
  preferences: UserPreferences
}

# Order domain
type Order {
  id: ID!
  user: User!
  items: [OrderItem!]!
  status: OrderStatus!
  total: Money!
  createdAt: DateTime!
}

enum OrderStatus {
  PENDING
  CONFIRMED
  SHIPPED
  DELIVERED
  CANCELLED
}

# Mutations
type Mutation {
  createOrder(input: CreateOrderInput!): CreateOrderPayload!
  updateUserProfile(input: UpdateUserProfileInput!): UpdateUserProfilePayload!
}

input CreateOrderInput {
  items: [OrderItemInput!]!
  shippingAddress: AddressInput!
}

type CreateOrderPayload {
  order: Order
  errors: [UserError!]!
}
```

#### Resolver Implementation

```javascript
const resolvers = {
  Query: {
    user: async (_, { id }, { dataSources }) => {
      return dataSources.userAPI.getUser(id);
    },
    orders: async (_, { first, after }, { dataSources, user }) => {
      return dataSources.orderAPI.getOrders({
        userId: user.id,
        first,
        after
      });
    }
  },
  
  User: {
    orders: async (user, { first, after }, { dataSources }) => {
      return dataSources.orderAPI.getOrdersByUser({
        userId: user.id,
        first,
        after
      });
    }
  },
  
  Mutation: {
    createOrder: async (_, { input }, { dataSources, user }) => {
      try {
        const order = await dataSources.orderAPI.createOrder({
          ...input,
          userId: user.id
        });
        return { order, errors: [] };
      } catch (error) {
        return {
          order: null,
          errors: [{ message: error.message, path: ['createOrder'] }]
        };
      }
    }
  }
};
```

### N+1 Query Problem Solutions

#### DataLoader Pattern

```javascript
const DataLoader = require('dataloader');

class UserDataSource {
  constructor() {
    this.userLoader = new DataLoader(this.batchGetUsers.bind(this));
    this.orderLoader = new DataLoader(this.batchGetOrdersByUser.bind(this));
  }
  
  async batchGetUsers(userIds) {
    const users = await User.findByIds(userIds);
    return userIds.map(id => users.find(user => user.id === id));
  }
  
  async batchGetOrdersByUser(userIds) {
    const orders = await Order.findByUserIds(userIds);
    return userIds.map(userId => 
      orders.filter(order => order.userId === userId)
    );
  }
  
  getUser(id) {
    return this.userLoader.load(id);
  }
  
  getOrdersByUser(userId) {
    return this.orderLoader.load(userId);
  }
}
```

### When to Choose GraphQL vs REST

| Factor | GraphQL | REST |
|--------|---------|------|
| Client flexibility | High - query exact needs | Low - fixed endpoints |
| Caching | Complex - query-based | Simple - URL-based |
| Learning curve | Steep | Gentle |
| Tooling maturity | Growing | Mature |
| File uploads | Requires extensions | Native support |
| Real-time | Subscriptions | WebSockets/SSE |

### Federation Pattern for Microservices

```javascript
// User service schema
extend type Query {
  user(id: ID!): User
}

type User @key(fields: "id") {
  id: ID!
  email: String!
  profile: UserProfile
}

// Order service schema
extend type User @key(fields: "id") {
  id: ID! @external
  orders: [Order!]!
}

type Order {
  id: ID!
  user: User!
  items: [OrderItem!]!
}

// Gateway composition
const gateway = new ApolloGateway({
  serviceList: [
    { name: 'users', url: 'http://user-service/graphql' },
    { name: 'orders', url: 'http://order-service/graphql' }
  ]
});
```

### Exercise 3: GraphQL vs REST Decision (10 minutes)

For each scenario, choose GraphQL or REST and justify:

1. **Mobile app with varying data needs**
   - Answer: GraphQL - reduces over-fetching on mobile networks

2. **Public API for third-party integrations**
   - Answer: REST - better tooling and familiar patterns

3. **Internal microservices communication**
   - Answer: gRPC - better performance and type safety

4. **Real-time collaborative application**
   - Answer: GraphQL with subscriptions - native real-time support

---

## gRPC and Protocol Buffers

### Google's gRPC: High-Performance RPC

gRPC excels in service-to-service communication with:
- Binary serialization (faster than JSON)
- HTTP/2 multiplexing
- Streaming support
- Language-agnostic interface definitions

### Protocol Buffer Definitions

```protobuf
// user.proto
syntax = "proto3";

package user.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc UpdateUser(UpdateUserRequest) returns (User);
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);
  rpc StreamUsers(google.protobuf.Empty) returns (stream User);
}

message User {
  string id = 1;
  string email = 2;
  UserProfile profile = 3;
  google.protobuf.Timestamp created_at = 4;
  google.protobuf.Timestamp updated_at = 5;
}

message UserProfile {
  string first_name = 1;
  string last_name = 2;
  string avatar_url = 3;
  map<string, string> preferences = 4;
}

message GetUserRequest {
  string id = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_count = 3;
}

message CreateUserRequest {
  string email = 1;
  UserProfile profile = 2;
}

message UpdateUserRequest {
  string id = 1;
  User user = 2;
  google.protobuf.FieldMask update_mask = 3;
}

message DeleteUserRequest {
  string id = 1;
}
```

### gRPC Server Implementation

```go
package main

import (
    "context"
    "log"
    "net"
    
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    
    pb "your-project/proto/user/v1"
)

type userServer struct {
    pb.UnimplementedUserServiceServer
    userRepo UserRepository
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    if req.Id == "" {
        return nil, status.Error(codes.InvalidArgument, "user ID is required")
    }
    
    user, err := s.userRepo.GetByID(ctx, req.Id)
    if err != nil {
        if err == ErrUserNotFound {
            return nil, status.Error(codes.NotFound, "user not found")
        }
        return nil, status.Error(codes.Internal, "failed to get user")
    }
    
    return &pb.User{
        Id:    user.ID,
        Email: user.Email,
        Profile: &pb.UserProfile{
            FirstName: user.Profile.FirstName,
            LastName:  user.Profile.LastName,
            AvatarUrl: user.Profile.AvatarURL,
        },
        CreatedAt: timestamppb.New(user.CreatedAt),
        UpdatedAt: timestamppb.New(user.UpdatedAt),
    }, nil
}

func (s *userServer) StreamUsers(req *emptypb.Empty, stream pb.UserService_StreamUsersServer) error {
    users, err := s.userRepo.GetAll(stream.Context())
    if err != nil {
        return status.Error(codes.Internal, "failed to get users")
    }
    
    for _, user := range users {
        pbUser := &pb.User{
            Id:    user.ID,
            Email: user.Email,
            // ... other fields
        }
        
        if err := stream.Send(pbUser); err != nil {
            return status.Error(codes.Internal, "failed to send user")
        }
    }
    
    return nil
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }
    
    s := grpc.NewServer(
        grpc.UnaryInterceptor(loggingInterceptor),
        grpc.StreamInterceptor(streamLoggingInterceptor),
    )
    
    userRepo := NewUserRepository()
    pb.RegisterUserServiceServer(s, &userServer{userRepo: userRepo})
    
    log.Println("gRPC server listening on :50051")
    if err := s.Serve(lis); err != nil {
        log.Fatalf("failed to serve: %v", err)
    }
}
```

### gRPC Client Implementation

```python
import grpc
import user_pb2
import user_pb2_grpc

class UserClient:
    def __init__(self, address="localhost:50051"):
        self.channel = grpc.insecure_channel(address)
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)
    
    def get_user(self, user_id):
        request = user_pb2.GetUserRequest(id=user_id)
        try:
            response = self.stub.GetUser(request)
            return response
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise
    
    def create_user(self, email, first_name, last_name):
        profile = user_pb2.UserProfile(
            first_name=first_name,
            last_name=last_name
        )
        request = user_pb2.CreateUserRequest(
            email=email,
            profile=profile
        )
        return self.stub.CreateUser(request)
    
    def stream_users(self):
        request = google_dot_protobuf_dot_empty__pb2.Empty()
        for user in self.stub.StreamUsers(request):
            yield user

# Usage
client = UserClient()
user = client.get_user("user_123")
if user:
    print(f"User: {user.email}")

# Streaming
for user in client.stream_users():
    print(f"Streaming user: {user.email}")
```

### gRPC Best Practices

#### 1. Error Handling

```go
import (
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

// Convert domain errors to gRPC status
func toGRPCError(err error) error {
    switch err {
    case ErrUserNotFound:
        return status.Error(codes.NotFound, "user not found")
    case ErrInvalidEmail:
        return status.Error(codes.InvalidArgument, "invalid email format")
    case ErrUserAlreadyExists:
        return status.Error(codes.AlreadyExists, "user already exists")
    default:
        return status.Error(codes.Internal, "internal server error")
    }
}
```

#### 2. Interceptors for Cross-Cutting Concerns

```go
func loggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    start := time.Now()
    
    log.Printf("gRPC call: %s", info.FullMethod)
    resp, err := handler(ctx, req)
    
    log.Printf("gRPC call: %s completed in %v", info.FullMethod, time.Since(start))
    return resp, err
}

func authInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    // Skip auth for public methods
    if isPublicMethod(info.FullMethod) {
        return handler(ctx, req)
    }
    
    token, err := extractToken(ctx)
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "missing or invalid token")
    }
    
    user, err := validateToken(token)
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }
    
    ctx = context.WithValue(ctx, "user", user)
    return handler(ctx, req)
}
```

### Exercise 4: gRPC Service Design (15 minutes)

Design a gRPC service for order management:
- Create, update, cancel orders
- List orders with pagination
- Stream order status updates
- Handle order validation errors

---

## API Versioning and Evolution

### Slack's API Evolution Strategy

Slack demonstrates careful API evolution:

```http
# v1 - Simple webhook format
POST /api/v1/chat.postMessage
{
  "channel": "#general",
  "text": "Hello World"
}

# v2 - Rich formatting support
POST /api/v2/chat.postMessage  
{
  "channel": "#general",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "Hello *World*"
      }
    }
  ]
}
```

### Versioning Strategies

#### 1. URL Path Versioning

```http
# Pros: Clear, cacheable
# Cons: URL proliferation
GET /api/v1/users
GET /api/v2/users
GET /api/v3/users
```

#### 2. Header Versioning

```http
# Pros: Clean URLs
# Cons: Less visible, caching complexity
GET /api/users
Accept: application/vnd.company.api+json;version=2
API-Version: 2
```

#### 3. Query Parameter Versioning

```http
# Pros: Simple, optional
# Cons: Can be ignored, URL cluttering
GET /api/users?version=2
```

### Backward Compatibility Patterns

#### Additive Changes (Safe)

```json
// Version 1
{
  "id": "user_123",
  "name": "John Doe",
  "email": "john@example.com"
}

// Version 2 (backward compatible)
{
  "id": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00Z",  // New field
  "preferences": {                        // New nested object
    "theme": "dark",
    "notifications": true
  }
}
```

#### Breaking Changes (Require New Version)

```json
// Version 1
{
  "id": "user_123",
  "name": "John Doe"  // Single name field
}

// Version 2 (breaking change)
{
  "id": "user_123",
  "first_name": "John",    // Split name field
  "last_name": "Doe"
}
```

### Version Migration Strategies

#### Adapter Pattern for Version Translation

```python
class APIVersionAdapter:
    def __init__(self):
        self.adapters = {
            'v1': self.adapt_to_v1,
            'v2': self.adapt_to_v2,
            'v3': self.adapt_to_v3
        }
    
    def adapt_response(self, data, version):
        adapter = self.adapters.get(version, self.adapt_to_latest)
        return adapter(data)
    
    def adapt_to_v1(self, data):
        # Convert to v1 format
        return {
            'id': data['id'],
            'name': f"{data['first_name']} {data['last_name']}",
            'email': data['email']
        }
    
    def adapt_to_v2(self, data):
        # Convert to v2 format
        return {
            'id': data['id'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'created_at': data['created_at']
        }
    
    def adapt_to_v3(self, data):
        # Latest format (no conversion needed)
        return data

# Usage in Flask
from flask import request, jsonify

@app.route('/api/users/<user_id>')
def get_user(user_id):
    version = request.headers.get('API-Version', 'v3')
    user_data = get_user_data(user_id)
    
    adapter = APIVersionAdapter()
    response_data = adapter.adapt_response(user_data, version)
    
    return jsonify(response_data)
```

### Deprecation Strategy

#### Gradual Deprecation Process

```python
import warnings
from datetime import datetime, timedelta

class DeprecationManager:
    def __init__(self):
        self.deprecation_schedule = {
            'v1': {
                'deprecated_date': '2024-01-01',
                'sunset_date': '2024-06-01',
                'replacement': 'v3'
            }
        }
    
    def check_deprecation(self, version):
        schedule = self.deprecation_schedule.get(version)
        if not schedule:
            return None
            
        deprecated = datetime.fromisoformat(schedule['deprecated_date'])
        sunset = datetime.fromisoformat(schedule['sunset_date'])
        now = datetime.now()
        
        if now > sunset:
            return {
                'status': 'sunset',
                'message': f'Version {version} is no longer supported'
            }
        elif now > deprecated:
            days_remaining = (sunset - now).days
            return {
                'status': 'deprecated',
                'message': f'Version {version} deprecated. {days_remaining} days until sunset',
                'replacement': schedule['replacement']
            }
        
        return None

# Usage in middleware
def deprecation_middleware():
    def middleware(request, response):
        version = request.headers.get('API-Version')
        deprecation = DeprecationManager().check_deprecation(version)
        
        if deprecation:
            if deprecation['status'] == 'sunset':
                return jsonify({'error': deprecation['message']}), 410
            else:
                response.headers['Deprecation'] = deprecation['message']
                response.headers['Sunset'] = 'Sun, 01 Jun 2024 00:00:00 GMT'
        
        return response
    return middleware
```

### Exercise 5: Version Migration Plan (10 minutes)

Create a migration plan for this breaking change:

**Current API (v2):**
```json
{
  "user_id": "123",
  "full_name": "John Doe",
  "contact": "john@example.com"
}
```

**Target API (v3):**
```json
{
  "id": "123",
  "name": {
    "first": "John",
    "last": "Doe"
  },
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

---

## Authentication and Authorization

### Production Auth Patterns

#### OAuth 2.0 with PKCE (Stripe Connect)

```javascript
// Authorization Code Flow with PKCE
class OAuth2Client {
    generateCodeChallenge() {
        const codeVerifier = this.generateCodeVerifier();
        const codeChallenge = base64URLEncode(sha256(codeVerifier));
        return { codeVerifier, codeChallenge };
    }
    
    async initiateAuth(clientId, redirectUri, scopes) {
        const { codeVerifier, codeChallenge } = this.generateCodeChallenge();
        
        // Store code verifier securely
        sessionStorage.setItem('code_verifier', codeVerifier);
        
        const authUrl = new URL('https://api.stripe.com/oauth/authorize');
        authUrl.searchParams.set('response_type', 'code');
        authUrl.searchParams.set('client_id', clientId);
        authUrl.searchParams.set('redirect_uri', redirectUri);
        authUrl.searchParams.set('scope', scopes.join(' '));
        authUrl.searchParams.set('code_challenge', codeChallenge);
        authUrl.searchParams.set('code_challenge_method', 'S256');
        
        window.location.href = authUrl.toString();
    }
    
    async exchangeCodeForToken(code, clientId, redirectUri) {
        const codeVerifier = sessionStorage.getItem('code_verifier');
        
        const response = await fetch('https://api.stripe.com/oauth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                code: code,
                client_id: clientId,
                redirect_uri: redirectUri,
                code_verifier: codeVerifier
            })
        });
        
        return response.json();
    }
}
```

#### JWT Implementation with Proper Security

```python
import jwt
import bcrypt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization

class JWTManager:
    def __init__(self, private_key_path, public_key_path, algorithm='RS256'):
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None
            )
        
        with open(public_key_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(f.read())
        
        self.algorithm = algorithm
    
    def create_tokens(self, user_id, permissions=None):
        now = datetime.utcnow()
        
        # Access token (short-lived)
        access_payload = {
            'sub': user_id,
            'iat': now,
            'exp': now + timedelta(minutes=15),
            'type': 'access',
            'permissions': permissions or []
        }
        
        access_token = jwt.encode(
            access_payload, 
            self.private_key, 
            algorithm=self.algorithm
        )
        
        # Refresh token (long-lived)
        refresh_payload = {
            'sub': user_id,
            'iat': now,
            'exp': now + timedelta(days=7),
            'type': 'refresh'
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            self.private_key,
            algorithm=self.algorithm
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 900,  # 15 minutes
            'token_type': 'Bearer'
        }
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError('Token expired')
        except jwt.InvalidTokenError:
            raise AuthError('Invalid token')
    
    def refresh_access_token(self, refresh_token):
        payload = self.verify_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise AuthError('Invalid token type')
        
        # Get fresh user permissions
        user_permissions = get_user_permissions(payload['sub'])
        
        return self.create_tokens(payload['sub'], user_permissions)
```

#### API Key Management

```python
import secrets
import hashlib
from datetime import datetime

class APIKeyManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.key_prefix = "api_key:"
        
    def generate_key(self, user_id, name=None, permissions=None, expires_days=None):
        # Generate cryptographically secure key
        key = f"ak_{secrets.token_urlsafe(32)}"
        
        # Hash the key for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        key_data = {
            'user_id': user_id,
            'name': name,
            'permissions': json.dumps(permissions or []),
            'created_at': datetime.utcnow().isoformat(),
            'last_used': None,
            'usage_count': 0
        }
        
        # Store with expiration if specified
        key_name = f"{self.key_prefix}{key_hash}"
        if expires_days:
            self.redis.setex(
                key_name,
                expires_days * 24 * 3600,
                json.dumps(key_data)
            )
        else:
            self.redis.set(key_name, json.dumps(key_data))
        
        return key  # Return the actual key (only shown once)
    
    def validate_key(self, key):
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        key_name = f"{self.key_prefix}{key_hash}"
        
        key_data_json = self.redis.get(key_name)
        if not key_data_json:
            return None
        
        key_data = json.loads(key_data_json)
        
        # Update usage statistics
        key_data['last_used'] = datetime.utcnow().isoformat()
        key_data['usage_count'] += 1
        
        self.redis.set(key_name, json.dumps(key_data))
        
        return {
            'user_id': key_data['user_id'],
            'permissions': json.loads(key_data['permissions'])
        }

# Usage in Flask
from functools import wraps

def require_api_key(permissions=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'API key required'}), 401
            
            api_key = auth_header.split(' ')[1]
            key_data = api_key_manager.validate_key(api_key)
            
            if not key_data:
                return jsonify({'error': 'Invalid API key'}), 401
            
            if permissions:
                user_permissions = key_data['permissions']
                if not all(p in user_permissions for p in permissions):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            request.user_id = key_data['user_id']
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

@app.route('/api/v1/users')
@require_api_key(permissions=['users:read'])
def list_users():
    return jsonify({'users': get_users()})
```

### Fine-Grained Authorization

#### Role-Based Access Control (RBAC)

```python
class RBACManager:
    def __init__(self):
        self.roles = {
            'admin': ['users:*', 'orders:*', 'products:*'],
            'user': ['users:read:own', 'orders:read:own', 'orders:create'],
            'support': ['users:read', 'orders:read', 'orders:update']
        }
        
        self.permissions = {}
        for role, perms in self.roles.items():
            for perm in perms:
                if perm not in self.permissions:
                    self.permissions[perm] = []
                self.permissions[perm].append(role)
    
    def check_permission(self, user_roles, required_permission, resource_owner=None):
        # Handle wildcard permissions
        for role in user_roles:
            role_permissions = self.roles.get(role, [])
            
            for perm in role_permissions:
                if self._match_permission(perm, required_permission, resource_owner):
                    return True
        
        return False
    
    def _match_permission(self, granted, required, resource_owner=None):
        # Handle wildcards
        if granted.endswith(':*'):
            prefix = granted[:-2]
            return required.startswith(prefix)
        
        # Handle own resource access
        if granted.endswith(':own') and resource_owner:
            base_perm = granted[:-4]
            return required == base_perm and resource_owner == request.user_id
        
        return granted == required

# Usage
rbac = RBACManager()

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_roles = get_user_roles(request.user_id)
            resource_owner = kwargs.get('user_id')  # For :own permissions
            
            if not rbac.check_permission(user_roles, permission, resource_owner):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/v1/users/<user_id>')
@require_api_key()
@require_permission('users:read')
def get_user(user_id):
    return jsonify(get_user_data(user_id))
```

### Exercise 6: Auth Strategy Design (10 minutes)

Design an authentication strategy for a multi-tenant SaaS API with:
- Tenant isolation
- User roles within tenants
- API key and OAuth support
- Fine-grained permissions

---

## Error Handling and Status Codes

### Twilio's Error Response Pattern

Twilio provides comprehensive error information:

```json
{
  "code": 20003,
  "message": "Authentication Error - No credentials provided",
  "more_info": "https://www.twilio.com/docs/errors/20003",
  "status": 401,
  "detail": "Twilio could not find a Account SID to authenticate this request."
}
```

### Comprehensive Error Response Design

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List

class ErrorCode(Enum):
    # Authentication errors (1000-1999)
    INVALID_CREDENTIALS = 1001
    TOKEN_EXPIRED = 1002
    INSUFFICIENT_PERMISSIONS = 1003
    
    # Validation errors (2000-2999) 
    MISSING_FIELD = 2001
    INVALID_FORMAT = 2002
    VALUE_OUT_OF_RANGE = 2003
    
    # Business logic errors (3000-3999)
    RESOURCE_NOT_FOUND = 3001
    RESOURCE_CONFLICT = 3002
    OPERATION_NOT_ALLOWED = 3003
    
    # System errors (5000-5999)
    DATABASE_ERROR = 5001
    EXTERNAL_SERVICE_ERROR = 5002
    RATE_LIMIT_EXCEEDED = 5003

@dataclass
class APIError:
    code: ErrorCode
    message: str
    details: Optional[Dict] = None
    field: Optional[str] = None
    more_info: Optional[str] = None
    
    def to_dict(self):
        result = {
            'error': {
                'code': self.code.value,
                'message': self.message,
                'type': self.code.name.lower()
            }
        }
        
        if self.details:
            result['error']['details'] = self.details
        if self.field:
            result['error']['field'] = self.field
        if self.more_info:
            result['error']['more_info'] = self.more_info
            
        return result

class ErrorHandler:
    ERROR_MAPPING = {
        ErrorCode.INVALID_CREDENTIALS: 401,
        ErrorCode.TOKEN_EXPIRED: 401,
        ErrorCode.INSUFFICIENT_PERMISSIONS: 403,
        ErrorCode.MISSING_FIELD: 400,
        ErrorCode.INVALID_FORMAT: 400,
        ErrorCode.VALUE_OUT_OF_RANGE: 400,
        ErrorCode.RESOURCE_NOT_FOUND: 404,
        ErrorCode.RESOURCE_CONFLICT: 409,
        ErrorCode.OPERATION_NOT_ALLOWED: 403,
        ErrorCode.DATABASE_ERROR: 500,
        ErrorCode.EXTERNAL_SERVICE_ERROR: 502,
        ErrorCode.RATE_LIMIT_EXCEEDED: 429,
    }
    
    def handle_error(self, error: APIError):
        status_code = self.ERROR_MAPPING.get(error.code, 500)
        return jsonify(error.to_dict()), status_code

# Usage in Flask
from flask import Flask, jsonify, request

app = Flask(__name__)
error_handler = ErrorHandler()

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    error = APIError(
        code=ErrorCode.INVALID_FORMAT,
        message=str(e),
        field=getattr(e, 'field', None),
        more_info="https://docs.example.com/errors/validation"
    )
    return error_handler.handle_error(error)

@app.errorhandler(404)
def handle_not_found(e):
    error = APIError(
        code=ErrorCode.RESOURCE_NOT_FOUND,
        message="The requested resource was not found",
        details={'path': request.path}
    )
    return error_handler.handle_error(error)
```

### Field-Level Validation Errors

```python
class ValidationErrorCollector:
    def __init__(self):
        self.errors = []
    
    def add_error(self, field: str, code: ErrorCode, message: str, details: Dict = None):
        self.errors.append({
            'field': field,
            'code': code.value,
            'message': message,
            'details': details
        })
    
    def has_errors(self):
        return len(self.errors) > 0
    
    def to_response(self):
        return {
            'error': {
                'type': 'validation_failed',
                'message': f'{len(self.errors)} validation error(s) occurred',
                'details': self.errors
            }
        }

# Usage with Pydantic
from pydantic import BaseModel, ValidationError

class CreateUserRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    age: int

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    try:
        user_data = CreateUserRequest(**request.json)
    except ValidationError as e:
        collector = ValidationErrorCollector()
        
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            collector.add_error(
                field=field,
                code=ErrorCode.INVALID_FORMAT,
                message=error['msg'],
                details={'type': error['type']}
            )
        
        return jsonify(collector.to_response()), 400
    
    # Process valid data...
    return jsonify({'user': created_user}), 201
```

### Circuit Breaker for External Service Errors

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise APIError(
                    code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                    message="Circuit breaker is OPEN",
                    details={'retry_after': self.timeout}
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise APIError(
                code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="External service unavailable",
                details={'original_error': str(e)}
            )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
payment_service_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=requests.RequestException
)

@app.route('/api/v1/charge', methods=['POST'])
def charge_payment():
    try:
        result = payment_service_breaker.call(
            charge_payment_service,
            request.json
        )
        return jsonify(result)
    except APIError as e:
        return error_handler.handle_error(e)
```

### Exercise 7: Error Handling Strategy (10 minutes)

Design error responses for these scenarios:
1. User tries to delete a resource that doesn't exist
2. Rate limit exceeded (1000 requests/hour)
3. Invalid JSON in request body
4. Required field missing
5. Database connection timeout

---

## Advanced API Patterns

### HATEOAS (Hypermedia as the Engine of Application State)

GitHub's REST API demonstrates HATEOAS principles:

```json
{
  "id": 1,
  "number": 1347,
  "state": "open",
  "title": "Bug fix",
  "body": "Fix the thing",
  "user": {
    "login": "octocat",
    "url": "https://api.github.com/users/octocat"
  },
  "url": "https://api.github.com/repos/octocat/Hello-World/issues/1347",
  "repository_url": "https://api.github.com/repos/octocat/Hello-World",
  "comments_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347/comments",
  "events_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347/events",
  "_links": {
    "self": {
      "href": "https://api.github.com/repos/octocat/Hello-World/issues/1347"
    },
    "html": {
      "href": "https://github.com/octocat/Hello-World/issues/1347"
    },
    "comments": {
      "href": "https://api.github.com/repos/octocat/Hello-World/issues/1347/comments"
    }
  }
}
```

#### HATEOAS Implementation

```python
class HATEOASBuilder:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def build_links(self, resource_type, resource_id, relationships=None):
        links = {
            'self': f"{self.base_url}/{resource_type}/{resource_id}"
        }
        
        # Add standard relationships
        if relationships:
            for rel_name, rel_config in relationships.items():
                if isinstance(rel_config, str):
                    # Simple relationship
                    links[rel_name] = f"{self.base_url}/{rel_config}"
                else:
                    # Complex relationship with conditions
                    if rel_config.get('condition', True):
                        links[rel_name] = f"{self.base_url}/{rel_config['path']}"
        
        return links
    
    def add_actions(self, resource, user_permissions):
        actions = []
        
        # Define available actions based on resource state and permissions
        resource_actions = {
            'order': {
                'cancel': {
                    'method': 'DELETE',
                    'href': f"/orders/{resource['id']}",
                    'condition': resource['status'] in ['pending', 'confirmed'],
                    'permission': 'orders:cancel'
                },
                'update': {
                    'method': 'PATCH',
                    'href': f"/orders/{resource['id']}",
                    'condition': resource['status'] != 'completed',
                    'permission': 'orders:update'
                }
            }
        }
        
        resource_type = resource['type']
        available_actions = resource_actions.get(resource_type, {})
        
        for action_name, action_config in available_actions.items():
            if (action_config.get('condition', True) and 
                action_config.get('permission') in user_permissions):
                actions.append({
                    'name': action_name,
                    'method': action_config['method'],
                    'href': f"{self.base_url}{action_config['href']}"
                })
        
        return actions

# Usage in Flask
hateoas = HATEOASBuilder('https://api.example.com/v1')

@app.route('/api/v1/orders/<order_id>')
def get_order(order_id):
    order = get_order_by_id(order_id)
    user_permissions = get_user_permissions(request.user_id)
    
    # Add HATEOAS links
    order['_links'] = hateoas.build_links(
        'orders', order_id,
        relationships={
            'customer': f"customers/{order['customer_id']}",
            'items': f"orders/{order_id}/items",
            'payments': f"orders/{order_id}/payments"
        }
    )
    
    # Add available actions
    order['_actions'] = hateoas.add_actions(order, user_permissions)
    
    return jsonify(order)
```

### Event-Driven API Patterns

#### Webhook Implementation

```python
import hmac
import hashlib
import json
from datetime import datetime

class WebhookManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def create_signature(self, payload, timestamp):
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def verify_signature(self, payload, signature, timestamp, tolerance=300):
        # Verify timestamp to prevent replay attacks
        current_time = int(datetime.utcnow().timestamp())
        if abs(current_time - int(timestamp)) > tolerance:
            raise ValueError("Request timestamp too old")
        
        expected_signature = self.create_signature(payload, timestamp)
        return hmac.compare_digest(signature, expected_signature)
    
    async def send_webhook(self, url, event_type, data, headers=None):
        timestamp = str(int(datetime.utcnow().timestamp()))
        payload = json.dumps({
            'event': event_type,
            'data': data,
            'timestamp': timestamp
        })
        
        signature = self.create_signature(payload, timestamp)
        
        webhook_headers = {
            'Content-Type': 'application/json',
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'User-Agent': 'YourAPI-Webhooks/1.0'
        }
        
        if headers:
            webhook_headers.update(headers)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=payload,
                headers=webhook_headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200

# Webhook delivery with retry logic
class WebhookDelivery:
    def __init__(self, webhook_manager, max_retries=3):
        self.webhook_manager = webhook_manager
        self.max_retries = max_retries
    
    async def deliver_with_retry(self, webhook_url, event_type, data):
        for attempt in range(self.max_retries):
            try:
                success = await self.webhook_manager.send_webhook(
                    webhook_url, event_type, data
                )
                if success:
                    return True
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Final failure - queue for manual retry
                    await self.queue_failed_webhook(webhook_url, event_type, data, str(e))
                    return False
                
                await asyncio.sleep(2 ** attempt)
        
        return False
    
    async def queue_failed_webhook(self, url, event_type, data, error):
        # Queue in dead letter queue for manual intervention
        failed_webhook = {
            'url': url,
            'event_type': event_type,
            'data': data,
            'error': error,
            'failed_at': datetime.utcnow().isoformat()
        }
        # Store in database or message queue
        pass
```

### Long-polling, WebSockets, and Server-Sent Events

#### Long-polling Implementation

```python
import asyncio
from flask import Flask, request, jsonify

class LongPollingManager:
    def __init__(self):
        self.subscribers = {}
    
    async def wait_for_updates(self, user_id, last_update_id, timeout=30):
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # Check for new updates
            updates = get_updates_since(user_id, last_update_id)
            if updates:
                return updates
            
            # Wait before checking again
            await asyncio.sleep(1)
        
        # Timeout reached, return empty response
        return []

@app.route('/api/v1/notifications/poll')
async def poll_notifications():
    user_id = request.user_id
    last_update_id = request.args.get('since', '0')
    timeout = min(int(request.args.get('timeout', 30)), 60)  # Max 60 seconds
    
    updates = await long_polling_manager.wait_for_updates(
        user_id, last_update_id, timeout
    )
    
    return jsonify({
        'updates': updates,
        'timestamp': int(time.time())
    })
```

#### Server-Sent Events (SSE)

```python
from flask import Response
import json
import time

@app.route('/api/v1/events/stream')
def event_stream():
    def generate():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': time.time()})}\n\n"
        
        # Subscribe to user-specific events
        user_id = request.user_id
        event_queue = subscribe_to_events(user_id)
        
        try:
            while True:
                try:
                    # Wait for event with timeout
                    event = event_queue.get(timeout=30)
                    
                    # Format as SSE
                    event_data = json.dumps({
                        'type': event['type'],
                        'data': event['data'],
                        'timestamp': time.time()
                    })
                    
                    yield f"id: {event['id']}\n"
                    yield f"event: {event['type']}\n"
                    yield f"data: {event_data}\n\n"
                    
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                
        except GeneratorExit:
            # Client disconnected
            unsubscribe_from_events(user_id, event_queue)
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )
```

### Batch Operations

```python
class BatchProcessor:
    def __init__(self, max_batch_size=100):
        self.max_batch_size = max_batch_size
    
    def process_batch(self, operations):
        if len(operations) > self.max_batch_size:
            raise ValueError(f"Batch size exceeds maximum of {self.max_batch_size}")
        
        results = []
        
        # Process operations atomically where possible
        with database.transaction():
            for i, operation in enumerate(operations):
                try:
                    result = self.process_single_operation(operation)
                    results.append({
                        'index': i,
                        'status': 'success',
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'index': i,
                        'status': 'error',
                        'error': {
                            'code': type(e).__name__,
                            'message': str(e)
                        }
                    })
        
        return results
    
    def process_single_operation(self, operation):
        op_type = operation.get('operation')
        
        if op_type == 'create':
            return self.create_resource(operation['resource'], operation['data'])
        elif op_type == 'update':
            return self.update_resource(operation['resource'], operation['id'], operation['data'])
        elif op_type == 'delete':
            return self.delete_resource(operation['resource'], operation['id'])
        else:
            raise ValueError(f"Unknown operation: {op_type}")

@app.route('/api/v1/batch', methods=['POST'])
def batch_operations():
    try:
        batch_request = request.json
        operations = batch_request.get('operations', [])
        
        if not operations:
            return jsonify({'error': 'No operations provided'}), 400
        
        results = batch_processor.process_batch(operations)
        
        # Calculate summary
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        return jsonify({
            'results': results,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### Idempotency Keys

```python
import uuid
import hashlib
from datetime import datetime, timedelta

class IdempotencyManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 24 * 3600  # 24 hours
    
    def get_or_create_result(self, idempotency_key, operation_func, *args, **kwargs):
        # Generate a hash of the operation for additional safety
        operation_hash = self._hash_operation(operation_func.__name__, args, kwargs)
        cache_key = f"idempotency:{idempotency_key}:{operation_hash}"
        
        # Check if we've seen this operation before
        cached_result = self.redis.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Execute operation
        result = operation_func(*args, **kwargs)
        
        # Cache result
        self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps({
                'result': result,
                'created_at': datetime.utcnow().isoformat(),
                'operation': operation_func.__name__
            })
        )
        
        return result
    
    def _hash_operation(self, func_name, args, kwargs):
        # Create a hash of the operation parameters
        operation_str = f"{func_name}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.sha256(operation_str.encode()).hexdigest()[:16]

# Decorator for idempotent operations
def idempotent(idempotency_manager):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            idempotency_key = request.headers.get('Idempotency-Key')
            
            if not idempotency_key:
                # Generate one if not provided (for GET requests)
                if request.method == 'GET':
                    idempotency_key = hashlib.sha256(request.url.encode()).hexdigest()
                else:
                    return jsonify({'error': 'Idempotency-Key header required'}), 400
            
            try:
                uuid.UUID(idempotency_key)  # Validate format
            except ValueError:
                return jsonify({'error': 'Invalid Idempotency-Key format'}), 400
            
            result = idempotency_manager.get_or_create_result(
                idempotency_key, f, *args, **kwargs
            )
            
            return result
        
        return wrapper
    return decorator

# Usage
@app.route('/api/v1/orders', methods=['POST'])
@require_api_key()
@idempotent(idempotency_manager)
def create_order():
    order_data = request.json
    # Process order creation...
    return jsonify({'order': created_order}), 201
```

### Exercise 8: Advanced Patterns (15 minutes)

Implement a batch endpoint that:
1. Accepts up to 50 operations
2. Supports create, update, delete for users
3. Returns detailed results for each operation
4. Uses idempotency keys
5. Implements proper error handling

---

## API Gateways and BFF Pattern

### API Gateway Architecture

```yaml
# Kong Gateway Configuration
services:
  - name: user-service
    url: http://user-service:3000
    plugins:
      - name: rate-limiting
        config:
          minute: 1000
          hour: 10000
      - name: jwt
        config:
          secret_is_base64: false
          key_claim_name: iss

  - name: order-service  
    url: http://order-service:3000
    plugins:
      - name: rate-limiting
        config:
          minute: 500
          hour: 5000

routes:
  - name: users-route
    service: user-service
    paths: ["/api/v1/users"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    
  - name: orders-route
    service: order-service  
    paths: ["/api/v1/orders"]
    methods: ["GET", "POST", "PUT", "DELETE"]
```

#### Custom API Gateway Implementation

```python
import asyncio
import aiohttp
from flask import Flask, request, jsonify
import yaml

class APIGateway:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.services = {s['name']: s for s in self.config['services']}
        self.routes = self.config['routes']
        self.middleware = []
    
    def add_middleware(self, middleware_func):
        self.middleware.append(middleware_func)
    
    async def route_request(self, path, method, headers, data=None):
        # Find matching route
        route = self.find_route(path, method)
        if not route:
            return {'error': 'Route not found'}, 404
        
        service = self.services[route['service']]
        
        # Apply middleware
        for middleware in self.middleware:
            result = await middleware(request, service)
            if result:  # Middleware blocked request
                return result
        
        # Forward request to service
        return await self.forward_request(service, path, method, headers, data)
    
    def find_route(self, path, method):
        for route in self.routes:
            if (method in route.get('methods', []) and 
                any(path.startswith(route_path) for route_path in route['paths'])):
                return route
        return None
    
    async def forward_request(self, service, path, method, headers, data):
        url = f"{service['url']}{path}"
        
        # Remove hop-by-hop headers
        forwarded_headers = {k: v for k, v in headers.items() 
                           if k.lower() not in ['host', 'connection']}
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, 
                headers=forwarded_headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.text()
                return response_data, response.status

# Rate limiting middleware
class RateLimitMiddleware:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def __call__(self, request, service):
        # Get rate limit config from service
        rate_limit_config = None
        for plugin in service.get('plugins', []):
            if plugin['name'] == 'rate-limiting':
                rate_limit_config = plugin['config']
                break
        
        if not rate_limit_config:
            return None  # No rate limiting configured
        
        client_id = request.headers.get('X-Client-ID', request.remote_addr)
        
        # Check rate limit
        current_minute = int(time.time() // 60)
        key = f"rate_limit:{service['name']}:{client_id}:{current_minute}"
        
        current_count = await self.redis.get(key) or 0
        if int(current_count) >= rate_limit_config['minute']:
            return {
                'error': 'Rate limit exceeded',
                'retry_after': 60 - (int(time.time()) % 60)
            }, 429
        
        # Increment counter
        await self.redis.incr(key)
        await self.redis.expire(key, 60)
        
        return None  # Allow request
```

### Backend for Frontend (BFF) Pattern

```python
class MobileBFF:
    """BFF optimized for mobile clients"""
    
    def __init__(self, user_service, order_service, product_service):
        self.user_service = user_service
        self.order_service = order_service
        self.product_service = product_service
    
    async def get_dashboard(self, user_id):
        """Aggregated dashboard data for mobile app"""
        
        # Fetch data in parallel
        tasks = [
            self.user_service.get_profile(user_id),
            self.order_service.get_recent_orders(user_id, limit=5),
            self.product_service.get_recommendations(user_id, limit=10)
        ]
        
        profile, recent_orders, recommendations = await asyncio.gather(*tasks)
        
        # Transform data for mobile consumption
        return {
            'user': {
                'name': profile['first_name'],
                'avatar': profile.get('avatar_url'),
                'membership': profile.get('membership_tier', 'basic')
            },
            'recent_orders': [
                {
                    'id': order['id'],
                    'status': order['status'],
                    'total': order['total'],
                    'date': order['created_at'][:10],  # Date only
                    'item_count': len(order.get('items', []))
                }
                for order in recent_orders
            ],
            'recommendations': [
                {
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'image': product.get('thumbnail_url'),
                    'rating': product.get('average_rating')
                }
                for product in recommendations
            ]
        }

class WebBFF:
    """BFF optimized for web clients"""
    
    def __init__(self, user_service, order_service, product_service):
        self.user_service = user_service
        self.order_service = order_service  
        self.product_service = product_service
    
    async def get_dashboard(self, user_id):
        """Detailed dashboard data for web interface"""
        
        # Web can handle more data and complexity
        tasks = [
            self.user_service.get_full_profile(user_id),
            self.order_service.get_orders_with_details(user_id, limit=20),
            self.product_service.get_recommendations_with_reasons(user_id, limit=20),
            self.user_service.get_preferences(user_id)
        ]
        
        profile, orders, recommendations, preferences = await asyncio.gather(*tasks)
        
        return {
            'user': profile,  # Full profile data
            'orders': orders,  # Detailed order information
            'recommendations': recommendations,  # With recommendation reasons
            'preferences': preferences,
            'analytics': {
                'total_orders': len(orders),
                'total_spent': sum(order['total'] for order in orders),
                'favorite_categories': self.calculate_favorite_categories(orders)
            }
        }

# Flask routes for BFF
@app.route('/api/mobile/v1/dashboard')
@require_api_key()
async def mobile_dashboard():
    mobile_bff = MobileBFF(user_service, order_service, product_service)
    dashboard_data = await mobile_bff.get_dashboard(request.user_id)
    return jsonify(dashboard_data)

@app.route('/api/web/v1/dashboard')  
@require_api_key()
async def web_dashboard():
    web_bff = WebBFF(user_service, order_service, product_service)
    dashboard_data = await web_bff.get_dashboard(request.user_id)
    return jsonify(dashboard_data)
```

### Service Mesh Integration

```yaml
# Istio Service Mesh Configuration
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-gateway
spec:
  hosts:
  - api.example.com
  gateways:
  - api-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1/users
    route:
    - destination:
        host: user-service
        port:
          number: 3000
    fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
      
  - match:
    - uri:
        prefix: /api/v1/orders
    route:
    - destination:
        host: order-service
        port:
          number: 3000
      weight: 90
    - destination:
        host: order-service-canary
        port:
          number: 3000
      weight: 10
```

### Exercise 9: BFF Design (10 minutes)

Design BFF endpoints for an e-commerce platform with different client needs:
- Mobile app (limited bandwidth)
- Web admin panel (detailed data)
- Third-party integrations (standardized format)

---

## Documentation and Testing

### OpenAPI 3.0 Specification

```yaml
openapi: 3.0.3
info:
  title: E-commerce API
  description: Comprehensive API for e-commerce platform
  version: 1.0.0
  contact:
    name: API Support
    email: api-support@example.com
    url: https://docs.example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
  termsOfService: https://example.com/terms

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

security:
  - ApiKeyAuth: []
  - BearerAuth: []

paths:
  /users:
    get:
      summary: List users
      description: Retrieve a paginated list of users
      tags: [Users]
      parameters:
        - name: limit
          in: query
          description: Number of users to return
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: cursor
          in: query
          description: Pagination cursor
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
              examples:
                typical_response:
                  summary: Typical user list response
                  value:
                    data:
                      - id: "user_123"
                        email: "john@example.com"
                        name: "John Doe"
                    has_more: true
                    next_cursor: "eyJpZCI6InVzZXJfMTIzIn0="
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '429':
          $ref: '#/components/responses/RateLimited'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
      properties:
        id:
          type: string
          description: Unique identifier for the user
          example: "user_123"
        email:
          type: string
          format: email
          description: User's email address
          example: "john@example.com"
        name:
          type: string
          description: User's full name
          example: "John Doe"
        created_at:
          type: string
          format: date-time
          description: When the user was created
          readOnly: true
        preferences:
          $ref: '#/components/schemas/UserPreferences'
    
    UserPreferences:
      type: object
      properties:
        theme:
          type: string
          enum: [light, dark, auto]
          default: auto
        notifications:
          type: boolean
          default: true
    
    UserList:
      type: object
      required:
        - data
        - has_more
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/User'
        has_more:
          type: boolean
          description: Whether more results are available
        next_cursor:
          type: string
          description: Cursor for the next page of results
          nullable: true
    
    Error:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: integer
              description: Error code
            message:
              type: string
              description: Human-readable error message
            details:
              type: object
              description: Additional error details

  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    RateLimited:
      description: Rate limit exceeded
      headers:
        Retry-After:
          description: Seconds to wait before retrying
          schema:
            type: integer
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for authentication
    
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT token for authentication
```

### Contract Testing with Pact

```python
import pytest
from pact import Consumer, Provider

# Consumer test (API client)
@pytest.fixture
def user_service_pact():
    pact = Consumer('mobile-app').has_pact_with(Provider('user-service'))
    pact.start_service()
    yield pact
    pact.stop_service()

def test_get_user_profile(user_service_pact):
    expected = {
        'id': 'user_123',
        'email': 'john@example.com',
        'name': 'John Doe',
        'created_at': '2024-01-01T00:00:00Z'
    }
    
    (user_service_pact
     .given('user user_123 exists')
     .upon_receiving('a request for user profile')
     .with_request('GET', '/api/v1/users/user_123', headers={'Authorization': 'Bearer token'})
     .will_respond_with(200, body=expected))
    
    with user_service_pact:
        # Make actual HTTP request
        response = requests.get(
            f'{user_service_pact.uri}/api/v1/users/user_123',
            headers={'Authorization': 'Bearer token'}
        )
        assert response.status_code == 200
        assert response.json() == expected

# Provider verification test
def test_provider_honors_contract():
    from pact import Verifier
    
    verifier = Verifier(provider='user-service', provider_base_url='http://localhost:3000')
    
    # Set up provider state
    def provider_state_setup():
        # Create test user
        test_db.create_user({
            'id': 'user_123',
            'email': 'john@example.com',
            'name': 'John Doe'
        })
    
    verifier.verify_pacts(
        './pacts/mobile-app-user-service.json',
        provider_states_setup_url='http://localhost:3000/pact/setup'
    )
```

### Load Testing with Locust

```python
from locust import HttpUser, task, between
import random

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get API token
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def get_users(self):
        """Most common operation - higher weight"""
        with self.client.get("/api/v1/users", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited")
    
    @task(1)
    def create_user(self):
        """Less common operation"""
        user_id = random.randint(10000, 99999)
        user_data = {
            "email": f"user{user_id}@example.com",
            "name": f"Test User {user_id}",
            "preferences": {
                "theme": random.choice(["light", "dark", "auto"]),
                "notifications": random.choice([True, False])
            }
        }
        
        with self.client.post("/api/v1/users", json=user_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                # Store created user ID for other tests
                created_user = response.json()
                self.user_id = created_user["id"]
            else:
                response.failure(f"Failed to create user: {response.status_code}")
    
    @task(2)
    def get_user_orders(self):
        """Test relationship endpoints"""
        if hasattr(self, 'user_id'):
            with self.client.get(f"/api/v1/users/{self.user_id}/orders", catch_response=True) as response:
                if response.status_code in [200, 404]:
                    response.success()
                else:
                    response.failure(f"Unexpected status: {response.status_code}")

# Custom load test scenarios
class StressTestUser(HttpUser):
    """Stress test with higher request rates"""
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task
    def rapid_api_calls(self):
        endpoints = [
            "/api/v1/users",
            "/api/v1/orders", 
            "/api/v1/products"
        ]
        
        endpoint = random.choice(endpoints)
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 429:
                # Expected under stress
                response.success()
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
```

### Automated API Testing

```python
import pytest
import requests
from jsonschema import validate

class TestUserAPI:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_url = "https://api.example.com/v1"
        self.headers = {"Authorization": "Bearer test_token"}
    
    def test_get_users_returns_valid_schema(self):
        """Test response matches OpenAPI schema"""
        response = requests.get(f"{self.base_url}/users", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate against JSON schema
        schema = {
            "type": "object",
            "required": ["data", "has_more"],
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "email", "name"],
                        "properties": {
                            "id": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "name": {"type": "string"}
                        }
                    }
                },
                "has_more": {"type": "boolean"},
                "next_cursor": {"type": ["string", "null"]}
            }
        }
        
        validate(instance=data, schema=schema)
    
    def test_pagination_works_correctly(self):
        """Test cursor-based pagination"""
        # Get first page
        response1 = requests.get(
            f"{self.base_url}/users?limit=2", 
            headers=self.headers
        )
        assert response1.status_code == 200
        
        page1 = response1.json()
        assert len(page1["data"]) <= 2
        
        if page1["has_more"]:
            # Get second page
            response2 = requests.get(
                f"{self.base_url}/users?limit=2&cursor={page1['next_cursor']}", 
                headers=self.headers
            )
            assert response2.status_code == 200
            
            page2 = response2.json()
            
            # Ensure no duplicate users
            page1_ids = {user["id"] for user in page1["data"]}
            page2_ids = {user["id"] for user in page2["data"]}
            assert page1_ids.isdisjoint(page2_ids)
    
    def test_error_responses_are_consistent(self):
        """Test error response format consistency"""
        # Test 404
        response = requests.get(
            f"{self.base_url}/users/nonexistent", 
            headers=self.headers
        )
        assert response.status_code == 404
        
        error_data = response.json()
        assert "error" in error_data
        assert "code" in error_data["error"]
        assert "message" in error_data["error"]
        
        # Test 400
        response = requests.post(
            f"{self.base_url}/users",
            headers=self.headers,
            json={"invalid": "data"}
        )
        assert response.status_code == 400
        
        error_data = response.json()
        assert "error" in error_data
    
    def test_rate_limiting_headers(self):
        """Test rate limiting behavior"""
        response = requests.get(f"{self.base_url}/users", headers=self.headers)
        
        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
```

### Exercise 10: Documentation Review (5 minutes)

Review this API documentation and identify what's missing:

```yaml
paths:
  /orders:
    post:
      summary: Create order
      requestBody:
        content:
          application/json:
            schema:
              type: object
      responses:
        '201':
          description: Created
```

**Missing elements:**
- Request schema definition
- Response schema
- Error responses
- Examples
- Authentication requirements
- Parameter validation

---

## Monitoring and Analytics

### API Metrics and Observability

#### Prometheus Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from functools import wraps

# Define metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'api_active_requests',
    'Number of active API requests',
    ['endpoint']
)

ERROR_RATE = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

def monitor_api_performance(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        method = request.method
        endpoint = request.endpoint or 'unknown'
        
        # Track active requests
        ACTIVE_REQUESTS.labels(endpoint=endpoint).inc()
        
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            status = getattr(result, 'status_code', 200)
            
            # Count successful requests
            REQUEST_COUNT.labels(
                method=method, 
                endpoint=endpoint, 
                status=status
            ).inc()
            
            return result
            
        except Exception as e:
            # Count errors
            ERROR_RATE.labels(
                endpoint=endpoint,
                error_type=type(e).__name__
            ).inc()
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()
            
            raise
        finally:
            # Track request duration
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Decrease active requests
            ACTIVE_REQUESTS.labels(endpoint=endpoint).dec()
    
    return wrapper

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

# Apply monitoring to all API endpoints
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request  
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        
        # Log slow requests
        if duration > 1.0:  # Requests slower than 1 second
            app.logger.warning(
                f"Slow request: {request.method} {request.path} took {duration:.2f}s"
            )
    
    return response
```

#### Structured Logging for APIs

```python
import logging
import json
from datetime import datetime
import uuid
from flask import g, request

class APILogger:
    def __init__(self, logger):
        self.logger = logger
    
    def log_request(self, user_id=None):
        """Log API request details"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': str(uuid.uuid4()),
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.args),
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'user_id': user_id,
            'content_length': request.content_length
        }
        
        # Store request ID for correlation
        g.request_id = log_data['request_id']
        
        self.logger.info(json.dumps({
            'event': 'api_request',
            **log_data
        }))
    
    def log_response(self, response, duration=None):
        """Log API response details"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'status_code': response.status_code,
            'response_size': len(response.get_data()),
            'duration_ms': duration * 1000 if duration else None
        }
        
        self.logger.info(json.dumps({
            'event': 'api_response',
            **log_data
        }))
    
    def log_error(self, error, user_id=None):
        """Log API errors with context"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': getattr(g, 'request_id', 'unknown'),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'method': request.method,
            'path': request.path,
            'user_id': user_id,
            'stack_trace': traceback.format_exc() if app.debug else None
        }
        
        self.logger.error(json.dumps({
            'event': 'api_error',
            **log_data
        }))

# Usage in Flask
api_logger = APILogger(logging.getLogger('api'))

@app.before_request
def before_request():
    request.start_time = time.time()
    user_id = getattr(request, 'user_id', None)
    api_logger.log_request(user_id)

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        api_logger.log_response(response, duration)
    
    return response

@app.errorhandler(Exception)
def handle_error(error):
    user_id = getattr(request, 'user_id', None)
    api_logger.log_error(error, user_id)
    
    return jsonify({'error': 'Internal server error'}), 500
```

### API Analytics and Business Metrics

```python
class APIAnalytics:
    def __init__(self, analytics_db):
        self.db = analytics_db
    
    def track_api_usage(self, endpoint, user_id, response_time, status_code):
        """Track API usage metrics"""
        self.db.insert('api_usage', {
            'timestamp': datetime.utcnow(),
            'endpoint': endpoint,
            'user_id': user_id,
            'response_time': response_time,
            'status_code': status_code,
            'date': datetime.utcnow().date()
        })
    
    def get_usage_stats(self, start_date, end_date):
        """Get comprehensive usage statistics"""
        return {
            'total_requests': self.get_total_requests(start_date, end_date),
            'unique_users': self.get_unique_users(start_date, end_date),
            'avg_response_time': self.get_avg_response_time(start_date, end_date),
            'error_rate': self.get_error_rate(start_date, end_date),
            'top_endpoints': self.get_top_endpoints(start_date, end_date),
            'slowest_endpoints': self.get_slowest_endpoints(start_date, end_date)
        }
    
    def get_user_behavior_analysis(self, user_id):
        """Analyze individual user API behavior"""
        usage_data = self.db.query("""
            SELECT 
                endpoint,
                COUNT(*) as request_count,
                AVG(response_time) as avg_response_time,
                DATE(timestamp) as date
            FROM api_usage 
            WHERE user_id = %s 
            AND timestamp >= NOW() - INTERVAL 30 DAY
            GROUP BY endpoint, DATE(timestamp)
        """, [user_id])
        
        return {
            'most_used_endpoints': self.calculate_endpoint_usage(usage_data),
            'usage_patterns': self.analyze_usage_patterns(usage_data),
            'performance_impact': self.calculate_user_impact(usage_data)
        }

# Real-time dashboard data
class APIDashboard:
    def __init__(self, redis_client, analytics):
        self.redis = redis_client
        self.analytics = analytics
    
    def get_real_time_metrics(self):
        """Get real-time API metrics for dashboard"""
        current_time = int(time.time())
        minute_key = f"metrics:{current_time // 60}"
        
        return {
            'requests_per_minute': self.redis.get(f"{minute_key}:requests") or 0,
            'errors_per_minute': self.redis.get(f"{minute_key}:errors") or 0,
            'avg_response_time': self.get_avg_response_time_minute(),
            'active_users': self.get_active_users_count(),
            'top_errors': self.get_recent_errors(),
            'api_health': self.calculate_api_health()
        }
    
    def calculate_api_health(self):
        """Calculate overall API health score"""
        metrics = {
            'error_rate': self.get_error_rate_last_5min(),
            'avg_response_time': self.get_avg_response_time_last_5min(),
            'availability': self.get_availability_last_5min()
        }
        
        # Health scoring algorithm
        health_score = 100
        
        if metrics['error_rate'] > 0.01:  # > 1% error rate
            health_score -= 30
        elif metrics['error_rate'] > 0.005:  # > 0.5% error rate
            health_score -= 15
        
        if metrics['avg_response_time'] > 1.0:  # > 1 second
            health_score -= 25
        elif metrics['avg_response_time'] > 0.5:  # > 500ms
            health_score -= 10
        
        if metrics['availability'] < 0.99:  # < 99% availability
            health_score -= 40
        elif metrics['availability'] < 0.995:  # < 99.5% availability
            health_score -= 20
        
        return max(0, health_score)

# API for dashboard consumption
@app.route('/api/v1/analytics/dashboard')
@require_api_key(permissions=['analytics:read'])
def get_dashboard_metrics():
    dashboard = APIDashboard(redis_client, analytics)
    metrics = dashboard.get_real_time_metrics()
    return jsonify(metrics)

@app.route('/api/v1/analytics/usage')
@require_api_key(permissions=['analytics:read'])
def get_usage_analytics():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date', datetime.utcnow().isoformat())
    
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    stats = analytics.get_usage_stats(start_date, end_date)
    return jsonify(stats)
```

### Alerting and SLA Monitoring

```python
class SLAMonitor:
    def __init__(self, alert_manager):
        self.alert_manager = alert_manager
        self.sla_targets = {
            'availability': 0.999,  # 99.9% uptime
            'response_time_p95': 500,  # 95th percentile < 500ms
            'error_rate': 0.001,  # < 0.1% error rate
        }
    
    def check_sla_compliance(self, time_window_minutes=5):
        """Check SLA compliance over time window"""
        current_metrics = self.get_current_metrics(time_window_minutes)
        violations = []
        
        # Check availability
        if current_metrics['availability'] < self.sla_targets['availability']:
            violations.append({
                'metric': 'availability',
                'current': current_metrics['availability'],
                'target': self.sla_targets['availability'],
                'severity': 'critical'
            })
        
        # Check response time
        if current_metrics['response_time_p95'] > self.sla_targets['response_time_p95']:
            violations.append({
                'metric': 'response_time_p95',
                'current': current_metrics['response_time_p95'],
                'target': self.sla_targets['response_time_p95'],
                'severity': 'warning' if current_metrics['response_time_p95'] < 1000 else 'critical'
            })
        
        # Check error rate
        if current_metrics['error_rate'] > self.sla_targets['error_rate']:
            violations.append({
                'metric': 'error_rate',
                'current': current_metrics['error_rate'],
                'target': self.sla_targets['error_rate'],
                'severity': 'critical' if current_metrics['error_rate'] > 0.01 else 'warning'
            })
        
        # Send alerts for violations
        for violation in violations:
            self.alert_manager.send_alert(
                title=f"SLA Violation: {violation['metric']}",
                message=f"Current: {violation['current']}, Target: {violation['target']}",
                severity=violation['severity'],
                tags=['sla', 'api', violation['metric']]
            )
        
        return violations

class AlertManager:
    def __init__(self, webhook_url=None, email_config=None):
        self.webhook_url = webhook_url
        self.email_config = email_config
    
    async def send_alert(self, title, message, severity='warning', tags=None):
        """Send alert to configured channels"""
        alert_data = {
            'title': title,
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'tags': tags or []
        }
        
        # Send to Slack/webhook
        if self.webhook_url:
            await self.send_webhook_alert(alert_data)
        
        # Send email for critical alerts
        if severity == 'critical' and self.email_config:
            await self.send_email_alert(alert_data)
    
    async def send_webhook_alert(self, alert_data):
        """Send alert to webhook (Slack, etc.)"""
        color = {
            'info': '#36a64f',
            'warning': '#ffcc00',
            'critical': '#ff0000'
        }.get(alert_data['severity'], '#cccccc')
        
        slack_message = {
            'attachments': [{
                'color': color,
                'title': alert_data['title'],
                'text': alert_data['message'],
                'fields': [
                    {'title': 'Severity', 'value': alert_data['severity'], 'short': True},
                    {'title': 'Time', 'value': alert_data['timestamp'], 'short': True}
                ],
                'footer': 'API Monitoring',
                'ts': int(datetime.utcnow().timestamp())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=slack_message)

# Scheduled SLA monitoring
@app.cli.command()
def monitor_sla():
    """CLI command to check SLA compliance"""
    alert_manager = AlertManager(webhook_url=os.getenv('SLACK_WEBHOOK_URL'))
    sla_monitor = SLAMonitor(alert_manager)
    
    violations = sla_monitor.check_sla_compliance()
    if violations:
        print(f"Found {len(violations)} SLA violations")
    else:
        print("All SLA targets met")
```

### Exercise 11: Monitoring Setup (10 minutes)

Design a monitoring strategy for a payment API that includes:
- Key metrics to track
- SLA definitions
- Alert conditions
- Dashboard requirements

---

## Hands-on Exercises

### Exercise 12: Complete API Design Challenge

**Scenario:** Design a comprehensive API for a ride-sharing platform similar to Uber.

**Requirements:**
1. **Core Resources:**
   - Users (riders and drivers)
   - Rides (trip requests and bookings)
   - Vehicles
   - Payments

2. **Functionality:**
   - User registration and authentication
   - Real-time ride matching
   - Location tracking
   - Payment processing
   - Rating system

3. **Technical Requirements:**
   - RESTful design with GraphQL for mobile optimization
   - Real-time updates using WebSockets/SSE
   - Geospatial queries for ride matching
   - Rate limiting for different user tiers
   - Comprehensive error handling
   - API versioning strategy

**Solution Framework:**

```yaml
# OpenAPI specification structure
paths:
  # Authentication
  /auth/register:
    post:
      summary: Register new user
      
  /auth/login:
    post:
      summary: User login
  
  # User management
  /users/{user_id}:
    get:
      summary: Get user profile
    patch:
      summary: Update user profile
  
  # Ride lifecycle
  /rides:
    post:
      summary: Request a ride
    get:
      summary: List user's rides
      
  /rides/{ride_id}:
    get:
      summary: Get ride details
    patch:
      summary: Update ride status
    delete:
      summary: Cancel ride
  
  # Real-time endpoints
  /rides/{ride_id}/location:
    get:
      summary: Get current ride location
      
  /events/stream:
    get:
      summary: SSE endpoint for real-time updates
  
  # Driver-specific endpoints
  /drivers/availability:
    patch:
      summary: Update driver availability
      
  /drivers/rides/accept:
    post:
      summary: Accept ride request
```

**Implementation Highlights:**

```python
# Geospatial ride matching
class RideMatchingService:
    def find_nearby_drivers(self, pickup_location, radius_km=5):
        """Find available drivers within radius"""
        return self.db.query("""
            SELECT driver_id, location, 
                   ST_Distance_Sphere(location, ST_GeomFromText(%s)) as distance
            FROM driver_locations 
            WHERE available = true
              AND ST_Distance_Sphere(location, ST_GeomFromText(%s)) <= %s
            ORDER BY distance
            LIMIT 10
        """, [pickup_location, pickup_location, radius_km * 1000])
    
    async def match_ride(self, ride_request):
        """Match rider with optimal driver"""
        nearby_drivers = self.find_nearby_drivers(ride_request['pickup_location'])
        
        for driver in nearby_drivers:
            # Send ride request to driver
            accepted = await self.send_ride_request(driver['driver_id'], ride_request)
            if accepted:
                return self.create_ride(ride_request, driver['driver_id'])
        
        return None  # No drivers available

# Real-time location updates
@socketio.on('location_update')
def handle_location_update(data):
    user_id = session.get('user_id')
    if not user_id:
        return False
    
    # Update location in database
    update_user_location(user_id, data['latitude'], data['longitude'])
    
    # Broadcast to interested parties (rider/driver)
    if data.get('ride_id'):
        socketio.emit('location_updated', {
            'user_id': user_id,
            'location': {
                'latitude': data['latitude'],
                'longitude': data['longitude']
            }
        }, room=f"ride_{data['ride_id']}")
```

### Time Investment Summary

- **Foundation & REST Design:** 105 minutes
- **Advanced Patterns (GraphQL, gRPC):** 85 minutes
- **Authentication & Security:** 50 minutes
- **Error Handling & Versioning:** 45 minutes
- **Advanced Features & Patterns:** 65 minutes
- **Documentation & Testing:** 40 minutes
- **Monitoring & Analytics:** 30 minutes

**Total Learning Time: 420+ minutes of comprehensive API design mastery**

---

## Conclusion

This comprehensive guide covers the essential patterns and practices for building production-scale APIs. You've learned from industry leaders like Stripe, Twilio, GitHub, and Google to understand how to:

1. **Design Consistent APIs** - Following REST principles and industry standards
2. **Choose the Right Technology** - Understanding when to use REST, GraphQL, or gRPC
3. **Implement Robust Security** - With proper authentication and authorization
4. **Handle Scale and Performance** - Through caching, rate limiting, and optimization
5. **Plan for Evolution** - With versioning and backward compatibility
6. **Monitor and Maintain** - With comprehensive observability and alerting

### Key Takeaways

- **Start with REST** for most APIs, but consider GraphQL for data-intensive applications
- **Security is not optional** - implement proper authentication from day one
- **Plan for scale** - design your APIs to handle growth from the beginning
- **Monitor everything** - you can't improve what you don't measure
- **Documentation is crucial** - APIs are only as good as their documentation

### Next Steps

1. **Practice** the patterns in your own projects
2. **Study** the APIs of companies you admire
3. **Measure** your API performance and user satisfaction
4. **Iterate** based on real-world usage and feedback
5. **Share** your learnings with the community

Continue building APIs that developers love to use and that scale to serve millions of users worldwide.

---

*Return to the [Architecture Patterns Index](index.md) or explore other [Pattern Library](../) topics.*