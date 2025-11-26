#!/usr/bin/env python3
"""
Pokemon Unite Tracker - PRODUCTION VERSION
- Perfect 1:1 aspect ratio
- Oval masking (no off-map detections)
- 3.5x radius clustering for creeps
- Green timestamps for creeps, yellow for objectives
- Proper scaling for heatmap overlay
"""

import cv2
import numpy as np
import json
import time
import signal
import sys
from pathlib import Path
from datetime import datetime

try:
    from PIL import ImageGrab
except ImportError:
    print("❌ pip install pillow")
    sys.exit(1)

# Config
DELETE_SCREENSHOTS = True
ORANGE_COLOR = (0, 154, 255)  # BGR  
PURPLE_COLOR = (255, 76, 175)
CAPTURE_DURATION = 600
CAPTURE_FPS = 1

OBJECTIVE_ZONES = [
    {'name': 'top', 'region': (0.35, 0.05, 0.65, 0.25)},
    {'name': 'center', 'region': (0.35, 0.35, 0.65, 0.65)},
    {'name': 'bottom', 'region': (0.35, 0.75, 0.65, 0.95)}
]

# Import detectors
from pokemon_detector import detect_pokemon_markers
from creep_objective_detector_final_v2 import detect_creeps, detect_objectives, cluster_positions
from minimap_detector_final import auto_detect_minimap_final

should_stop = False

def signal_handler(sig, frame):
    global should_stop
    print('\n⚠️  Stopping...')
    should_stop = True

signal.signal(signal.SIGINT, signal_handler)


def assign_objective_to_zone(position, minimap_width, minimap_height):
    x, y = position
    x_frac = x / minimap_width
    y_frac = y / minimap_height
    for zone in OBJECTIVE_ZONES:
        x1, y1, x2, y2 = zone['region']
        if x1 <= x_frac <= x2 and y1 <= y_frac <= y2:
            return zone['name']
    return None


class Tracker:
    def __init__(self):
        self.output_dir = Path("outputs")
        self.tmp_dir = Path("tmp")
        self.output_dir.mkdir(exist_ok=True)
        self.tmp_dir.mkdir(exist_ok=True)
        
        # Clear tmp
        for f in self.tmp_dir.glob("*.png"):
            f.unlink()
        
        # Load reference map
        ref_paths = [Path("/mnt/project/theiaskyruins.png"), Path("theiaskyruins.png")]
        self.reference_map = None
        for rp in ref_paths:
            if rp.exists():
                self.reference_map = cv2.imread(str(rp))
                print(f"✅ Map loaded: {self.reference_map.shape[1]}x{self.reference_map.shape[0]}")
                break
        
        if self.reference_map is None:
            print("❌ theiaskyruins.png not found!")
            sys.exit(1)
        
        self.minimap_region = None
        self.screenshots_captured = 0
        self.start_time = None
    
    def capture_screen(self):
        try:
            screenshot = ImageGrab.grab()
            screen = np.array(screenshot)
            return cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        except:
            return None
    
    def phase1_capture(self):
        global should_stop
        print("\n" + "=" * 70)
        print("📸 PHASE 1: CAPTURE")
        print("=" * 70)
        
        print("🔍 Waiting for minimap...")
        while not should_stop:
            screen = self.capture_screen()
            if screen is None:
                time.sleep(0.5)
                continue
            
            region = auto_detect_minimap_final(screen)
            if region:
                self.minimap_region = region
                x1, y1, x2, y2 = region
                w, h = x2 - x1, y2 - y1
                aspect = w / h
                print(f"✅ DETECTED at ({x1},{y1}) to ({x2},{y2})")
                print(f"   Size: {w}x{h}, Aspect: {aspect:.6f}")
                
                minimap = screen[y1:y2, x1:x2]
                cv2.imwrite(str(self.output_dir / "minimap_preview.png"), minimap)
                break
            time.sleep(0.5)
        
        if should_stop:
            return
        
        print(f"\n⏱️  Capturing for {CAPTURE_DURATION}s...")
        self.start_time = time.time()
        frame_interval = 1.0 / CAPTURE_FPS
        
        while not should_stop and self.screenshots_captured < CAPTURE_DURATION * CAPTURE_FPS:
            frame_start = time.time()
            
            screen = self.capture_screen()
            if screen is not None and self.minimap_region:
                x1, y1, x2, y2 = self.minimap_region
                minimap = screen[y1:y2, x1:x2]
                
                path = self.tmp_dir / f"screenshot_{self.screenshots_captured:04d}.png"
                cv2.imwrite(str(path), minimap)
                self.screenshots_captured += 1
                
                if self.screenshots_captured % 60 == 0:
                    print(f"   {self.screenshots_captured}/{CAPTURE_DURATION}")
            
            elapsed = time.time() - frame_start
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
        
        print(f"\n✅ Captured {self.screenshots_captured} frames")
    
    def phase2_process(self):
        print("\n" + "=" * 70)
        print("📄 PHASE 2: PROCESS")
        print("=" * 70)
        
        purple_pos = []
        orange_pos = []
        creep_det = []
        obj_det = []
        
        files = sorted(self.tmp_dir.glob("screenshot_*.png"))
        total = len(files)
        
        if total == 0:
            print("❌ No screenshots!")
            return None, None, None, None
        
        first_img = cv2.imread(str(files[0]))
        minimap_height, minimap_width = first_img.shape[:2]
        
        for idx, f in enumerate(files):
            img = cv2.imread(str(f))
            if img is None:
                continue
            
            # Players
            markers, _, _ = detect_pokemon_markers(img)
            for m in markers:
                pos = m['position']
                if m['team'] == 'orange':
                    orange_pos.append({'x': pos[0], 'y': pos[1]})
                else:
                    purple_pos.append({'x': pos[0], 'y': pos[1]})
            
            # Creeps (exclude objective zones)
            creeps = detect_creeps(img)
            for c in creeps:
                pos = c['position']
                zone = assign_objective_to_zone(pos, minimap_width, minimap_height)
                if zone is None:
                    creep_det.append({
                        'position': pos, 
                        'frame': idx,
                        'radius': c.get('radius', 3)
                    })
            
            # Objectives (only in zones)
            objectives = detect_objectives(img)
            for obj in objectives:
                pos = obj['position']
                zone = assign_objective_to_zone(pos, minimap_width, minimap_height)
                if zone:
                    obj_det.append({'position': pos, 'zone': zone, 'frame': idx})
            
            if (idx + 1) % 50 == 0:
                print(f"   {idx + 1}/{total}")
        
        print(f"\n✅ Purple: {len(purple_pos)}, Orange: {len(orange_pos)}")
        print(f"   Creeps: {len(creep_det)}, Objectives: {len(obj_det)}")
        
        return purple_pos, orange_pos, creep_det, obj_det
    
    def phase3_generate(self, purple_pos, orange_pos, creep_det, obj_det):
        if purple_pos is None:
            return
        
        print("\n" + "=" * 70)
        print("🎨 PHASE 3: GENERATE")
        print("=" * 70)
        
        base = self.reference_map.copy()
        height, width = base.shape[:2]
        
        # Scaling
        files = sorted(self.tmp_dir.glob("screenshot_*.png"))
        if files:
            sample = cv2.imread(str(files[0]))
            capture_h, capture_w = sample.shape[:2]
            scale_x = width / capture_w
            scale_y = height / capture_h
            
            print(f"   Capture: {capture_w}x{capture_h}")
            print(f"   Reference: {width}x{height}")
            print(f"   Scale: {scale_x:.4f}x, {scale_y:.4f}y")
        else:
            scale_x = scale_y = 1.0
        
        # Heatmaps
        hmap_o = np.zeros((height, width), dtype=np.float32)
        hmap_p = np.zeros((height, width), dtype=np.float32)
        
        for pos in orange_pos:
            x, y = int(pos['x'] * scale_x), int(pos['y'] * scale_y)
            if 0 <= x < width and 0 <= y < height:
                hmap_o[y, x] += 1
        
        for pos in purple_pos:
            x, y = int(pos['x'] * scale_x), int(pos['y'] * scale_y)
            if 0 <= x < width and 0 <= y < height:
                hmap_p[y, x] += 1
        
        # Blur
        if hmap_o.max() > 0:
            hmap_o = cv2.GaussianBlur(hmap_o, (25, 25), 0)
            hmap_o = hmap_o / hmap_o.max()
        
        if hmap_p.max() > 0:
            hmap_p = cv2.GaussianBlur(hmap_p, (25, 25), 0)
            hmap_p = hmap_p / hmap_p.max()
        
        # Apply
        overlay = base.copy().astype(np.float32)
        for y in range(height):
            for x in range(width):
                if hmap_o[y, x] > 0:
                    intensity = 0.01 + hmap_o[y, x] * 0.99
                    alpha = min(intensity * 0.6, 0.8)
                    overlay[y, x] = overlay[y, x] * (1 - alpha) + np.array(ORANGE_COLOR) * alpha
                if hmap_p[y, x] > 0:
                    intensity = 0.01 + hmap_p[y, x] * 0.99
                    alpha = min(intensity * 0.6, 0.8)
                    overlay[y, x] = overlay[y, x] * (1 - alpha) + np.array(PURPLE_COLOR) * alpha
        
        final = overlay.astype(np.uint8)
        
        # Creeps with 3.5x clustering
        creep_camps = cluster_positions(creep_det)
        for camp_id, dets in creep_camps.items():
            if not dets:
                continue
            avg_x = int(np.mean([d['position'][0] for d in dets]) * scale_x)
            avg_y = int(np.mean([d['position'][1] for d in dets]) * scale_y)
            if avg_x < 10 or avg_y < 10 or avg_x >= width - 10 or avg_y >= height - 10:
                continue
            uptime_s = len(dets)
            mins = uptime_s // 60
            secs = uptime_s % 60
            txt = f"{mins:02d}:{secs:02d}"
            
            # Yellow dot, GREEN text
            cv2.circle(final, (avg_x, avg_y), 3, (0, 255, 255), -1)
            cv2.putText(final, txt, (avg_x + 8, avg_y + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
        
        print(f"   {len(creep_camps)} creep camps (3.5x clustering)")
        
        # Objectives
        obj_zones = {}
        for det in obj_det:
            zone = det['zone']
            if zone not in obj_zones:
                obj_zones[zone] = []
            obj_zones[zone].append(det)
        
        for zone_name, dets in obj_zones.items():
            if not dets:
                continue
            avg_x = int(np.mean([d['position'][0] for d in dets]) * scale_x)
            avg_y = int(np.mean([d['position'][1] for d in dets]) * scale_y)
            if avg_x < 10 or avg_y < 10 or avg_x >= width - 10 or avg_y >= height - 10:
                continue
            uptime_s = len(dets)
            mins = uptime_s // 60
            secs = uptime_s % 60
            txt = f"{mins:02d}:{secs:02d}"
            
            # Yellow dot, YELLOW text
            cv2.circle(final, (avg_x, avg_y), 3, (0, 255, 255), -1)
            cv2.putText(final, txt, (avg_x + 8, avg_y + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
        
        print(f"   {len(obj_zones)} objective zones")
        
        # Save
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = self.output_dir / f"heatmap_final_{ts}.png"
        cv2.imwrite(str(final_path), final)
        print(f"\n✅ {final_path}")
        
        # JSON
        tracking_data = {
            'purple_team': purple_pos,
            'orange_team': orange_pos,
            'creep_camps': {str(cid): {'position': (int(np.mean([d['position'][0] for d in dets]) * scale_x),
                                                    int(np.mean([d['position'][1] for d in dets]) * scale_y)),
                                       'uptime_seconds': len(dets)}
                            for cid, dets in creep_camps.items()},
            'objective_zones': {zone: {'position': (int(np.mean([d['position'][0] for d in dets]) * scale_x),
                                                    int(np.mean([d['position'][1] for d in dets]) * scale_y)),
                                       'uptime_seconds': len(dets)}
                                for zone, dets in obj_zones.items()},
            'metadata': {'duration': self.screenshots_captured, 'fps': CAPTURE_FPS}
        }
        
        json_path = self.output_dir / f"tracking_data_{ts}.json"
        with open(json_path, 'w') as f:
            json.dump(tracking_data, f, indent=2)
        print(f"📊 {json_path}")
        
        # Cleanup
        if DELETE_SCREENSHOTS:
            print("\n🗑️  Cleaning tmp/...")
            for f in self.tmp_dir.glob("*.png"):
                f.unlink()
    
    def run(self):
        try:
            self.phase1_capture()
            if self.screenshots_captured > 0:
                purple, orange, creeps, objs = self.phase2_process()
                self.phase3_generate(purple, orange, creeps, objs)
            print("\n✅ DONE!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    tracker = Tracker()
    tracker.run()
