---
type: pattern
category: visual-assets
title: Rendering_Instructions
description: 'TODO: Add description'
---

# Visual Asset Rendering Instructions

## Prerequisites

### Install Mermaid CLI
```bash
# Using npm
npm install -g @mermaid-js/mermaid-cli

# Using yarn
yarn global add @mermaid-js/mermaid-cli

# Verify installation
mmdc --version
```

### Install Image Processing Tools
```bash
# On Ubuntu/Debian
sudo apt-get install inkscape imagemagick optipng

# On macOS
brew install inkscape imagemagick optipng

# On Windows (using Chocolatey)
choco install inkscape imagemagick optipng
```

## Rendering Commands

### 1. Convert Mermaid to SVG
```bash
# Basic conversion
mmdc -i circuit-breaker/state-machine.mmd -o circuit-breaker/state-machine.svg

# With custom theme
mmdc -i circuit-breaker/state-machine.mmd -o circuit-breaker/state-machine.svg -t dark

# With transparent background
mmdc -i circuit-breaker/state-machine.mmd -o circuit-breaker/state-machine.svg -b transparent

# High quality with custom config
mmdc -i circuit-breaker/state-machine.mmd -o circuit-breaker/state-machine.svg -c mermaid-config.json
```

### 2. Convert SVG to PNG
```bash
# Using Inkscape (recommended for quality)
inkscape circuit-breaker/state-machine.svg --export-png=circuit-breaker/state-machine.png --export-dpi=300

# Using ImageMagick
convert -density 300 -background transparent circuit-breaker/state-machine.svg circuit-breaker/state-machine.png
```

### 3. Optimize Files
```bash
# Optimize SVG
svgo circuit-breaker/state-machine.svg -o circuit-breaker/state-machine.min.svg

# Optimize PNG
optipng -o7 circuit-breaker/state-machine.png
```

## Batch Processing Scripts

### Render All Diagrams
```bash
#!/bin/bash
# render-all.sh

# Find all .mmd files and convert to SVG
find . -name "*.mmd" -type f | while read file; do
    output="${file%.mmd}.svg"
    echo "Converting $file to $output"
    mmdc -i "$file" -o "$output" -b transparent
done

# Convert all SVGs to PNGs
find . -name "*.svg" -type f | while read file; do
    output="${file%.svg}.png"
    echo "Converting $file to $output"
    inkscape "$file" --export-png="$output" --export-dpi=300
done

# Optimize all files
find . -name "*.svg" -type f -exec svgo {} \;
find . -name "*.png" -type f -exec optipng -o7 {} \;
```

### Make script executable
```bash
chmod +x render-all.sh
./render-all.sh
```

## Mermaid Configuration File

Create `mermaid-config.json`:
```json
{
  "theme": "base",
  "themeVariables": {
    "primaryColor": "#5448C8",
    "primaryTextColor": "#fff",
    "primaryBorderColor": "#3f33a6",
    "lineColor": "#64748b",
    "secondaryColor": "#00BCD4",
    "tertiaryColor": "#81c784",
    "background": "#f8fafc",
    "mainBkg": "#ffffff",
    "secondBkg": "#f1f5f9",
    "fontSize": "16px"
  },
  "flowchart": {
    "htmlLabels": true,
    "curve": "basis"
  },
  "sequence": {
    "diagramMarginX": 50,
    "diagramMarginY": 10,
    "actorMargin": 50,
    "width": 150,
    "height": 65,
    "boxMargin": 10,
    "boxTextMargin": 5,
    "noteMargin": 10,
    "messageMargin": 35
  }
}
```

## Integration with Documentation

### Embedding in Markdown
```markdown
<!-- Direct SVG embed -->
![Circuit Breaker State Machine](./visual-assets/circuit-breaker/state-machine.svg/index.md)

<!-- With fallback to PNG -->
<picture>
  <source srcset="./visual-assets/circuit-breaker/state-machine.svg" type="image/svg+xml">
  <img src="./visual-assets/circuit-breaker/state-machine.png" alt="Circuit Breaker State Machine">
</picture>
```

### Responsive Images
```html
<div class="diagram-container">
  <img src="./visual-assets/circuit-breaker/state-machine.svg" 
       alt="Circuit Breaker State Machine"
       style="max-width: 100%; height: auto;">
</div>
```

## Quality Checklist

- [ ] All text is readable at mobile resolutions
- [ ] Colors follow the defined palette
- [ ] Diagrams have consistent styling
- [ ] File sizes are optimized (<500KB for PNG, <100KB for SVG)
- [ ] Alt text is descriptive for accessibility
- [ ] Both light and dark mode versions exist (if needed)

## Troubleshooting

### Common Issues

1. **Text cut off in SVG**
   - Increase diagram margins in config
   - Use shorter labels or line breaks

2. **PNG quality issues**
   - Increase DPI to 300 or higher
   - Use Inkscape instead of ImageMagick

3. **Large file sizes**
   - Run optimization tools
   - Reduce complexity of diagrams
   - Use SVG instead of PNG where possible

4. **Rendering errors**
   - Check Mermaid syntax
   - Update mermaid-cli to latest version
   - Verify all dependencies are installed