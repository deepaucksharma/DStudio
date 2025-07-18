# Component Library

## Component Philosophy

### Design Principles
1. **Single Responsibility**: Each component does one thing well
2. **Composition Over Configuration**: Build complex UIs from simple parts
3. **Consistent API**: Similar components behave similarly
4. **Visual Cohesion**: All components feel part of the same system
5. **Performance By Default**: Optimized rendering and minimal DOM

## Component Architecture

### Component Hierarchy
```
Atoms → Molecules → Organisms → Templates → Pages
```

- **Atoms**: Basic building blocks (buttons, inputs, labels)
- **Molecules**: Simple groups of atoms (form fields, cards)
- **Organisms**: Complex components (navigation, data tables)
- **Templates**: Page-level patterns
- **Pages**: Specific implementations

### Component Structure
```tsx
// Standard component anatomy
interface ComponentProps {
  // Required props
  id: string;
  
  // Optional props
  className?: string;
  style?: CSSProperties;
  
  // Event handlers
  onClick?: (event: MouseEvent) => void;
  
  // Content
  children?: ReactNode;
  
  // State
  disabled?: boolean;
  loading?: boolean;
}
```

## Core Components

### Buttons

#### Button Variants
```css
/* Primary Button - Main CTA */
.btn-primary {
  background: var(--primary-600);
  color: var(--text-inverse);
  border: 1px solid var(--primary-600);
  padding: var(--space-2) var(--space-4);
  font-weight: var(--font-medium);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--primary-700);
  border-color: var(--primary-700);
  transform: translateY(-1px);
}

.btn-primary:active {
  background: var(--primary-800);
  transform: translateY(0);
}

/* Secondary Button - Default */
.btn-secondary {
  background: var(--surface-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover {
  background: var(--surface-secondary);
  border-color: var(--border-strong);
}

/* Ghost Button - Minimal */
.btn-ghost {
  background: transparent;
  color: var(--primary-600);
  border: 1px solid transparent;
}

.btn-ghost:hover {
  background: var(--surface-overlay);
  border-color: var(--border-subtle);
}

/* Danger Button - Destructive */
.btn-danger {
  background: var(--error-600);
  color: var(--text-inverse);
  border: 1px solid var(--error-600);
}

.btn-danger:hover {
  background: var(--error-700);
  border-color: var(--error-700);
}
```

#### Button Sizes
```css
.btn-xs {
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
}

.btn-sm {
  padding: calc(var(--space-1) * 1.5) var(--space-3);
  font-size: var(--text-sm);
}

.btn-md { /* Default */
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-lg);
}

.btn-xl {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-xl);
}
```

#### Button States
```css
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.btn-loading {
  position: relative;
  color: transparent;
}

.btn-loading::after {
  content: "";
  position: absolute;
  width: 16px;
  height: 16px;
  top: 50%;
  left: 50%;
  margin-left: -8px;
  margin-top: -8px;
  border: 2px solid var(--primary-600);
  border-radius: 50%;
  border-top-color: transparent;
  animation: spinner 0.6s linear infinite;
}

@keyframes spinner {
  to { transform: rotate(360deg); }
}
```

#### Button Groups
```css
.btn-group {
  display: flex;
  gap: -1px;
}

.btn-group .btn {
  border-radius: 0;
}

.btn-group .btn:first-child {
  border-radius: 4px 0 0 4px;
}

.btn-group .btn:last-child {
  border-radius: 0 4px 4px 0;
}

.btn-group .btn:not(:last-child) {
  border-right: 0;
}
```

### Form Elements

#### Input Fields
```css
/* Base Input */
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  transition: all 0.2s ease;
}

.input:hover {
  border-color: var(--border-strong);
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(var(--primary-500-rgb), 0.1);
}

/* Input Variants */
.input-error {
  border-color: var(--error-500);
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(var(--error-500-rgb), 0.1);
}

.input-success {
  border-color: var(--success-500);
}

.input-success:focus {
  box-shadow: 0 0 0 3px rgba(var(--success-500-rgb), 0.1);
}
```

#### Select Dropdown
```css
.select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath d='M7 10l5 5 5-5z' fill='%23616161'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--space-2) center;
  background-size: 20px;
  padding-right: var(--space-10);
}

/* Custom Select */
.custom-select {
  position: relative;
}

.custom-select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  cursor: pointer;
}

.custom-select-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  z-index: 10;
}

.custom-select-option {
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  transition: background 0.1s ease;
}

.custom-select-option:hover {
  background: var(--surface-secondary);
}

.custom-select-option.selected {
  background: var(--primary-50);
  color: var(--primary-700);
}
```

#### Checkbox & Radio
```css
/* Custom Checkbox */
.checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-input {
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-strong);
  border-radius: 4px;
  margin-right: var(--space-2);
  position: relative;
  transition: all 0.2s ease;
}

.checkbox-input:checked {
  background: var(--primary-600);
  border-color: var(--primary-600);
}

.checkbox-input:checked::after {
  content: "";
  position: absolute;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* Custom Radio */
.radio-input {
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-strong);
  border-radius: 50%;
  margin-right: var(--space-2);
  position: relative;
  transition: all 0.2s ease;
}

.radio-input:checked {
  border-color: var(--primary-600);
}

.radio-input:checked::after {
  content: "";
  position: absolute;
  left: 4px;
  top: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-600);
}
```

#### Toggle Switch
```css
.toggle {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.toggle-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--gray-400);
  border-radius: 24px;
  transition: all 0.3s ease;
}

.toggle-slider::before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.toggle-input:checked + .toggle-slider {
  background: var(--primary-600);
}

.toggle-input:checked + .toggle-slider::before {
  transform: translateX(24px);
}
```

### Cards

#### Basic Card
```css
.card {
  background: var(--surface-primary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.card-body {
  padding: var(--space-4);
}

.card-footer {
  padding: var(--space-3) var(--space-4);
  background: var(--surface-secondary);
  border-top: 1px solid var(--border-light);
}
```

#### Interactive Card
```css
.card-interactive {
  cursor: pointer;
  transition: all 0.2s ease;
}

.card-interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-interactive:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}
```

#### Card Variants
```css
/* Elevated Card */
.card-elevated {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: none;
}

/* Outlined Card */
.card-outlined {
  box-shadow: none;
  border: 2px solid var(--border-default);
}

/* Filled Card */
.card-filled {
  background: var(--surface-secondary);
  border: none;
}

/* Gradient Card */
.card-gradient {
  background: linear-gradient(135deg, var(--primary-50), var(--primary-100));
  border: none;
}
```

### Navigation

#### Navbar
```css
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 var(--space-4);
  background: var(--surface-primary);
  border-bottom: 1px solid var(--border-light);
}

.navbar-brand {
  display: flex;
  align-items: center;
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  text-decoration: none;
}

.navbar-nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.navbar-link {
  padding: var(--space-2) var(--space-3);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.navbar-link:hover {
  color: var(--text-primary);
  background: var(--surface-overlay);
}

.navbar-link.active {
  color: var(--primary-600);
  background: var(--primary-50);
}
```

#### Sidebar
```css
.sidebar {
  width: 280px;
  height: 100%;
  background: var(--surface-secondary);
  border-right: 1px solid var(--border-light);
  overflow-y: auto;
}

.sidebar-section {
  padding: var(--space-2);
}

.sidebar-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--text-tertiary);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-1);
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.sidebar-link:hover {
  color: var(--text-primary);
  background: var(--surface-overlay);
}

.sidebar-link.active {
  color: var(--primary-600);
  background: var(--primary-50);
  font-weight: var(--font-medium);
}

.sidebar-link.active::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-600);
  border-radius: 0 2px 2px 0;
}
```

#### Tabs
```css
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-light);
}

.tab {
  padding: var(--space-3) var(--space-4);
  color: var(--text-secondary);
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
}

.tab:hover {
  color: var(--text-primary);
  background: var(--surface-overlay);
}

.tab.active {
  color: var(--primary-600);
  border-bottom-color: var(--primary-600);
  font-weight: var(--font-medium);
}

.tab-content {
  padding: var(--space-4);
}
```

### Alerts & Notifications

#### Alert Component
```css
.alert {
  padding: var(--space-3) var(--space-4);
  border-radius: 4px;
  border-left: 4px solid;
  margin-bottom: var(--space-4);
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

/* Alert variants */
.alert-info {
  background: rgba(var(--info-500-rgb), 0.1);
  border-left-color: var(--info-500);
  color: var(--info-700);
}

.alert-success {
  background: rgba(var(--success-500-rgb), 0.1);
  border-left-color: var(--success-500);
  color: var(--success-700);
}

.alert-warning {
  background: rgba(var(--warning-500-rgb), 0.1);
  border-left-color: var(--warning-500);
  color: var(--warning-700);
}

.alert-error {
  background: rgba(var(--error-500-rgb), 0.1);
  border-left-color: var(--error-500);
  color: var(--error-700);
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-1);
}

.alert-dismiss {
  flex-shrink: 0;
  padding: var(--space-1);
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.alert-dismiss:hover {
  opacity: 1;
}
```

#### Toast Notifications
```css
.toast-container {
  position: fixed;
  bottom: var(--space-4);
  right: var(--space-4);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.toast {
  background: var(--gray-900);
  color: var(--text-inverse);
  padding: var(--space-3) var(--space-4);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 500px;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast.toast-exit {
  animation: slideOut 0.3s ease forwards;
}

@keyframes slideOut {
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}
```

### Modals & Dialogs

#### Modal Component
```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--surface-scrim);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: var(--surface-primary);
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: scaleIn 0.2s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.modal-body {
  padding: var(--space-4);
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}

/* Modal sizes */
.modal-sm { width: 400px; }
.modal-md { width: 600px; }
.modal-lg { width: 800px; }
.modal-xl { width: 1000px; }
.modal-full { width: calc(100vw - var(--space-8)); height: calc(100vh - var(--space-8)); }
```

### Data Display

#### Tables
```css
.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  text-align: left;
  font-weight: var(--font-semibold);
  padding: var(--space-3);
  background: var(--surface-secondary);
  border-bottom: 2px solid var(--border-default);
  color: var(--text-secondary);
}

.table td {
  padding: var(--space-3);
  border-bottom: 1px solid var(--border-light);
}

.table tbody tr:hover {
  background: var(--surface-overlay);
}

/* Table variants */
.table-striped tbody tr:nth-child(even) {
  background: var(--surface-secondary);
}

.table-bordered {
  border: 1px solid var(--border-light);
}

.table-bordered th,
.table-bordered td {
  border: 1px solid var(--border-light);
}

.table-compact th,
.table-compact td {
  padding: var(--space-2);
}
```

#### Lists
```css
.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-item {
  padding: var(--space-3);
  border-bottom: 1px solid var(--border-light);
  transition: background 0.2s ease;
}

.list-item:hover {
  background: var(--surface-overlay);
}

.list-item:last-child {
  border-bottom: none;
}

/* List with icons */
.list-icon {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.list-icon-element {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: var(--text-tertiary);
}

/* Ordered list */
.list-ordered {
  counter-reset: list-counter;
}

.list-ordered .list-item {
  counter-increment: list-counter;
  position: relative;
  padding-left: var(--space-10);
}

.list-ordered .list-item::before {
  content: counter(list-counter);
  position: absolute;
  left: var(--space-3);
  top: var(--space-3);
  width: 24px;
  height: 24px;
  background: var(--primary-100);
  color: var(--primary-700);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}
```

### Loading States

#### Skeleton Screens
```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--gray-200) 25%,
    var(--gray-100) 50%,
    var(--gray-200) 75%
  );
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes skeleton {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-text {
  height: var(--text-base);
  margin-bottom: var(--space-2);
}

.skeleton-title {
  height: var(--text-2xl);
  margin-bottom: var(--space-4);
  width: 60%;
}

.skeleton-box {
  height: 100px;
  margin-bottom: var(--space-4);
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
}
```

#### Spinners
```css
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--gray-200);
  border-top-color: var(--primary-600);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Spinner sizes */
.spinner-xs { width: 12px; height: 12px; border-width: 1px; }
.spinner-sm { width: 16px; height: 16px; }
.spinner-md { width: 20px; height: 20px; }
.spinner-lg { width: 32px; height: 32px; border-width: 3px; }
.spinner-xl { width: 48px; height: 48px; border-width: 4px; }

/* Spinner colors */
.spinner-primary { border-top-color: var(--primary-600); }
.spinner-success { border-top-color: var(--success-600); }
.spinner-error { border-top-color: var(--error-600); }
.spinner-warning { border-top-color: var(--warning-600); }
```

### Badges & Tags

#### Badges
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: 1;
  border-radius: 12px;
  white-space: nowrap;
}

/* Badge variants */
.badge-primary {
  background: var(--primary-100);
  color: var(--primary-700);
}

.badge-success {
  background: var(--success-100);
  color: var(--success-700);
}

.badge-warning {
  background: var(--warning-100);
  color: var(--warning-700);
}

.badge-error {
  background: var(--error-100);
  color: var(--error-700);
}

.badge-neutral {
  background: var(--gray-200);
  color: var(--gray-700);
}

/* Badge with dot */
.badge-dot {
  padding-left: var(--space-3);
  position: relative;
}

.badge-dot::before {
  content: "";
  position: absolute;
  left: var(--space-1);
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
```

#### Tags
```css
.tag {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  background: var(--surface-secondary);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  font-size: var(--text-sm);
  cursor: default;
  transition: all 0.2s ease;
}

.tag:hover {
  background: var(--surface-tertiary);
  border-color: var(--border-default);
}

.tag-dismissible {
  cursor: pointer;
  padding-right: var(--space-2);
}

.tag-dismiss {
  margin-left: var(--space-1);
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.tag-dismiss:hover {
  opacity: 1;
}
```

## Component Guidelines

### Naming Conventions
```css
/* Component structure */
.component {}
.component-element {}
.component-element-subelement {}
.component--modifier {}
.component.is-state {}

/* Examples */
.card {}
.card-header {}
.card-header-title {}
.card--elevated {}
.card.is-loading {}
```

### State Management
```css
/* States */
.is-active {}
.is-disabled {}
.is-loading {}
.is-selected {}
.is-expanded {}
.is-collapsed {}
.has-error {}
.has-success {}
```

### Composition Patterns
```css
/* Compound components */
.form-group {
  margin-bottom: var(--space-4);
}

.form-group .label {
  margin-bottom: var(--space-1);
}

.form-group .input {
  width: 100%;
}

.form-group .help-text {
  margin-top: var(--space-1);
}

.form-group.has-error .input {
  border-color: var(--error-500);
}

.form-group.has-error .help-text {
  color: var(--error-600);
}
```

## Testing Components

### Visual Regression Tests
- Component screenshots at different states
- Cross-browser rendering checks
- Dark mode appearance
- Responsive behavior

### Component Documentation
Each component should include:
1. Purpose and use cases
2. Props/attributes API
3. Visual examples
4. Code snippets
5. Do's and don'ts