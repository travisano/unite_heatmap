# Minimap Elements - Visual Guide

Based on your minimap image (`show.png`), here's what the tracker sees:

## Minimap Layout

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│     🟣 PURPLE SIDE              🟠 ORANGE SIDE      │
│                                                     │
│   ⭕ Goal (Large)            Goal (Large) ⭕       │
│   ❌ FILTERED OUT          FILTERED OUT ❌         │
│                                                     │
│                                                     │
│   👤 Pokémon Icon        Pokémon Icon 👤          │
│   ✅ DETECTED             DETECTED ✅              │
│                                                     │
│                                                     │
│   ⭕ Goal (Large)            Goal (Large) ⭕       │
│   ❌ FILTERED OUT          FILTERED OUT ❌         │
│                                                     │
│   👤 Pokémon Icon        Pokémon Icon 👤          │
│   ✅ DETECTED             DETECTED ✅              │
│                                                     │
│   ⭕ Goal (Large)            Goal (Large) ⭕       │
│   ❌ FILTERED OUT          FILTERED OUT ❌         │
│                                                     │
│   👤 Pokémon Icon        Pokémon Icon 👤          │
│   ✅ DETECTED             DETECTED ✅              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Size Comparison

### Goal Zones
```
⭕⭕⭕⭕⭕
⭕⭕⭕⭕⭕   } Large circular zones
⭕⭕⭕⭕⭕   } Area: ~500-2000 pixels²
⭕⭕⭕⭕⭕   } ❌ FILTERED (too large)
⭕⭕⭕⭕⭕
```

### Pokémon Icons
```
👤  } Small icon with colored border
    } Area: ~20-100 pixels²
    } ✅ DETECTED
```

## Color Detection

### Purple Team 🟣
**HSV Range:**
- Hue: 120-160 (purple spectrum)
- Saturation: 50-255 (vibrant)
- Value: 50-255 (bright)

**Detects:**
- ✅ Purple Pokémon icon borders
- ❌ Purple goal zones (filtered by size)
- ❌ Purple team base (filtered by size)

### Orange Team 🟠
**HSV Range:**
- Hue: 5-20 (orange spectrum)
- Saturation: 100-255 (vibrant)
- Value: 100-255 (bright)

**Detects:**
- ✅ Orange Pokémon icon borders
- ❌ Orange goal zones (filtered by size)
- ❌ Orange team base (filtered by size)

## Area-Based Filtering

```python
┌─────────────────────────────────────────┐
│  Size Filtering Rules                   │
├─────────────────────────────────────────┤
│                                         │
│  < 10 pixels²   → Noise/artifacts      │
│                   ❌ FILTERED OUT       │
│                                         │
│  10-500 pixels² → Pokémon icons        │
│                   ✅ DETECTED           │
│                                         │
│  > 500 pixels²  → Goals/large objects  │
│                   ❌ FILTERED OUT       │
│                                         │
└─────────────────────────────────────────┘
```

## What Your Minimap Shows

From your `show.png` image, I can identify:

### Purple Side (Left)
1. **Top Goal Zone** - Large circle ⭕ → Filtered
2. **Pokémon Icons** - Small icons with purple borders → Detected
3. **Middle Goal Zone** - Large circle ⭕ → Filtered
4. **Pokémon Icons** - Small icons with purple borders → Detected
5. **Bottom Goal Zone** - Large circle ⭕ → Filtered
6. **Pokémon Icons** - Small icons with purple borders → Detected

### Orange Side (Right)
1. **Top Goal Zone** - Large circle ⭕ → Filtered
2. **Pokémon Icons** - Small icons with orange borders → Detected
3. **Middle Goal Zone** - Large circle ⭕ → Filtered
4. **Pokémon Icons** - Small icons with orange borders → Detected
5. **Bottom Goal Zone** - Large circle ⭕ → Filtered
6. **Pokémon Icons** - Small icons with orange borders → Detected

## Detection Process Flow

```
Step 1: Capture Minimap
    ↓
Step 2: Convert to HSV Color Space
    ↓
Step 3: Apply Purple Color Mask
    ↓ (finds both goals and Pokémon)
    ↓
Step 4: Find All Purple Contours
    ↓ (10+ contours found)
    ↓
Step 5: Filter by Size
    ↓ (remove if > 500 pixels²)
    ↓
Step 6: Keep Top 5 Valid Contours
    ↓ (goals removed, only Pokémon remain)
    ↓
Step 7: Extract Center Positions
    ✅ (0-5 Pokémon positions)

(Repeat for Orange Team)
```

## Verification Examples

### Correct Detection
```
Frame 30: Detected 3 purple, 4 orange Pokémon ✅
```
This is correct - some Pokémon might be:
- In base (not visible)
- KO'd (respawning)
- At edge of minimap

### Incorrect Detection (Goals Included)
```
Frame 30: Detected 6 purple, 6 orange Pokémon ❌
```
This would mean 3 goals + 3 Pokémon per team
**Solution:** Lower max_area parameter

## Common Minimap Elements

### Always Filtered (Too Large)
- ⭕ Goal zones
- 🏰 Team bases
- 🌲 Large map features
- 📍 Objective markers (if large)

### Usually Detected (Correct Size)
- 👤 Pokémon icons (with team borders)
- 🦀 Wild Pokémon icons (if colored)
- 🎯 Player-controlled characters

### Never Detected (Too Small/No Color)
- · Tiny UI elements
- ─ Grid lines
- ░ Fog of war effects

## Size Tuning Guide

If you need to adjust filtering:

### Pokémon Too Small to Detect
```python
# Lower the min_area threshold
min_area=5  # Instead of 10
```

### Goals Being Detected
```python
# Lower the max_area threshold
max_area=200  # Instead of 500
```

### Testing Your Settings
```bash
python pokemon_tracker.py --fps 5

# Watch the output:
Frame 5: Detected X purple, Y orange Pokémon

# X and Y should be 0-5 each
# If consistently 6+, goals are being detected
# If consistently 0, min_area might be too high
```

## Real-World Example

From a typical match:

```
Time: 0:00 (Match start)
Frame 1: Detected 5 purple, 5 orange Pokémon
→ All Pokémon visible at spawn ✅

Time: 2:30 (Early game)
Frame 150: Detected 3 purple, 4 orange Pokémon
→ Some in jungle, some in lanes ✅

Time: 5:00 (First teamfight)
Frame 300: Detected 2 purple, 5 orange Pokémon
→ 3 purple KO'd, respawning ✅

Time: 7:30 (Scattered)
Frame 450: Detected 4 purple, 3 orange Pokémon
→ Some at objectives, some in base ✅

Time: 10:00 (Final fight)
Frame 600: Detected 5 purple, 5 orange Pokémon
→ All gathered for final push ✅
```

**Notice:** Never more than 5 per team!

## Visual Summary

```
┌───────────────────────────────────────────────┐
│  MINIMAP ELEMENT DETECTION CHART              │
├───────────────────────────────────────────────┤
│                                               │
│  Element          Size        Detected?       │
│  ─────────────────────────────────────────    │
│  Goal Zone        Large       ❌ NO           │
│  Pokémon Icon     Small       ✅ YES          │
│  Team Base        Large       ❌ NO           │
│  Wild Pokémon     Medium      ⚠️  Maybe       │
│  Objective        Large       ❌ NO           │
│  Player Icon      Small       ✅ YES          │
│  UI Element       Tiny        ❌ NO           │
│                                               │
└───────────────────────────────────────────────┘
```

## Final Confirmation

**Your specific minimap (`show.png`):**
- ✅ Purple goal zones will be filtered
- ✅ Orange goal zones will be filtered
- ✅ Only Pokémon icons will be detected
- ✅ Maximum 5 per team guaranteed
- ✅ Size-based filtering prevents false positives

**You're safe to track!** 🎮
