#!/usr/bin/env python3
"""
Creep and Objective Detector for Pokemon Unite
===============================================
Detects:
- Creeps: Dark yellowish circular dots (small and medium sizes)
- Objectives: Yellow Abra head icons (larger, distinct shape)
- Avoids: Yellow countdown numbers

TUNING PARAMETERS: Adjust these based on your game footage
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple

# ============================================================================
# TUNING PARAMETERS - ADJUST THESE FOR YOUR GAME FOOTAGE
# ============================================================================

# Creep detection (dark yellow/brown dots on minimap)
# These appear as small circular dots, darker than objectives
CREEP_HSV_LOWER_1 = [15, 50, 50]      # Yellow-brown range 1
CREEP_HSV_UPPER_1 = [30, 200, 140]    

CREEP_HSV_LOWER_2 = [20, 40, 60]      # Yellow-brown range 2 (backup)
CREEP_HSV_UPPER_2 = [35, 180, 150]

CREEP_MIN_AREA = 3                     # Very small
CREEP_MAX_AREA = 150                   # Medium-large
CREEP_MIN_CIRCULARITY = 0.3            # Allow some irregularity

# Objective detection (larger bright yellow icons)
OBJ_HSV_LOWER = [18, 100, 160]         # Bright yellow
OBJ_HSV_UPPER = [32, 255, 255]

OBJ_MIN_AREA = 60                      # Larger than creeps
OBJ_MAX_AREA = 600
OBJ_MIN_FILL_RATIO = 0.25

# Clustering (group detections at same location)
CLUSTER_DISTANCE = 15                  # Pixels

# ============================================================================


def detect_creeps(minimap_img: np.ndarray) -> List[Dict]:
    """
    Detect creep camps (small/medium yellow-brown dots on minimap)
    
    Uses multiple detection methods to find ALL creep dots:
    1. HSV color range detection (two ranges for better coverage)
    2. Blob detection for circular objects
    3. Contour detection for irregular shapes
    
    Returns:
        List of dicts with 'position' (x, y) and 'size' ('small' or 'medium')
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2GRAY)
    height, width = minimap_img.shape[:2]
    
    # ========================================================================
    # METHOD 1: HSV Color Detection (Multiple Ranges)
    # ========================================================================
    # Create mask using two overlapping yellow-brown ranges
    lower1 = np.array(CREEP_HSV_LOWER_1)
    upper1 = np.array(CREEP_HSV_UPPER_1)
    mask1 = cv2.inRange(hsv, lower1, upper1)
    
    lower2 = np.array(CREEP_HSV_LOWER_2)
    upper2 = np.array(CREEP_HSV_UPPER_2)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    
    # Combine masks
    yellow_mask = cv2.bitwise_or(mask1, mask2)
    
    # Clean up
    kernel_small = np.ones((1, 1), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel_small)
    
    # ========================================================================
    # METHOD 2: Blob Detection
    # ========================================================================
    params = cv2.SimpleBlobDetector_Params()
    params.filterByColor = True
    params.blobColor = 255
    params.filterByArea = True
    params.minArea = CREEP_MIN_AREA
    params.maxArea = CREEP_MAX_AREA
    params.filterByCircularity = True
    params.minCircularity = CREEP_MIN_CIRCULARITY
    params.filterByConvexity = False  # Don't require convex
    params.filterByInertia = False    # Don't require roundness
    
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(yellow_mask)
    
    creeps_from_blobs = []
    for kp in keypoints:
        cx, cy = int(kp.pt[0]), int(kp.pt[1])
        radius = max(1, int(kp.size / 2))
        
        if cx < 2 or cy < 2 or cx >= width - 2 or cy >= height - 2:
            continue
        
        size = "small" if radius <= 5 else "medium"
        creeps_from_blobs.append({
            'position': (cx, cy),
            'radius': radius,
            'size': size,
            'method': 'blob'
        })
    
    # ========================================================================
    # METHOD 3: Contour Detection (for irregular/partial dots)
    # ========================================================================
    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    creeps_from_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Very small to medium
        if area < CREEP_MIN_AREA or area > CREEP_MAX_AREA:
            continue
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate center
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        if cx < 2 or cy < 2 or cx >= width - 2 or cy >= height - 2:
            continue
        
        # Check if already detected by blob method
        already_detected = False
        for existing in creeps_from_blobs:
            ex, ey = existing['position']
            dist = np.sqrt((cx - ex)**2 + (cy - ey)**2)
            if dist < 5:
                already_detected = True
                break
        
        if already_detected:
            continue
        
        # Estimate size
        radius = int(np.sqrt(area / np.pi))
        size = "small" if radius <= 5 else "medium"
        
        creeps_from_contours.append({
            'position': (cx, cy),
            'radius': radius,
            'size': size,
            'method': 'contour'
        })
    
    # ========================================================================
    # METHOD 4: Direct pixel scanning for very small dots
    # ========================================================================
    # Dilate mask slightly to connect nearby pixels
    kernel_dilate = np.ones((2, 2), np.uint8)
    dilated_mask = cv2.dilate(yellow_mask, kernel_dilate, iterations=1)
    
    # Find connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dilated_mask, connectivity=8)
    
    creeps_from_pixels = []
    for i in range(1, num_labels):  # Skip background (0)
        area = stats[i, cv2.CC_STAT_AREA]
        
        if area < CREEP_MIN_AREA or area > CREEP_MAX_AREA:
            continue
        
        cx, cy = int(centroids[i][0]), int(centroids[i][1])
        
        if cx < 2 or cy < 2 or cx >= width - 2 or cy >= height - 2:
            continue
        
        # Check if already detected
        already_detected = False
        for existing in creeps_from_blobs + creeps_from_contours:
            ex, ey = existing['position']
            dist = np.sqrt((cx - ex)**2 + (cy - ey)**2)
            if dist < 5:
                already_detected = True
                break
        
        if already_detected:
            continue
        
        radius = int(np.sqrt(area / np.pi))
        size = "small" if radius <= 5 else "medium"
        
        creeps_from_pixels.append({
            'position': (cx, cy),
            'radius': max(1, radius),
            'size': size,
            'method': 'pixel'
        })
    
    # ========================================================================
    # Combine all detection methods
    # ========================================================================
    all_creeps = creeps_from_blobs + creeps_from_contours + creeps_from_pixels
    
    # Final deduplication (remove very close duplicates)
    final_creeps = []
    for creep in all_creeps:
        cx, cy = creep['position']
        
        # Check if too close to existing
        too_close = False
        for existing in final_creeps:
            ex, ey = existing['position']
            dist = np.sqrt((cx - ex)**2 + (cy - ey)**2)
            if dist < 4:  # Within 4 pixels = same creep
                too_close = True
                break
        
        if not too_close:
            final_creeps.append(creep)
    
    return final_creeps


def detect_objectives(minimap_img: np.ndarray) -> List[Dict]:
    """
    Detect objectives (Abra head icons - larger yellow icons)
    
    Returns:
        List of dicts with 'position' (x, y)
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    height, width = minimap_img.shape[:2]
    
    # Find bright yellow regions
    lower = np.array(OBJ_HSV_LOWER)
    upper = np.array(OBJ_HSV_UPPER)
    yellow_mask = cv2.inRange(hsv, lower, upper)
    
    # Clean up
    kernel = np.ones((3, 3), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    objectives = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if area < OBJ_MIN_AREA or area > OBJ_MAX_AREA:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        # Filter elongated shapes (numbers)
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            continue
        
        # Calculate center
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        if cx < 10 or cy < 10 or cx >= width - 10 or cy >= height - 10:
            continue
        
        # Check fill ratio
        region_mask = yellow_mask[y:y+h, x:x+w]
        region_area = w * h
        filled_pixels = cv2.countNonZero(region_mask)
        fill_ratio = filled_pixels / region_area if region_area > 0 else 0
        
        if fill_ratio < OBJ_MIN_FILL_RATIO:
            continue
        
        objectives.append({
            'position': (cx, cy),
            'area': area,
            'aspect_ratio': aspect_ratio,
            'bbox': (x, y, w, h)
        })
    
    return objectives


def cluster_positions(detections: List[Dict], distance_threshold: int = None) -> Dict[int, List[Dict]]:
    """
    Cluster detections that are in the same location across frames.
    
    Args:
        detections: List of detection dicts with 'position' and 'frame'
        distance_threshold: Max distance in pixels (default: CLUSTER_DISTANCE)
    
    Returns:
        Dict mapping cluster_id to list of detections in that cluster
    """
    if distance_threshold is None:
        distance_threshold = CLUSTER_DISTANCE
    
    if not detections:
        return {}
    
    detections = sorted(detections, key=lambda d: d.get('frame', 0))
    
    clusters = {}
    cluster_id = 0
    
    for detection in detections:
        pos = detection['position']
        found_cluster = False
        
        for cid, cluster_detections in clusters.items():
            cluster_positions = [d['position'] for d in cluster_detections]
            avg_x = np.mean([p[0] for p in cluster_positions])
            avg_y = np.mean([p[1] for p in cluster_positions])
            
            distance = np.sqrt((pos[0] - avg_x)**2 + (pos[1] - avg_y)**2)
            
            if distance <= distance_threshold:
                clusters[cid].append(detection)
                found_cluster = True
                break
        
        if not found_cluster:
            clusters[cluster_id] = [detection]
            cluster_id += 1
    
    return clusters


# ============================================================================
# TESTING AND DEBUGGING
# ============================================================================

def create_debug_visualization(minimap_img: np.ndarray, creeps: List[Dict], 
                               objectives: List[Dict]) -> np.ndarray:
    """Create visualization with HSV mask overlay for tuning"""
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    
    # Create debug image with 3 panels: original, creep mask, obj mask
    h, w = minimap_img.shape[:2]
    debug_img = np.zeros((h, w*3, 3), dtype=np.uint8)
    
    # Panel 1: Original with detections
    panel1 = minimap_img.copy()
    for creep in creeps:
        pos = creep['position']
        radius = creep['radius']
        cv2.circle(panel1, pos, radius + 2, (0, 255, 0), 2)  # Green
        cv2.circle(panel1, pos, 1, (0, 255, 0), -1)
    
    for obj in objectives:
        pos = obj['position']
        cv2.circle(panel1, pos, 10, (0, 255, 255), 2)  # Yellow
        cv2.circle(panel1, pos, 2, (0, 255, 255), -1)
    
    debug_img[:, :w] = panel1
    
    # Panel 2: Creep mask (combined)
    mask1 = cv2.inRange(hsv, np.array(CREEP_HSV_LOWER_1), np.array(CREEP_HSV_UPPER_1))
    mask2 = cv2.inRange(hsv, np.array(CREEP_HSV_LOWER_2), np.array(CREEP_HSV_UPPER_2))
    creep_mask = cv2.bitwise_or(mask1, mask2)
    debug_img[:, w:w*2] = cv2.cvtColor(creep_mask, cv2.COLOR_GRAY2BGR)
    
    # Panel 3: Objective mask
    obj_mask = cv2.inRange(hsv, np.array(OBJ_HSV_LOWER), np.array(OBJ_HSV_UPPER))
    debug_img[:, w*2:] = cv2.cvtColor(obj_mask, cv2.COLOR_GRAY2BGR)
    
    # Labels
    cv2.putText(debug_img, "Detections", (10, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(debug_img, "Creep Mask", (w + 10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(debug_img, "Obj Mask", (w*2 + 10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return debug_img


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python creep_objective_detector.py <minimap_image>")
        print("\nThis will show you:")
        print("  - Left: Detected creeps (green) and objectives (yellow)")
        print("  - Middle: HSV mask for creeps")
        print("  - Right: HSV mask for objectives")
        print("\nUse this to tune the HSV parameters at the top of the file!")
        sys.exit(1)
    
    img_path = sys.argv[1]
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"Error: Could not load image {img_path}")
        sys.exit(1)
    
    print(f"\n" + "="*60)
    print(f"ANALYZING: {img_path}")
    print("="*60)
    
    print(f"\nCurrent Parameters:")
    print(f"  Creeps HSV Range 1: {CREEP_HSV_LOWER_1} to {CREEP_HSV_UPPER_1}")
    print(f"  Creeps HSV Range 2: {CREEP_HSV_LOWER_2} to {CREEP_HSV_UPPER_2}")
    print(f"  Creeps Area: {CREEP_MIN_AREA} to {CREEP_MAX_AREA} pixels")
    print(f"  Objectives HSV: {OBJ_HSV_LOWER} to {OBJ_HSV_UPPER}")
    print(f"  Objectives Area: {OBJ_MIN_AREA} to {OBJ_MAX_AREA} pixels")
    
    creeps = detect_creeps(img)
    objectives = detect_objectives(img)
    
    print(f"\n🟡 Found {len(creeps)} creeps:")
    for i, creep in enumerate(creeps[:20], 1):  # Show first 20
        pos = creep['position']
        size = creep['size']
        print(f"  {i}. {size.upper():6s} at ({pos[0]:3d}, {pos[1]:3d}) radius={creep['radius']}px")
    if len(creeps) > 20:
        print(f"  ... and {len(creeps) - 20} more")
    
    print(f"\n🎯 Found {len(objectives)} objectives:")
    for i, obj in enumerate(objectives, 1):
        pos = obj['position']
        print(f"  {i}. OBJECTIVE at ({pos[0]:3d}, {pos[1]:3d}) area={obj['area']:.0f}px")
    
    # Create debug visualization
    debug_img = create_debug_visualization(img, creeps, objectives)
    
    # Save outputs
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'creep_objective_detection.png'
    debug_path = output_dir / 'debug_visualization.png'
    
    # Regular detection
    regular_img = img.copy()
    for creep in creeps:
        pos = creep['position']
        cv2.circle(regular_img, pos, creep['radius'] + 2, (0, 255, 0), 2)
    for obj in objectives:
        pos = obj['position']
        cv2.circle(regular_img, pos, 10, (0, 255, 255), 2)
    
    cv2.imwrite(str(output_path), regular_img)
    cv2.imwrite(str(debug_path), debug_img)
    
    print(f"\n✅ Saved:")
    print(f"   {output_path}")
    print(f"   {debug_path} (3-panel debug view)")
    print(f"\nTIP: Open debug_visualization.png to see HSV masks")
    print(f"     Adjust parameters at top of file if detection is wrong")


def detect_objectives(minimap_img: np.ndarray) -> List[Dict]:
    """
    Detect objectives (Abra head icons - larger yellow icons)
    
    Returns:
        List of dicts with 'position' (x, y)
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2GRAY)
    height, width = minimap_img.shape[:2]
    
    # ====================================================================
    # STEP 1: Find bright yellow regions (objectives are brighter)
    # ====================================================================
    # Objectives are brighter yellow than creeps
    lower_obj_yellow = np.array([20, 100, 150])  # Bright yellow
    upper_obj_yellow = np.array([35, 255, 255])
    
    yellow_mask = cv2.inRange(hsv, lower_obj_yellow, upper_obj_yellow)
    
    # Clean up
    kernel = np.ones((3, 3), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)
    
    # ====================================================================
    # STEP 2: Find contours (objectives have distinct shape)
    # ====================================================================
    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    objectives = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Objectives are larger than creeps but not huge
        # Filter by area to exclude small dots (creeps) and numbers
        if area < 50 or area > 500:  # Objectives are medium-sized
            continue
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Objectives have relatively compact shape (not elongated like numbers)
        aspect_ratio = w / h if h > 0 else 0
        
        # Filter out elongated shapes (numbers are often elongated)
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            continue
        
        # Calculate center
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        # Bounds check
        if cx < 10 or cy < 10 or cx >= width - 10 or cy >= height - 10:
            continue
        
        objectives.append({
            'position': (cx, cy),
            'area': area,
            'aspect_ratio': aspect_ratio,
            'bbox': (x, y, w, h)
        })
    
    # ====================================================================
    # STEP 3: Filter to avoid detecting numbers
    # ====================================================================
    # Numbers usually appear near objectives, so we can use spatial filtering
    # Also, numbers tend to have more irregular shapes
    
    filtered_objectives = []
    
    for obj in objectives:
        # Additional verification: check if the region is mostly filled
        x, y, w, h = obj['bbox']
        region_mask = yellow_mask[y:y+h, x:x+w]
        region_area = w * h
        filled_pixels = cv2.countNonZero(region_mask)
        
        fill_ratio = filled_pixels / region_area if region_area > 0 else 0
        
        # Objectives should be relatively filled (>30%)
        # Numbers are more sparse
        if fill_ratio > 0.3:
            filtered_objectives.append(obj)
    
    return filtered_objectives


def cluster_positions(detections: List[Dict], distance_threshold: int = 15) -> Dict[int, List[Dict]]:
    """
    Cluster detections that are in the same location across frames.
    Creeps and objectives are fixed positions, so group nearby detections.
    
    Args:
        detections: List of detection dicts with 'position' and 'frame'
        distance_threshold: Max distance in pixels to consider same location
    
    Returns:
        Dict mapping cluster_id to list of detections in that cluster
    """
    if not detections:
        return {}
    
    # Sort by frame for consistent processing
    detections = sorted(detections, key=lambda d: d.get('frame', 0))
    
    clusters = {}
    cluster_id = 0
    
    for detection in detections:
        pos = detection['position']
        
        # Find if this position belongs to an existing cluster
        found_cluster = False
        
        for cid, cluster_detections in clusters.items():
            # Check average position of cluster
            cluster_positions = [d['position'] for d in cluster_detections]
            avg_x = np.mean([p[0] for p in cluster_positions])
            avg_y = np.mean([p[1] for p in cluster_positions])
            
            # Calculate distance
            distance = np.sqrt((pos[0] - avg_x)**2 + (pos[1] - avg_y)**2)
            
            if distance <= distance_threshold:
                clusters[cid].append(detection)
                found_cluster = True
                break
        
        # Create new cluster if no match found
        if not found_cluster:
            clusters[cluster_id] = [detection]
            cluster_id += 1
    
    return clusters


# ============================================================================
# Testing and debugging
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python creep_objective_detector.py <minimap_image>")
        sys.exit(1)
    
    img_path = sys.argv[1]
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"Error: Could not load image {img_path}")
        sys.exit(1)
    
    print(f"\nAnalyzing: {img_path}")
    print("="*50)
    
    # Detect creeps
    creeps = detect_creeps(img)
    print(f"\n🟡 Found {len(creeps)} creeps:")
    for i, creep in enumerate(creeps, 1):
        pos = creep['position']
        size = creep['size']
        print(f"  {i}. {size.upper():6s} at ({pos[0]:3d}, {pos[1]:3d}) radius={creep['radius']}px")
    
    # Detect objectives
    objectives = detect_objectives(img)
    print(f"\n🎯 Found {len(objectives)} objectives:")
    for i, obj in enumerate(objectives, 1):
        pos = obj['position']
        print(f"  {i}. OBJECTIVE at ({pos[0]:3d}, {pos[1]:3d}) area={obj['area']:.0f}px")
    
    # Visualize
    debug_img = img.copy()
    
    # Draw creeps in green
    for creep in creeps:
        pos = creep['position']
        radius = creep['radius']
        cv2.circle(debug_img, pos, radius + 2, (0, 255, 0), 2)
        cv2.circle(debug_img, pos, 1, (0, 255, 0), -1)
    
    # Draw objectives in yellow
    for obj in objectives:
        pos = obj['position']
        cv2.circle(debug_img, pos, 10, (0, 255, 255), 2)
        cv2.circle(debug_img, pos, 2, (0, 255, 255), -1)
    
    # Save output
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'creep_objective_detection.png'
    cv2.imwrite(str(output_path), debug_img)
    
    print(f"\n✅ Visualization saved: {output_path}")
