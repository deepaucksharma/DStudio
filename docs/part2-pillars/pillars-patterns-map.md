# Pillars ↔ Patterns Mini-Map

## Quick Reference Grid

```
                 Patterns that help with each Pillar
              Work    State   Truth   Control  Intelligence

Queues         ███     ░░      ░       █         ░
CQRS           ██      ███     ██      ░         █
Event-Driven   ███     █       █       ██        ██
Event Sourcing █       ███     ███     █         ██
Saga           ██      ██      ███     ██        █
Service Mesh   ██      ░       █       ███       ██
GraphQL        ██      █       ░       ██        █
Serverless     ███     ░       ░       █         ██
Edge/IoT       ██      ██      █       █         ███
CDC            █       ███     ██      █         ██
Tunable        ░       ██      ███     █         █
Sharding       █       ███     █       ██        █
Caching        ██      ███     █       █         ██
Circuit Break  ███     ░       ░       ██        █
Retry/Backoff  ██      ░       █       █         ██
Bulkhead       ███     █       ░       ██        █
Geo-Replica    █       ███     ██      ██        █
Observable     █       █       █       ███       ███
FinOps         █       █       ░       ██        ██

Legend: ███ Strong fit  ██ Good fit  █ Some fit  ░ Minimal
```

## Usage Example

"I need better Work Distribution" → Look at Queues, Serverless, Circuit Breaker

"State is my bottleneck" → Consider CQRS, Event Sourcing, Sharding, Caching

---

**Next**: [Transition to Part III →](transition-part3.md)