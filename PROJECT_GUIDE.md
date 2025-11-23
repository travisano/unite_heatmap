# POKEMON UNITE MINIMAP TRACKER - PROJECT GUIDE
## For Starting New Conversations

---

## NEW CONVERSATION PROMPT

```
I have a Pokemon Unite minimap tracker project that detects Pokemon positions on the minimap.

PROJECT OVERVIEW:
- Detects Pokemon markers (perfect circles with white centers and colored borders)
- Orange team vs Purple team detection
- Tracks positions over time and generates heatmaps

DETECTION METHOD (WORKING PERFECTLY):
1. Find white pixels (unique identifier - nothing else on minimap has white)
2. Use Hough Circle detection to find perfect circles (all same size)
3. Verify circles contain white centers
4. Determine team by ring color:
   - Orange team: Hue 0-30 (red-orange-yellow)
   - Purple team: Hue 100-160 (includes blue-tinted borders)

KEY CONSTRAINTS:
- White detection: HSV [0,0,210] to [180,35,255] (bright but allows slight translucency)
- Never detect gray (spawns/towers have gray, not white)
- All Pokemon markers are same size (radius 8-14 pixels)
- Must have white center + colored ring

The detection is in pokemon_detector.py and works perfectly.
I need help with: [describe your issue]
```

---

## FILES TO KEEP (FINAL PROJECT)

### Core Files (ESSENTIAL):
```
pokemon_detector.py          # Final tuned detector (USE THIS)
pokemon_tracker.py           # Full tracking system with video processing
heatmap_generator.py         # Generates heatmaps from tracking data
launcher.py                  # Main UI launcher
```

### Supporting Files:
```
tracking_data.json           # Example tracking output
heatmap_viewer.html          # View generated heatmaps
```

### Test Images:
```
1.png, 2.png, 3.png, 4.png   # Test minimap images
4_detected_GOLD.png          # Perfect detection example
```

### Documentation:
```
README.md                    # Project overview
QUICKSTART.md                # Quick start guide
```

---

## FILES TO DELETE (OLD/OBSOLETE)

### Old Detection Attempts:
```
final_detection.py           # Superseded by pokemon_detector.py
final_pokemon_detector.py    # Old version
minimap_pokemon_detector.py  # Old version
ratio_based_detector.py      # Old approach
robust_detection.py          # Old approach
scale_independent_detection.py  # Old approach
test_detection.py            # Old test file
test_detector.py             # Old test file
test_on_4.py                 # Old test file
```

### Old Documentation:
```
ANSWERS_TO_YOUR_QUESTIONS.md
CIRCLE_DETECTION_FIX.md
COMPLETE_ANSWERS.md
DETECTION_HELP.md
DETECTION_STATUS.md
FAQ_DETAILED.md
FINAL_SUMMARY.md
HOLLOW_CIRCLE_FIX.md
IMAGE_ANALYSIS.md
IMPROVEMENTS_SUMMARY.md
INDEX.md
MINIMAP_GUIDE.md
MULTI_POKEMON_DETECTION.md
OVERVIEW.md
SETUP.md
START_HERE.md
TROUBLESHOOTING_DETECTION.md
YES_MULTIPLE_POKEMON.md
```

### Old Sample Data:
```
sample_tracking_data.json    # Use tracking_data.json instead
```

### Old Test Results:
```
show.png
debug_edges.png
minimapbugv0zo6xv38n985e1*.webp files
image6bdf1523a332f0f98.webp
```

---

## QUICK COMMAND TO CLEAN UP

```bash
# Create new clean project directory
mkdir pokemon_tracker_clean
cd pokemon_tracker_clean

# Copy ONLY essential files
cp /path/to/old/pokemon_detector.py .
cp /path/to/old/pokemon_tracker.py .
cp /path/to/old/heatmap_generator.py .
cp /path/to/old/launcher.py .
cp /path/to/old/README.md .
cp /path/to/old/QUICKSTART.md .
cp /path/to/old/*.png .  # Test images

# Done! Clean project ready
```

---

## WHAT EACH CORE FILE DOES

**pokemon_detector.py**
- Main detection function: `detect_pokemon_markers(minimap_img)`
- Returns: markers list, debug image, white mask
- Each marker has: position, radius, team, confidence

**pokemon_tracker.py**
- Full video processing pipeline
- Extracts minimap from video frames
- Runs detection on each frame
- Outputs tracking data JSON

**heatmap_generator.py**
- Reads tracking data JSON
- Generates heatmap images
- Shows Pokemon activity over time

**launcher.py**
- Simple GUI to run tracker
- Select video file
- Choose minimap region
- Start tracking

---

## INTEGRATION NOTES

The detection function is standalone and can be imported:

```python
from pokemon_detector import detect_pokemon_markers
import cv2

# Load minimap image
minimap = cv2.imread('minimap.png')

# Detect Pokemon
markers, debug_img, white_mask = detect_pokemon_markers(minimap)

# Use results
for marker in markers:
    print(f"{marker['team']} at {marker['position']}")
```

Output format:
```python
{
    'position': (x, y),      # Center coordinates
    'radius': 12,            # Circle radius in pixels
    'team': 'orange',        # 'orange' or 'purple'
    'confidence': 45,        # Colored pixel count
    'white_pixels': 23       # White pixel count
}
```
