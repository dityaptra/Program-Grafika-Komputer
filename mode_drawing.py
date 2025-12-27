# mode_drawing.py
import cv2
import numpy as np
import math
import config as cfg
from algorithms import Algo

class DrawingMode:
    def __init__(self):
        self.window_name = "MODE 1: Algoritma Garis & Lingkaran"
        self.width, self.height = cfg.WIDTH, cfg.HEIGHT
        self.center_x, self.center_y = self.width // 2, self.height // 2
        self.canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        self.points, self.shapes = [], []
        self.algo_idx = None
        self.algo_map = {
            ord('1'): ("Brute Force (Line)", 'line', Algo.brute_force_line),
            ord('2'): ("Brute Force (Circle)", 'circle', Algo.brute_force_circle),
            ord('3'): ("DDA (Line)", 'line', Algo.dda_line),
            ord('4'): ("Bresenham (Line)", 'line', Algo.bresenham_line),
            ord('5'): ("Bresenham (Circle)", 'circle', Algo.bresenham_circle)
        }
        self.current_algo_name = "Pilih 1-5"
        self.refresh_canvas()

    def to_logical(self, sx, sy):
        return int(round((sx - self.center_x) / cfg.GRID_SIZE)), int(round((self.center_y - sy) / cfg.GRID_SIZE))

    def to_screen(self, lx, ly):
        return int(self.center_x + (lx * cfg.GRID_SIZE)), int(self.center_y - (ly * cfg.GRID_SIZE))

    def draw_label(self, screen_pos):
        lx, ly = self.to_logical(screen_pos[0], screen_pos[1])
        text = f"({lx}, {ly})"
        (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        x, y = screen_pos[0], screen_pos[1] - 15
        x, y = max(5, min(x, self.width - w - 5)), max(h + 5, y)
        cv2.rectangle(self.canvas, (x-2, y+5), (x+w+2, y-h-5), (255,255,255), -1)
        cv2.putText(self.canvas, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cfg.TEXT_COLOR, 1, cv2.LINE_AA)

    def refresh_canvas(self):
        self.canvas[:] = cfg.BG_COLOR
        for s in self.shapes:
            p1, p2 = self.to_screen(*s['p1']), self.to_screen(*s['p2'])
            if s['type'] == 'line':
                cv2.line(self.canvas, p1, p2, cfg.DRAW_COLOR, 2, cv2.LINE_AA)
                cv2.circle(self.canvas, p1, 5, cfg.DRAW_COLOR, -1); self.draw_label(p1)
                cv2.circle(self.canvas, p2, 5, cfg.DRAW_COLOR, -1); self.draw_label(p2)
            elif s['type'] == 'circle':
                r = int(math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2))
                cv2.circle(self.canvas, p1, r, cfg.DRAW_COLOR, 2, cv2.LINE_AA)
                cv2.circle(self.canvas, p1, 5, cfg.DRAW_COLOR, -1); self.draw_label(p1)
                cv2.circle(self.canvas, p2, 5, (0,0,255), -1); self.draw_label(p2)
        
        for pt in self.points: cv2.circle(self.canvas, pt, 4, (0,255,0), -1)
        
        cv2.rectangle(self.canvas, (10, 10), (350, 80), (245, 245, 245), -1)
        cv2.rectangle(self.canvas, (10, 10), (350, 80), (0, 0, 0), 1)
        cv2.putText(self.canvas, f"Mode: {self.current_algo_name}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
        cv2.putText(self.canvas, "Klik: Gambar, R: Reset, ESC: Menu Utama", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.algo_idx is None: return
            self.points.append((x, y))
            if len(self.points) == 2:
                lp1, lp2 = self.to_logical(*self.points[0]), self.to_logical(*self.points[1])
                algo_name, stype, func = self.algo_map[self.algo_idx]
                
                print(f"\n[LOG] Algoritma: {algo_name}")
                if stype == 'line': res = func(*lp1, *lp2)
                else: 
                    r = int(math.sqrt((lp2[0]-lp1[0])**2 + (lp2[1]-lp1[1])**2))
                    res = func(*lp1, r)
                    print(f"Radius: {r}")
                print(f"Titik pixel: {res[:5]} ... ({len(res)} total)")
                
                self.shapes.append({'type': stype, 'p1': lp1, 'p2': lp2})
                self.points = []
            self.refresh_canvas()

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        while True:
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1: break
            except: break
            
            cv2.imshow(self.window_name, self.canvas)
            key = cv2.waitKey(20) & 0xFF
            
            if key == 27: break # ESC
            if key in self.algo_map:
                self.algo_idx = key
                self.current_algo_name = self.algo_map[key][0]
                self.points = []
                self.refresh_canvas()
            elif key == ord('r'):
                self.points, self.shapes = [], []
                self.refresh_canvas()
        cv2.destroyWindow(self.window_name)