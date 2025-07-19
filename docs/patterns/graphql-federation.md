# GraphQL Federation

**One graph to rule them all**

## THE PROBLEM

```
REST API explosion:
- /api/user/{id}
- /api/user/{id}/orders
- /api/order/{id}/items
- /api/product/{id}

Client needs user + orders + products = 4+ round trips
Mobile on 3G = 2 seconds just in latency!
```

## THE SOLUTION

```
GraphQL: Query exactly what you need

query {
  user(id: "123") {
    name
    orders(last: 5) {
      items {
        product {
          name
          price
        }
      }
    }
  }
}

One request, shaped response, no overfetching
```

## Federation Pattern

```
Multiple services, one graph:

User Service    Order Service    Product Service
    ↓                ↓                 ↓
[Schema]         [Schema]          [Schema]
    ↓                ↓                 ↓
    └────────────────┴─────────────────┘
                     ↓
              Gateway (Stitches schemas)
                     ↓
                  Client
```

## IMPLEMENTATION

```python
from graphql import GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString
from dataclasses import dataclass
import asyncio

# Domain models
@dataclass
class User:
    id: str
    name: str
    email: str

@dataclass  
class Order:
    id: str
    user_id: str
    total: float
    items: list

@dataclass
class Product:
    id: str
    name: str
    price: float

# Service interfaces
class UserService:
    async def get_user(self, user_id: str) -> User:
        # Simulate DB call
        return User(id=user_id, name="John Doe", email="john@example.com")
    
    async def get_users_batch(self, user_ids: list) -> dict:
        # Batch loading for efficiency
        users = await asyncio.gather(*[
            self.get_user(uid) for uid in user_ids
        ])
        return {u.id: u for u in users}

class OrderService:
    async def get_user_orders(self, user_id: str) -> list:
        return [
            Order(id="ord1", user_id=user_id, total=99.99, items=["item1"]),
            Order(id="ord2", user_id=user_id, total=149.99, items=["item2"])
        ]
    
    async def get_order(self, order_id: str) -> Order:
        return Order(id=order_id, user_id="123", total=99.99, items=[])

# GraphQL Schema with federation
class GraphQLFederation:
    def __init__(self):
        self.services = {
            'user': UserService(),
            'order': OrderService(),
            'product': ProductService()
        }
        self.schema = self.build_schema()
        
    def build_schema(self):
        # User type with federation directive
        user_type = GraphQLObjectType(
            'User',
            fields=lambda: {
                'id': GraphQLField(GraphQLString),
                'name': GraphQLField(GraphQLString),
                'email': GraphQLField(GraphQLString),
                'orders': GraphQLField(
                    GraphQLList(order_type),
                    resolve=self.resolve_user_orders
                )
            }
        )
        
        # Order type extending User
        order_type = GraphQLObjectType(
            'Order',
            fields=lambda: {
                'id': GraphQLField(GraphQLString),
                'total': GraphQLField(GraphQLFloat),
                'user': GraphQLField(
                    user_type,
                    resolve=self.resolve_order_user
                ),
                'items': GraphQLField(
                    GraphQLList(item_type),
                    resolve=self.resolve_order_items
                )
            }
        )
        
        # Query root
        query_type = GraphQLObjectType(
            'Query',
            fields={
                'user': GraphQLField(
                    user_type,
                    args={'id': GraphQLArgument(GraphQLString)},
                    resolve=self.resolve_user
                ),
                'order': GraphQLField(
                    order_type,
                    args={'id': GraphQLArgument(GraphQLString)},
                    resolve=self.resolve_order
                )
            }
        )
        
        return GraphQLSchema(query=query_type)
    
    # Resolvers with DataLoader pattern
    async def resolve_user(self, root, info, id):
        return await self.services['user'].get_user(id)
    
    async def resolve_user_orders(self, user, info):
        return await self.services['order'].get_user_orders(user.id)
    
    async def resolve_order_user(self, order, info):
        # Use DataLoader to batch user lookups
        return await info.context.user_loader.load(order.user_id)

# DataLoader for N+1 prevention
class DataLoader:
    def __init__(self, batch_fn, max_batch_size=100):
        self.batch_fn = batch_fn
        self.max_batch_size = max_batch_size
        self.queue = []
        self.cache = {}
        
    async def load(self, key):
        if key in self.cache:
            return self.cache[key]
            
        # Add to batch queue
        future = asyncio.Future()
        self.queue.append((key, future))
        
        # Dispatch batch if full or after delay
        if len(self.queue) >= self.max_batch_size:
            await self.dispatch()
        else:
            asyncio.create_task(self.dispatch_after_delay())
            
        return await future
    
    async def dispatch(self):
        if not self.queue:
            return
            
        # Extract keys and futures
        batch = self.queue[:self.max_batch_size]
        self.queue = self.queue[self.max_batch_size:]
        
        keys = [item[0] for item in batch]
        futures = {item[0]: item[1] for item in batch}
        
        # Call batch function
        try:
            results = await self.batch_fn(keys)
            
            # Resolve futures
            for key, future in futures.items():
                if key in results:
                    self.cache[key] = results[key]
                    future.set_result(results[key])
                else:
                    future.set_exception(KeyError(f"Key {key} not found"))
                    
        except Exception as e:
            for future in futures.values():
                future.set_exception(e)
    
    async def dispatch_after_delay(self):
        await asyncio.sleep(0.001)  # 1ms delay
        await self.dispatch()

# Federation gateway
class FederationGateway:
    def __init__(self, service_schemas):
        self.service_schemas = service_schemas
        self.composed_schema = self.compose_schemas()
        
    def compose_schemas(self):
        """Stitch together multiple schemas"""
        types = {}
        queries = {}
        
        for service_name, schema in self.service_schemas.items():
            # Merge types
            for type_name, type_def in schema.type_map.items():
                if type_name.startswith('__'):  # Skip introspection
                    continue
                    
                if type_name in types:
                    # Extend existing type
                    types[type_name] = self.merge_types(
                        types[type_name], type_def
                    )
                else:
                    types[type_name] = type_def
            
            # Merge queries
            query_type = schema.query_type
            if query_type:
                for field_name, field in query_type.fields.items():
                    queries[f"{service_name}_{field_name}"] = field
        
        # Build unified schema
        unified_query = GraphQLObjectType('Query', queries)
        return GraphQLSchema(query=unified_query, types=list(types.values()))
    
    def merge_types(self, type1, type2):
        """Merge two GraphQL types"""
        merged_fields = {**type1.fields, **type2.fields}
        return GraphQLObjectType(type1.name, merged_fields)

# Query planning and execution
class QueryPlanner:
    def __init__(self, schema, services):
        self.schema = schema
        self.services = services
        
    def plan_query(self, query):
        """Create execution plan for query"""
        plan = QueryPlan()
        
        # Parse query and identify required services
        selections = self.parse_selections(query)
        
        for selection in selections:
            service = self.identify_service(selection)
            plan.add_step(service, selection)
            
        # Optimize plan (merge calls to same service)
        return plan.optimize()
    
    async def execute_plan(self, plan, context):
        """Execute query plan with optimal batching"""
        results = {}
        
        # Execute in parallel where possible
        for parallel_group in plan.parallel_groups:
            group_results = await asyncio.gather(*[
                self.execute_step(step, context)
                for step in parallel_group
            ])
            
            for step, result in zip(parallel_group, group_results):
                results[step.key] = result
                
        return self.merge_results(results)
```

## Advanced Features

```python
# Schema directives for federation
class FederationDirectives:
    @staticmethod
    def key(fields: str):
        """Mark type as entity with key fields"""
        return f'@key(fields: "{fields}")'
    
    @staticmethod
    def external():
        """Mark field as owned by another service"""
        return '@external'
    
    @staticmethod
    def requires(fields: str):
        """Specify required fields from other service"""
        return f'@requires(fields: "{fields}")'
    
    @staticmethod
    def provides(fields: str):
        """Specify fields this service provides"""
        return f'@provides(fields: "{fields}")'

# Subscription support
class GraphQLSubscriptions:
    def __init__(self):
        self.subscriptions = {}
        
    def add_subscription(self, name, resolver):
        subscription_type = GraphQLField(
            GraphQLString,
            subscribe=resolver,
            resolve=lambda obj, info: obj
        )
        self.subscriptions[name] = subscription_type
        
    async def order_updated_subscription(self, root, info, order_id):
        """Real-time order updates"""
        async for update in self.order_update_stream(order_id):
            yield update
            
    async def order_update_stream(self, order_id):
        """Stream order updates from event bus"""
        event_bus = info.context.event_bus
        
        async for event in event_bus.subscribe(f'order.{order_id}.updated'):
            yield {
                'orderId': order_id,
                'status': event['status'],
                'timestamp': event['timestamp']
            }

# Performance monitoring
class GraphQLMetrics:
    def __init__(self):
        self.resolver_times = defaultdict(list)
        self.query_complexity = []
        
    def track_resolver(self, field_name):
        def decorator(resolver_fn):
            async def wrapper(*args, **kwargs):
                start = time.time()
                result = await resolver_fn(*args, **kwargs)
                duration = time.time() - start
                
                self.resolver_times[field_name].append(duration)
                
                if duration > 0.1:  # Slow resolver warning
                    logger.warning(f"Slow resolver {field_name}: {duration}s")
                    
                return result
            return wrapper
        return decorator
    
    def calculate_query_cost(self, query):
        """Estimate query complexity for rate limiting"""
        cost = 0
        depth = 0
        
        def visit_field(field, current_depth):
            nonlocal cost, depth
            
            # Base cost per field
            cost += 1
            
            # Additional cost for lists
            if field.return_type.is_list:
                cost += 10
                
            # Track max depth
            depth = max(depth, current_depth)
            
            # Recursively visit selections
            if field.selections:
                for selection in field.selections:
                    visit_field(selection, current_depth + 1)
        
        visit_field(query.root_field, 1)
        
        # Exponential cost for deep queries
        cost *= (1.5 ** depth)
        
        return cost
```

## ✓ CHOOSE THIS WHEN:
• Multiple backend services
• Mobile/web clients need different data
• Reducing network round trips critical
• Type safety important
• Real-time subscriptions needed

## ⚠️ BEWARE OF:
• N+1 query problems
• Complex authorization
• Caching challenges
• Query complexity attacks
• Schema versioning pain

## REAL EXAMPLES
• **GitHub**: Migrated API v3 (REST) to v4 (GraphQL)
• **Shopify**: 1000+ types in federated graph
• **Netflix**: Federated graph for UI teams