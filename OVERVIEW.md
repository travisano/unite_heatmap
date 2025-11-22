# Pokémon Unite Heatmap Tracker - Project Overview

## 🎯 What This Does

This tool helps you analyze Pokémon Unite replays by:
1. **Tracking** Pokémon positions from your screen capture
2. **Generating** visual heatmaps showing team movements
3. **Visualizing** the data with an interactive web viewer

## 🎨 Visual Guide

### What You'll Get

**Input**: Your Pokémon Unite replay playing in OBS/screen capture

**Output**: Beautiful heatmaps showing:
- 🟣 Purple team movement patterns (purple heatmap)
- 🟠 Orange team movement patterns (orange heatmap)
- 📍 Hot spots where teams spend the most time
- 🗺️ Full map visualization with overlay

## 📁 File Structure

```
pokemon-unite-heatmap/
│
├── 🐍 Python Scripts (Core Functionality)
│   ├── pokemon_tracker.py      # Captures positions from screen
│   ├── heatmap_generator.py    # Creates heatmap images
│   └── launcher.py             # Easy-to-use menu interface
│
├── 🌐 Web Interface
│   └── heatmap_viewer.html     # Interactive viewer with controls
│
├── 🖼️ Image Files
│   ├── show.png                # Minimap template for detection
│   └── image-*.webp            # Full map template for overlay
│
├── 📊 Sample Data
│   └── sample_tracking_data.json  # Example tracking data
│
└── 📚 Documentation
    ├── SETUP.md                # Installation instructions
    ├── QUICKSTART.md           # Getting started guide
    └── README.md               # Complete documentation
```

## 🔄 Workflow

### Simple 3-Step Process

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: TRACK                                              │
│  ─────────────────────────────────────────────────────────  │
│  Run: python pokemon_tracker.py                             │
│                                                              │
│  • Watches your screen/OBS                                  │
│  • Finds the minimap automatically                          │
│  • Tracks purple & orange Pokémon positions                 │
│  • Saves to tracking_data.json                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: GENERATE                                           │
│  ─────────────────────────────────────────────────────────  │
│  Run: python heatmap_generator.py --map yourmap.webp        │
│                                                              │
│  • Reads tracking_data.json                                 │
│  • Converts positions to full map coordinates               │
│  • Applies Gaussian blur for smooth visualization           │
│  • Creates heatmap.png                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: VIEW                                               │
│  ─────────────────────────────────────────────────────────  │
│  Open: heatmap_viewer.html in browser                       │
│                                                              │
│  • Interactive controls                                     │
│  • Toggle teams on/off                                      │
│  • Adjust intensity                                         │
│  • View statistics                                          │
└─────────────────────────────────────────────────────────────┘
```

## 🎛️ Features Breakdown

### Pokemon Tracker (`pokemon_tracker.py`)

**What it does:**
- Automatically finds the minimap on your screen
- Uses color detection to identify purple and orange team Pokémon
- Records X, Y coordinates and timestamps
- Saves data in JSON format

**Key Features:**
- ⚡ Real-time tracking at configurable FPS
- 🎯 Template-based minimap detection
- 🎨 HSV color-based Pokémon identification
- 💾 Continuous data saving

### Heatmap Generator (`heatmap_generator.py`)

**What it does:**
- Converts minimap coordinates to full map coordinates
- Creates smooth heatmaps using Gaussian blur
- Generates color-coded team overlays
- Blends heatmaps with map template

**Key Features:**
- 🗺️ Coordinate scaling and transformation
- 🌊 Gaussian smoothing for professional look
- 🎨 Customizable colors and intensity
- 📸 High-quality PNG output

### Interactive Viewer (`heatmap_viewer.html`)

**What it does:**
- Displays heatmaps in your web browser
- Provides interactive controls
- Shows real-time statistics
- Supports custom data and map loading

**Key Features:**
- ✅ Team toggle checkboxes
- 🎚️ Intensity slider
- 📁 File upload support
- 📊 Statistics display
- 🎨 Beautiful UI design

### Launcher (`launcher.py`)

**What it does:**
- Provides easy menu-based interface
- Guides you through the workflow
- Checks system files
- Runs complete workflow automatically

**Key Features:**
- 📋 Interactive menu
- 🔍 System file checking
- 🚀 One-command workflow
- 💡 Helpful prompts

## 🎓 Use Cases

### For Players
- 📈 Analyze your positioning habits
- 🎯 Identify optimal farming routes
- 🛡️ Review defensive patterns
- ⚔️ Study aggressive plays

### For Coaches
- 👥 Compare team strategies
- 📊 Analyze opponent patterns
- 📝 Create training materials
- 🎥 Review match VODs

### For Content Creators
- 🎬 Create analysis videos
- 📱 Generate social media content
- 📚 Make educational guides
- 🏆 Showcase gameplay stats

## 🔧 Technical Details

### Color Detection

**Purple Team:**
- HSV Range: [120-160, 50-255, 50-255]
- Represents: Purple border on Pokémon icons

**Orange Team:**
- HSV Range: [5-20, 100-255, 100-255]
- Represents: Orange border on Pokémon icons

### Coordinate Transformation

```
Minimap (200x200) → Full Map (1280x720)
Scale X: 1280 / 200 = 6.4x
Scale Y: 720 / 200 = 3.6x
```

### Heatmap Algorithm

1. Create empty matrix (map size)
2. Add points at each Pokémon position
3. Apply Gaussian blur (configurable sigma)
4. Normalize to 0-1 range
5. Blend with map image

## 📊 Data Format

### Tracking Data JSON

```json
{
  "purple_team": [
    {
      "x": 100,           // X coordinate on minimap
      "y": 150,           // Y coordinate on minimap
      "timestamp": 1234567890.123  // Unix timestamp
    }
  ],
  "orange_team": [ ... ],
  "metadata": {
    "start_time": "2024-11-22T01:00:00",
    "end_time": "2024-11-22T01:10:00",
    "fps": 10,
    "total_frames": 6000
  }
}
```

## 🎨 Customization Options

### Adjust Tracking
- `--fps`: Capture rate (higher = more data, more CPU)
- `--minimap`: Different minimap template
- `--output`: Custom output filename

### Adjust Heatmap
- `--sigma`: Blur amount (10-40 recommended)
- `--purple-only`: Show only purple team
- `--orange-only`: Show only orange team
- `--minimap-width/height`: Minimap dimensions

### Adjust Colors
Edit the code to change:
- Heatmap colors (RGB values)
- Detection ranges (HSV values)
- Transparency/opacity

## 📈 Performance

### Recommended Settings

**For Basic Analysis:**
- FPS: 5-10
- Sigma: 20
- Resolution: Standard (1920x1080)

**For Detailed Analysis:**
- FPS: 15-30
- Sigma: 10-15
- Resolution: High (2560x1440+)

**For Quick Review:**
- FPS: 3-5
- Sigma: 30-40
- Resolution: Any

## 🚀 Quick Commands Cheat Sheet

```bash
# Install dependencies
pip install opencv-python numpy pillow matplotlib scipy

# Interactive launcher
python launcher.py

# Quick track (10 FPS)
python pokemon_tracker.py

# Generate heatmap
python heatmap_generator.py --map map.webp

# Complete workflow
python launcher.py --workflow --minimap show.png --map map.webp

# Team-specific heatmaps
python heatmap_generator.py --map map.webp --purple-only
python heatmap_generator.py --map map.webp --orange-only

# Custom settings
python pokemon_tracker.py --fps 15 --output match1.json
python heatmap_generator.py --map map.webp --sigma 15 --data match1.json
```

## 📚 Documentation Guide

- **New users**: Start with `SETUP.md` then `QUICKSTART.md`
- **Advanced users**: See `README.md` for all options
- **Troubleshooting**: Check README troubleshooting section
- **Reference**: This overview for quick lookup

## 🎯 Success Criteria

You'll know it's working when:
- ✅ Tracker finds minimap and shows positions detected
- ✅ Generator creates heatmap.png file
- ✅ Viewer displays heatmap with controls working
- ✅ Statistics show reasonable position counts

## 🌟 Next-Level Features

After mastering the basics, try:
- 📊 Combine multiple matches for meta-analysis
- 🎥 Create time-lapse heatmap videos
- 📈 Export data to spreadsheets for stats
- 🤖 Train ML models on positioning patterns

---

**Ready to analyze your gameplay? Start with SETUP.md!** 🎮

