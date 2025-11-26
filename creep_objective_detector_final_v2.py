#!/usr/bin/env python3
"""
FINAL V2 Creep and Objective Detector
- Improved creep clustering (3.5x radius zone)
- Only detects INSIDE minimap oval (no off-map detections)
- Better deduplication
"""

import cv2
import numpy as np
from typing import List, Dict

# Creep detection - broader yellow range
CREEP_HSV_LOWER = [10, 20, 120]
CREEP_HSV_UPPER = [45, 255, 255]
CREEP_MIN_AREA = 3
CREEP_MAX_AREA = 150
CREEP_MIN_CIRCULARITY = 0.3

# Objectives - bright yellow
OBJ_HSV_LOWER = [18, 80, 140]
OBJ_HSV_UPPER = [32, 255, 255]
OBJ_MIN_AREA = 80
OBJ_MAX_AREA = 500

# Clustering - 3.5x radius zone
CLUSTER_RADIUS_MULTIPLIER = 3.5


def get_minimap_mask(minimap_img: np.ndarray) -> np.ndarray:
    """
    Create a mask of the actual minimap oval to exclude off-map detections
    The minimap is an oval shape, we need to mask out areas outside it
    """
    height, width = minimap_img.shape[:2]
    
    # Create mask - start with all black
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # The minimap is roughly centered with some margin
    # Oval dimensions (slightly smaller than full image to exclude edges)
    center_x = width // 2
    center_y = height // 2
    
    # Axes (make oval slightly smaller than image to avoid edges)
    axes_x = int(width * 0.45)   # 90% of half-width
    axes_y = int(height * 0.45)  # 90% of half-height
    
    # Draw filled ellipse (this is the playable area)
    cv2.ellipse(mask, (center_x, center_y), (axes_x, axes_y), 0, 0, 360, 255, -1)
    
    return mask


def detect_creeps(minimap_img: np.ndarray) -> List[Dict]:
    """
    Detect creep camps - tiny yellow/brown dots
    Only detects INSIDE the minimap oval
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    height, width = minimap_img.shape[:2]
    
    # Get minimap mask (only detect inside oval)
    minimap_mask = get_minimap_mask(minimap_img)
    
    # Find yellow regions
    lower = np.array(CREEP_HSV_LOWER)
    upper = np.array(CREEP_HSV_UPPER)
    yellow_mask = cv2.inRange(hsv, lower, upper)
    
    # Apply minimap mask - only keep detections INSIDE the oval
    yellow_mask = cv2.bitwise_and(yellow_mask, minimap_mask)
    
    # Clean morphology (very gentle)
    kernel = np.ones((2, 2), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Blob detection
    params = cv2.SimpleBlobDetector_Params()
    params.filterByColor = True
    params.blobColor = 255
    params.filterByArea = True
    params.minArea = CREEP_MIN_AREA
    params.maxArea = CREEP_MAX_AREA
    params.filterByCircularity = True
    params.minCircularity = CREEP_MIN_CIRCULARITY
    params.filterByConvexity = False
    params.filterByInertia = False
    
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(yellow_mask)
    
    creeps = []
    
    for kp in keypoints:
        cx, cy = int(kp.pt[0]), int(kp.pt[1])
        radius = int(kp.size / 2)
        
        # Extra check: is this point inside the mask?
        if minimap_mask[cy, cx] == 0:
            continue
        
        if cx < 3 or cy < 3 or cx >= width - 3 or cy >= height - 3:
            continue
        
        size = "small" if radius <= 5 else "medium"
        
        creeps.append({
            'position': (cx, cy),
            'radius': max(radius, 2),
            'size': size
        })
    
    return creeps


def detect_objectives(minimap_img: np.ndarray) -> List[Dict]:
    """
    Detect objectives - bright yellow icons
    Only detects INSIDE the minimap oval
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    height, width = minimap_img.shape[:2]
    
    # Get minimap mask
    minimap_mask = get_minimap_mask(minimap_img)
    
    lower = np.array(OBJ_HSV_LOWER)
    upper = np.array(OBJ_HSV_UPPER)
    yellow_mask = cv2.inRange(hsv, lower, upper)
    
    # Apply minimap mask
    yellow_mask = cv2.bitwise_and(yellow_mask, minimap_mask)
    
    kernel = np.ones((3, 3), np.uint8)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    objectives = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if area < OBJ_MIN_AREA or area > OBJ_MAX_AREA:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 0
        
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            continue
        
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        # Check inside mask
        if minimap_mask[cy, cx] == 0:
            continue
        
        if cx < 10 or cy < 10 or cx >= width - 10 or cy >= height - 10:
            continue
        
        objectives.append({
            'position': (cx, cy),
            'area': area,
            'bbox': (x, y, w, h)
        })
    
    return objectives


def cluster_positions(detections: List[Dict], distance_threshold: int = None) -> Dict[int, List[Dict]]:
    """
    Cluster detections using 3.5x radius zone
    Anything within 3.5x the detected radius is considered the same creep
    """
    if not detections:
        return {}
    
    detections = sorted(detections, key=lambda d: d.get('frame', 0))
    
    clusters = {}
    cluster_id = 0
    
    for detection in detections:
        pos = detection['position']
        radius = detection.get('radius', 3)
        
        # Cluster distance is 3.5x the radius of this detection
        cluster_dist = radius * CLUSTER_RADIUS_MULTIPLIER
        
        found_cluster = False
        
        for cid, cluster_detections in clusters.items():
            cluster_positions = [d['position'] for d in cluster_detections]
            avg_x = np.mean([p[0] for p in cluster_positions])
            avg_y = np.mean([p[1] for p in cluster_positions])
            
            distance = np.sqrt((pos[0] - avg_x)**2 + (pos[1] - avg_y)**2)
            
            # Use the cluster distance from this detection
            if distance <= cluster_dist:
                clusters[cid].append(detection)
                found_cluster = True
                break
        
        if not found_cluster:
            clusters[cluster_id] = [detection]
            cluster_id += 1
    
    return clusters


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python creep_objective_detector_final_v2.py <image.png>")
        sys.exit(1)
    
    img_path = sys.argv[1]
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"Error: Could not load {img_path}")
        sys.exit(1)
    
    print(f"\nAnalyzing: {img_path}")
    
    # Show mask
    mask = get_minimap_mask(img)
    
    creeps = detect_creeps(img)
    objectives = detect_objectives(img)
    
    print(f"\n🟢 Found {len(creeps)} creeps (inside oval only)")
    print(f"🟡 Found {len(objectives)} objectives")
    
    # Visualize
    debug_img = img.copy()
    
    # Draw mask boundary for reference
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(debug_img, contours, -1, (255, 0, 0), 1)
    
    for creep in creeps:
        pos = creep['position']
        cv2.circle(debug_img, pos, 2, (0, 255, 0), -1)  # Green dot
    
    for obj in objectives:
        pos = obj['position']
        cv2.circle(debug_img, pos, 10, (0, 255, 255), 2)  # Yellow circle
    
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'detection_v2_with_mask.png'
    cv2.imwrite(str(output_path), debug_img)
    
    # Save mask
    cv2.imwrite(str(output_dir / 'minimap_mask.png'), mask)
    
    print(f"\n✅ Saved: {output_path}")
    print(f"✅ Saved: minimap_mask.png")

