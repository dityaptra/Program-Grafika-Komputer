# models.py
import numpy as np
import math

class GraphObject:
    def __init__(self):
        # KUBUS 3D Wireframe
        s, d = 6, 3 # Size (Ukuran), Depth (Kedalaman)
        
        self.vertices = np.array([
            [-s, -s, 1], [ s, -s, 1], [ s,  s, 1], [-s,  s, 1], # Depan
            [-s+d, -s+d, 1], [ s+d, -s+d, 1], [ s+d,  s+d, 1], [-s+d,  s+d, 1], # Belakang
            [d/2, d/2, 1] # Pusat (Iseng tambah titik tengah)
        ], dtype=float)

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0), # Sisi Depan
            (4, 5), (5, 6), (6, 7), (7, 4), # Sisi Belakang
            (0, 4), (1, 5), (2, 6), (3, 7), # Rusuk Penghubung
            (0, 8), (2, 8), (4, 8), (6, 8)  # Garis Diagonal ke tengah
        ]
        
        # Matriks Transformasi Awal (Identitas)
        self.transform_matrix = np.identity(3)

    def reset_transform(self):
        self.transform_matrix = np.identity(3)

    def get_transformed_vertices(self):
        """Mengambil koordinat vertices setelah dikali matriks transformasi"""
        # Transpose vertices (N x 3) -> (3 x N) agar bisa dikali matriks (3 x 3)
        v_T = self.vertices.T 
        transformed_T = self.transform_matrix @ v_T
        # Kembalikan ke bentuk (N x 2) ambil x,y saja
        return transformed_T.T[:, :2]

    # --- FUNGSI TRANSLASI (GESER) ---
    def translate(self, dx, dy):
        # Matriks Translasi sederhana
        T = np.array([
            [1, 0, dx],
            [0, 1, dy],
            [0, 0, 1]
        ])
        # Kalikan ke matriks utama
        self.transform_matrix = T @ self.transform_matrix

    # --- FUNGSI SKALA (ZOOM) - FIXED ---
    def scale(self, sx, sy):
        # 1. Cari titik tengah objek SAAT INI
        curr_verts = self.get_transformed_vertices()
        cx = np.mean(curr_verts[:, 0])
        cy = np.mean(curr_verts[:, 1])

        # 2. Geser ke (0,0)
        T1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]])
        
        # 3. Lakukan Scaling
        S = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
        
        # 4. Geser balik ke posisi asal
        T2 = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]])

        # Gabungkan: T2 * S * T1 * MatriksLama
        self.transform_matrix = T2 @ S @ T1 @ self.transform_matrix

    # --- FUNGSI ROTASI (PUTAR) - FIXED ---
    def rotate(self, angle_degree):
        # 1. Cari titik tengah objek SAAT INI (Centroid)
        # Ini kuncinya: kita cari pusat objek di layar, bukan pusat layar (0,0)
        curr_verts = self.get_transformed_vertices()
        cx = np.mean(curr_verts[:, 0])
        cy = np.mean(curr_verts[:, 1])

        theta = math.radians(angle_degree)
        c, s = math.cos(theta), math.sin(theta)

        # 2. Geser objek agar titik tengahnya ada di (0,0)
        T1 = np.array([
            [1, 0, -cx], 
            [0, 1, -cy], 
            [0, 0, 1]
        ])

        # 3. Matriks Rotasi
        R = np.array([
            [c, -s, 0], 
            [s,  c, 0], 
            [0,  0, 1]
        ])

        # 4. Geser balik objek ke posisi asalnya
        T2 = np.array([
            [1, 0, cx], 
            [0, 1, cy], 
            [0, 0, 1]
        ])

        # Gabungkan semua matriks: T2 * R * T1 * MatriksLama
        self.transform_matrix = T2 @ R @ T1 @ self.transform_matrix