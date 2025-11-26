#!/usr/bin/env python3
"""
Perfect Circle Pokemon Detector - FINAL TUNED VERSION
"""

import cv2
import numpy as np

def detect_pokemon_markers(minimap_img):
    """
    Detect Pokemon markers using circle detection + white center verification.
    """
    hsv = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2GRAY)
    height, width = minimap_img.shape[:2]
    
    # White detection
    lower_white = np.array([0, 0, 210])
    upper_white = np.array([180, 35, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Detect circles
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
        
        # Verify white center
        circle_mask = np.zeros(white_mask.shape, dtype=np.uint8)
        cv2.circle(circle_mask, (cx, cy), radius - 2, 255, -1)
        
        white_in_circle = cv2.bitwise_and(white_mask, circle_mask)
        white_pixel_count = cv2.countNonZero(white_in_circle)
        
        if white_pixel_count < 8:
            continue
        
        # Determine team by ring color
        ring_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.circle(ring_mask, (cx, cy), radius, 255, 2)
        
        ring_hsv = cv2.bitwise_and(hsv, hsv, mask=ring_mask)
        
        # Orange
        lower_orange = np.array([0, 70, 70])
        upper_orange = np.array([30, 255, 255])
        orange_mask = cv2.inRange(ring_hsv, lower_orange, upper_orange)
        orange_pixels = cv2.countNonZero(orange_mask)
        
        # Purple  
        lower_purple = np.array([100, 30, 30])
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

