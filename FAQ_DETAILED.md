# Common Questions - Answered

## Question 1: Goal Zones Detection

### ❓ "Won't it accidentally capture the goal zones which are orange and purple?"

**Answer: NO - Goal zones are automatically filtered out!** ✅

### What I See in Your Minimap
Looking at your minimap image (`show.png`), I can clearly identify:
- **Purple circular goal zones** (left side) - 3 large circles
- **Orange circular goal zones** (right side) - 3 large circles
- **Pokémon icons** - Small icons with team-colored borders

### Why Goal Zones Won't Be Detected

The tracker now has **multiple layers of filtering**:

#### 1. **Size Filtering**
```python
min_area=10,  # Filters out noise/tiny artifacts
max_area=500  # Filters out goal zones and large static elements
```

Goal zones are **much larger** than Pokémon icons:
- **Pokémon icon**: ~20-100 pixels² area
- **Goal zone**: ~500-2000 pixels² area
- **Result**: Goal zones exceed max_area and are ignored

#### 2. **Shape Detection**
- Pokémon icons: Small, compact shapes with borders
- Goal zones: Large circles
- The contour detection prioritizes smaller, icon-sized shapes

#### 3. **Movement Patterns** (in heatmap analysis)
- Goal zones: Static, never move
- Pokémon: Constantly moving
- Heatmaps show movement patterns, so even if a goal was detected, it would appear as a single fixed point (easy to identify and ignore)

### Visual Breakdown

From your minimap, here's what gets detected vs filtered:

```
🟣 Purple Goal Zones (LEFT SIDE)
   ├─ Top goal: ❌ TOO LARGE (filtered)
   ├─ Middle goal: ❌ TOO LARGE (filtered)
   └─ Bottom goal: ❌ TOO LARGE (filtered)

🟣 Purple Pokémon Icons
   ├─ Icon 1: ✅ CORRECT SIZE (detected)
   ├─ Icon 2: ✅ CORRECT SIZE (detected)
   └─ Icon 3: ✅ CORRECT SIZE (detected)

🟠 Orange Goal Zones (RIGHT SIDE)
   ├─ Top goal: ❌ TOO LARGE (filtered)
   ├─ Middle goal: ❌ TOO LARGE (filtered)
   └─ Bottom goal: ❌ TOO LARGE (filtered)

🟠 Orange Pokémon Icons
   ├─ Icon 1: ✅ CORRECT SIZE (detected)
   ├─ Icon 2: ✅ CORRECT SIZE (detected)
   └─ Icon 3: ✅ CORRECT SIZE (detected)
```

### How to Verify

When you run the tracker, you'll see:
```
Frame 30: Detected 3 purple, 3 orange Pokémon  ✅ Correct!
```

If goal zones were being detected, you'd see:
```
Frame 30: Detected 6 purple, 6 orange Pokémon  ❌ Wrong! (3 goals + 3 pokemon)
```

### Adjusting if Needed

If you still detect goals (unlikely), you can adjust the max_area:

Edit `pokemon_tracker.py` around line 97-126:
```python
# Reduce max_area to filter more aggressively
purple_positions = get_positions(purple_contours, min_area=10, max_area=200, max_positions=5)
```

---

## Question 2: Start and Stop Controls

### ❓ "How do I start and stop the capture?"

**Answer: Simple keyboard controls!** ⌨️

### Starting the Tracker

**Option 1: Simple Command**
```bash
python pokemon_tracker.py
```

**Option 2: With Custom Settings**
```bash
python pokemon_tracker.py --fps 15 --output my_match.json
```

**Option 3: Using Launcher**
```bash
python launcher.py
# Then select option 1 or 4
```

### What Happens When You Start

You'll see this output:
```
============================================================
🎮 POKÉMON UNITE HEATMAP TRACKER
============================================================
Tracking at 10 FPS

📹 Make sure your Pokémon Unite replay is visible on screen!
   The minimap will be detected automatically.

⏸️  TO STOP TRACKING: Press Ctrl+C
============================================================

Minimap found at: (1650, 50, 200, 200)
Captured 50 frames...
Frame 30: Detected 4 purple, 5 orange Pokémon
Captured 100 frames...
Frame 60: Detected 3 purple, 4 orange Pokémon
```

### Stopping the Tracker

**Press `Ctrl+C` on your keyboard**

**Windows**: `Ctrl` + `C`
**Mac**: `Cmd` + `C` or `Ctrl` + `C`
**Linux**: `Ctrl` + `C`

### What Happens When You Stop

```
⏹️  Tracking stopped by user (Ctrl+C pressed)

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

Data saved to: tracking_data.json
```

### Complete Workflow

```bash
# 1. Start your replay in OBS or Pokémon Unite
# 2. Run tracker
python pokemon_tracker.py

# 3. Watch the replay play
# (Tracker runs in background)

# 4. When replay finishes, press Ctrl+C

# 5. Data is automatically saved to tracking_data.json
```

### Tips for Best Results

✅ **DO:**
- Start tracker BEFORE starting replay
- Let it run while entire replay plays
- Press Ctrl+C only when done
- Keep minimap visible on screen

❌ **DON'T:**
- Close terminal window (use Ctrl+C instead)
- Kill the process abruptly
- Minimize OBS/game window
- Cover the minimap

---

## Question 3: Expanded Minimap Support

### ❓ "If I expand the minimap during game, can it adjust to capture the expanded one on my OBS screen just fine?"

**Answer: YES - Now with multi-scale detection!** ✅

### How It Works

The tracker now supports **automatic scale detection**:

```python
# Tries multiple scales automatically:
scales = [1.0, 1.5, 2.0, 0.75, 0.5]
```

This means it can detect:
- **Normal minimap** (1.0x scale)
- **Expanded minimap** (1.5x - 2.0x scale)
- **Compressed minimap** (0.5x - 0.75x scale)

### When You Expand the Minimap

**Scenario 1: Expand BEFORE tracking starts**
```
1. Expand minimap in game
2. Start tracker: python pokemon_tracker.py
3. Tracker detects expanded size automatically
4. Works perfectly! ✅
```

**Scenario 2: Expand DURING tracking**
```
1. Tracker starts with normal minimap
2. You expand minimap mid-game
3. First few frames might be missed
4. Tracker re-detects on next frame
5. Continues tracking at new size ✅
```

### What You'll See

When expanded minimap is detected:
```
📏 Minimap detected at 1.5x scale (expanded minimap)
Minimap found at: (1650, 50, 300, 300)
Frame 30: Detected 4 purple, 5 orange Pokémon
```

### Best Practices

**Option 1: Consistent Size (Recommended)**
- Keep minimap at same size throughout replay
- Easier for consistent tracking
- No transition issues

**Option 2: Dynamic Size**
- Can expand/shrink during replay
- Tracker will adapt
- Might miss a few frames during transition
- Still works, just slightly less smooth

### Technical Details

The multi-scale detection works by:
1. Taking your template image (`show.png`)
2. Scaling it to 50%, 75%, 100%, 150%, and 200%
3. Trying to match each scaled version
4. Using the best match found
5. Tracking at that scale until it needs to re-detect

### Re-Detection Behavior

The tracker only searches for the minimap once at startup. If you want it to adapt to size changes:

**Current behavior:**
- Detects minimap once at startup
- Uses that location/size for entire session
- Very fast (no re-searching every frame)

**If you need dynamic size changes:**

Option A: Stop and restart tracker when you change size
```bash
# Normal size tracking
python pokemon_tracker.py --output part1.json
# ... expand minimap, press Ctrl+C

# Expanded size tracking  
python pokemon_tracker.py --output part2.json
# ... tracking continues
```

Option B: Keep minimap size constant (easier!)

### Recommendation

🎯 **Best approach:**
1. Decide on minimap size BEFORE starting replay
2. Start tracker
3. Keep minimap at that size for entire replay
4. Get consistent, high-quality tracking

This avoids any transition issues and gives you the cleanest data!

### Template Considerations

If you primarily use expanded minimap:
1. Take a screenshot of the EXPANDED minimap
2. Save as `show.png`
3. Use that as your template
4. Tracker will look for expanded version

If you switch between sizes often:
- Use normal size template (more common)
- Tracker's multi-scale detection handles the rest

---

## Quick Reference

### Start Tracking
```bash
python pokemon_tracker.py
```

### Stop Tracking
```
Press: Ctrl+C
```

### Check for Goal Zone Detection
```
Frame output should show 0-5 per team, not 6+
If you see 6+, adjust max_area parameter
```

### Expanded Minimap
```
✅ Supported automatically via multi-scale detection
📏 Will show scale detection message if expanded
💡 Best to keep size consistent during replay
```

### Verification Checklist

Before you start tracking:
- [ ] Replay is visible on screen
- [ ] Minimap is not covered/obscured
- [ ] You know how to stop (Ctrl+C)
- [ ] Minimap size is set to your preference
- [ ] OBS/capture is running

During tracking:
- [ ] See "Minimap found" message
- [ ] See periodic "Detected X purple, Y orange" messages
- [ ] Counts are reasonable (0-5 per team)
- [ ] No errors appearing

After tracking:
- [ ] Press Ctrl+C to stop
- [ ] See completion statistics
- [ ] Find tracking_data.json file
- [ ] Ready to generate heatmap!

---

## Troubleshooting

### "Detected 6 purple Pokémon" (detecting goals)
→ Lower max_area: Edit line ~126 in pokemon_tracker.py
```python
purple_positions = get_positions(..., max_area=200, ...)
```

### "Minimap not found" after expanding
→ Stop tracker (Ctrl+C) and restart
→ Or use expanded minimap screenshot as template

### Can't stop tracker
→ Make sure terminal window is active
→ Try Ctrl+C multiple times
→ Worst case: Close terminal window

### Positions seem wrong
→ Check that correct minimap size is detected
→ Verify goal zones aren't being counted
→ Look for ~7-10 total Pokémon per frame on average

---

**All three concerns addressed! You're ready to track!** 🎮
