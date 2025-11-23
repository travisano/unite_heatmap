# 🎮 HOW TO USE THE REAL-TIME TRACKER

## Quick Start (3 Steps!)

### 1. Install Dependencies
```bash
pip install opencv-python numpy pillow
```

### 2. Start Pokemon Unite
- Launch the game
- Make sure the minimap is visible on your screen

### 3. Run the Tracker
**Windows:**
- Right-click `launcher.py` → Open with → Python

**Mac/Linux:**
```bash
python launcher.py
```

**That's it!** The tracker will:
1. Auto-detect the minimap on your screen
2. Show you a preview and ask for confirmation
3. Start tracking Pokemon positions in real-time
4. Close the window when you're done
5. Automatically generate heatmaps

---

## What Happens

### Step 1: Minimap Detection
The tracker scans your screen looking for the circular minimap (usually bottom-right).

You'll see a popup asking "Is this correct?" with the detected region coordinates.

### Step 2: Real-Time Tracking
A window opens showing live Pokemon detection on the minimap.

You'll see:
- Orange circles around enemy Pokemon
- Purple circles around ally Pokemon
- Detection stats in the console

### Step 3: Auto-Generate Heatmap (When You Close)
When you close the tracking window:
1. Tracking data is saved to `outputs/tracking_data_TIMESTAMP.json`
2. Three heatmaps are generated automatically:
   - Combined heatmap (both teams)
   - Orange team heatmap
   - Purple team heatmap
3. All files saved to `outputs/` folder

---

## Files Generated

All outputs go to `outputs/` folder:

```
outputs/
├── minimap_region_preview.png     # Preview of detected region
├── tracking_data_TIMESTAMP.json   # Raw tracking data
├── heatmap_combined_TIMESTAMP.png # Combined heatmap
├── heatmap_orange_TIMESTAMP.png   # Orange team heatmap
└── heatmap_purple_TIMESTAMP.png   # Purple team heatmap
```

---

## Tips

### ✅ Best Practices
- Make sure Pokemon Unite is in windowed or borderless mode
- Keep the minimap visible and not obscured
- Run tracker during actual gameplay for best results
- Track for at least 30 seconds for meaningful heatmaps

### ⚠️ If Minimap Detection Fails
The tracker tries to auto-detect the minimap, but if it fails:
1. Make sure the game window is visible
2. Try moving the game window
3. Check `outputs/minimap_region_preview.png` to see what was detected
4. Restart and try again

### 🔧 Adjusting Detection
The tracker uses these files (in same folder):
- `pokemon_detector.py` - Core detection algorithm
- `launcher.py` - This real-time tracker

Don't modify these unless you know what you're doing!

---

## Keyboard Shortcuts

While tracking:
- **ESC** - Stop tracking and generate heatmap
- **Close window** - Same as ESC

---

## Troubleshooting

**"pokemon_detector.py not found"**
- Make sure pokemon_detector.py is in the same folder as launcher.py

**"Missing Dependencies"**
- Install: `pip install opencv-python numpy pillow`

**No Pokemon detected**
- Check if minimap is clearly visible
- Verify the minimap region was detected correctly
- Make sure Pokemon icons are visible on minimap

**Heatmap is empty/black**
- Track for longer (at least 30 seconds)
- Make sure Pokemon were actually detected during tracking

---

## Output Examples

### Tracking Console Output
```
🔍 Looking for minimap on your screen...
✅ Minimap found at: (1650, 850) to (1900, 1100)

🎮 Tracking started!
   Frame 10 | Time: 1.0s | Total detections: 45
   Frame 20 | Time: 2.0s | Total detections: 89
   ...
```

### Heatmap Preview
After closing, you'll see:
- Hot spots (red/yellow) = High activity areas
- Cool spots (blue/dark) = Low activity areas
- Separate heatmaps for each team

---

## Advanced: Manual Test

To test detection on a single image:
```bash
python pokemon_detector.py minimap_screenshot.png
```

Outputs will be in `outputs/` folder:
- `detection_result.png` - Image with detected Pokemon circles
- `white_mask.png` - White pixel detection visualization

---

## Need Help?

Check these files:
- `README.md` - Full project documentation
- `COMPLETE_PROJECT_GUIDE.md` - Detailed technical guide
- `QUICK_REFERENCE.txt` - Quick lookup for parameters

---

## Summary

**TO USE:**
1. Install: `pip install opencv-python numpy pillow`
2. Start game, make sure minimap visible
3. Run: `python launcher.py` (or right-click → Python)
4. Confirm minimap region
5. Track during gameplay
6. Close window when done
7. Heatmaps automatically generated!

**ALL OUTPUTS GO TO: `outputs/` folder**

That's it! Enjoy tracking! 🎮✨
