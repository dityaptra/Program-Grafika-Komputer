import numpy as np
import math
import os

class GraphObject:
    def __init__(self):
        # Inisialisasi list kosong
        self.vertices = []
        self.edges = []
        
        # Matriks Transformasi 4x4 (Identitas)
        self.transform_matrix = np.identity(4)
        
        # Jarak Kamera (Untuk Proyeksi Perspektif)
        self.camera_distance = 4.0
        
        # --- LOGIKA PEMBACAAN FILE OTOMATIS ---
        # Cari folder tempat script ini berada
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Gabungkan path folder + nama file
        v_path = os.path.join(base_dir, "data_vertices.txt")
        e_path = os.path.join(base_dir, "data_edges.txt")
        
        try:
            self.load_from_files(v_path, e_path)
            print(f"[INFO] Data berhasil dimuat.")
        except FileNotFoundError:
            print(f"[ERROR] File tidak ditemukan! Pastikan 'data_vertices.txt' dan 'data_edges.txt' ada.")
            # Buat kubus darurat jika file hilang agar tidak crash
            self.create_default_cube()

    def load_from_files(self, vertex_file, edge_file):
        """Membaca koordinat dan koneksi garis dari file eksternal"""
        # 1. Baca Vertices (x, y, z)
        verts = []
        with open(vertex_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    x, y, z = map(float, parts)
                    # Tambahkan 1 untuk koordinat homogen (x, y, z, 1)
                    verts.append([x, y, z, 1.0])
        self.vertices = np.array(verts, dtype=float)

        # 2. Baca Edges (idx1, idx2)
        edges = []
        with open(edge_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    idx1, idx2 = map(int, parts)
                    edges.append((idx1, idx2))
        self.edges = edges

    def create_default_cube(self):
        self.vertices = np.array([
            [-1, -1, 1, 1], [1, -1, 1, 1], [1, 1, 1, 1], [-1, 1, 1, 1],
            [-1, -1, -1, 1], [1, -1, -1, 1], [1, 1, -1, 1], [-1, 1, -1, 1]
        ], dtype=float)
        self.edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]

    def reset_transform(self):
        self.transform_matrix = np.identity(4)

    # --- OPERASI MATRIKS (Translasi, Skala, Rotasi) ---
    def translate(self, dx, dy, dz=0):
        T = np.identity(4)
        T[0, 3], T[1, 3], T[2, 3] = dx, dy, dz
        self.transform_matrix = T @ self.transform_matrix

    def scale(self, sx, sy, sz=1):
        S = np.identity(4)
        S[0, 0], S[1, 1], S[2, 2] = sx, sy, sz
        # Post-Multiply (@ S di belakang) untuk skala dari pusat objek
        self.transform_matrix = self.transform_matrix @ S

    def rotate_x(self, angle_degree): # Pitch
        rad = math.radians(angle_degree)
        c, s = math.cos(rad), math.sin(rad)
        Rx = np.identity(4)
        Rx[1, 1], Rx[1, 2] = c, -s
        Rx[2, 1], Rx[2, 2] = s, c
        self.transform_matrix = self.transform_matrix @ Rx

    def rotate_y(self, angle_degree): # Yaw
        rad = math.radians(angle_degree)
        c, s = math.cos(rad), math.sin(rad)
        Ry = np.identity(4)
        Ry[0, 0], Ry[0, 2] = c, s
        Ry[2, 0], Ry[2, 2] = -s, c
        self.transform_matrix = self.transform_matrix @ Ry
        
    def rotate_z(self, angle_degree): # Roll
        rad = math.radians(angle_degree)
        c, s = math.cos(rad), math.sin(rad)
        Rz = np.identity(4)
        Rz[0, 0], Rz[0, 1] = c, -s
        Rz[1, 0], Rz[1, 1] = s, c
        self.transform_matrix = self.transform_matrix @ Rz

    # --- PROYEKSI KE LAYAR ---
    def project_and_transform(self):
        # 1. Terapkan Transformasi Matriks
        transformed_verts_4d = (self.transform_matrix @ self.vertices.T).T
        projected_2d = []
        
        for v in transformed_verts_4d:
            x, y, z = v[0], v[1], v[2]
            
            # 2. Proyeksi Perspektif
            z_factor = z + self.camera_distance
            if z_factor <= 0.1: z_factor = 0.1 # Cegah error bagi 0
            
            projection_scale = 1.0 / z_factor
            x_proj = x * projection_scale
            y_proj = y * projection_scale
            
            projected_2d.append([x_proj, y_proj])
            
        return np.array(projected_2d)