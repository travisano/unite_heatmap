#!/usr/bin/env python3
"""
Pokémon Unite Heatmap Tracker
Captures minimap from screen and tracks Pokémon positions for heatmap generation
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
from PIL import ImageGrab
import os


class PokemonTracker:
    def __init__(self, minimap_template_path):
        """
        Initialize the Pokémon tracker
        
        Args:
            minimap_template_path: Path to the minimap template image for matching
        """
        self.minimap_template = cv2.imread(minimap_template_path)
        if self.minimap_template is None:
            raise ValueError(f"Could not load minimap template from {minimap_template_path}")
        
        self.minimap_location = None
        self.tracking_data = {
            'purple_team': [],
            'orange_team': [],
            'metadata': {
                'start_time': None,
                'end_time': None,
                'fps': 0,
                'total_frames': 0
            }
        }
        self.is_tracking = False
        
    def find_minimap(self, screenshot):
        """
        Locate the minimap on the screen using template matching
        Supports multiple scales to handle expanded minimap
        
        Args:
            screenshot: Full screen capture as numpy array
            
        Returns:
            Tuple of (x, y, width, height) or None if not found
        """
        # Convert to grayscale for template matching
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(self.minimap_template, cv2.COLOR_BGR2GRAY)
        
        best_match = None
        best_val = 0
        
        # Try multiple scales to handle expanded minimap (0.5x to 2.0x)
        for scale in [1.0, 1.5, 2.0, 0.75, 0.5]:
            # Resize template to current scale
            if scale != 1.0:
                width = int(gray_template.shape[1] * scale)
                height = int(gray_template.shape[0] * scale)
                if width < 20 or height < 20:  # Skip if too small
                    continue
                scaled_template = cv2.resize(gray_template, (width, height))
            else:
                scaled_template = gray_template
            
            # Skip if template is larger than screenshot
            if (scaled_template.shape[0] > gray_screenshot.shape[0] or 
                scaled_template.shape[1] > gray_screenshot.shape[1]):
                continue
            
            # Perform template matching
            result = cv2.matchTemplate(gray_screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Track best match across all scales
            if max_val > best_val:
                best_val = max_val
                h, w = scaled_template.shape[:2]
                x, y = max_loc
                best_match = (x, y, w, h, scale)
        
        # If match quality is good enough
        if best_val > 0.6:
            x, y, w, h, scale = best_match
            if scale != 1.0:
                print(f"📏 Minimap detected at {scale:.1f}x scale (expanded minimap)")
            return (x, y, w, h)
        
        return None
    
    def detect_pokemon_positions(self, minimap_image):
        """
        Detect Pokémon positions on the minimap by color
        
        Args:
            minimap_image: Cropped minimap image
            
        Returns:
            Dictionary with 'purple' and 'orange' lists of (x, y) positions
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(minimap_image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for purple and orange borders
        # Purple team (adjust these ranges as needed)
        purple_lower = np.array([120, 50, 50])
        purple_upper = np.array([160, 255, 255])
        
        # Orange team (adjust these ranges as needed)
        orange_lower = np.array([5, 100, 100])
        orange_upper = np.array([20, 255, 255])
        
        # Create masks
        purple_mask = cv2.inRange(hsv, purple_lower, purple_upper)
        orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
        
        # Find contours
        purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        def get_positions(contours, min_area=10, max_area=500, max_positions=5):
            """
            Extract center positions from contours (up to max_positions per team)
            
            Args:
                contours: OpenCV contours to process
                min_area: Minimum area to consider (filters noise)
                max_area: Maximum area to consider (filters goal zones and large static elements)
                max_positions: Maximum positions to return per team
            
            Returns:
                List of (x, y) positions
            """
            positions = []
            
            # Sort contours by area (largest first) to prioritize clear detections
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            for contour in sorted_contours:
                if len(positions) >= max_positions:
                    break  # Found all 5 Pokémon already
                    
                area = cv2.contourArea(contour)
                
                # Filter by area: must be between min and max
                # This excludes noise (too small) and goal zones (too large)
                if min_area < area < max_area:
                    M = cv2.moments(contour)
                    if M['m00'] != 0:
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])
                        positions.append((cx, cy))
            return positions
        
        purple_positions = get_positions(purple_contours, min_area=10, max_area=500, max_positions=5)
        orange_positions = get_positions(orange_contours, min_area=10, max_area=500, max_positions=5)
        
        return {
            'purple': purple_positions,
            'orange': orange_positions
        }
    
    def capture_frame(self):
        """
        Capture current screen and process for Pokémon positions
        
        Returns:
            Boolean indicating success
        """
        # Capture screen
        screenshot = np.array(ImageGrab.grab())
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        # Find minimap if not already located
        if self.minimap_location is None:
            self.minimap_location = self.find_minimap(screenshot)
            if self.minimap_location is None:
                print("Minimap not found on screen")
                return False
            print(f"Minimap found at: {self.minimap_location}")
        
        # Extract minimap region
        x, y, w, h = self.minimap_location
        minimap = screenshot[y:y+h, x:x+w]
        
        # Detect Pokémon positions
        positions = self.detect_pokemon_positions(minimap)
        
        # Store positions with timestamp
        timestamp = time.time()
        
        purple_count = len(positions['purple'])
        orange_count = len(positions['orange'])
        
        for pos in positions['purple']:
            self.tracking_data['purple_team'].append({
                'x': pos[0],
                'y': pos[1],
                'timestamp': timestamp
            })
        
        for pos in positions['orange']:
            self.tracking_data['orange_team'].append({
                'x': pos[0],
                'y': pos[1],
                'timestamp': timestamp
            })
        
        self.tracking_data['metadata']['total_frames'] += 1
        
        # Debug output every 30 frames (3 seconds at 10 FPS)
        frame_count = self.tracking_data['metadata']['total_frames']
        if frame_count % 30 == 0:
            print(f"Frame {frame_count}: Detected {purple_count} purple, {orange_count} orange Pokémon")
        
        return True
    
    def start_tracking(self, fps=10):
        """
        Start tracking Pokémon positions
        
        Args:
            fps: Frames per second to capture (default: 10)
        """
        self.is_tracking = True
        self.tracking_data['metadata']['start_time'] = datetime.now().isoformat()
        self.tracking_data['metadata']['fps'] = fps
        
        frame_delay = 1.0 / fps
        
        print(f"\n{'='*60}")
        print(f"🎮 POKÉMON UNITE HEATMAP TRACKER")
        print(f"{'='*60}")
        print(f"Tracking at {fps} FPS")
        print(f"\n📹 Make sure your Pokémon Unite replay is visible on screen!")
        print(f"   The minimap will be detected automatically.\n")
        print(f"⏸️  TO STOP TRACKING: Press Ctrl+C")
        print(f"{'='*60}\n")
        
        try:
            while self.is_tracking:
                success = self.capture_frame()
                if success:
                    frame_count = self.tracking_data['metadata']['total_frames']
                    if frame_count % (fps * 5) == 0:  # Print every 5 seconds
                        print(f"Captured {frame_count} frames...")
                time.sleep(frame_delay)
        except KeyboardInterrupt:
            print("\n\n⏹️  Tracking stopped by user (Ctrl+C pressed)")
        finally:
            self.stop_tracking()
    
    def stop_tracking(self):
        """Stop tracking and finalize data"""
        self.is_tracking = False
        self.tracking_data['metadata']['end_time'] = datetime.now().isoformat()
        
        purple_count = len(self.tracking_data['purple_team'])
        orange_count = len(self.tracking_data['orange_team'])
        total_frames = self.tracking_data['metadata']['total_frames']
        
        print(f"\n{'='*60}")
        print(f"Tracking Complete!")
        print(f"{'='*60}")
        print(f"Total frames captured: {total_frames}")
        print(f"Purple team positions: {purple_count}")
        print(f"Orange team positions: {orange_count}")
        
        if total_frames > 0:
            print(f"\nAverage Pokémon per frame:")
            print(f"  Purple: {purple_count / total_frames:.2f} Pokémon/frame")
            print(f"  Orange: {orange_count / total_frames:.2f} Pokémon/frame")
            print(f"  Total:  {(purple_count + orange_count) / total_frames:.2f} Pokémon/frame")
        
        print(f"{'='*60}\n")
    
    def save_data(self, output_path='tracking_data.json'):
        """
        Save tracking data to JSON file
        
        Args:
            output_path: Path to save the JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(self.tracking_data, f, indent=2)
        
        print(f"Data saved to: {output_path}")
        return output_path


def main():
    """Main function to run the tracker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pokémon Unite Heatmap Tracker')
    parser.add_argument('--minimap', type=str, default='show.png',
                        help='Path to minimap template image')
    parser.add_argument('--fps', type=int, default=10,
                        help='Frames per second to capture (default: 10)')
    parser.add_argument('--output', type=str, default='tracking_data.json',
                        help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Check if minimap template exists
    if not os.path.exists(args.minimap):
        print(f"Error: Minimap template not found at {args.minimap}")
        return
    
    # Create tracker
    tracker = PokemonTracker(args.minimap)
    
    # Start tracking
    tracker.start_tracking(fps=args.fps)
    
    # Save data
    tracker.save_data(args.output)


if __name__ == '__main__':
    main()
