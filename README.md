# Pokémon Unite Heatmap Tracker

A Python-based tool for tracking Pokémon positions from replays and generating team heatmaps for strategic analysis.

## Features

- 🎮 **Screen Capture**: Automatically detects and tracks the minimap from your OBS/screen
- 🔍 **Color Detection**: Identifies purple and orange team Pokémon by their border colors
- 📊 **Heatmap Generation**: Creates beautiful heatmap visualizations showing team positioning
- 🌐 **Interactive Viewer**: Web-based viewer with team toggles and intensity controls
- 💾 **Data Export**: Saves tracking data in JSON format for later analysis

## System Requirements

- Python 3.8 or higher
- Required Python packages:
  - opencv-python
  - numpy
  - pillow
  - matplotlib
  - scipy

## Installation

1. Install Python dependencies:
```bash
pip install opencv-python numpy pillow matplotlib scipy --break-system-packages
```

2. Place your files in the working directory:
   - `show.png` - Screenshot of the minimap (for template matching)
   - `image-6bdf1523a332f-0f98.webp` - Full map template (for heatmap overlay)

## Usage

### Step 1: Track Pokémon Positions

Run the tracker while watching a replay in OBS or any screen capture:

```bash
python pokemon_tracker.py --minimap show.png --fps 10 --output tracking_data.json
```

**Parameters:**
- `--minimap`: Path to minimap template image (default: show.png)
- `--fps`: Frames per second to capture (default: 10)
- `--output`: Output JSON file path (default: tracking_data.json)

**Controls:**
- Press `Ctrl+C` to stop tracking
- The script will automatically find the minimap on your screen
- Position data is saved continuously

### Step 2: Generate Heatmap

Create heatmap visualizations from the tracking data:

```bash
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data tracking_data.json --output heatmap.png
```

**Parameters:**
- `--map`: Path to full map template image (required)
- `--data`: Path to tracking data JSON (default: tracking_data.json)
- `--output`: Output heatmap image path (default: heatmap.png)
- `--minimap-width`: Width of minimap in pixels (default: 200)
- `--minimap-height`: Height of minimap in pixels (default: 200)
- `--sigma`: Gaussian blur sigma for smoothing (default: 20)
- `--purple-only`: Show only purple team heatmap
- `--orange-only`: Show only orange team heatmap

### Step 3: Interactive Viewing

Open the HTML viewer in your web browser:

```bash
# Just open heatmap_viewer.html in any web browser
```

**Features:**
- ✅ Toggle purple team heatmap on/off
- ✅ Toggle orange team heatmap on/off
- 🎚️ Adjust heatmap intensity slider
- 📁 Load custom map images
- 📊 Load tracking data files
- 📈 View statistics (positions tracked, frames, duration)

## How It Works

### 1. Minimap Detection
The tracker uses template matching to locate the minimap on your screen. It compares the provided minimap template (`show.png`) against your screen capture to find the exact position.

### 2. Color-Based Pokémon Detection
The system detects Pokémon by their team-colored borders:
- **Purple Team**: HSV range [120-160, 50-255, 50-255]
- **Orange Team**: HSV range [5-20, 100-255, 100-255]

These ranges can be adjusted in the code if needed for different lighting conditions.

### 3. Position Tracking
Each detected Pokémon position is recorded with:
- X, Y coordinates on the minimap
- Timestamp
- Team affiliation (purple or orange)

### 4. Heatmap Generation
The generator:
- Converts minimap coordinates to full map coordinates
- Applies Gaussian blur for smooth visualization
- Creates color-coded overlays (purple for purple team, orange for orange team)
- Blends the heatmaps with the map template

### 5. Visualization
The heatmap uses intensity to show:
- **Darker areas**: More time spent / higher traffic
- **Lighter areas**: Less time spent / lower traffic

## File Formats

### Tracking Data JSON
```json
{
  "purple_team": [
    {"x": 100, "y": 150, "timestamp": 1234567890.123},
    ...
  ],
  "orange_team": [
    {"x": 120, "y": 80, "timestamp": 1234567890.456},
    ...
  ],
  "metadata": {
    "start_time": "2024-01-15T10:30:00",
    "end_time": "2024-01-15T10:40:00",
    "fps": 10,
    "total_frames": 6000
  }
}
```

## Customization

### Adjusting Color Detection
Edit `pokemon_tracker.py` and modify the HSV ranges in the `detect_pokemon_positions` method:

```python
# Purple team
purple_lower = np.array([120, 50, 50])
purple_upper = np.array([160, 255, 255])

# Orange team
orange_lower = np.array([5, 100, 100])
orange_upper = np.array([20, 255, 255])
```

### Adjusting Heatmap Appearance
Modify the Gaussian blur sigma for different spread:
- Lower sigma (10-15): Tighter, more precise heatmaps
- Higher sigma (25-40): Wider, more diffuse heatmaps

### Changing Heatmap Colors
Edit `heatmap_generator.py` in the `create_colored_heatmap` method:

```python
# Purple color (B, G, R)
purple_overlay = self.create_colored_heatmap(
    self.purple_heatmap,
    (180, 50, 180)  # Adjust these RGB values
)

# Orange color (B, G, R)
orange_overlay = self.create_colored_heatmap(
    self.orange_heatmap,
    (0, 140, 255)  # Adjust these RGB values
)
```

## Tips for Best Results

1. **Minimap Template**: Use a clear, high-quality screenshot of the minimap
2. **Capture FPS**: 10 FPS is usually sufficient; higher FPS = more data but larger files
3. **Lighting**: Ensure consistent lighting in your replays for better color detection
4. **Screen Resolution**: Higher resolution captures give more accurate position data
5. **Replay Speed**: Normal or slightly slower replay speed works best
6. **Map Template**: Use the highest quality full map image you can find

## Troubleshooting

### "Minimap not found on screen"
- Ensure the minimap template matches your current screen
- Try capturing a new minimap template screenshot
- Check that the minimap is visible on screen

### "No Pokémon detected"
- Adjust the HSV color ranges in the code
- Verify the minimap has clear team-colored borders
- Check that the minimap region is being correctly extracted

### Heatmap looks wrong
- Verify minimap dimensions match your actual minimap size
- Adjust the sigma parameter for better blur
- Check coordinate scaling between minimap and full map

## Example Workflow

```bash
# 1. Start tracking
python pokemon_tracker.py --fps 10

# 2. Watch your replay (press Ctrl+C when done)

# 3. Generate heatmap
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp

# 4. Open heatmap_viewer.html in browser to explore

# 5. (Optional) Generate team-specific heatmaps
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --purple-only --output purple_heatmap.png
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --orange-only --output orange_heatmap.png
```

## Advanced Usage

### Batch Processing Multiple Replays
```bash
# Track multiple replays
python pokemon_tracker.py --output replay1.json
# ... watch replay 1, press Ctrl+C
python pokemon_tracker.py --output replay2.json
# ... watch replay 2, press Ctrl+C

# Generate comparison heatmaps
python heatmap_generator.py --map map.webp --data replay1.json --output heatmap1.png
python heatmap_generator.py --map map.webp --data replay2.json --output heatmap2.png
```

### Analyzing Specific Time Periods
You can filter the tracking data JSON to analyze specific portions of matches by editing the timestamp ranges.

## License

This tool is for personal educational use. Pokémon Unite is a trademark of The Pokémon Company.

## Contributing

Feel free to submit issues or pull requests for improvements!
