import cv2
import numpy as np
import config as cfg
from models import GraphObject

class Transform:
    def __init__(self):
        self.window_name = "TUGAS GRAFIKA: 3D Viewer"
        self.width, self.height = cfg.WIDTH, cfg.HEIGHT
        self.center_x, self.center_y = self.width // 2, self.height // 2
        
        self.canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        self.obj = GraphObject() # Membaca file txt otomatis
        
        self.auto_animate = False
        self.rot_speed = 1.5

    def to_screen(self, lx, ly):
        # Konversi koordinat logika ke pixel layar
        return int(self.center_x + (lx * cfg.GRID_SIZE)), int(self.center_y - (ly * cfg.GRID_SIZE))

    def refresh_canvas(self):
        self.canvas[:] = cfg.BG_COLOR # Reset Background

        # 1. Hitung Posisi Titik
        projected_verts = self.obj.project_and_transform()

        # 2. Gambar GARIS (Manipulasi Pixel)
        if len(self.obj.edges) > 0:
            for edge in self.obj.edges:
                # Pastikan index valid
                if edge[0] < len(projected_verts) and edge[1] < len(projected_verts):
                    p1 = projected_verts[edge[0]]
                    p2 = projected_verts[edge[1]]
                    sp1 = self.to_screen(*p1)
                    sp2 = self.to_screen(*p2)
                    cv2.line(self.canvas, sp1, sp2, cfg.LINE_COLOR, 2, cv2.LINE_AA)
        
        # 3. Gambar TITIK
        for v in projected_verts:
            cv2.circle(self.canvas, self.to_screen(*v), 4, cfg.VERTEX_COLOR, -1)
        
        self.draw_ui()

    def draw_ui(self):
        status = "AUTO ANIMASI" if self.auto_animate else "MANUAL CONTROL"
        color = (0, 255, 0) if self.auto_animate else (0, 255, 255)
        
        cv2.putText(self.canvas, f"STATUS: {status}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        info = [
            "[SPASI] : Auto On/Off",
            "-----------------------",
            "[W/A/S/D] : GESER (Translasi)",
            "[I/J/K/L] : PUTAR (Rotasi)",
            "[U / O]   : MIRING (Rotasi Z)",
            "[Z / X]   : ZOOM (Skala)",
            "[R]       : RESET"
        ]
        for i, txt in enumerate(info):
            cv2.putText(self.canvas, txt, (20, 60 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cfg.TEXT_COLOR, 1)

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self.refresh_canvas()

        while True:
            try:
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1: break
            except: break
            
            if self.auto_animate:
                self.obj.rotate_y(self.rot_speed)
                self.obj.rotate_x(self.rot_speed * 0.5)
                self.refresh_canvas()

            cv2.imshow(self.window_name, self.canvas)
            key = cv2.waitKey(20) & 0xFF

            if key == 27: break # ESC
            elif key == 32: self.auto_animate = not self.auto_animate
            
            # --- TRANSLASI (WASD) ---
            elif key == ord('w'): self.obj.translate(0, 0.1, 0); self.refresh_canvas()
            elif key == ord('s'): self.obj.translate(0, -0.1, 0); self.refresh_canvas()
            elif key == ord('a'): self.obj.translate(-0.1, 0, 0); self.refresh_canvas()
            elif key == ord('d'): self.obj.translate(0.1, 0, 0); self.refresh_canvas()
            
            # --- ROTASI (IJKL + UO) ---
            elif key == ord('i'): self.obj.rotate_x(cfg.ROT_STEP); self.refresh_canvas()
            elif key == ord('k'): self.obj.rotate_x(-cfg.ROT_STEP); self.refresh_canvas()
            elif key == ord('j'): self.obj.rotate_y(cfg.ROT_STEP); self.refresh_canvas()
            elif key == ord('l'): self.obj.rotate_y(-cfg.ROT_STEP); self.refresh_canvas()
            elif key == ord('u'): self.obj.rotate_z(cfg.ROT_STEP); self.refresh_canvas()
            elif key == ord('o'): self.obj.rotate_z(-cfg.ROT_STEP); self.refresh_canvas()
            
            # --- SKALA (ZX) ---
            elif key == ord('z'): self.obj.scale(1.1, 1.1, 1.1); self.refresh_canvas()
            elif key == ord('x'): self.obj.scale(0.9, 0.9, 0.9); self.refresh_canvas()
            
            # --- RESET ---
            elif key == ord('r'): self.obj.reset_transform(); self.refresh_canvas()
        
        cv2.destroyWindow(self.window_name)