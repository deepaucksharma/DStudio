# Color System & Design Tokens

## Color Philosophy

### Principles
1. **Minimal Palette**: Fewer colors = stronger brand identity
2. **Functional Over Decorative**: Every color has a job
3. **Visual Hierarchy**: Colors create clear information structure
4. **Semantic Naming**: Colors describe purpose, not appearance
5. **Systematic Variations**: Predictable tint/shade progression

## Core Palette

### Neutral Scale
Our foundation built on true grays for maximum flexibility:

```css
/* True Gray Scale - No color cast */
--gray-50:   #FAFAFA;  /* Background subtle */
--gray-100:  #F5F5F5;  /* Background elevated */
--gray-200:  #EEEEEE;  /* Border light */
--gray-300:  #E0E0E0;  /* Border default */
--gray-400:  #BDBDBD;  /* Text disabled */
--gray-500:  #9E9E9E;  /* Text tertiary */
--gray-600:  #757575;  /* Text secondary */
--gray-700:  #616161;  /* Text secondary emphasis */
--gray-800:  #424242;  /* Text primary dark */
--gray-900:  #212121;  /* Text primary */
--gray-950:  #121212;  /* Background dark mode */
```

#### Usage Guidelines
- **50-200**: Backgrounds and subtle borders
- **300-400**: Borders and disabled states
- **500-600**: Secondary text and icons
- **700-900**: Primary text and emphasis
- **950**: True black for dark mode base

### Primary Scale
Refined Indigo for brand identity and key actions:

```css
/* Indigo - Conveys trust and intelligence */
--primary-50:   #E8EAF6;  /* Backgrounds */
--primary-100:  #C5CAE9;  /* Hover backgrounds */
--primary-200:  #9FA8DA;  /* Selected backgrounds */
--primary-300:  #7986CB;  /* Subtle borders */
--primary-400:  #5C6BC0;  /* Hover states */
--primary-500:  #3F51B5;  /* Default brand */
--primary-600:  #3949AB;  /* Emphasis */
--primary-700:  #303F9F;  /* Active states */
--primary-800:  #283593;  /* High emphasis */
--primary-900:  #1A237E;  /* Maximum emphasis */
```

#### Application Rules
- **Primary Action**: 500-600 for buttons
- **Hover States**: Darken by 100 points
- **Focus Rings**: 500 with transparency
- **Backgrounds**: 50-100 for subtle emphasis
- **Text Links**: 600 on light, 400 on dark

### Semantic Colors

#### Success States
```css
--success-50:   #E8F5E9;
--success-100:  #C8E6C9;
--success-200:  #A5D6A7;
--success-300:  #81C784;
--success-400:  #66BB6A;
--success-500:  #4CAF50;  /* Primary success */
--success-600:  #43A047;
--success-700:  #388E3C;
--success-800:  #2E7D32;
--success-900:  #1B5E20;
```

#### Warning States
```css
--warning-50:   #FFF3E0;
--warning-100:  #FFE0B2;
--warning-200:  #FFCC80;
--warning-300:  #FFB74D;
--warning-400:  #FFA726;
--warning-500:  #FF9800;  /* Primary warning */
--warning-600:  #FB8C00;
--warning-700:  #F57C00;
--warning-800:  #EF6C00;
--warning-900:  #E65100;
```

#### Error States
```css
--error-50:   #FFEBEE;
--error-100:  #FFCDD2;
--error-200:  #EF9A9A;
--error-300:  #E57373;
--error-400:  #EF5350;
--error-500:  #F44336;  /* Primary error */
--error-600:  #E53935;
--error-700:  #D32F2F;
--error-800:  #C62828;
--error-900:  #B71C1C;
```

#### Information States
```css
--info-50:   #E3F2FD;
--info-100:  #BBDEFB;
--info-200:  #90CAF9;
--info-300:  #64B5F6;
--info-400:  #42A5F5;
--info-500:  #2196F3;  /* Primary info */
--info-600:  #1E88E5;
--info-700:  #1976D2;
--info-800:  #1565C0;
--info-900:  #0D47A1;
```

## Functional Tokens

### Surface Colors
```css
/* Light Mode */
--surface-ground:     var(--gray-50);   /* Page background */
--surface-primary:    #FFFFFF;          /* Card/component background */
--surface-secondary:  var(--gray-50);   /* Alternate sections */
--surface-tertiary:   var(--gray-100);  /* Nested components */
--surface-overlay:    rgba(0,0,0,0.04); /* Hover overlays */
--surface-scrim:      rgba(0,0,0,0.32); /* Modal backdrops */

/* Dark Mode */
[data-theme="dark"] {
  --surface-ground:     var(--gray-950);
  --surface-primary:    var(--gray-900);
  --surface-secondary:  var(--gray-800);
  --surface-tertiary:   var(--gray-700);
  --surface-overlay:    rgba(255,255,255,0.08);
  --surface-scrim:      rgba(0,0,0,0.75);
}
```

### Text Colors
```css
/* Light Mode */
--text-primary:       var(--gray-900);    /* Body text */
--text-secondary:     var(--gray-700);    /* Supporting text */
--text-tertiary:      var(--gray-600);    /* Captions/labels */
--text-disabled:      var(--gray-400);    /* Inactive text */
--text-inverse:       #FFFFFF;            /* On dark backgrounds */
--text-link:          var(--primary-600); /* Hyperlinks */
--text-link-hover:    var(--primary-700); /* Hyperlink hover */

/* Dark Mode */
[data-theme="dark"] {
  --text-primary:       var(--gray-50);
  --text-secondary:     var(--gray-300);
  --text-tertiary:      var(--gray-400);
  --text-disabled:      var(--gray-600);
  --text-inverse:       var(--gray-900);
  --text-link:          var(--primary-400);
  --text-link-hover:    var(--primary-300);
}
```

### Border Colors
```css
/* Light Mode */
--border-subtle:      var(--gray-200);    /* Minimal separation */
--border-default:     var(--gray-300);    /* Standard borders */
--border-strong:      var(--gray-400);    /* Emphasized borders */
--border-inverse:     var(--gray-800);    /* On dark surfaces */

/* Dark Mode */
[data-theme="dark"] {
  --border-subtle:      var(--gray-700);
  --border-default:     var(--gray-600);
  --border-strong:      var(--gray-500);
  --border-inverse:     var(--gray-200);
}
```

### State Colors
```css
/* Interactive States */
--state-hover:        var(--surface-overlay);
--state-active:       var(--primary-100);
--state-selected:     var(--primary-50);
--state-focus:        var(--primary-500);
--state-disabled:     var(--gray-200);

/* Feedback States */
--state-success:      var(--success-500);
--state-warning:      var(--warning-500);
--state-error:        var(--error-500);
--state-info:         var(--info-500);
```

## Color Application Patterns

### Component Coloring
```css
/* Button Example */
.btn-primary {
  background: var(--primary-600);
  color: var(--text-inverse);
  border: 1px solid var(--primary-600);
}

.btn-primary:hover {
  background: var(--primary-700);
  border-color: var(--primary-700);
}

.btn-primary:active {
  background: var(--primary-800);
  border-color: var(--primary-800);
}

.btn-primary:focus {
  box-shadow: 0 0 0 3px rgba(var(--primary-500-rgb), 0.25);
}
```

### Semantic Alerts
```css
/* Success Alert */
.alert-success {
  background: var(--success-50);
  border-left: 4px solid var(--success-500);
  color: var(--success-900);
}

.alert-success-icon {
  color: var(--success-600);
}
```

### Data Visualization
```css
/* Chart Colors - Distinct visual separation */
--chart-1: #3F51B5;  /* Primary indigo */
--chart-2: #FF9800;  /* Orange */
--chart-3: #4CAF50;  /* Green */
--chart-4: #00BCD4;  /* Cyan */
--chart-5: #9C27B0;  /* Purple */
--chart-6: #F44336;  /* Red */
--chart-7: #795548;  /* Brown */
--chart-8: #607D8B;  /* Blue Gray */
```

## Implementation Details

### CSS Custom Properties
```css
/* RGB Values for transparency */
:root {
  --primary-500-rgb: 63, 81, 181;
  --success-500-rgb: 76, 175, 80;
  --warning-500-rgb: 255, 152, 0;
  --error-500-rgb: 244, 67, 54;
}

/* Usage */
.overlay {
  background: rgba(var(--primary-500-rgb), 0.1);
}
```

### Sass Implementation
```scss
// _colors.scss
$gray-50: #FAFAFA;
$gray-100: #F5F5F5;
// ... etc

// Functions
@function tint($color, $percentage) {
  @return mix(white, $color, $percentage);
}

@function shade($color, $percentage) {
  @return mix(black, $color, $percentage);
}
```

### JavaScript Tokens
```javascript
// tokens/colors.js
export const colors = {
  gray: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    // ...
  },
  primary: {
    50: '#E8EAF6',
    100: '#C5CAE9',
    // ...
  }
};

// Usage
import { colors } from '@/tokens/colors';
const primaryButton = colors.primary[600];
```

### Design Token JSON
```json
{
  "color": {
    "gray": {
      "50": {
        "value": "#FAFAFA",
        "type": "color",
        "description": "Lightest gray for subtle backgrounds"
      }
    }
  }
}
```

## Migration Strategy

### Phase 1: Audit Current Colors
```bash
# Find all color declarations
grep -r "color:" --include="*.css" --include="*.scss"
grep -r "#[0-9a-fA-F]\{3,6\}" --include="*.css"
```

### Phase 2: Create Mapping
```css
/* Old → New Mapping */
#5448C8 → var(--primary-600)
#F5F5F5 → var(--gray-100)
#333333 → var(--gray-900)
```

### Phase 3: Progressive Replacement
1. Add new tokens alongside old values
2. Test thoroughly
3. Remove old values
4. Update documentation

## Color Usage Guidelines

### Do's
- Use semantic tokens over raw values
- Test color combinations for contrast
- Consider context (light/dark mode)
- Limit color choices to system palette
- Document any exceptions

### Don'ts
- Create one-off colors
- Use color as sole differentiator
- Override system colors locally
- Ignore brand guidelines
- Mix color systems

## Testing & Validation

### Automated Testing
```javascript
// color-contrast.test.js
describe('Color Contrast', () => {
  test('Primary text on white', () => {
    const ratio = getContrastRatio('#212121', '#FFFFFF');
    expect(ratio).toBeGreaterThan(7);
  });
});
```

### Manual Testing
1. Browser DevTools contrast checker
2. Stark (Figma plugin)
3. Colorblinding Chrome extension
4. Real device testing

## Future Considerations

### P3 Color Space
```css
/* Future-proofing for wider gamut */
@supports (color: color(display-p3 1 1 1)) {
  --primary-500-p3: color(display-p3 0.247 0.318 0.710);
}
```

### Dynamic Color
- User preference adaptation
- Ambient light response
- Cultural color considerations
- Seasonal variations

### AI-Driven Optimization
- Automatic contrast adjustment
- Personalized color schemes
- A/B testing integration
- Performance monitoring

## Lessons Learned from Implementation

### Real-World Color Challenges

#### 1. Dark Mode Complexity
Our testing revealed that simple color inversion doesn't work:
- **Background colors**: Need careful adjustment, not just inversion
- **Shadow effects**: Must be rethought for dark surfaces
- **Contrast ratios**: Different requirements for dark vs light
- **Brand colors**: May need adjustment for dark backgrounds

#### 2. Gradient Considerations
```css
/* Light mode gradient */
.hero {
  background: linear-gradient(135deg, #5448C8 0%, #00BCD4 100%);
}

/* Dark mode needs adjusted colors */
[data-md-color-scheme="slate"] .hero {
  background: linear-gradient(135deg, #6B5ED6 0%, #00D9F5 100%);
}
```

#### 3. Transparency Best Practices
```css
/* Use RGB values for flexible transparency */
:root {
  --primary-rgb: 84, 72, 200;
  --success-rgb: 16, 185, 129;
}

/* Apply with rgba() */
.box {
  background: rgba(var(--primary-rgb), 0.05);
}
```

#### 4. Component-Specific Colors
Different components need different color treatments:
- **Admonitions**: Light tints with strong borders
- **Code blocks**: Dark backgrounds even in light mode
- **Tables**: Alternating row colors for readability
- **Buttons**: Clear hover and active states

### Practical Implementation Tips

#### 1. CSS Custom Properties Organization
```css
:root {
  /* Base colors first */
  --gray-50: #FAFAFA;
  
  /* Semantic mappings */
  --text-primary: var(--gray-900);
  
  /* Component-specific */
  --button-primary-bg: var(--primary-600);
}
```

#### 2. Color Testing Checklist
- [ ] WCAG AAA contrast for body text
- [ ] WCAG AA for large text and UI components
- [ ] Dark mode contrast validation
- [ ] Color blind simulation testing
- [ ] Print stylesheet considerations

#### 3. Performance Optimizations
- Avoid excessive CSS custom property lookups
- Group color changes in media queries
- Use native CSS color functions when possible

### Common Pitfalls Avoided

1. **Over-reliance on transparency**: Can cause readability issues
2. **Insufficient dark mode testing**: Many edge cases discovered
3. **Ignoring hover states**: Critical for user feedback
4. **Hard-coded colors**: Always use tokens

### Recommended Color Combinations

#### High Contrast Pairs
```css
/* Text on backgrounds */
--high-contrast-pairs: {
  /* Light mode */
  text: var(--gray-900);
  background: var(--gray-50);
  
  /* Dark mode */
  text: var(--gray-50);
  background: var(--gray-900);
}
```

#### Semantic Color Usage
```css
/* Status indicators */
.status-success { color: var(--success-700); }
.status-warning { color: var(--warning-700); }
.status-error { color: var(--error-700); }

/* Backgrounds */
.bg-success { background: var(--success-50); }
.bg-warning { background: var(--warning-50); }
.bg-error { background: var(--error-50); }
```