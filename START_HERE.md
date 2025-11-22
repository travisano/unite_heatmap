# 🎮 Pokémon Unite Heatmap Tracker

## ⚡ Quick Start (30 seconds)

```bash
# 1. Install dependencies (one time)
pip install opencv-python numpy pillow matplotlib scipy

# 2. Run the launcher
python launcher.py

# 3. Follow the menu!
```

That's it! The launcher will guide you through everything.

## 📖 New User? Start Here!

**Read these files in order:**

1. **[INDEX.md](INDEX.md)** ← **START HERE!** Navigation guide
2. **[SETUP.md](SETUP.md)** - Install and setup
3. **[QUICKSTART.md](QUICKSTART.md)** - First use guide
4. **[README.md](README.md)** - Full documentation

## 🎯 What This Tool Does

Track Pokémon positions from replays → Generate beautiful heatmaps → Analyze team strategies

**Detects 0-10 Pokémon per frame** (up to 5 per team) 🎯  
**Purple team** gets purple heatmaps 🟣  
**Orange team** gets orange heatmaps 🟠  
Darker = more time spent in that area

The tracker automatically detects all visible Pokémon on both teams using color detection.

## 📁 Files Included

### Essential Scripts
- `pokemon_tracker.py` - Tracks Pokémon from your screen
- `heatmap_generator.py` - Creates heatmap visualizations
- `launcher.py` - Easy menu-based interface ⭐ Use this!
- `heatmap_viewer.html` - Interactive web viewer

### Documentation
- `INDEX.md` - Start here! Navigation guide
- `SETUP.md` - Installation instructions
- `QUICKSTART.md` - Getting started guide
- `OVERVIEW.md` - Project overview
- `README.md` - Complete documentation

### Templates & Samples
- `show.png` - Minimap template
- `image-*.webp` - Full map template
- `sample_tracking_data.json` - Example data

## 🚀 Three Ways to Get Started

### 1️⃣ Interactive Launcher (Easiest!)
```bash
python launcher.py
```
Menu-driven interface. Perfect for beginners!

### 2️⃣ Step-by-Step Commands
```bash
# Track positions
python pokemon_tracker.py

# Generate heatmap
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp

# Open viewer
# Double-click heatmap_viewer.html
```

### 3️⃣ All-in-One Command
```bash
python launcher.py --workflow
```
Does everything automatically!

## ✅ Verify Installation

```bash
python launcher.py
```

If you see a menu, you're ready! Select option 5 to check all files.

## 🎮 Typical Workflow

1. **Start** your Pokémon Unite replay in OBS
2. **Run** `python pokemon_tracker.py`
3. **Watch** the replay (tracker runs in background)
4. **Press** Ctrl+C when done
5. **Generate** heatmap with launcher or generator script
6. **View** results in heatmap_viewer.html

## 📊 What You'll Get

- **tracking_data.json** - All position data
- **heatmap.png** - Visual heatmap image
- **Interactive viewer** - Explore with controls

## 🆘 Quick Troubleshooting

**"Minimap not found"**
→ Make sure minimap is visible on screen

**"No Pokémon detected"**
→ Check that replays have team-colored borders

**"Package not found"**
→ Run: `pip install opencv-python numpy pillow matplotlib scipy`

**Need more help?**
→ Check the troubleshooting sections in README.md

## 🎯 Next Steps

After installation:
1. Test with sample data: `python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data sample_tracking_data.json`
2. Open `heatmap_viewer.html` to see results
3. Try tracking your own replay!

## 📚 Documentation Quick Links

- **Installation Help** → [SETUP.md](SETUP.md)
- **Usage Guide** → [QUICKSTART.md](QUICKSTART.md)
- **Common Questions** → [FAQ_DETAILED.md](FAQ_DETAILED.md) ⭐ NEW!
- **Full Docs** → [README.md](README.md)
- **Navigation** → [INDEX.md](INDEX.md)
- **Overview** → [OVERVIEW.md](OVERVIEW.md)
- **Minimap Details** → [MINIMAP_GUIDE.md](MINIMAP_GUIDE.md)

## 💡 Pro Tips

- Use `launcher.py` for easiest experience
- Test with `sample_tracking_data.json` first
- Normal/slower replay speed works best
- 10 FPS is usually sufficient for tracking

## 🌟 Features

✅ Automatic minimap detection  
✅ Color-based Pokémon tracking  
✅ Beautiful heatmap visualization  
✅ Interactive web viewer  
✅ Team-specific analysis  
✅ Adjustable intensity  
✅ Easy-to-use launcher  

---

**Ready to start? Open [INDEX.md](INDEX.md) for your personalized starting path!** 🚀

Or just run: `python launcher.py` and follow the menu! 🎮
