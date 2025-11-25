#!/usr/bin/env python3
"""
Pokemon Unite Enhanced Real-Time Tracker
=========================================
Features:
- 10-minute (600 second) tracking window
- Screenshot buffering (1 per second)
- Player heatmaps (purple/orange)
- Creep/objective uptime tracking
- Accurate coordinate mapping to Theia Sky Ruins map
"""

import cv2
import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import sys
import shutil

# Import screen capture
try:
    from PIL import ImageGrab
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    print("❌ Error: Please install Pillow")
    print("   Run: pip install pillow")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================
DELETE_TMP_SCREENSHOTS = True  # Set to False to keep screenshots for debugging
MAX_TRACKING_SECONDS = 600     # 10 minutes
SCREENSHOT_INTERVAL = 1.0      # 1 screenshot per second

# Purple/Orange team colors
PURPLE_COLOR = (124, 65, 133)  # #7C4185 in BGR
ORANGE_COLOR = (35, 97, 235)   # #EB6123 in BGR

# Map dimensions (Theia Sky Ruins)
MAP_WIDTH = 560
MAP_HEIGHT = 420


class EnhancedPokemonTracker:
    def __init__(self):
        self.tracking = True
        self.output_dir = Path("outputs")
        self.tmp_dir = Path("tmp_screenshots")
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.tmp_dir.mkdir(exist_ok=True)
        
        # Import detector
        try:
            from pokemon_detector import detect_pokemon_markers
            self.detect_pokemon_markers = detect_pokemon_markers
        except ImportError:
            print("❌ Error: pokemon_detector.py not found!")
            print("   Make sure it's in the same folder.")
            sys.exit(1)
        
        # Tracking data
        self.screenshots = []  # List of (timestamp, screenshot_path, minimap_region)
        self.purple_positions = []  # List of (timestamp, x, y)
        self.orange_positions = []  # List of (timestamp, x, y)
        self.creep_sightings = {}   # {(x, y): [timestamps]}
        self.objective_sightings = {}  # {(x, y): [timestamps]}
        
        self.start_time = None
        self.minimap_detected = False
        self.screenshot_count = 0
        
        # Minimap to map coordinate transform
        self.minimap_size = None  # Will be set when first minimap is detected
        
    def cleanup_tmp_folder(self):
        """Delete tmp screenshots folder if configured"""
        if DELETE_TMP_SCREENSHOTS and self.tmp_dir.exists():
            print(f"\n🗑️  Cleaning up temporary screenshots...")
            shutil.rmtree(self.tmp_dir)
            print(f"   Deleted {self.tmp_dir}")
    
    def minimap_to_map_coords(self, minimap_x, minimap_y, minimap_width, minimap_height):
        """
        Convert minimap coordinates to Theia Sky Ruins map coordinates.
        The minimap is circular but we treat it as fitting within a square.
        """
        # Normalize to 0-1 range
        norm_x = minimap_x / minimap_width
        norm_y = minimap_y / minimap_height
        
        # Map to full map coordinates
        map_x = int(norm_x * MAP_WIDTH)
        map_y = int(norm_y * MAP_HEIGHT)
        
        return map_x, map_y
    
    def detect_creeps_and_objectives(self, minimap):
        """
        Detect creep camps (dark yellow circles) and objectives (yellow Pokemon faces).
        Returns: creeps [(x, y)], objectives [(x, y)]
        """
        hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
        height, width = minimap.shape[:2]
        
        creeps = []
        objectives = []
        
        # Detect DARK YELLOW circles (creeps)
        # Dark yellow: Hue ~20-35, lower saturation and value than bright yellow
        lower_dark_yellow = np.array([15, 60, 60])
        upper_dark_yellow = np.array([40, 255, 200])
        dark_yellow_mask = cv2.inRange(hsv, lower_dark_yellow, upper_dark_yellow)
        
        # Find circles in dark yellow mask
        circles = cv2.HoughCircles(
            dark_yellow_mask,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=10,
            param1=50,
            param2=10,
            minRadius=3,
            maxRadius=10
        )
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0]:
                cx, cy, r = circle
                # Verify it's actually dark yellow
                mask = np.zeros(dark_yellow_mask.shape, dtype=np.uint8)
                cv2.circle(mask, (cx, cy), r, 255, -1)
                overlap = cv2.bitwise_and(dark_yellow_mask, mask)
                if cv2.countNonZero(overlap) > 5:
                    creeps.append((int(cx), int(cy)))
        
        # Detect YELLOW objectives (bright yellow, Pokemon face shape)
        # Bright yellow: Hue ~20-35, high saturation and value
        lower_bright_yellow = np.array([15, 100, 180])
        upper_bright_yellow = np.array([40, 255, 255])
        bright_yellow_mask = cv2.inRange(hsv, lower_bright_yellow, upper_bright_yellow)
        
        # Find contours for objectives (not perfect circles)
        contours, _ = cv2.findContours(bright_yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 500:  # Reasonable size for objectives
                M = cv2.moments(contour)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    
                    # Verify not a countdown timer (timers are in specific regions)
                    # Timers are usually at bottom-center or top-center
                    if not (cy < height * 0.2 or cy > height * 0.8):
                        objectives.append((cx, cy))
        
        return creeps, objectives
    
    def find_minimap_in_frame(self, screen):
        """Find minimap by detecting small colored circular markers (Pokemon)"""
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        h, w = screen.shape[:2]
        
        # Detect small circles (Pokemon markers)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=8,
            param1=50,
            param2=15,
            minRadius=8,
            maxRadius=16
        )
        
        if circles is None:
            return None
        
        circles = np.uint16(np.around(circles))
        
        # Filter circles to only those that are COLORED (orange or purple)
        colored_circles = []
        
        for circle in circles[0]:
            cx, cy, r = circle
            if cx < 3 or cy < 3 or cx >= w-3 or cy >= h-3:
                continue
            
            # Sample the ring of the circle
            ring_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            cv2.circle(ring_mask, (cx, cy), r, 255, 2)
            ring_hsv = cv2.bitwise_and(hsv, hsv, mask=ring_mask)
            
            # Check for orange
            lower_orange = np.array([0, 70, 50])
            upper_orange = np.array([30, 255, 255])
            orange_mask = cv2.inRange(ring_hsv, lower_orange, upper_orange)
            orange_pixels = cv2.countNonZero(orange_mask)
            
            # Check for purple
            lower_purple = np.array([100, 30, 30])
            upper_purple = np.array([160, 255, 255])
            purple_mask = cv2.inRange(ring_hsv, lower_purple, upper_purple)
            purple_pixels = cv2.countNonZero(purple_mask)
            
            # Must have significant colored pixels
            if orange_pixels > 5 or purple_pixels > 5:
                colored_circles.append([cx, cy, r])
        
        # Need at least 3 Pokemon markers
        if len(colored_circles) < 3:
            return None
        
        # Find densest cluster of colored circles
        cell_size = 250
        best_x, best_y = 0, 0
        best_count = 0
        
        for y in range(0, max(1, h - cell_size), 40):
            for x in range(0, max(1, w - cell_size), 40):
                count = 0
                for cx, cy, r in colored_circles:
                    if x <= cx < x + cell_size and y <= cy < y + cell_size:
                        count += 1
                
                if count > best_count:
                    best_count = count
                    best_x, best_y = x, y
        
        if best_count < 3:
            return None
        
        # Get circles in best region
        minimap_circles = []
        for cx, cy, r in colored_circles:
            if best_x <= cx < best_x + cell_size and best_y <= cy < best_y + cell_size:
                minimap_circles.append([cx, cy, r])
        
        if len(minimap_circles) == 0:
            return None
        
        # Get bounding box
        minimap_circles = np.array(minimap_circles)
        min_x = np.min(minimap_circles[:, 0] - minimap_circles[:, 2])
        max_x = np.max(minimap_circles[:, 0] + minimap_circles[:, 2])
        min_y = np.min(minimap_circles[:, 1] - minimap_circles[:, 2])
        max_y = np.max(minimap_circles[:, 1] + minimap_circles[:, 2])
        
        # Add padding
        padding = 50
        x1 = max(0, int(min_x) - padding)
        y1 = max(0, int(min_y) - padding)
        x2 = min(w, int(max_x) + padding)
        y2 = min(h, int(max_y) + padding)
        
        # Make it square (minimap is circular)
        width = x2 - x1
        height = y2 - y1
        size = max(width, height)
        center_x = x1 + width // 2
        center_y = y1 + height // 2
        
        x1 = max(0, center_x - size // 2)
        y1 = max(0, center_y - size // 2)
        x2 = min(w, x1 + size)
        y2 = min(h, y1 + size)
        
        # Size check
        final_width = x2 - x1
        final_height = y2 - y1
        
        if final_width < 150 or final_height < 150 or final_width > 500 or final_height > 500:
            return None
        
        return (x1, y1, x2, y2)
    
    def capture_full_screen(self):
        """Capture entire screen"""
        try:
            screenshot = ImageGrab.grab()
            screen = np.array(screenshot)
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
            return screen
        except Exception as e:
            print(f"❌ Error capturing screen: {e}")
            return None
    
    def tracking_loop(self):
        """Main tracking loop - captures screenshots every second"""
        print("\n" + "="*70)
        print("🎮 POKEMON UNITE ENHANCED TRACKER")
        print("="*70)
        print("\n🎯 Waiting for minimap to appear on screen...")
        print(f"   Will track for {MAX_TRACKING_SECONDS} seconds once detected")
        print(f"   Capturing 1 screenshot per second")
        print(f"   Press ESC or close window to stop early\n")
        
        last_capture_time = 0
        
        while self.tracking:
            try:
                current_time = time.time()
                
                # Capture screen at specified interval
                if current_time - last_capture_time < SCREENSHOT_INTERVAL:
                    time.sleep(0.1)
                    continue
                
                last_capture_time = current_time
                
                # Capture full screen
                screen = self.capture_full_screen()
                if screen is None:
                    time.sleep(0.1)
                    continue
                
                # Find minimap in current frame
                minimap_region = self.find_minimap_in_frame(screen)
                
                if minimap_region is None:
                    # Show searching message
                    if not self.minimap_detected:
                        print("   Searching for minimap...", end="\r")
                    continue
                
                # Minimap detected!
                if not self.minimap_detected:
                    self.minimap_detected = True
                    self.start_time = time.time()
                    x1, y1, x2, y2 = minimap_region
                    self.minimap_size = (x2 - x1, y2 - y1)
                    print(f"\n✅ Minimap detected! Starting tracking...")
                    print(f"   Region: ({x1}, {y1}) to ({x2}, {y2})")
                    print(f"   Size: {self.minimap_size[0]}x{self.minimap_size[1]}")
                    print()
                
                # Check if we've reached time limit
                elapsed = time.time() - self.start_time
                if elapsed >= MAX_TRACKING_SECONDS:
                    print(f"\n⏱️  Reached {MAX_TRACKING_SECONDS} second limit!")
                    break
                
                # Save screenshot
                screenshot_path = self.tmp_dir / f"frame_{self.screenshot_count:04d}.png"
                cv2.imwrite(str(screenshot_path), screen)
                
                timestamp = elapsed
                self.screenshots.append((timestamp, screenshot_path, minimap_region))
                self.screenshot_count += 1
                
                # Show progress
                remaining = MAX_TRACKING_SECONDS - elapsed
                print(f"   Frame {self.screenshot_count:3d} | "
                      f"Time: {int(elapsed):3d}s / {MAX_TRACKING_SECONDS}s | "
                      f"Remaining: {int(remaining):3d}s", end="\r")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in tracking: {e}")
                import traceback
                traceback.print_exc()
                break
        
        self.tracking = False
        print("\n")
    
    def process_screenshots(self):
        """Process all buffered screenshots to extract player positions and creep/objective data"""
        print(f"\n📊 Processing {len(self.screenshots)} screenshots...")
        
        for i, (timestamp, screenshot_path, minimap_region) in enumerate(self.screenshots):
            try:
                # Load screenshot
                screen = cv2.imread(str(screenshot_path))
                if screen is None:
                    continue
                
                # Extract minimap
                x1, y1, x2, y2 = minimap_region
                minimap = screen[y1:y2, x1:x2]
                minimap_width = x2 - x1
                minimap_height = y2 - y1
                
                # Detect Pokemon players
                markers, _, _ = self.detect_pokemon_markers(minimap)
                
                for marker in markers:
                    pos = marker['position']
                    team = marker['team']
                    
                    # Convert to map coordinates
                    map_x, map_y = self.minimap_to_map_coords(
                        pos[0], pos[1], minimap_width, minimap_height
                    )
                    
                    if team == 'orange':
                        self.orange_positions.append((timestamp, map_x, map_y))
                    else:
                        self.purple_positions.append((timestamp, map_x, map_y))
                
                # Detect creeps and objectives
                creeps, objectives = self.detect_creeps_and_objectives(minimap)
                
                for creep_pos in creeps:
                    map_x, map_y = self.minimap_to_map_coords(
                        creep_pos[0], creep_pos[1], minimap_width, minimap_height
                    )
                    # Round to nearest 5 pixels to group nearby sightings
                    key = (round(map_x / 5) * 5, round(map_y / 5) * 5)
                    if key not in self.creep_sightings:
                        self.creep_sightings[key] = []
                    self.creep_sightings[key].append(timestamp)
                
                for obj_pos in objectives:
                    map_x, map_y = self.minimap_to_map_coords(
                        obj_pos[0], obj_pos[1], minimap_width, minimap_height
                    )
                    # Round to nearest 5 pixels to group nearby sightings
                    key = (round(map_x / 5) * 5, round(map_y / 5) * 5)
                    if key not in self.objective_sightings:
                        self.objective_sightings[key] = []
                    self.objective_sightings[key].append(timestamp)
                
                if (i + 1) % 50 == 0:
                    print(f"   Processed {i + 1}/{len(self.screenshots)} frames...")
                
            except Exception as e:
                print(f"   Error processing frame {i}: {e}")
                continue
        
        print(f"✅ Processing complete!")
        print(f"   Purple positions: {len(self.purple_positions)}")
        print(f"   Orange positions: {len(self.orange_positions)}")
        print(f"   Creep camps: {len(self.creep_sightings)}")
        print(f"   Objectives: {len(self.objective_sightings)}")
    
    def generate_enhanced_heatmap(self):
        """Generate heatmap with purple/orange heat and creep/objective uptimes"""
        print(f"\n🗺️  Generating enhanced heatmap...")
        
        # Load base map
        base_map_path = Path("theiaskyruins.png")
        if not base_map_path.exists():
            print(f"⚠️  Warning: {base_map_path} not found, using blank map")
            base_map = np.ones((MAP_HEIGHT, MAP_WIDTH, 3), dtype=np.uint8) * 50
        else:
            base_map = cv2.imread(str(base_map_path))
            base_map = cv2.resize(base_map, (MAP_WIDTH, MAP_HEIGHT))
        
        # Create heatmaps
        heatmap_orange = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=np.float32)
        heatmap_purple = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=np.float32)
        
        # Accumulate orange positions
        for timestamp, x, y in self.orange_positions:
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                heatmap_orange[y, x] += 1
        
        # Accumulate purple positions
        for timestamp, x, y in self.purple_positions:
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                heatmap_purple[y, x] += 1
        
        # Apply Gaussian blur
        if heatmap_orange.max() > 0:
            heatmap_orange = cv2.GaussianBlur(heatmap_orange, (35, 35), 0)
            heatmap_orange = heatmap_orange / heatmap_orange.max()
        
        if heatmap_purple.max() > 0:
            heatmap_purple = cv2.GaussianBlur(heatmap_purple, (35, 35), 0)
            heatmap_purple = heatmap_purple / heatmap_purple.max()
        
        # Create colored overlays
        result = base_map.copy().astype(np.float32)
        
        # Add orange heatmap
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if heatmap_orange[y, x] > 0.05:  # Threshold for visibility
                    alpha = heatmap_orange[y, x] * 0.6
                    result[y, x] = result[y, x] * (1 - alpha) + np.array(ORANGE_COLOR) * alpha
        
        # Add purple heatmap
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if heatmap_purple[y, x] > 0.05:  # Threshold for visibility
                    alpha = heatmap_purple[y, x] * 0.6
                    result[y, x] = result[y, x] * (1 - alpha) + np.array(PURPLE_COLOR) * alpha
        
        result = result.astype(np.uint8)
        
        # Add creep uptime labels
        for (x, y), timestamps in self.creep_sightings.items():
            uptime_seconds = len(timestamps)
            minutes = uptime_seconds // 60
            seconds = uptime_seconds % 60
            label = f"{minutes:02d}:{seconds:02d}"
            
            # Draw small circle for creep camp
            cv2.circle(result, (x, y), 6, (0, 200, 200), -1)
            cv2.circle(result, (x, y), 6, (0, 0, 0), 1)
            
            # Draw label
            font_scale = 0.3
            thickness = 1
            cv2.putText(result, label, (x - 12, y - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness + 1)
            cv2.putText(result, label, (x - 12, y - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
        
        # Add objective uptime labels
        for (x, y), timestamps in self.objective_sightings.items():
            uptime_seconds = len(timestamps)
            minutes = uptime_seconds // 60
            seconds = uptime_seconds % 60
            label = f"{minutes:02d}:{seconds:02d}"
            
            # Draw larger circle for objectives
            cv2.circle(result, (x, y), 8, (0, 255, 255), -1)
            cv2.circle(result, (x, y), 8, (0, 0, 0), 1)
            
            # Draw label
            font_scale = 0.35
            thickness = 1
            cv2.putText(result, label, (x - 14, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness + 1)
            cv2.putText(result, label, (x - 14, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f'enhanced_heatmap_{timestamp}.png'
        cv2.imwrite(str(output_path), result)
        
        print(f"\n✅ Enhanced heatmap generated:")
        print(f"   {output_path}")
        
        # Also save tracking data
        tracking_data = {
            'purple_positions': [(t, x, y) for t, x, y in self.purple_positions],
            'orange_positions': [(t, x, y) for t, x, y in self.orange_positions],
            'creep_sightings': {f"{x},{y}": timestamps for (x, y), timestamps in self.creep_sightings.items()},
            'objective_sightings': {f"{x},{y}": timestamps for (x, y), timestamps in self.objective_sightings.items()},
            'metadata': {
                'total_frames': len(self.screenshots),
                'duration_seconds': MAX_TRACKING_SECONDS if len(self.screenshots) >= MAX_TRACKING_SECONDS else len(self.screenshots),
                'map_dimensions': {'width': MAP_WIDTH, 'height': MAP_HEIGHT}
            }
        }
        
        json_path = self.output_dir / f'tracking_data_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(tracking_data, f, indent=2)
        
        print(f"   {json_path}")
        
        return output_path
    
    def start(self):
        """Start the tracker"""
        try:
            # Capture screenshots
            self.tracking_loop()
            
            if self.screenshot_count == 0:
                print("\n⚠️  No minimap detected - nothing to process")
                return
            
            # Process all screenshots
            self.process_screenshots()
            
            # Generate heatmap
            heatmap_path = self.generate_enhanced_heatmap()
            
            # Show preview
            print(f"\n👁️  Showing preview (press any key to close)...")
            heatmap = cv2.imread(str(heatmap_path))
            preview = cv2.resize(heatmap, (MAP_WIDTH * 2, MAP_HEIGHT * 2))
            cv2.imshow('Enhanced Heatmap (Press any key to close)', preview)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        finally:
            # Cleanup
            self.cleanup_tmp_folder()
            print("\n✅ Done!")


def main():
    tracker = EnhancedPokemonTracker()
    tracker.start()


if __name__ == '__main__':
    main()
