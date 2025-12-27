# main.py
import cv2
import numpy as np
import config as cfg

# Import kedua mode
from mode_drawing import DrawingMode
from mode_transform import TransformMode

def show_main_menu():
    window_name = "MAIN MENU: Grafika Komputer"
    canvas = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    # Design Menu Sederhana
    cv2.rectangle(canvas, (50, 50), (550, 350), (240, 240, 240), -1)
    cv2.rectangle(canvas, (50, 50), (550, 350), (0, 0, 0), 2)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "PILIH MODE APLIKASI", (140, 100), font, 0.8, (0,0,0), 2)
    
    cv2.putText(canvas, "[1] Algoritma Garis & Lingkaran", (100, 180), font, 0.6, (50,0,0), 1)
    cv2.putText(canvas, "    (Brute Force, DDA, Bresenham)", (100, 205), font, 0.4, (100,100,100), 1)
    
    cv2.putText(canvas, "[2] Transformasi Geometri", (100, 250), font, 0.6, (0,0,50), 1)
    cv2.putText(canvas, "    (Translasi, Rotasi, Skala Kubus)", (100, 275), font, 0.4, (100,100,100), 1)
    
    cv2.putText(canvas, "[ESC] Keluar", (250, 330), font, 0.6, (0,0,255), 1)

    cv2.namedWindow(window_name)
    
    while True:
        try:
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                return False # Exit signal
        except: return False

        cv2.imshow(window_name, canvas)
        key = cv2.waitKey(50) & 0xFF
        
        if key == 27: # ESC
            return False
        
        elif key == ord('1'):
            cv2.destroyWindow(window_name) # Tutup menu sementara
            app = DrawingMode()
            app.run() # Masuk Mode 1
            # Setelah Mode 1 selesai (tekan ESC), loop akan ulang dan menu muncul lagi
            cv2.namedWindow(window_name) 
            
        elif key == ord('2'):
            cv2.destroyWindow(window_name)
            app = TransformMode()
            app.run() # Masuk Mode 2
            cv2.namedWindow(window_name)
            
    return False

if __name__ == "__main__":
    show_main_menu()
    cv2.destroyAllWindows()