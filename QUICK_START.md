# 🚀 QUICK START GUIDE - Enhanced Pokemon Unite Tracker

## ⚡ GET STARTED IN 3 STEPS

### 1. Install Dependencies
```bash
pip install opencv-python numpy pillow
```

### 2. Run the Tracker
```bash
python launcher_improved.py
```

### 3. Wait for Output
The tracker will:
- ✅ Detect minimap automatically
- ✅ Capture for exactly 10 minutes (600 seconds)
- ✅ Process all screenshots
- ✅ Generate final heatmap with overlays
- ✅ Save everything to `outputs/` folder

## 📁 WHAT YOU GET

After running, check `outputs/` folder:

```
outputs/
├── heatmap_final_TIMESTAMP.png      ← YOUR FINAL HEATMAP!
├── tracking_data_TIMESTAMP.json     ← All detection data
```

## 🎨 HEATMAP FEATURES

✅ **Custom Team Colors**
- Orange Team: #FF9A00 (bright orange)
- Purple Team: #AF4CFF (bright purple)

✅ **Smart Intensity Scaling**
- 1 second in area = 1% opacity
- 100 seconds in area = 100% full color

✅ **Creep & Objective Tracking**
- Yellow circles mark creep camps
- Bright yellow circles mark objectives  
- MM:SS uptime displayed next to each

✅ **Proper Map Overlay**
- Uses theiaskyruins.png as base
- Correct aspect ratio maintained
- All detections positioned accurately

## ⚙️ CONFIGURATION

Edit these at the top of `launcher_improved.py`:

```python
# Keep or delete tmp/ screenshots after processing
DELETE_SCREENSHOTS_AFTER_PROCESSING = True

# Heatmap colors (BGR format)
ORANGE_COLOR = (0, 154, 255)  # #FF9A00
PURPLE_COLOR = (255, 76, 175)  # #AF4CFF

# Capture settings
CAPTURE_DURATION = 600  # 10 minutes
CAPTURE_FPS = 1         # 1 screenshot per second
```

## 🔧 TUNING CREEP/OBJECTIVE DETECTION

The tracker is ready for player detection out of the box. However, creep/objective detection may need tuning based on your specific game footage.

### Test Individual Screenshots

1. Set `DELETE_SCREENSHOTS_AFTER_PROCESSING = False`
2. Run the tracker
3. Check `tmp/` folder for screenshots
4. Test detection on a single frame:

```bash
python creep_objective_detector.py tmp/screenshot_0100.png
```

This creates `debug_visualization.png` showing:
- Left panel: Detections overlaid
- Middle panel: Creep HSV mask
- Right panel: Objective HSV mask

### Adjust Parameters

Edit the top of `creep_objective_detector.py`:

```python
# If creeps not detected, try:
CREEP_HSV_LOWER = [15, 50, 70]    # Lower thresholds
CREEP_HSV_UPPER = [35, 220, 200]  # Higher thresholds

# If too many false positives:
CREEP_MIN_AREA = 12               # Increase minimum size
CREEP_MIN_CIRCULARITY = 0.6       # Require more circular
```

## 🎯 HOW IT WORKS

### Phase 1: Capture (Silent)
- Waits for minimap to appear on your screen
- Captures exactly 1 screenshot per second
- Saves all to `tmp/` folder
- Runs for exactly 600 seconds (10 minutes)

### Phase 2: Processing (Batch)
- Loads all screenshots from `tmp/`
- Detects players (orange/purple teams)
- Detects creeps (yellow dots)
- Detects objectives (larger yellow icons)
- Clusters by position to track uptimes

### Phase 3: Output (Final)
- Generates heatmaps with custom colors
- Overlays creeps and objectives
- Adds uptime timestamps
- Saves PNG and JSON
- Cleans up `tmp/` if configured

## 💡 TIPS

### For Best Results
- ✅ Run game in **windowed** or **borderless** mode
- ✅ Keep minimap **visible** and **unobscured**
- ✅ Let it run for the full 10 minutes
- ✅ Don't move the game window during capture

### If Minimap Not Detected
- Make sure Pokemon icons are visible on minimap
- Try moving game window to different position
- Check that minimap isn't obscured by UI elements

### If Processing Takes Too Long
- Normal processing time: 2-5 minutes for 600 screenshots
- Check CPU usage - should be using available cores
- Close other heavy applications

## 🐛 TROUBLESHOOTING

### "Minimap not found"
→ Game must be running with minimap visible
→ Pokemon icons must be showing on minimap

### "Module not found"
→ Run: `pip install opencv-python numpy pillow`

### "Too many/few creeps detected"
→ Tune parameters in `creep_objective_detector.py`
→ Test on individual screenshots first
→ Check `debug_visualization.png` to see masks

### "Wrong colors on heatmap"
→ Check ORANGE_COLOR and PURPLE_COLOR in launcher
→ Values are in BGR format, not RGB

### "Map aspect ratio wrong"
→ Make sure `theiaskyruins.png` is in the same folder
→ Check that file loads successfully (message at startup)

## 📊 OUTPUT FORMAT

### PNG Heatmap
- Base: Reference map (theiaskyruins.png) or last screenshot
- Overlay: Translucent orange/purple heatmaps
- Markers: Yellow circles for creeps/objectives
- Text: MM:SS uptime at each marker location

### JSON Data
```json
{
  "purple_team": [
    {"x": 120, "y": 85},
    ...
  ],
  "orange_team": [
    {"x": 200, "y": 150},
    ...
  ],
  "creep_camps": {
    "0": {
      "position": [125, 90],
      "uptime_seconds": 450,
      "detections": 450
    }
  },
  "objective_camps": {
    "0": {
      "position": [250, 160],
      "uptime_seconds": 180,
      "detections": 180
    }
  }
}
```

## 🎮 WORKFLOW EXAMPLE

```bash
# 1. Start tracking
python launcher_improved.py

# Output:
# 🎮 POKEMON UNITE ADVANCED TRACKER
# 🔍 Waiting for minimap detection...
# ✅ Minimap detected at: (1650, 850, 1900, 1100)
# 🎬 Starting capture...

# [Wait 10 minutes while playing]

# Output:
# ✅ Capture complete! 600 screenshots saved
# 🔬 PHASE 2: PROCESSING SCREENSHOTS
# 📊 Processing 600 screenshots...
# [Processing happens automatically]

# ✅ Processing complete!
# 🎨 PHASE 3: GENERATING FINAL HEATMAP
# [Heatmap generation]

# ✅ Final heatmap saved: outputs/heatmap_final_20231125_143022.png
# 🎉 ALL DONE!

# 2. View your heatmap
# Open: outputs/heatmap_final_20231125_143022.png
```

## ✨ NEW vs OLD

| Feature | Old Tracker | New Enhanced Tracker |
|---------|-------------|----------------------|
| Processing | Live (slow) | Buffered (fast) |
| Colors | Generic | Custom #FF9A00 #AF4CFF |
| Map | Square guess | Exact theiaskyruins.png ratio |
| Duration | Manual stop | Auto-stop at 600 seconds |
| Creeps | ❌ Not detected | ✅ Detected with uptime |
| Objectives | ❌ Not detected | ✅ Detected with uptime |
| Cleanup | Manual | Auto (configurable) |
| Debugging | Hard | Easy (tmp/ + debug images) |

## 🎉 YOU'RE READY!

That's it! Just run:

```bash
python launcher_improved.py
```

The system is fully configured and ready for use with player detection. Creep/objective detection will work out of the box for many setups, but can be fine-tuned if needed using the debug tools provided.

Happy tracking! 🎮✨

---

**Need Help?**
- Check `IMPLEMENTATION_GUIDE.md` for technical details
- Test individual screenshots with `creep_objective_detector.py`
- Review `debug_visualization.png` to tune HSV parameters
