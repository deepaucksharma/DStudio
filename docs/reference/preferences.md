# User Preferences

The Distributed Systems Compendium provides a comprehensive preferences system to customize your reading experience.

## Accessing Preferences

You can access preferences in two ways:

1. **Preferences Button**: Click the ⚙️ button in the bottom-right corner
2. **Keyboard Shortcut**: Press `Ctrl+,` (or `Cmd+,` on Mac)

## Available Preferences

### Appearance

#### Theme
Choose between automatic (follows system), light, or dark themes.

- **Auto**: Automatically switches based on your system preferences
- **Light**: Always use light theme
- **Dark**: Always use dark theme

#### Font Size
Adjust the base font size for better readability.

- **Small**: 14px base size
- **Medium**: 16px base size (default)
- **Large**: 18px base size
- **Extra Large**: 20px base size

#### Code Theme
Select your preferred syntax highlighting theme for code blocks.

- **Material**: Material Design inspired (default)
- **Monokai**: Popular dark theme
- **GitHub**: Clean, light theme
- **Dracula**: High contrast dark theme
- **Solarized**: Reduced eye strain theme

#### Content Density
Control spacing and padding throughout the site.

- **Compact**: Minimal spacing for more content
- **Comfortable**: Balanced spacing (default)
- **Spacious**: Extra breathing room

### Behavior

#### Enable Animations
Toggle all animations and transitions on/off.

#### Smooth Scrolling
Enable or disable smooth scrolling behavior.

#### Show Tooltips
Control whether helpful tooltips appear on hover.

#### Autoplay Videos
Automatically play embedded videos when they come into view.

#### Sound Effects
Enable UI sound effects (when available).

### Reading

#### Show Reading Progress
Display a progress bar showing how far you've read.

#### Show Line Numbers
Toggle line numbers in code blocks.

#### Expand Sidebar by Default
Keep the navigation sidebar expanded on page load.

#### Enable Keyboard Shortcuts
Turn keyboard shortcuts on/off.

### Accessibility

#### Reduce Motion
Minimize animations for users sensitive to motion.

!!! note "System Integration"
    The reduce motion preference automatically syncs with your system's "prefers-reduced-motion" setting.

## Import/Export Preferences

### Export
Save your preferences to a JSON file:

1. Open preferences panel
2. Click "Export" button
3. Save the `ds-preferences.json` file

### Import
Load preferences from a saved file:

1. Open preferences panel
2. Click "Import" button
3. Select your `ds-preferences.json` file

### Reset
Reset all preferences to defaults:

1. Open preferences panel
2. Click "Reset All" button
3. Confirm the action

## Keyboard Shortcuts

When keyboard shortcuts are enabled:

| Shortcut | Action |
|----------|--------|
| `Ctrl+,` | Open preferences |
| `Ctrl+Shift+T` | Toggle theme |
| `/` | Focus search |
| `Esc` | Close panels |

## Storage

Preferences are stored locally in your browser using `localStorage`. They persist across sessions but are specific to each browser/device.

## Advanced Usage

### Programmatic Access

For developers, preferences can be accessed via JavaScript:

```javascript
// Get a preference
const theme = DSApp.modules.get('preferences').get('theme');

// Set a preference
DSApp.modules.get('preferences').set('fontSize', 'large');

// Listen for changes
DSApp.on('preference:changed', (e) => {
  console.log(`${e.detail.key} changed to ${e.detail.value}`);
});
```

### URL Parameters

You can temporarily override preferences via URL parameters:

- `?theme=dark` - Force dark theme
- `?fontSize=large` - Set font size
- `?animations=false` - Disable animations

Example: `https://site.com/page/?theme=dark&fontSize=large`

## Troubleshooting

### Preferences Not Saving

If preferences aren't persisting:

1. Check if cookies/localStorage are enabled
2. Ensure you're not in private/incognito mode
3. Try clearing browser cache
4. Check browser console for errors

### Reset Individual Preference

To reset a single preference to default, use the browser console:

```javascript
DSApp.modules.get('preferences').reset('theme');
```

### Export All Settings

To see all current settings:

```javascript
console.log(DSApp.modules.get('preferences').preferences);
```