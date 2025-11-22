# Multi-Pokémon Detection - Technical Details

## How It Works

The tracker is designed to detect **all visible Pokémon** from both teams in each frame, with support for:
- **0-5 Pokémon per team** (purple and orange)
- **0-10 total Pokémon** per frame

## Detection Process

### 1. Color-Based Detection
Each frame, the system:
1. Converts the minimap to HSV color space
2. Creates color masks for purple and orange team borders
3. Finds **all contours** matching each color
4. Extracts center positions for up to 5 Pokémon per team

### 2. Position Extraction
```python
# For each team:
- Find ALL colored contours (not just one)
- Sort by area (largest/clearest first)
- Extract up to 5 positions per team
- Store each position with timestamp
```

### 3. Data Storage
Each detected Pokémon creates one entry:
```json
{
  "x": 100,
  "y": 150,
  "timestamp": 1700000000.123
}
```

## Example Scenarios

### Scenario 1: Full Teams (10 Pokémon)
- Purple team: 5 Pokémon visible → 5 positions detected
- Orange team: 5 Pokémon visible → 5 positions detected
- **Total: 10 positions per frame**

### Scenario 2: Partial Teams (6 Pokémon)
- Purple team: 3 Pokémon visible → 3 positions detected
- Orange team: 3 Pokémon visible → 3 positions detected
- **Total: 6 positions per frame**

### Scenario 3: Asymmetric (7 Pokémon)
- Purple team: 2 Pokémon visible → 2 positions detected
- Orange team: 5 Pokémon visible → 5 positions detected
- **Total: 7 positions per frame**

### Scenario 4: Early Game/Respawning (0 Pokémon)
- Purple team: 0 Pokémon visible → 0 positions detected
- Orange team: 0 Pokémon visible → 0 positions detected
- **Total: 0 positions per frame** (this is fine!)

## Why Pokémon Might Not Be Detected

### Common Reasons
1. **Off-screen**: Pokémon in base or far from minimap view
2. **KO'd**: Defeated Pokémon don't show on minimap
3. **Color issues**: Border not visible due to effects/overlays
4. **Occlusion**: Overlapping icons or UI elements

### This is Normal!
- Not all 10 Pokémon will always be visible
- Detection count varies throughout the match
- The heatmap will still be accurate for visible Pokémon

## Data Volume Examples

### 10-minute match at 10 FPS:
- Total frames: 6,000
- If average 7 Pokémon/frame: **42,000 position points**
- If average 10 Pokémon/frame: **60,000 position points**

### 5-minute match at 10 FPS:
- Total frames: 3,000
- If average 7 Pokémon/frame: **21,000 position points**
- If average 10 Pokémon/frame: **30,000 position points**

## Verification Features

### Real-Time Monitoring
The tracker shows detection counts every 3 seconds:
```
Frame 30: Detected 4 purple, 5 orange Pokémon
Frame 60: Detected 3 purple, 4 orange Pokémon
Frame 90: Detected 5 purple, 5 orange Pokémon
```

### End Statistics
When tracking completes:
```
============================================================
Tracking Complete!
============================================================
Total frames captured: 6000
Purple team positions: 28,500
Orange team positions: 30,000

Average Pokémon per frame:
  Purple: 4.75 Pokémon/frame
  Orange: 5.00 Pokémon/frame
  Total:  9.75 Pokémon/frame
============================================================
```

This tells you:
- Total detection success
- Average visibility per team
- Overall match dynamics

## Quality Indicators

### Good Detection
- **8-10 Pokémon/frame average**: Excellent visibility
- Most frames have 4-5 per team
- Indicates clear minimap and good tracking

### Moderate Detection
- **5-7 Pokémon/frame average**: Good visibility
- Some Pokémon frequently off-screen
- Still produces useful heatmaps

### Low Detection
- **<5 Pokémon/frame average**: Check settings
- May indicate color detection issues
- Review HSV ranges or minimap clarity

## Optimization Tips

### To Detect More Pokémon

1. **Adjust Color Ranges**
   ```python
   # In pokemon_tracker.py, try wider ranges:
   purple_lower = np.array([115, 40, 40])  # Wider range
   purple_upper = np.array([165, 255, 255])
   ```

2. **Lower Minimum Area**
   ```python
   # In get_positions function:
   purple_positions = get_positions(purple_contours, min_area=5)  # Lower threshold
   ```

3. **Higher FPS**
   ```bash
   python pokemon_tracker.py --fps 15  # More samples
   ```

### To Improve Accuracy

1. **Use Higher Quality Minimap**
   - Capture at higher resolution
   - Ensure clear team-colored borders
   - Minimize compression artifacts

2. **Stable Lighting**
   - Consistent game brightness
   - No overlay effects obscuring minimap
   - Clear visibility of all icons

## Technical Limitations

### Maximum Detections
- **Hard limit: 5 per team** (by design, matches game)
- **Soft limit: 10 total** (5 purple + 5 orange)
- Extra detections beyond 5 are filtered out

### Why 5 per Team?
- Pokémon Unite has exactly 5 Pokémon per team
- Any more would be false positives
- Sorting by contour area ensures we get the clearest 5

### False Positives
Rare, but can occur from:
- UI elements with similar colors
- Map decorations
- Visual effects

The area sorting helps prioritize actual Pokémon icons.

## Heatmap Impact

### With Multiple Pokémon
Each position adds to the heatmap, so:
- **More detections** = **denser heatmap** = better analysis
- Areas where 5 Pokémon gather show up very clearly
- Individual movement patterns still visible

### Example Interpretation
If you see:
- **Very dark area**: Multiple Pokémon spent lots of time there
  - Could be all 5 farming same lane
  - Or 1-2 Pokémon staying in one spot for long time
- **Spread patterns**: Team splitting across map
- **Concentrated then spread**: Grouping then dispersing

## Debugging Detection Issues

### Check Detection Counts
```bash
python pokemon_tracker.py --fps 10
```
Watch the output:
```
Frame 30: Detected 4 purple, 5 orange Pokémon  # Good!
Frame 60: Detected 0 purple, 1 orange Pokémon  # Problem!
```

### If Counts Too Low
1. Review minimap visibility in your capture
2. Check color ranges match your game settings
3. Verify minimap template is accurate
4. Test with different parts of replay

### If Counts Too High (>5 per team)
The code now limits to 5, but if you see this:
1. Adjust min_area threshold higher
2. Tighten HSV color ranges
3. Check for UI elements interfering

## Advanced: Custom Detection Limits

To track different numbers of Pokémon (for testing):

```python
# In pokemon_tracker.py, modify:
purple_positions = get_positions(purple_contours, max_positions=10)  # Track up to 10
```

This is useful for:
- Testing with custom game modes
- Debugging false positives
- Experimental analysis

## Summary

✅ **YES** - System detects multiple Pokémon per team  
✅ **YES** - Handles 0-10 total Pokémon per frame  
✅ **YES** - Automatically adapts to visible Pokémon count  
✅ **YES** - Provides statistics and debug output  
✅ **YES** - Optimized for accuracy (sorted by area)  

The tracker is production-ready for full match analysis with realistic Pokémon counts!
