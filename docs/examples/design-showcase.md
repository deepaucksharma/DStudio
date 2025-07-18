# Design System Showcase

This page demonstrates the new flat, minimalistic design system implemented for DStudio.

## Typography Scale

### Heading Hierarchy

# H1: The Compendium Title
## H2: Section Headers  
### H3: Subsection Headers
#### H4: Component Headers
##### H5: Detail Headers
###### H6: Smallest Headers

Body text follows a comfortable reading rhythm with proper line height and spacing. The typography scale uses the Major Third ratio (1.25x) for harmonious progression between sizes.

## Color System

<div class="grid grid-4 gap-4">
  <div class="card p-4 bg-primary text-white">
    <h4>Primary</h4>
    <p>Indigo #3F51B5</p>
  </div>
  <div class="card p-4 bg-success text-white">
    <h4>Success</h4>
    <p>Green #4CAF50</p>
  </div>
  <div class="card p-4 bg-warning text-white">
    <h4>Warning</h4>
    <p>Orange #FF9800</p>
  </div>
  <div class="card p-4 bg-error text-white">
    <h4>Error</h4>
    <p>Red #F44336</p>
  </div>
</div>

## Custom Components

### Axiom Box
<div class="axiom-box">
<strong>Axiom of Latency</strong>

Speed of light is the fundamental limit. No amount of engineering can overcome physics. Design your systems with this constraint in mind.
</div>

### Decision Box
<div class="decision-box">
<strong>Choosing a Database</strong>

When selecting a database, consider:
- Data model requirements
- Consistency guarantees  
- Performance characteristics
- Operational complexity
</div>

### Failure Vignette
<div class="failure-vignette">
<strong>The Day the CDN Failed</strong>

In 2021, a major CDN provider experienced a global outage due to a configuration error. This cascading failure took down thousands of websites for over an hour, demonstrating the importance of failure isolation.
</div>

### Truth Box
<div class="truth-box">
<strong>CAP Theorem Reality</strong>

You can have at most two of: Consistency, Availability, and Partition Tolerance. In distributed systems, partition tolerance is mandatory, so you're really choosing between consistency and availability.
</div>

## Buttons

<div class="flex gap-2 items-center">
  <button class="btn btn-primary">Primary Action</button>
  <button class="btn btn-secondary">Secondary</button>
  <button class="btn btn-ghost">Ghost Button</button>
  <button class="btn btn-danger">Danger Zone</button>
</div>

### Button Sizes

<div class="flex gap-2 items-center">
  <button class="btn btn-primary btn-xs">Extra Small</button>
  <button class="btn btn-primary btn-sm">Small</button>
  <button class="btn btn-primary">Default</button>
  <button class="btn btn-primary btn-lg">Large</button>
  <button class="btn btn-primary btn-xl">Extra Large</button>
</div>

## Forms

<div class="form-group">
  <label class="form-label">Email Address</label>
  <input type="email" class="form-control" placeholder="user@example.com">
  <p class="form-help">We'll never share your email with anyone else.</p>
</div>

<div class="form-group">
  <label class="form-label">Select Region</label>
  <select class="form-control form-select">
    <option>US East (N. Virginia)</option>
    <option>US West (Oregon)</option>
    <option>EU (Ireland)</option>
    <option>Asia Pacific (Singapore)</option>
  </select>
</div>

<div class="form-group">
  <label class="form-checkbox">
    <input type="checkbox">
    <span>Enable automatic backups</span>
  </label>
</div>

## Alerts

<div class="alert alert-info">
  <strong>Info:</strong> This is an informational message providing additional context.
</div>

<div class="alert alert-success">
  <strong>Success!</strong> Your distributed system is now operational.
</div>

<div class="alert alert-warning">
  <strong>Warning:</strong> High latency detected between regions.
</div>

<div class="alert alert-error">
  <strong>Error:</strong> Connection to database cluster failed.
</div>

## Cards

<div class="grid grid-3 gap-4">
  <div class="card">
    <div class="card-header">
      <h3>Latency Optimization</h3>
    </div>
    <div class="card-body">
      <p>Techniques for reducing latency in distributed systems through caching, CDNs, and edge computing.</p>
    </div>
    <div class="card-footer">
      <button class="btn btn-primary btn-sm">Learn More</button>
    </div>
  </div>
  
  <div class="card card-elevated">
    <div class="card-body">
      <h3>Elevated Card</h3>
      <p>This card uses subtle shadows for depth while maintaining the flat design aesthetic.</p>
    </div>
  </div>
  
  <div class="card card-interactive">
    <div class="card-body">
      <h3>Interactive Card</h3>
      <p>Hover over this card to see the interactive lift effect with smooth transitions.</p>
    </div>
  </div>
</div>

## Tables

| Service | Region | Latency | Status |
|---------|--------|---------|--------|
| API Gateway | us-east-1 | 12ms | 🟢 Healthy |
| Database Primary | us-east-1 | 8ms | 🟢 Healthy |
| Database Replica | eu-west-1 | 45ms | 🟡 Degraded |
| Cache Layer | ap-south-1 | 92ms | 🔴 Down |

## Grid System

<div class="grid grid-12 gap-2">
  <div class="col-span-12 bg-gray-100 p-3 rounded">12 columns</div>
  <div class="col-span-6 bg-gray-200 p-3 rounded">6 columns</div>
  <div class="col-span-6 bg-gray-200 p-3 rounded">6 columns</div>
  <div class="col-span-4 bg-gray-300 p-3 rounded">4 cols</div>
  <div class="col-span-4 bg-gray-300 p-3 rounded">4 cols</div>
  <div class="col-span-4 bg-gray-300 p-3 rounded">4 cols</div>
  <div class="col-span-3 bg-gray-400 p-3 rounded">3</div>
  <div class="col-span-3 bg-gray-400 p-3 rounded">3</div>
  <div class="col-span-3 bg-gray-400 p-3 rounded">3</div>
  <div class="col-span-3 bg-gray-400 p-3 rounded">3</div>
</div>

## Spacing System

The design system uses an 8-point grid for consistent spacing:

<div class="flex gap-2 items-end">
  <div class="bg-primary-100 p-1" style="height: 8px; width: 40px;"></div>
  <div class="bg-primary-200 p-2" style="height: 16px; width: 40px;"></div>
  <div class="bg-primary-300 p-3" style="height: 24px; width: 40px;"></div>
  <div class="bg-primary-400 p-4" style="height: 32px; width: 40px;"></div>
  <div class="bg-primary-500 p-5" style="height: 40px; width: 40px;"></div>
  <div class="bg-primary-600 p-6" style="height: 48px; width: 40px;"></div>
  <div class="bg-primary-700 p-8" style="height: 64px; width: 40px;"></div>
</div>

## Loading States

<div class="spinner mb-4"></div>

<div class="skeleton skeleton-title mb-4"></div>
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-text" style="width: 60%;"></div>

## Utility Classes

### Text Utilities
<p class="text-xs">Extra small text</p>
<p class="text-sm">Small text</p>
<p class="text-base">Base text size</p>
<p class="text-lg">Large text</p>
<p class="text-xl">Extra large text</p>
<p class="text-2xl">2X large text</p>

### Border Radius
<div class="flex gap-2">
  <div class="bg-gray-300 p-4 rounded-none">None</div>
  <div class="bg-gray-300 p-4 rounded-sm">Small</div>
  <div class="bg-gray-300 p-4 rounded">Base</div>
  <div class="bg-gray-300 p-4 rounded-lg">Large</div>
  <div class="bg-gray-300 p-4 rounded-full">Full</div>
</div>

## Responsive Design

The design system is mobile-first with responsive utilities:

<div class="grid grid-1 sm:grid-2 md:grid-3 lg:grid-4 gap-4">
  <div class="card p-4">
    <p class="text-sm">Responsive grid item</p>
  </div>
  <div class="card p-4">
    <p class="text-sm">Adapts to screen size</p>
  </div>
  <div class="card p-4">
    <p class="text-sm">Mobile-first approach</p>
  </div>
  <div class="card p-4">
    <p class="text-sm">Fluid layouts</p>
  </div>
</div>

---

!!! note "Design System Documentation"
    For complete design system documentation, see the [Design System Overview](../design/01-design-system-overview.md).