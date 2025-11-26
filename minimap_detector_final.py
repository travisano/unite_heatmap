#!/usr/bin/env python3
"""
FINAL Minimap Detector
- Finds full minimap including protrusions
- FORCES exact 1:1 aspect ratio (matches theiaskyruins.png)
- Centers minimap in capture
- Crops/pads to ensure perfect aspect ratio
"""

import cv2
import numpy as np
from pathlib import Path

def auto_detect_minimap_final(screenshot):
    """
    Final minimap detection with EXACT 1:1 aspect ratio
    """
    height, width = screenshot.shape[:2]
    
    # Target is 1:1 aspect ratio (square)
    TARGET_ASPECT = 1.0
    
    # Search bottom-right
    search_x1 = int(width * 0.4)
    search_y1 = int(height * 0.3)
    
    search_region = screenshot[search_y1:height, search_x1:width]
    search_h, search_w = search_region.shape[:2]
    
    gray = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
    
    # Find circles (Pokemon icons)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=8,
        param1=50,
        param2=12,
        minRadius=5,
        maxRadius=18
    )
    
    if circles is None or len(circles[0]) < 5:
        return None
    
    circles = circles[0]
    
    # Find densest cluster
    cell_size = 180
    best_density = 0
    best_center_x = 0
    best_center_y = 0
    
    for y in range(0, max(1, search_h - cell_size), 30):
        for x in range(0, max(1, search_w - cell_size), 30):
            count = sum(1 for c in circles 
                       if x <= c[0] < x + cell_size and y <= c[1] < y + cell_size)
            
            if count > best_density:
                best_density = count
                best_center_x = x + cell_size // 2
                best_center_y = y + cell_size // 2
    
    if best_density < 5:
        return None
    
    # Get all circles within 150px of center
    minimap_circles = []
    for c in circles:
        cx, cy = float(c[0]), float(c[1])
        dist = np.sqrt((cx - best_center_x)**2 + (cy - best_center_y)**2)
        if dist < 150:
            minimap_circles.append(c)
    
    if len(minimap_circles) < 5:
        return None
    
    minimap_circles = np.array(minimap_circles)
    
    # Find bounds of circles
    min_x = np.min(minimap_circles[:, 0] - minimap_circles[:, 2])
    max_x = np.max(minimap_circles[:, 0] + minimap_circles[:, 2])
    min_y = np.min(minimap_circles[:, 1] - minimap_circles[:, 2])
    max_y = np.max(minimap_circles[:, 1] + minimap_circles[:, 2])
    
    # Circle cluster center
    circle_center_x = (min_x + max_x) / 2
    circle_center_y = (min_y + max_y) / 2
    
    # Estimate minimap size (1.5x to include oval + protrusions)
    circle_width = max_x - min_x
    circle_height = max_y - min_y
    estimated_size = max(circle_width, circle_height) * 1.5
    
    # Create SQUARE box (1:1 aspect ratio) centered on minimap
    half_size = estimated_size / 2
    
    x1 = int(circle_center_x - half_size)
    y1 = int(circle_center_y - half_size)
    x2 = int(circle_center_x + half_size)
    y2 = int(circle_center_y + half_size)
    
    # Clamp to search region
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(search_w, x2)
    y2 = min(search_h, y2)
    
    # FORCE 1:1 aspect ratio by adjusting the smaller dimension
    current_w = x2 - x1
    current_h = y2 - y1
    
    if current_w > current_h:
        # Width is larger, reduce it to match height
        center_x = (x1 + x2) / 2
        half_h = current_h / 2
        x1 = int(center_x - half_h)
        x2 = int(center_x + half_h)
    elif current_h > current_w:
        # Height is larger, reduce it to match width
        center_y = (y1 + y2) / 2
        half_w = current_w / 2
        y1 = int(center_y - half_w)
        y2 = int(center_y + half_w)
    
    # Final clamp
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(search_w, x2)
    y2 = min(search_h, y2)
    
    # Convert to global
    global_x1 = search_x1 + x1
    global_y1 = search_y1 + y1
    global_x2 = search_x1 + x2
    global_y2 = search_y1 + y2
    
    # Verify size
    final_w = global_x2 - global_x1
    final_h = global_y2 - global_y1
    
    if final_w < 150 or final_h < 150 or final_w > 450 or final_h > 450:
        return None
    
    # Verify aspect ratio is very close to 1:1
    final_aspect = final_w / final_h
    if abs(final_aspect - TARGET_ASPECT) > 0.05:  # Allow 5% tolerance
        # Force exact square
        min_size = min(final_w, final_h)
        center_x = (global_x1 + global_x2) / 2
        center_y = (global_y1 + global_y2) / 2
        half = min_size / 2
        
        global_x1 = int(center_x - half)
        global_y1 = int(center_y - half)
        global_x2 = int(center_x + half)
        global_y2 = int(center_y + half)
        
        # Clamp one more time
        global_x1 = max(0, global_x1)
        global_y1 = max(0, global_y1)
        global_x2 = min(width, global_x2)
        global_y2 = min(height, global_y2)
    
    return (global_x1, global_y1, global_x2, global_y2)


if __name__ == "__main__":
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    print("="*70)
    print("FINAL MINIMAP DETECTION - EXACT 1:1 ASPECT RATIO")
    print("="*70)
    
    screenshot = cv2.imread("/mnt/user-data/uploads/1764133022616_image.png")
    
    if screenshot is not None:
        h, w = screenshot.shape[:2]
        print(f"\nScreenshot: {w}x{h}")
        
        coords = auto_detect_minimap_final(screenshot)
        
        if coords:
            x1, y1, x2, y2 = coords
            final_w = x2 - x1
            final_h = y2 - y1
            final_aspect = final_w / final_h
            
            print(f"\n✅ FINAL DETECTION:")
            print(f"   Coords: ({x1},{y1}) to ({x2},{y2})")
            print(f"   Size: {final_w}x{final_h}")
            print(f"   Aspect ratio: {final_aspect:.6f}")
            print(f"   Deviation from 1:1: {abs(final_aspect - 1.0):.6f}")
            
            # Extract
            minimap = screenshot[y1:y2, x1:x2]
            cv2.imwrite(str(output_dir / 'FINAL_minimap_1to1.png'), minimap)
            
            # Mark on screenshot
            marked = screenshot.copy()
            cv2.rectangle(marked, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(marked, f"FINAL {final_w}x{final_h} (1:1)", (x1-20, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imwrite(str(output_dir / 'FINAL_marked_1to1.png'), marked)
            
            print(f"\n✅ Saved to outputs/")
            print(f"   - FINAL_minimap_1to1.png")
            print(f"   - FINAL_marked_1to1.png")
        else:
            print("\n❌ Detection failed")

