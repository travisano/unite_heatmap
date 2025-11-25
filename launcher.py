#!/usr/bin/env python3
"""
Pokemon Unite Real-Time Tracker
================================
Captures full screen, auto-detects minimap, tracks Pokemon positions
Close window → Auto-generates heatmap
"""

import cv2
import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime
import sys

# Import screen capture
try:
    from PIL import ImageGrab
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    print("❌ Error: Please install Pillow")
    print("   Run: pip install pillow")
    sys.exit(1)


class PokemonTracker:
    def __init__(self):
        self.tracking = True
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Clear old tracking data
        tracking_file = self.output_dir / 'tracking_data.json'
        if tracking_file.exists():
            tracking_file.unlink()
        
        # Import detector
        try:
            from pokemon_detector import detect_pokemon_markers
            self.detect_pokemon_markers = detect_pokemon_markers
        except ImportError:
            print("❌ Error: pokemon_detector.py not found!")
            print("   Make sure it's in the same folder.")
            sys.exit(1)
        
        # Tracking data
        self.purple_positions = []
        self.orange_positions = []
        self.start_time = time.time()
        self.frame_count = 0
    
    def find_minimap_in_frame(self, screen):
        """Find minimap by detecting small colored circular markers (Pokemon)"""
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        h, w = screen.shape[:2]
        
        # Detect small circles (Pokemon markers are small)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=8,
            param1=50,
            param2=15,
            minRadius=8,   # Pokemon markers are ~8-14 pixels
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
        """Main tracking loop"""
        print("\n" + "="*60)
        print("🎮 POKEMON UNITE REAL-TIME TRACKER")
        print("="*60)
        print("\n🎯 Capturing full screen and auto-detecting minimap...")
        print("   Close the tracking window to stop and generate heatmap\n")
        
        last_status_time = time.time()
        
        while self.tracking:
            try:
                # Capture full screen
                screen = self.capture_full_screen()
                if screen is None:
                    time.sleep(0.1)
                    continue
                
                # Find minimap in current frame
                minimap_region = self.find_minimap_in_frame(screen)
                
                if minimap_region is None:
                    # Show full screen if no minimap found
                    small_screen = cv2.resize(screen, (960, 540))
                    cv2.putText(small_screen, "Searching for minimap...", (20, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow('Pokemon Tracker (Close to stop)', small_screen)
                    
                    key = cv2.waitKey(100) & 0xFF
                    if key == 27 or cv2.getWindowProperty('Pokemon Tracker (Close to stop)', cv2.WND_PROP_VISIBLE) < 1:
                        break
                    continue
                
                # Extract minimap
                x1, y1, x2, y2 = minimap_region
                minimap = screen[y1:y2, x1:x2]
                
                # Detect Pokemon
                markers, debug_img, white_mask = self.detect_pokemon_markers(minimap)
                
                # Record positions
                for marker in markers:
                    pos = marker['position']
                    team = marker['team']
                    
                    if team == 'orange':
                        self.orange_positions.append({'x': pos[0], 'y': pos[1]})
                    else:
                        self.purple_positions.append({'x': pos[0], 'y': pos[1]})
                
                self.frame_count += 1
                
                # Show detection on minimap
                cv2.putText(debug_img, f"Frame: {self.frame_count}", (10, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(debug_img, f"Orange: {len([m for m in markers if m['team'] == 'orange'])}", 
                           (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
                cv2.putText(debug_img, f"Purple: {len([m for m in markers if m['team'] == 'purple'])}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                
                cv2.imshow('Pokemon Tracker (Close to stop)', debug_img)
                
                # Show white mask too
                cv2.imshow('White Detection', white_mask)
                
                # Check for window close or ESC key
                key = cv2.waitKey(100) & 0xFF
                if key == 27 or cv2.getWindowProperty('Pokemon Tracker (Close to stop)', cv2.WND_PROP_VISIBLE) < 1:
                    break
                
                # Print status every 5 seconds
                if time.time() - last_status_time >= 5:
                    elapsed = time.time() - self.start_time
                    total_detections = len(self.purple_positions) + len(self.orange_positions)
                    print(f"   Frame {self.frame_count} | Time: {elapsed:.1f}s | "
                          f"Total: {total_detections} (Purple: {len(self.purple_positions)}, "
                          f"Orange: {len(self.orange_positions)})")
                    last_status_time = time.time()
                
            except KeyboardInterrupt:
                print("\n⚠️  Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error in tracking: {e}")
                import traceback
                traceback.print_exc()
                break
        
        cv2.destroyAllWindows()
        self.tracking = False
    
    def save_and_generate_heatmap(self):
        """Save tracking data and generate heatmap"""
        print(f"\n📊 Tracking complete!")
        print(f"   Frames: {self.frame_count}")
        print(f"   Duration: {time.time() - self.start_time:.1f}s")
        print(f"   Purple detections: {len(self.purple_positions)}")
        print(f"   Orange detections: {len(self.orange_positions)}")
        
        if len(self.purple_positions) == 0 and len(self.orange_positions) == 0:
            print("\n⚠️  No Pokemon detected - no heatmap generated")
            return
        
        # Save tracking data
        tracking_data = {
            'purple_team': self.purple_positions,
            'orange_team': self.orange_positions,
            'metadata': {
                'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
                'end_time': datetime.now().isoformat(),
                'fps': self.frame_count / (time.time() - self.start_time) if self.frame_count > 0 else 0,
                'total_frames': self.frame_count
            }
        }
        
        json_path = self.output_dir / 'tracking_data.json'
        with open(json_path, 'w') as f:
            json.dump(tracking_data, f, indent=2)
        
        print(f"\n💾 Tracking data saved: {json_path}")
        
        # Generate heatmap
        print(f"\n🗺️  Generating heatmap...")
        
        minimap_size = (300, 300)
        heatmap_orange = np.zeros(minimap_size, dtype=np.float32)
        heatmap_purple = np.zeros(minimap_size, dtype=np.float32)
        
        # Accumulate positions
        for pos in self.orange_positions:
            x, y = int(pos['x']), int(pos['y'])
            if 0 <= x < minimap_size[0] and 0 <= y < minimap_size[1]:
                heatmap_orange[y, x] += 1
        
        for pos in self.purple_positions:
            x, y = int(pos['x']), int(pos['y'])
            if 0 <= x < minimap_size[0] and 0 <= y < minimap_size[1]:
                heatmap_purple[y, x] += 1
        
        # Apply Gaussian blur
        if heatmap_orange.max() > 0:
            heatmap_orange = cv2.GaussianBlur(heatmap_orange, (25, 25), 0)
            heatmap_orange = heatmap_orange / heatmap_orange.max() * 255
        
        if heatmap_purple.max() > 0:
            heatmap_purple = cv2.GaussianBlur(heatmap_purple, (25, 25), 0)
            heatmap_purple = heatmap_purple / heatmap_purple.max() * 255
        
        # Create colored heatmaps
        heatmap_orange_colored = cv2.applyColorMap(heatmap_orange.astype(np.uint8), cv2.COLORMAP_HOT)
        heatmap_purple_colored = cv2.applyColorMap(heatmap_purple.astype(np.uint8), cv2.COLORMAP_WINTER)
        
        # Combine
        combined = cv2.addWeighted(heatmap_orange_colored, 0.5, heatmap_purple_colored, 0.5, 0)
        
        # Save heatmaps
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        heatmap_combined_path = self.output_dir / f'heatmap_combined_{timestamp}.png'
        heatmap_orange_path = self.output_dir / f'heatmap_orange_{timestamp}.png'
        heatmap_purple_path = self.output_dir / f'heatmap_purple_{timestamp}.png'
        
        cv2.imwrite(str(heatmap_combined_path), combined)
        cv2.imwrite(str(heatmap_orange_path), heatmap_orange_colored)
        cv2.imwrite(str(heatmap_purple_path), heatmap_purple_colored)
        
        print(f"\n✅ Heatmaps generated:")
        print(f"   Combined: {heatmap_combined_path}")
        print(f"   Orange: {heatmap_orange_path}")
        print(f"   Purple: {heatmap_purple_path}")
        
        # Show preview
        print("\n👁️  Showing preview (press any key to close)...")
        preview = cv2.resize(combined, (600, 600))
        cv2.imshow('Final Heatmap', preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def start(self):
        """Start the tracker"""
        try:
            self.tracking_loop()
        finally:
            self.save_and_generate_heatmap()
            print("\n✅ Done!")


def main():
    tracker = PokemonTracker()
    tracker.start()


if __name__ == '__main__':
    main()
