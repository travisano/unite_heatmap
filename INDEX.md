# 🎮 Pokémon Unite Heatmap Tracker - Start Here!

Welcome to your complete Pokémon Unite position tracking and heatmap analysis toolkit!

## 🚀 Getting Started (Choose Your Path)

### 👶 Complete Beginner?
1. Read **[SETUP.md](SETUP.md)** - Install everything
2. Read **[QUICKSTART.md](QUICKSTART.md)** - Use the tool
3. Run `python launcher.py` - Start tracking!

### 🎓 Familiar with Python?
1. Install: `pip install opencv-python numpy pillow matplotlib scipy`
2. Run: `python launcher.py --workflow`
3. Done! ✅

### 🚀 Just Want to Try It?
1. Run: `python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data sample_tracking_data.json`
2. Open: `heatmap_viewer.html` in your browser
3. See what it does!

## 📚 Documentation Index

| File | Purpose | When to Read |
|------|---------|--------------|
| **[OVERVIEW.md](OVERVIEW.md)** | Project overview & features | Want to understand what this does |
| **[SETUP.md](SETUP.md)** | Installation instructions | First time setting up |
| **[QUICKSTART.md](QUICKSTART.md)** | Quick start guide | Ready to start using it |
| **[README.md](README.md)** | Complete documentation | Need detailed info |
| **[MULTI_POKEMON_DETECTION.md](MULTI_POKEMON_DETECTION.md)** | Multi-Pokémon tracking details | Want to know how 0-10 Pokémon detection works |
| **INDEX.md** | This file! | Finding your way around |

## 🎯 What Each File Does

### 📂 Core Scripts

| File | What It Does | When to Use |
|------|--------------|-------------|
| `pokemon_tracker.py` | Captures Pokémon positions from screen | When watching replays |
| `heatmap_generator.py` | Creates heatmap images | After tracking data is collected |
| `heatmap_viewer.html` | Interactive web viewer | To view and explore heatmaps |
| `launcher.py` | Easy menu interface | Easiest way to run everything |

### 🖼️ Image Files

| File | What It Is | How to Use |
|------|-----------|------------|
| `show.png` | Minimap template | Used for minimap detection |
| `image-*.webp` | Full map template | Background for heatmaps |

### 📊 Data Files

| File | What It Contains | When Created |
|------|-----------------|--------------|
| `sample_tracking_data.json` | Example tracking data | Included for testing |
| `tracking_data.json` | Your actual tracking data | Created when you run tracker |
| `heatmap.png` | Generated heatmap image | Created by heatmap generator |

## 🎮 Common Workflows

### Workflow 1: First Time User

```bash
# Step 1: Setup (one time)
pip install opencv-python numpy pillow matplotlib scipy

# Step 2: Test with sample data
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data sample_tracking_data.json

# Step 3: Open viewer
# Double-click heatmap_viewer.html

# Step 4: Read the guides
# Open QUICKSTART.md
```

### Workflow 2: Analyze a Replay

```bash
# Step 1: Start tracking
python pokemon_tracker.py
# (Press Ctrl+C when done)

# Step 2: Generate heatmap
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp

# Step 3: View results
# Open heatmap_viewer.html and load tracking_data.json
```

### Workflow 3: Using the Launcher (Easiest!)

```bash
# Just run the launcher
python launcher.py

# Then select from menu:
# 1 = Track positions
# 2 = Generate heatmap
# 3 = Open viewer
# 4 = Do all three automatically
```

## ❓ Quick FAQ

### How do I start tracking?
```bash
python pokemon_tracker.py
```
or
```bash
python launcher.py
```
Then choose option 1.

### Can it track all 5 Pokémon per team?
**Yes!** The system detects up to 5 Pokémon per team (10 total) in each frame. It uses color detection to find all purple and orange team borders on the minimap. See [MULTI_POKEMON_DETECTION.md](MULTI_POKEMON_DETECTION.md) for details.

### How do I know if all Pokémon are being detected?
The tracker shows detection counts every 3 seconds:
```
Frame 30: Detected 4 purple, 5 orange Pokémon
```
And provides averages when complete. Typically you'll see 7-10 Pokémon/frame depending on the match.

### How do I make a heatmap?
```bash
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp
```
or use the launcher menu option 2.

### How do I view my heatmap?
Double-click `heatmap_viewer.html` or use launcher option 3.

### Where's my data saved?
- Tracking data: `tracking_data.json`
- Heatmap image: `heatmap.png`
- All in the same folder as the scripts

### Can I change the colors?
Yes! Edit the color values in `heatmap_generator.py` or adjust in the viewer.

### How accurate is the tracking?
Very accurate! It depends on:
- Screen resolution (higher = better)
- Capture FPS (higher = more data points)
- Minimap visibility (clear = better detection)

## 🎓 Learning Path

### Week 1: Getting Started
- [ ] Read SETUP.md and install everything
- [ ] Run sample data to see what it does
- [ ] Track one replay and generate heatmap

### Week 2: Understanding the Tool
- [ ] Read OVERVIEW.md to understand how it works
- [ ] Experiment with different FPS settings
- [ ] Try team-specific heatmaps

### Week 3: Advanced Usage
- [ ] Read full README.md
- [ ] Adjust color detection ranges
- [ ] Compare multiple matches
- [ ] Create custom analysis

## 🆘 Troubleshooting Quick Links

| Problem | Solution Location |
|---------|------------------|
| Installation issues | [SETUP.md](SETUP.md) → Troubleshooting Installation |
| Can't find minimap | [README.md](README.md) → Troubleshooting |
| No Pokémon detected | [README.md](README.md) → Troubleshooting |
| Heatmap looks wrong | [QUICKSTART.md](QUICKSTART.md) → Common Issues |
| Python errors | [SETUP.md](SETUP.md) → Troubleshooting Installation |

## 📋 Checklist: Am I Ready to Use This?

Before you start tracking, make sure you have:

- [ ] Python 3.8+ installed
- [ ] All required packages installed
- [ ] All files in the same folder
- [ ] `show.png` (minimap template)
- [ ] `image-*.webp` (map template)
- [ ] Read at least QUICKSTART.md

## 🎯 Quick Commands Reference

```bash
# Most common commands you'll use:

# Interactive launcher (recommended)
python launcher.py

# Track replays
python pokemon_tracker.py

# Generate heatmap
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp

# Complete workflow in one command
python launcher.py --workflow

# Test with sample data
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data sample_tracking_data.json
```

## 🌟 Pro Tips

1. **Start Simple**: Use launcher.py for your first few runs
2. **Test First**: Use sample_tracking_data.json to verify everything works
3. **Read Docs**: QUICKSTART.md has everything you need to know
4. **Experiment**: Try different sigma values and FPS settings
5. **Have Fun**: The tool is powerful but easy to use!

## 📞 Need More Help?

1. Check the relevant documentation file above
2. Review the troubleshooting sections
3. Try with sample data to isolate issues
4. Run launcher.py option 5 to check files

## 🚀 Ready to Go?

### Option A: I Want to Learn
Read in this order:
1. OVERVIEW.md (understand the project)
2. SETUP.md (install everything)
3. QUICKSTART.md (start using it)
4. README.md (advanced features)

### Option B: I Just Want to Use It
1. Run: `pip install opencv-python numpy pillow matplotlib scipy`
2. Run: `python launcher.py`
3. Follow the menu!

### Option C: I Want to See It First
1. Run: `python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data sample_tracking_data.json`
2. Open: `heatmap_viewer.html`
3. Explore the example heatmap!

---

## 📂 Full File Listing

```
pokemon-unite-heatmap/
├── 📜 Documentation
│   ├── INDEX.md (You are here!)
│   ├── OVERVIEW.md (Project overview)
│   ├── SETUP.md (Installation guide)
│   ├── QUICKSTART.md (Quick start guide)
│   └── README.md (Complete documentation)
│
├── 🐍 Python Scripts
│   ├── pokemon_tracker.py (Position tracker)
│   ├── heatmap_generator.py (Heatmap creator)
│   └── launcher.py (Easy launcher)
│
├── 🌐 Web Interface
│   └── heatmap_viewer.html (Interactive viewer)
│
├── 🖼️ Templates
│   ├── show.png (Minimap template)
│   └── image-*.webp (Map template)
│
└── 📊 Sample Data
    └── sample_tracking_data.json (Example data)
```

---

**Choose your path above and get started! Happy tracking! 🎮📊**

