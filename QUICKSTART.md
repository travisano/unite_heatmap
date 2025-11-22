# 🚀 Quick Start Guide

## Prerequisites

1. **Install Python** (3.8 or higher)
2. **Install dependencies**:
   ```bash
   pip install opencv-python numpy pillow matplotlib scipy --break-system-packages
   ```

## Files You Need

Before starting, make sure you have:
- ✅ `show.png` - A screenshot of the minimap from your game
- ✅ `image-6bdf1523a332f-0f98.webp` - The full Pokémon Unite map image

## Three Ways to Use This Tool

### 🎯 Method 1: Interactive Launcher (Easiest)

```bash
python launcher.py
```

Then follow the on-screen menu! Perfect for beginners.

### 🎯 Method 2: Command Line (Quick)

**Step 1: Start tracking while watching a replay**
```bash
python pokemon_tracker.py --minimap show.png --fps 10
```
Press Ctrl+C when done watching the replay.

**Step 2: Generate the heatmap**
```bash
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp
```

**Step 3: View in browser**
Open `heatmap_viewer.html` in your web browser and load your data!

### 🎯 Method 3: One-Shot Workflow

```bash
python launcher.py --workflow --minimap show.png --map image-6bdf1523a332f-0f98.webp
```

This runs everything automatically!

## Understanding the Output

### Files Created

1. **`tracking_data.json`** - Raw position data
   - Contains all Pokémon positions tracked
   - Can be reused to generate different heatmaps
   - Format: JSON with timestamps and coordinates

2. **`heatmap.png`** - Static heatmap image
   - Visual representation of team movements
   - Purple and orange overlays on the map
   - Can be shared or analyzed offline

3. **`heatmap_data.npz`** - Raw heatmap data
   - Used by the interactive viewer
   - Contains normalized heatmap arrays
   - Binary format for efficiency

## Tips for First-Time Users

### 📸 Getting a Good Minimap Template

1. Open Pokémon Unite in OBS or your screen capture
2. Start a replay
3. Take a screenshot when the minimap is clearly visible
4. Crop just the minimap area
5. Save as `show.png`

### 🗺️ Getting the Full Map Image

You can use the provided `image-6bdf1523a332f-0f98.webp` or find a high-resolution map image online.

### ⚙️ Adjusting Settings

**If colors aren't detected properly:**

Edit `pokemon_tracker.py` and adjust these lines:
```python
# Around line 90-96
purple_lower = np.array([120, 50, 50])  # Adjust these values
purple_upper = np.array([160, 255, 255])

orange_lower = np.array([5, 100, 100])  # Adjust these values
orange_upper = np.array([20, 255, 255])
```

**If heatmap is too blurry or too precise:**

Use the `--sigma` parameter:
```bash
# More precise (tighter clusters)
python heatmap_generator.py --map map.webp --sigma 10

# More spread out (wider areas)
python heatmap_generator.py --map map.webp --sigma 40
```

## Common Issues & Solutions

### ❌ "Minimap not found on screen"

**Solution**: Make sure:
1. The minimap is visible on your screen
2. The template image matches your current display
3. Try capturing a new minimap template

### ❌ "No Pokémon detected"

**Solution**: 
1. Check that Pokémon have colored borders in the minimap
2. Adjust the HSV color ranges (see above)
3. Ensure the minimap is clear and not obstructed

### ❌ Heatmap looks strange

**Solution**:
1. Verify minimap dimensions (usually 200x200 or similar)
2. Adjust the `--minimap-width` and `--minimap-height` parameters
3. Try different `--sigma` values for blur

### ❌ Python package errors

**Solution**:
```bash
pip install --upgrade opencv-python numpy pillow matplotlib scipy --break-system-packages
```

## Example Workflows

### 📊 Analyzing a Single Match

```bash
# 1. Track the replay
python pokemon_tracker.py --output match1.json

# 2. Generate heatmap
python heatmap_generator.py --map map.webp --data match1.json --output match1_heatmap.png

# 3. View interactively
# Open heatmap_viewer.html and load match1.json
```

### 📊 Comparing Two Matches

```bash
# Track first match
python pokemon_tracker.py --output match1.json

# Track second match
python pokemon_tracker.py --output match2.json

# Generate separate heatmaps
python heatmap_generator.py --map map.webp --data match1.json --output match1.png
python heatmap_generator.py --map map.webp --data match2.json --output match2.png

# Compare side by side!
```

### 📊 Team-Specific Analysis

```bash
# Track match
python pokemon_tracker.py

# Generate purple team only
python heatmap_generator.py --map map.webp --purple-only --output purple.png

# Generate orange team only
python heatmap_generator.py --map map.webp --orange-only --output orange.png
```

## Interactive Viewer Features

The `heatmap_viewer.html` file provides:

✅ **Team Toggles** - Show/hide purple and orange teams independently

✅ **Intensity Slider** - Adjust heatmap opacity for better visibility

✅ **Custom Map Upload** - Use different map templates

✅ **Data Upload** - Load different tracking data files

✅ **Statistics** - View total positions, frames, and duration

## Performance Tips

### For Smooth Tracking

- **FPS**: 10 FPS is usually enough (lower = less CPU usage)
- **Screen Resolution**: Higher resolution = more accurate tracking
- **Replay Speed**: Normal or 0.5x speed works best

### For Better Heatmaps

- **More Data**: Track longer replays for more comprehensive heatmaps
- **Multiple Matches**: Combine data from multiple matches
- **Team Separation**: Analyze each team independently

## Next Steps

Once you're comfortable with the basics:

1. **Experiment with settings** - Try different sigma values and color ranges
2. **Analyze patterns** - Look for team positioning strategies
3. **Compare matches** - Track wins vs losses to find patterns
4. **Share insights** - Export heatmaps to share with your team

## Getting Help

If you're stuck:
1. Check the main README.md for detailed documentation
2. Review the troubleshooting section above
3. Verify all files are in the correct location
4. Run `python launcher.py` and choose option 5 to check files

## Ready to Start?

Just run:
```bash
python launcher.py
```

And follow the interactive prompts! 🎮

---

**Happy tracking!** 🎮📊✨
