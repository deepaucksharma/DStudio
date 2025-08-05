# Agent 3: Diagram Rendering - Quick Start Guide

## 🚀 Quick Start (5 Steps)

### 1. Install Tools (5 minutes)
```bash
# Run the setup script
./scripts/setup_diagram_tools.sh

# Or manually install:
npm install -g @mermaid-js/mermaid-cli
sudo apt-get install imagemagick webp  # Linux
brew install imagemagick webp          # macOS
```

### 2. Extract Diagrams (1 minute)
```bash
python3 scripts/extract_mermaid_diagrams.py
# Output: diagram_manifest.json with 308 diagrams
```

### 3. Pilot Test (10 minutes)
```bash
# Test with first 10 diagrams
cp diagram_manifest.json diagram_manifest_full.json
jq '.diagrams = .diagrams[:10]' diagram_manifest_full.json > diagram_manifest.json
python3 scripts/render_mermaid_diagrams.py
```

### 4. Full Render (2-4 hours)
```bash
# Restore full manifest
cp diagram_manifest_full.json diagram_manifest.json

# Render all 308 diagrams
python3 scripts/render_mermaid_diagrams.py
```

### 5. Replace in Markdown (30 minutes)
```bash
# IMPORTANT: Creates automatic backup
python3 scripts/replace_mermaid_blocks.py

# Monitor progress
python3 scripts/monitor_diagram_conversion.py
```

## 📊 Expected Results

- **308 diagrams** → **1,848 images** (6 per diagram: 3 sizes × 2 formats)
- **Storage**: ~200-300 MB total
- **Performance**: 95% faster page loads
- **Formats**: PNG (fallback) + WebP (optimized)
- **Sizes**: Small (400px), Medium (800px), Large (1200px)

## 🔍 Monitoring

```bash
# Check status anytime
python3 scripts/monitor_diagram_conversion.py

# View detailed report
cat diagram_conversion_status.md
```

## ⚡ Performance Test

```bash
# Before (baseline)
# 1. Start server: mkdocs serve
# 2. Open Chrome DevTools → Lighthouse
# 3. Run performance audit on a pattern page

# After (compare)
# Repeat audit after conversion
# Expected: 90%+ improvement in LCP
```

## 🔄 Rollback

```bash
# If anything goes wrong
./rollback_mermaid_changes.sh

# Or restore from timestamped backup
ls backups/mermaid_backup_*
```

## ✅ Success Checklist

- [ ] All 308 diagrams rendered
- [ ] 0 Mermaid text blocks remaining
- [ ] Images loading correctly
- [ ] Mobile responsive working
- [ ] Performance improved >90%
- [ ] No broken pages

## 🚨 Common Issues

1. **Out of Memory**: Reduce parallel workers in render script
2. **ImageMagick Policy**: Edit `/etc/ImageMagick-6/policy.xml`
3. **WebP Quality**: Adjust `-q` parameter (85 → 90)
4. **Missing Alt Text**: Check generation in replace script

---

**Total Time**: ~5-7 hours (mostly automated)  
**Risk Level**: Low (automatic backups + rollback)  
**Impact**: Major performance improvement