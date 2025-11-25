#!/usr/bin/env python3
"""
Conservative Creep and Objective Detector
==========================================
Tuned to find exactly ~24 creeps (dark yellowish-brown dots) 
and ~1 objective (bright yellow icon) from objectives.png

Creeps: Small dark yellowish-brown filled circles, NO border
Objectives: Larger bright yellow Abra head icons
"""

import cv2
import numpy as np
from typing import List, Dict

# ============================================================================
# TUNED FOR OBJECTIVES.PNG: 24 green circles (creeps), 1 yellow circle (objective)
# ============================================================================

# EXACT values from actual creep samples (1764077925228_image.png, 1764077932937_image.png)
# Creeps appear as yellowish-brown dots
# HSV from samples: H=15-35, S=50-184, V=100-210

CREEP_HSV_LOWER = [15, 50, 100]           # Exact from samples
CREEP_HSV_UPPER = [35, 190, 215]          # Slightly wider than max

CREEP_MIN_AREA = 5                         # Very small dots
CREEP_MAX_AREA = 150                       # Medium max (some creeps appear larger)
CREEP_MIN_CIRCULARITY = 0.4                # Less strict - creeps can be irregular

# Objectives: Bright yellow Abra icons  
OBJ_HSV_LOWER = [18, 80, 140]            # Bright yellow
OBJ_HSV_UPPER = [32, 255, 255]

OBJ_MIN_AREA = 80                        # Much larger than creeps
OBJ_MAX_AREA = 500

# Clustering
CLUSTER_DISTANCE = 15

# ============================================================================


def detect_creeps(minimap_img: np.ndarray) -> List[Dict]:
    """
    Detect creep camps - the dark yellowish-brown dots
    
    These are small filled circles with NO border that appear at
    fixed camp locations. Should find ~24 from objectives.png
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2GRAY)
    height, width = minimap_img.shape[:2]
    
    # Find dark yellowish-brown regions
    lower = np.array(CREEP_HSV_LOWER)
    upper = np.array(CREEP_HSV_UPPER)
    yellow_mask = cv2.inRange(hsv, lower, upper)
    
    # Clean morphology
    kernel = np.ones((2, 2), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)
    
    # Blob detection with STRICT parameters
    params = cv2.SimpleBlobDetector_Params()
    params.filterByColor = True
    params.blobColor = 255
    params.filterByArea = True
    params.minArea = CREEP_MIN_AREA
    params.maxArea = CREEP_MAX_AREA
    params.filterByCircularity = True
    params.minCircularity = CREEP_MIN_CIRCULARITY
    params.filterByConvexity = True
    params.minConvexity = 0.75
    params.filterByInertia = True
    params.minInertiaRatio = 0.6
    
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(yellow_mask)
    
    creeps = []
    
    for kp in keypoints:
        cx, cy = int(kp.pt[0]), int(kp.pt[1])
        radius = int(kp.size / 2)
        
        if cx < 5 or cy < 5 or cx >= width - 5 or cy >= height - 5:
            continue
        
        # Verify it's dark (not bright like objectives)
        sample_size = max(3, radius + 2)
        y1 = max(0, cy - sample_size)
        y2 = min(height, cy + sample_size)
        x1 = max(0, cx - sample_size)
        x2 = min(width, cx + sample_size)
        
        sample_region = hsv[y1:y2, x1:x2]
        if sample_region.size == 0:
            continue
        
        # Check color match
        sample_mask = cv2.inRange(sample_region, lower, upper)
        yellow_ratio = cv2.countNonZero(sample_mask) / sample_mask.size if sample_mask.size > 0 else 0
        
        if yellow_ratio < 0.2:  # Lower threshold
            continue
        
        size = "small" if radius <= 5 else "medium"
        
        creeps.append({
            'position': (cx, cy),
            'radius': radius if radius > 0 else 3,
            'size': size
        })
    
    return creeps


def detect_objectives(minimap_img: np.ndarray) -> List[Dict]:
    """
    Detect objectives - bright yellow Abra head icons
    Should find ~1 from objectives.png
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    height, width = minimap_img.shape[:2]
    
    # Find bright yellow
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
        
        # Not too elongated
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            continue
        
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        if cx < 10 or cy < 10 or cx >= width - 10 or cy >= height - 10:
            continue
        
        objectives.append({
            'position': (cx, cy),
            'area': area,
            'bbox': (x, y, w, h)
        })
    
    return objectives


def cluster_positions(detections: List[Dict], distance_threshold: int = None) -> Dict[int, List[Dict]]:
    """Cluster detections at same location across frames"""
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
# TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python creep_objective_detector_v2.py <image.png>")
        sys.exit(1)
    
    img_path = sys.argv[1]
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"Error: Could not load {img_path}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"ANALYZING: {img_path}")
    print(f"{'='*60}")
    print(f"\nTarget: ~24 creeps, ~1 objective (from objectives.png)")
    
    creeps = detect_creeps(img)
    objectives = detect_objectives(img)
    
    print(f"\n🟡 Found {len(creeps)} creeps:")
    for i, creep in enumerate(creeps, 1):
        pos = creep['position']
        print(f"  {i}. {creep['size'].upper():6s} at ({pos[0]:3d}, {pos[1]:3d}) "
              f"radius={creep['radius']}px")
    
    print(f"\n🎯 Found {len(objectives)} objectives:")
    for i, obj in enumerate(objectives, 1):
        pos = obj['position']
        print(f"  {i}. OBJECTIVE at ({pos[0]:3d}, {pos[1]:3d}) area={obj['area']:.0f}px")
    
    # Visualize
    debug_img = img.copy()
    
    for creep in creeps:
        pos = creep['position']
        # Just a small dot, no circle
        cv2.circle(debug_img, pos, 2, (0, 255, 0), -1)  # Green filled dot
    
    for obj in objectives:
        pos = obj['position']
        cv2.circle(debug_img, pos, 10, (0, 255, 255), 2)  # Yellow circle
        cv2.circle(debug_img, pos, 2, (0, 255, 255), -1)
    
    # Save
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'creep_detection_v2.png'
    cv2.imwrite(str(output_path), debug_img)
    
    # Create HSV mask visualization
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    creep_mask = cv2.inRange(hsv, np.array(CREEP_HSV_LOWER), np.array(CREEP_HSV_UPPER))
    obj_mask = cv2.inRange(hsv, np.array(OBJ_HSV_LOWER), np.array(OBJ_HSV_UPPER))
    
    h, w = img.shape[:2]
    debug_full = np.zeros((h, w*3, 3), dtype=np.uint8)
    debug_full[:, :w] = debug_img
    debug_full[:, w:w*2] = cv2.cvtColor(creep_mask, cv2.COLOR_GRAY2BGR)
    debug_full[:, w*2:] = cv2.cvtColor(obj_mask, cv2.COLOR_GRAY2BGR)
    
    cv2.putText(debug_full, f"Detected ({len(creeps)} creeps)", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(debug_full, "Creep HSV Mask", (w + 10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(debug_full, "Objective HSV Mask", (w*2 + 10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    debug_path = output_dir / 'debug_v2.png'
    cv2.imwrite(str(debug_path), debug_full)
    
    print(f"\n✅ Saved:")
    print(f"   {output_path}")
    print(f"   {debug_path}")
    
    if len(creeps) > 30:
        print(f"\n⚠️  Too many creeps detected! Expected ~24")
        print(f"   Increase CREEP_HSV_LOWER or decrease CREEP_HSV_UPPER")
    elif len(creeps) < 20:
        print(f"\n⚠️  Too few creeps detected! Expected ~24")
        print(f"   Decrease CREEP_HSV_LOWER or increase CREEP_HSV_UPPER")
    else:
        print(f"\n✅ Good detection count! (~24 expected)")
