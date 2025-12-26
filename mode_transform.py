# mode_transform.py
import cv2
import numpy as np
import config as cfg
from models import GraphObject

class TransformMode:
    def __init__(self):
        self.window_name = "MODE 2: Transformasi Geometri"
        self.width, self.height = cfg.WIDTH, cfg.HEIGHT
        self.center_x, self.center_y = self.width // 2, self.height // 2
        
        self.canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        self.obj = GraphObject()
        
        # State
        self.auto_animate = False
        
        # Kecepatan Meluncur (Pelan)
        self.vx = 0.3
        self.vy = 0.3
        
        # Kecepatan Putar (Derajat per frame)
        self.rot_speed = 1.0 

    def to_screen(self, lx, ly):
        return int(self.center_x + (lx * cfg.GRID_SIZE)), int(self.center_y - (ly * cfg.GRID_SIZE))

    def refresh_canvas(self):
        self.canvas[:] = cfg.BG_COLOR
        
        # --- BAGIAN YANG DIHAPUS ---
        # Baris berikut ini yang sebelumnya menggambar sumbu X dan Y telah dihapus.
        # cv2.line(self.canvas, (0, self.center_y), (self.width, self.center_y), cfg.AXIS_COLOR, 1)
        # cv2.line(self.canvas, (self.center_x, 0), (self.center_x, self.height), cfg.AXIS_COLOR, 1)
        # ---------------------------

        curr_verts = self.obj.get_transformed_vertices()
        for edge in self.obj.edges:
            p1, p2 = curr_verts[edge[0]], curr_verts[edge[1]]
            sp1, sp2 = self.to_screen(*p1), self.to_screen(*p2)
            cv2.line(self.canvas, sp1, sp2, cfg.DRAW_COLOR, 2, cv2.LINE_AA)
        
        for v in curr_verts:
            cv2.circle(self.canvas, self.to_screen(*v), 4, cfg.VERTEX_COLOR, -1)
        
        self.draw_ui()

    # ... (Sisa kode di bawah ini tidak berubah dari versi sebelumnya) ...
    def draw_ui(self):
        cv2.rectangle(self.canvas, (10, 10), (380, 220), (245, 245, 245), -1)
        cv2.rectangle(self.canvas, (10, 10), (380, 220), (0, 0, 0), 1)
        
        status_text = "OTOMATIS (Spin & Bounce)" if self.auto_animate else "MANUAL (User Control)"
        status_color = (0, 200, 0) if self.auto_animate else (255, 0, 0)

        info = [
            f"STATUS: {status_text}",
            "-----------------------------",
            "[SPASI]   : Play/Pause Animasi",
            "-----------------------------",
            "KONTROL MANUAL:",
            "[W/A/S/D] : Geser (Translasi)",
            "[Q / E]   : Putar (Rotasi)",
            "[Z / X]   : Zoom (Skala)",
            "[R]       : Reset Posisi",
            "[ESC]     : Kembali ke Menu Utama"
        ]
        
        cv2.putText(self.canvas, info[0], (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2, cv2.LINE_AA)
        for i, txt in enumerate(info[1:]):
            cv2.putText(self.canvas, txt, (20, 60 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,50,50), 1, cv2.LINE_AA)

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        # Refresh awal
        self.refresh_canvas()

        while True:
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1: break
            except: break
            
            # --- LOGIKA OTOMATIS ---
            if self.auto_animate:
                # 1. Geser Objek
                self.obj.translate(self.vx, self.vy)
                
                # 2. Putar Objek (DINAMIS)
                # Cek arah gerak horizontal (vx)
                # Jika vx positif (kanan), putar positif (searah jarum jam di koordinat layar)
                # Jika vx negatif (kiri), putar negatif (berlawanan jarum jam)
                direction = 1 if self.vx > 0 else -1
                self.obj.rotate(self.rot_speed * direction) 
                
                # 3. Cek Tabrakan Dinding
                verts = self.obj.get_transformed_vertices()
                screen_verts = [self.to_screen(*v) for v in verts]
                
                xs = [v[0] for v in screen_verts]
                ys = [v[1] for v in screen_verts]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                
                # Pantul X (Kiri/Kanan) - Ini akan membalik arah vx, 
                # yang otomatis akan membalik arah putaran di frame berikutnya.
                if (min_x <= 0 and self.vx < 0) or (max_x >= self.width and self.vx > 0):
                    self.vx *= -1 
                
                # Pantul Y (Atas/Bawah)
                if (min_y <= 0 and self.vy > 0) or (max_y >= self.height and self.vy < 0):
                    self.vy *= -1

                self.refresh_canvas()

            cv2.imshow(self.window_name, self.canvas)
            
            # Delay
            key = cv2.waitKey(20) & 0xFF
            
            if key == 27: break # ESC
            
            # --- TOMBOL PENGALIH MODE ---
            elif key == 32: # SPASI
                self.auto_animate = not self.auto_animate
                self.refresh_canvas()

            # --- KONTROL MANUAL (Tetap Aktif) ---
            if key == ord('w'): self.obj.translate(0, cfg.MOVE_STEP); self.refresh_canvas()
            elif key == ord('s'): self.obj.translate(0, -cfg.MOVE_STEP); self.refresh_canvas()
            elif key == ord('a'): self.obj.translate(-cfg.MOVE_STEP, 0); self.refresh_canvas()
            elif key == ord('d'): self.obj.translate(cfg.MOVE_STEP, 0); self.refresh_canvas()
            
            elif key == ord('q'): self.obj.rotate(cfg.ROT_STEP); self.refresh_canvas()
            elif key == ord('e'): self.obj.rotate(-cfg.ROT_STEP); self.refresh_canvas()
                
            elif key == ord('z'): self.obj.scale(1 + cfg.SCALE_STEP, 1 + cfg.SCALE_STEP); self.refresh_canvas()
            elif key == ord('x'): self.obj.scale(1 - cfg.SCALE_STEP, 1 - cfg.SCALE_STEP); self.refresh_canvas()
                
            elif key == ord('r'): self.obj.reset_transform(); self.refresh_canvas()
        
        cv2.destroyWindow(self.window_name)