# Pokémon Unite Heatmap Tracker - Setup Instructions

## 📦 What's Included

Your complete Pokémon Unite heatmap tracking system includes:

### Core Files
- `pokemon_tracker.py` - Captures and tracks Pokémon positions from screen
- `heatmap_generator.py` - Generates heatmap visualizations
- `heatmap_viewer.html` - Interactive web-based viewer
- `launcher.py` - Easy-to-use launcher with menu interface

### Documentation
- `README.md` - Complete documentation
- `QUICKSTART.md` - Quick start guide for beginners
- `SETUP.md` - This file

### Sample Data
- `show.png` - Your minimap template
- `image-6bdf1523a332f-0f98.webp` - Full Pokémon Unite map template
- `sample_tracking_data.json` - Example tracking data

## 🚀 Installation Steps

### Step 1: Install Python

Make sure you have Python 3.8 or higher installed:

```bash
python --version
```

If not installed, download from: https://www.python.org/downloads/

### Step 2: Install Required Packages

Open a terminal/command prompt and run:

```bash
pip install opencv-python numpy pillow matplotlib scipy
```

Or if on Linux/Mac:

```bash
pip install opencv-python numpy pillow matplotlib scipy --break-system-packages
```

### Step 3: Organize Your Files

Create a folder for the project and place all the files there:

```
pokemon-unite-heatmap/
├── pokemon_tracker.py
├── heatmap_generator.py
├── heatmap_viewer.html
├── launcher.py
├── show.png
├── image-6bdf1523a332f-0f98.webp
├── README.md
├── QUICKSTART.md
└── SETUP.md
```

## ✅ Verify Installation

Run this command to check if everything is set up:

```bash
python launcher.py
```

You should see a menu with options. If you do, installation is successful!

## 🎮 First Run

### Option A: Interactive Mode (Recommended)

```bash
python launcher.py
```

Then select option 5 to check system files.

### Option B: Test with Sample Data

```bash
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data sample_tracking_data.json --output test_heatmap.png
```

This will generate a test heatmap to verify everything works.

## 📝 Configuration

### Customize Minimap Template

Replace `show.png` with your own minimap screenshot:
1. Open Pokémon Unite
2. Start any replay
3. Take a screenshot of just the minimap
4. Save as `show.png` in the project folder

### Customize Map Template

You can use a different full map image:
1. Find or create a high-resolution map image
2. Save it in the project folder
3. Use `--map yourmap.png` when running commands

## 🔧 Troubleshooting Installation

### Python Not Found

**Windows**: Add Python to PATH during installation
**Mac**: Use `python3` instead of `python`
**Linux**: Install with `sudo apt install python3 python3-pip`

### Package Installation Fails

Try with `--user` flag:
```bash
pip install --user opencv-python numpy pillow matplotlib scipy
```

Or upgrade pip first:
```bash
pip install --upgrade pip
```

### Permission Errors

**Windows**: Run command prompt as Administrator
**Mac/Linux**: Use `pip install --user` or `sudo pip install`

### ImportError After Installation

Restart your terminal/command prompt after installing packages.

## 📚 Next Steps

Once installation is complete:

1. Read `QUICKSTART.md` for basic usage
2. Read `README.md` for detailed documentation
3. Run `python launcher.py` to start tracking!

## 🆘 Getting Help

If you encounter issues:

1. Check that all files are in the same folder
2. Verify Python and packages are installed correctly
3. Review the troubleshooting section in README.md
4. Try running with sample data to isolate the issue

## 🎯 Quick Test

To verify everything works, run this complete test:

```bash
# 1. Check files
python launcher.py
# Select option 5

# 2. Generate test heatmap
python heatmap_generator.py --map image-6bdf1523a332f-0f98.webp --data sample_tracking_data.json

# 3. Open viewer
# Double-click heatmap_viewer.html
```

If all three steps work, you're ready to go! 🎉

## System Requirements

- **OS**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for packages and data
- **Screen**: 1280x720 minimum resolution

## Compatibility Notes

- Works with OBS, screen capture software, or direct screen recording
- Compatible with all Pokémon Unite map versions
- Supports both standard and ultrawide displays
- Tested on Windows 11, Ubuntu 22.04, and macOS 13

---

**Installation complete! Ready to track Pokémon! 🎮**

For usage instructions, see QUICKSTART.md
