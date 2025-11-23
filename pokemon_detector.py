#!/usr/bin/env python3
"""
Perfect Circle Pokemon Detector - FINAL TUNED VERSION
======================================================
Key insights:
1. Pokemon markers are PERFECT CIRCLES
2. ALL markers are the SAME SIZE
3. They contain white/off-white centers (slightly translucent but still WHITE)
4. Thin colored ring - can be orange, purple, or BLUE-tinted (still purple team)

Strategy:
1. Find white pixels (slightly more lenient for translucent effect)
2. Use Hough Circle detection to find PERFECT circles
3. Verify circles contain white
4. Determine team by ring color family (including blue as purple team)
"""

import cv2
import numpy as np

def detect_pokemon_markers(minimap_img):
    """
    Detect Pokemon markers using circle detection + white center verification.
    All Pokemon markers are perfect circles of the same size.
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2GRAY)
    height, width = minimap_img.shape[:2]
    
    # ==================================================================
    # STEP 1: Create white mask - SLIGHTLY more lenient for translucency
    # ==================================================================
    # White detection: bright but can be slightly off-white due to translucency
    # Still must be WHITE - never gray (gray = spawns/towers)
    lower_white = np.array([0, 0, 210])  # Slightly lower brightness threshold
    upper_white = np.array([180, 35, 255])  # Slightly higher saturation tolerance
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # ==================================================================
    # STEP 2: Detect CIRCLES using Hough Transform
    # ==================================================================
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,
        param1=50,
        param2=15,
        minRadius=8,
        maxRadius=14
    )
    
    markers = []
    debug_img = minimap_img.copy()
    
    if circles is None:
        return markers, debug_img, white_mask
    
    circles = np.uint16(np.around(circles))
    
    for circle in circles[0, :]:
        cx, cy, radius = circle
        
        # ==================================================================
        # STEP 3: Verify this circle contains WHITE
        # ==================================================================
        circle_mask = np.zeros(white_mask.shape, dtype=np.uint8)
        cv2.circle(circle_mask, (cx, cy), radius - 2, 255, -1)
        
        white_in_circle = cv2.bitwise_and(white_mask, circle_mask)
        white_pixel_count = cv2.countNonZero(white_in_circle)
        
        if white_pixel_count < 8:  # Slightly more lenient
            continue
        
        # ==================================================================
        # STEP 4: Determine team by ring color - INCLUDING BLUE
        # ==================================================================
        ring_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.circle(ring_mask, (cx, cy), radius, 255, 2)
        
        ring_hsv = cv2.bitwise_and(hsv, hsv, mask=ring_mask)
        
        # ORANGE team: red-orange-yellow range
        lower_orange = np.array([0, 70, 70])
        upper_orange = np.array([30, 255, 255])
        orange_mask = cv2.inRange(ring_hsv, lower_orange, upper_orange)
        orange_pixels = cv2.countNonZero(orange_mask)
        
        # PURPLE team: blue-purple-violet range
        # IMPORTANT: Blue-tinted borders are still PURPLE team
        # Expanded range to include blue (100-160 instead of 120-160)
        lower_purple = np.array([100, 30, 30])  # Include blue hues
        upper_purple = np.array([160, 255, 255])
        purple_mask = cv2.inRange(ring_hsv, lower_purple, upper_purple)
        purple_pixels = cv2.countNonZero(purple_mask)
        
        total_colored = orange_pixels + purple_pixels
        if total_colored < 5:
            continue
        
        # Determine team
        if orange_pixels > purple_pixels:
            team = "orange"
            color = (0, 165, 255)
        else:
            team = "purple"
            color = (255, 0, 255)
        
        markers.append({
            'position': (int(cx), int(cy)),
            'radius': int(radius),
            'team': team,
            'confidence': total_colored,
            'white_pixels': white_pixel_count
        })
        
        cv2.circle(debug_img, (int(cx), int(cy)), int(radius), color, 2)
        cv2.circle(debug_img, (int(cx), int(cy)), 2, (0, 255, 0), -1)
    
    return markers, debug_img, white_mask


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python pokemon_detector.py <image_path>")
        sys.exit(1)
    
    img_path = sys.argv[1]
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"Error: Could not load image {img_path}")
        sys.exit(1)
    
    markers, debug_img, white_mask = detect_pokemon_markers(img)
    
    print(f"\nFound {len(markers)} Pokemon markers:")
    orange_count = sum(1 for m in markers if m['team'] == 'orange')
    purple_count = sum(1 for m in markers if m['team'] == 'purple')
    
    print(f"  Orange team: {orange_count}")
    print(f"  Purple team: {purple_count}")
    print()
    
    for i, marker in enumerate(markers, 1):
        pos = marker['position']
        team = marker['team']
        radius = marker['radius']
        print(f"  {i}. {team.upper():6s} at ({pos[0]:3d}, {pos[1]:3d}) radius={radius} px")
    
    # Save to outputs folder
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    result_path = output_dir / 'detection_result.png'
    mask_path = output_dir / 'white_mask.png'
    
    cv2.imwrite(str(result_path), debug_img)
    cv2.imwrite(str(mask_path), white_mask)
    
    print(f"\nSaved to outputs/:")
    print(f"  {result_path}")
    print(f"  {mask_path}")
