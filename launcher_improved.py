#!/usr/bin/env python3
"""
Pokemon Unite Advanced Heatmap Tracker
=======================================
Features:
- 600-second (10 minute) capture with 1 FPS
- Buffered screenshot capture to tmp/ folder
- Post-processing for players, creeps, and objectives
- Custom heatmap colors (#FF9A00 orange, #AF4CFF purple)
- Creep and objective uptime tracking
- Proper map aspect ratio matching (Theia Sky Ruins)
"""

import cv2
import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import sys
import shutil

# ============================================================================
# CONFIGURATION
# ============================================================================
DELETE_SCREENSHOTS_AFTER_PROCESSING = False  # Set to False to keep tmp/ files for debugging

# Heatmap colors
ORANGE_COLOR = (0, 154, 255)  # #FF9A00 in BGR
PURPLE_COLOR = (255, 76, 175)  # #AF4CFF in BGR

# Capture settings
CAPTURE_DURATION = 600  # 10 minutes in seconds
CAPTURE_FPS = 1  # 1 screenshot per second

# ============================================================================
# IMPORTS
# ============================================================================
try:
    from PIL import ImageGrab
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    print("❌ Error: Please install Pillow")
    print("   Run: pip install pillow")
    sys.exit(1)

try:
    from pokemon_detector import detect_pokemon_markers
    from creep_objective_detector import detect_creeps, detect_objectives, cluster_positions
except ImportError:
    print("❌ Error: Missing detector modules!")
    print("   Make sure pokemon_detector.py and creep_objective_detector.py are in the same folder.")
    sys.exit(1)


class AdvancedPokemonTracker:
    def __init__(self):
        self.tmp_dir = Path("tmp")
        self.output_dir = Path("outputs")
        
        # Create directories
        self.tmp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Clear old tmp files
        for f in self.tmp_dir.glob("*"):
            if f.is_file():
                f.unlink()
        
        # Reference map
        self.reference_map_path = Path("theiaskyruins.png")
        if not self.reference_map_path.exists():
            print(f"⚠️  Warning: Reference map not found: {self.reference_map_path}")
            self.reference_map = None
        else:
            self.reference_map = cv2.imread(str(self.reference_map_path))
            print(f"✅ Loaded reference map: {self.reference_map.shape}")
        
        # Tracking state
        self.minimap_detected = False
        self.start_time = None
        self.screenshots_captured = 0
        self.minimap_region = None
        
    def capture_screen(self):
        """Capture full screen"""
        try:
            screenshot = ImageGrab.grab()
            screen = np.array(screenshot)
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
            return screen
        except Exception as e:
            print(f"❌ Error capturing screen: {e}")
            return None
    
    def find_minimap_region(self, screen):
        """
        Find minimap by detecting colored Pokemon markers.
        STRICT DETECTION: Requires multiple Pokemon markers and proper circular map structure.
        Returns (x1, y1, x2, y2) or None
        """
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        h, w = screen.shape[:2]
        
        # First, detect white pixels (Pokemon markers have WHITE centers)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Detect small circles (Pokemon markers)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=10,
            param1=50,
            param2=15,
            minRadius=8,
            maxRadius=16
        )
        
        if circles is None:
            return None
        
        circles = np.uint16(np.around(circles))
        
        # Filter to Pokemon markers only (must have WHITE center + colored ring)
        pokemon_circles = []
        
        for circle in circles[0]:
            cx, cy, r = circle
            if cx < 5 or cy < 5 or cx >= w-5 or cy >= h-5:
                continue
            
            # CRITICAL: Must have white center (Pokemon face)
            center_mask = np.zeros(white_mask.shape, dtype=np.uint8)
            cv2.circle(center_mask, (cx, cy), max(2, r-2), 255, -1)
            white_in_center = cv2.bitwise_and(white_mask, center_mask)
            white_count = cv2.countNonZero(white_in_center)
            
            if white_count < 3:  # No white center = not a Pokemon
                continue
            
            # Sample the ring
            ring_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            cv2.circle(ring_mask, (cx, cy), r, 255, 2)
            ring_hsv = cv2.bitwise_and(hsv, hsv, mask=ring_mask)
            
            # Check for orange
            lower_orange = np.array([0, 70, 70])
            upper_orange = np.array([30, 255, 255])
            orange_mask = cv2.inRange(ring_hsv, lower_orange, upper_orange)
            orange_pixels = cv2.countNonZero(orange_mask)
            
            # Check for purple/blue
            lower_purple = np.array([100, 30, 30])
            upper_purple = np.array([160, 255, 255])
            purple_mask = cv2.inRange(ring_hsv, lower_purple, upper_purple)
            purple_pixels = cv2.countNonZero(purple_mask)
            
            # Must have colored ring
            if orange_pixels > 8 or purple_pixels > 8:
                pokemon_circles.append([cx, cy, r])
        
        # STRICT: Need at least 5 Pokemon markers for valid minimap
        if len(pokemon_circles) < 5:
            return None
        
        # Find densest cluster
        cell_size = 280
        best_x, best_y, best_count = 0, 0, 0
        
        for y in range(0, max(1, h - cell_size), 30):
            for x in range(0, max(1, w - cell_size), 30):
                count = sum(1 for cx, cy, r in pokemon_circles 
                           if x <= cx < x + cell_size and y <= cy < y + cell_size)
                if count > best_count:
                    best_count = count
                    best_x, best_y = x, y
        
        # Need at least 5 Pokemon in the region
        if best_count < 5:
            return None
        
        # Get circles in best region
        minimap_circles = [[cx, cy, r] for cx, cy, r in pokemon_circles
                          if best_x <= cx < best_x + cell_size and best_y <= cy < best_y + cell_size]
        
        if len(minimap_circles) < 5:
            return None
        
        # Calculate bounding box
        minimap_circles = np.array(minimap_circles)
        min_x = np.min(minimap_circles[:, 0] - minimap_circles[:, 2])
        max_x = np.max(minimap_circles[:, 0] + minimap_circles[:, 2])
        min_y = np.min(minimap_circles[:, 1] - minimap_circles[:, 2])
        max_y = np.max(minimap_circles[:, 1] + minimap_circles[:, 2])
        
        # Check if this looks like a circular minimap
        width_bbox = max_x - min_x
        height_bbox = max_y - min_y
        
        # Minimap should be roughly square/circular (not a vertical character portrait)
        aspect = width_bbox / height_bbox if height_bbox > 0 else 0
        if aspect < 0.7 or aspect > 1.4:  # Too elongated = not minimap
            return None
        
        # Add padding and adjust to match reference map aspect ratio
        padding = 45
        x1 = max(0, int(min_x) - padding)
        y1 = max(0, int(min_y) - padding)
        x2 = min(w, int(max_x) + padding)
        y2 = min(h, int(max_y) + padding)
        
        # Match aspect ratio to reference map if available
        if self.reference_map is not None:
            ref_h, ref_w = self.reference_map.shape[:2]
            ref_aspect = ref_w / ref_h
            
            current_w = x2 - x1
            current_h = y2 - y1
            current_aspect = current_w / current_h
            
            # Adjust to match reference aspect ratio
            if current_aspect > ref_aspect:
                # Too wide, increase height
                target_h = int(current_w / ref_aspect)
                diff = target_h - current_h
                y1 = max(0, y1 - diff // 2)
                y2 = min(h, y2 + diff // 2)
            else:
                # Too tall, increase width
                target_w = int(current_h * ref_aspect)
                diff = target_w - current_w
                x1 = max(0, x1 - diff // 2)
                x2 = min(w, x2 + diff // 2)
        
        # Size validation (minimap is usually 200-400 pixels)
        width = x2 - x1
        height = y2 - y1
        
        if width < 180 or height < 180 or width > 450 or height > 450:
            return None
        
        # FINAL CHECK: This region should be in a corner (minimaps are typically in corners)
        # Not strictly enforced but provides additional validation
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Allow anywhere for now, but log position for debugging
        print(f"      Minimap candidate at ({x1}, {y1}) size {width}x{height}, {len(minimap_circles)} Pokemon")
        
        return (x1, y1, x2, y2)
    
    def capture_phase(self):
        """
        Phase 1: Capture screenshots
        Wait for minimap detection, then capture for 600 seconds at 1 FPS
        """
        print("\n" + "="*70)
        print("🎮 POKEMON UNITE ADVANCED TRACKER")
        print("="*70)
        print("\n📸 PHASE 1: SCREENSHOT CAPTURE")
        print(f"   Duration: {CAPTURE_DURATION} seconds ({CAPTURE_DURATION//60} minutes)")
        print(f"   Rate: {CAPTURE_FPS} screenshot per second")
        print(f"   Total screenshots: {CAPTURE_DURATION}")
        print("\n🔍 Waiting for minimap detection...")
        
        last_capture_time = 0
        
        while self.screenshots_captured < CAPTURE_DURATION:
            current_time = time.time()
            
            # Capture screen
            screen = self.capture_screen()
            if screen is None:
                time.sleep(0.1)
                continue
            
            # Find minimap
            if self.minimap_region is None:
                minimap_region = self.find_minimap_region(screen)
                
                if minimap_region is not None:
                    self.minimap_region = minimap_region
                    self.minimap_detected = True
                    self.start_time = current_time
                    print(f"\n✅ Minimap detected at: {minimap_region}")
                    print(f"🎬 Starting capture... (Press Ctrl+C to stop early)\n")
                else:
                    # Still searching
                    time.sleep(0.1)
                    continue
            
            # Check if it's time for next capture (1 per second)
            if current_time - last_capture_time >= 1.0:
                # Extract minimap
                x1, y1, x2, y2 = self.minimap_region
                minimap = screen[y1:y2, x1:x2]
                
                # Save screenshot
                screenshot_path = self.tmp_dir / f"screenshot_{self.screenshots_captured:04d}.png"
                cv2.imwrite(str(screenshot_path), minimap)
                
                self.screenshots_captured += 1
                last_capture_time = current_time
                
                elapsed = current_time - self.start_time
                remaining = CAPTURE_DURATION - elapsed
                
                # Progress update every 10 seconds
                if self.screenshots_captured % 10 == 0:
                    print(f"   📸 {self.screenshots_captured}/{CAPTURE_DURATION} "
                          f"({elapsed:.0f}s elapsed, {remaining:.0f}s remaining)")
            else:
                time.sleep(0.05)
        
        print(f"\n✅ Capture complete! {self.screenshots_captured} screenshots saved to tmp/")
    
    def processing_phase(self):
        """
        Phase 2: Process all screenshots
        Detect players, creeps, and objectives
        """
        print("\n" + "="*70)
        print("🔬 PHASE 2: PROCESSING SCREENSHOTS")
        print("="*70)
        
        # Initialize tracking data
        purple_positions = []
        orange_positions = []
        creep_detections = []  # List of all creep detections with frame number
        objective_detections = []  # List of all objective detections with frame number
        
        screenshot_files = sorted(self.tmp_dir.glob("screenshot_*.png"))
        total_files = len(screenshot_files)
        
        print(f"\n📊 Processing {total_files} screenshots...")
        print("   Detecting: Players, Creeps, Objectives\n")
        
        for i, screenshot_path in enumerate(screenshot_files):
            # Load screenshot
            minimap = cv2.imread(str(screenshot_path))
            if minimap is None:
                continue
            
            # Detect players
            markers, _, _ = detect_pokemon_markers(minimap)
            for marker in markers:
                pos = marker['position']
                if marker['team'] == 'orange':
                    orange_positions.append({'x': pos[0], 'y': pos[1]})
                else:
                    purple_positions.append({'x': pos[0], 'y': pos[1]})
            
            # Detect creeps
            creeps = detect_creeps(minimap)
            for creep in creeps:
                creep_detections.append({
                    'frame': i,
                    'position': creep['position'],
                    'size': creep['size']
                })
            
            # Detect objectives
            objectives = detect_objectives(minimap)
            for obj in objectives:
                objective_detections.append({
                    'frame': i,
                    'position': obj['position']
                })
            
            # Progress update
            if (i + 1) % 50 == 0 or (i + 1) == total_files:
                print(f"   🔄 {i+1}/{total_files} processed "
                      f"(Players: {len(orange_positions) + len(purple_positions)}, "
                      f"Creeps: {len(creep_detections)}, "
                      f"Objectives: {len(objective_detections)})")
        
        print(f"\n✅ Processing complete!")
        print(f"   Purple positions: {len(purple_positions)}")
        print(f"   Orange positions: {len(orange_positions)}")
        print(f"   Creep detections: {len(creep_detections)}")
        print(f"   Objective detections: {len(objective_detections)}")
        
        return purple_positions, orange_positions, creep_detections, objective_detections
    
    def generate_final_output(self, purple_positions, orange_positions, 
                             creep_detections, objective_detections):
        """
        Phase 3: Generate final heatmap with overlays
        """
        print("\n" + "="*70)
        print("🎨 PHASE 3: GENERATING FINAL HEATMAP")
        print("="*70)
        
        # CRITICAL: Use reference map as base, NOT a screenshot
        if self.reference_map is None:
            print("❌ Error: Reference map (theiaskyruins.png) not found!")
            print("   Cannot generate heatmap without base map.")
            return None
        
        base_minimap = self.reference_map.copy()
        height, width = base_minimap.shape[:2]
        print(f"   Using reference map: {width}x{height}")
        
        # Get the size of captured minimap for coordinate scaling
        screenshot_files = sorted(self.tmp_dir.glob("screenshot_*.png"))
        if screenshot_files:
            sample_screenshot = cv2.imread(str(screenshot_files[0]))
            if sample_screenshot is not None:
                capture_h, capture_w = sample_screenshot.shape[:2]
                scale_x = width / capture_w
                scale_y = height / capture_h
                print(f"   Scaling coordinates: {capture_w}x{capture_h} → {width}x{height}")
            else:
                scale_x = scale_y = 1.0
        else:
            scale_x = scale_y = 1.0
        
        # ====================================================================
        # Generate heatmaps with custom colors
        # ====================================================================
        print("   🎨 Generating heatmaps...")
        
        heatmap_orange = np.zeros((height, width), dtype=np.float32)
        heatmap_purple = np.zeros((height, width), dtype=np.float32)
        
        # Accumulate positions with scaling
        for pos in orange_positions:
            x, y = int(pos['x'] * scale_x), int(pos['y'] * scale_y)
            if 0 <= x < width and 0 <= y < height:
                heatmap_orange[y, x] += 1
        
        for pos in purple_positions:
            x, y = int(pos['x'] * scale_x), int(pos['y'] * scale_y)
            if 0 <= x < width and 0 <= y < height:
                heatmap_purple[y, x] += 1
        
        # Apply Gaussian blur
        if heatmap_orange.max() > 0:
            heatmap_orange = cv2.GaussianBlur(heatmap_orange, (25, 25), 0)
            # Normalize to 0-1 range
            heatmap_orange = heatmap_orange / heatmap_orange.max()
        
        if heatmap_purple.max() > 0:
            heatmap_purple = cv2.GaussianBlur(heatmap_purple, (25, 25), 0)
            # Normalize to 0-1 range
            heatmap_purple = heatmap_purple / heatmap_purple.max()
        
        # Create overlay with custom colors
        overlay = base_minimap.copy().astype(np.float32)
        
        for y in range(height):
            for x in range(width):
                # Orange heatmap (1% min intensity, 100% at max)
                if heatmap_orange[y, x] > 0:
                    intensity = 0.01 + heatmap_orange[y, x] * 0.99  # 1% to 100%
                    alpha = min(intensity * 0.6, 0.8)  # Max 80% opacity
                    overlay[y, x] = overlay[y, x] * (1 - alpha) + np.array(ORANGE_COLOR) * alpha
                
                # Purple heatmap (1% min intensity, 100% at max)
                if heatmap_purple[y, x] > 0:
                    intensity = 0.01 + heatmap_purple[y, x] * 0.99  # 1% to 100%
                    alpha = min(intensity * 0.6, 0.8)  # Max 80% opacity
                    overlay[y, x] = overlay[y, x] * (1 - alpha) + np.array(PURPLE_COLOR) * alpha
        
        final_output = overlay.astype(np.uint8)
        
        # ====================================================================
        # Cluster and overlay creeps with uptime (with coordinate scaling)
        # ====================================================================
        print("   🟡 Processing creep camps...")
        
        creep_camps = cluster_positions(creep_detections, distance_threshold=15)
        
        for camp_id, detections in creep_camps.items():
            if not detections:
                continue
            
            # Calculate average position and scale to reference map
            avg_x = int(np.mean([d['position'][0] for d in detections]) * scale_x)
            avg_y = int(np.mean([d['position'][1] for d in detections]) * scale_y)
            
            # Bounds check
            if avg_x < 10 or avg_y < 10 or avg_x >= width - 10 or avg_y >= height - 10:
                continue
            
            # Calculate uptime in seconds
            uptime_seconds = len(detections)
            minutes = uptime_seconds // 60
            seconds = uptime_seconds % 60
            uptime_text = f"{minutes:02d}:{seconds:02d}"
            
            # Draw creep indicator - SINGLE YELLOW DOT (not circle)
            cv2.circle(final_output, (avg_x, avg_y), 3, (0, 255, 255), -1)  # Filled yellow dot
            
            # Draw uptime text (larger font)
            cv2.putText(final_output, uptime_text, (avg_x + 8, avg_y + 4),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
        
        print(f"   Found {len(creep_camps)} unique creep camps")
        
        # ====================================================================
        # Cluster and overlay objectives with uptime (with coordinate scaling)
        # ====================================================================
        print("   🎯 Processing objectives...")
        
        objective_camps = cluster_positions(objective_detections, distance_threshold=15)
        
        for camp_id, detections in objective_camps.items():
            if not detections:
                continue
            
            # Calculate average position and scale to reference map
            avg_x = int(np.mean([d['position'][0] for d in detections]) * scale_x)
            avg_y = int(np.mean([d['position'][1] for d in detections]) * scale_y)
            
            # Bounds check
            if avg_x < 10 or avg_y < 10 or avg_x >= width - 10 or avg_y >= height - 10:
                continue
            
            # Calculate uptime in seconds
            uptime_seconds = len(detections)
            minutes = uptime_seconds // 60
            seconds = uptime_seconds % 60
            uptime_text = f"{minutes:02d}:{seconds:02d}"
            
            # Draw objective indicator (different from creep)
            cv2.circle(final_output, (avg_x, avg_y), 12, (0, 255, 255), 2)  # Bright yellow
            cv2.circle(final_output, (avg_x, avg_y), 3, (0, 255, 255), -1)
            
            # Draw uptime text (larger font)
            cv2.putText(final_output, uptime_text, (avg_x + 15, avg_y + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        
        print(f"   Found {len(objective_camps)} unique objectives")
        
        # ====================================================================
        # Save outputs
        # ====================================================================
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        final_path = self.output_dir / f"heatmap_final_{timestamp}.png"
        cv2.imwrite(str(final_path), final_output)
        
        print(f"\n✅ Final heatmap saved: {final_path}")
        
        # Save tracking data JSON
        tracking_data = {
            'purple_team': purple_positions,
            'orange_team': orange_positions,
            'creep_camps': {
                str(camp_id): {
                    'position': (int(np.mean([d['position'][0] for d in detections]) * scale_x),
                               int(np.mean([d['position'][1] for d in detections]) * scale_y)),
                    'uptime_seconds': len(detections),
                    'detections': len(detections)
                }
                for camp_id, detections in creep_camps.items()
            },
            'objective_camps': {
                str(camp_id): {
                    'position': (int(np.mean([d['position'][0] for d in detections]) * scale_x),
                               int(np.mean([d['position'][1] for d in detections]) * scale_y)),
                    'uptime_seconds': len(detections),
                    'detections': len(detections)
                }
                for camp_id, detections in objective_camps.items()
            },
            'metadata': {
                'start_time': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
                'end_time': datetime.now().isoformat(),
                'total_screenshots': self.screenshots_captured,
                'duration_seconds': CAPTURE_DURATION,
                'reference_map': str(self.reference_map_path),
                'scaling': {'x': scale_x, 'y': scale_y}
            }
        }
        
        json_path = self.output_dir / f"tracking_data_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(tracking_data, f, indent=2)
        
        print(f"📊 Tracking data saved: {json_path}")
        
        return final_path
    
    def cleanup(self):
        """Clean up temporary files if configured"""
        if DELETE_SCREENSHOTS_AFTER_PROCESSING:
            print("\n🧹 Cleaning up temporary files...")
            for f in self.tmp_dir.glob("*"):
                if f.is_file():
                    f.unlink()
            print("   ✅ Temporary files deleted")
        else:
            print(f"\n📁 Temporary files kept in: {self.tmp_dir}/")
    
    def start(self):
        """Main execution flow"""
        try:
            # Phase 1: Capture
            self.capture_phase()
            
            # Phase 2: Process
            purple_pos, orange_pos, creep_det, obj_det = self.processing_phase()
            
            # Phase 3: Generate output
            final_path = self.generate_final_output(purple_pos, orange_pos, creep_det, obj_det)
            
            # Cleanup
            self.cleanup()
            
            print("\n" + "="*70)
            print("🎉 ALL DONE!")
            print("="*70)
            print(f"\n📁 Output saved to: outputs/")
            print(f"🖼️  View your heatmap: {final_path}")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            print("Processing captured screenshots so far...")
            
            # Still process what we have
            if self.screenshots_captured > 0:
                purple_pos, orange_pos, creep_det, obj_det = self.processing_phase()
                self.generate_final_output(purple_pos, orange_pos, creep_det, obj_det)
                self.cleanup()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    tracker = AdvancedPokemonTracker()
    tracker.start()


if __name__ == '__main__':
    main()
