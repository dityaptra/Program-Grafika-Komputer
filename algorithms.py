# algorithms.py
import math

class Algo:
    @staticmethod
    def brute_force_line(x1, y1, x2, y2):
        points = []
        if x1 == x2:
            y = min(y1, y2)
            while y <= max(y1, y2):
                points.append((x1, y))
                y += 1
        elif y1 == y2:
            x = min(x1, x2)
            while x <= max(x1, x2):
                points.append((x, y1))
                x += 1
        else:
            m = (y2 - y1) / (x2 - x1)
            step = 1 if x1 < x2 else -1
            N = abs(x2 - x1) + 1
            x = x1
            for _ in range(N):
                y = m * (x - x1) + y1
                points.append((x, round(y)))
                x += step
        return points

    @staticmethod
    def brute_force_circle(xc, yc, r):
        points = []
        if r == 0: return [(xc, yc)]
        for x in range(-r, r + 1):
            if r**2 - x**2 >= 0:
                y = math.sqrt(r**2 - x**2)
                points.append((xc + x, yc + round(y)))
                points.append((xc + x, yc - round(y)))
        return points

    @staticmethod
    def dda_line(x1, y1, x2, y2):
        points = []
        dx, dy = x2 - x1, y2 - y1
        step = max(abs(dx), abs(dy))
        if step == 0: return [(x1, y1)]
        x_inc = dx / step
        y_inc = dy / step
        x, y = x1, y1
        for _ in range(int(step) + 1):
            points.append((round(x), round(y)))
            x += x_inc
            y += y_inc
        return points

    @staticmethod
    def bresenham_line(x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        if dx > dy:
            p = 2 * dy - dx
            while x != x2:
                points.append((x, y))
                x += sx
                if p >= 0: y += sy; p -= 2 * dx
                p += 2 * dy
        else:
            p = 2 * dx - dy
            while y != y2:
                points.append((x, y))
                y += sy
                if p >= 0: x += sx; p -= 2 * dy
                p += 2 * dx
        points.append((x2, y2))
        return points

    @staticmethod
    def bresenham_circle(xc, yc, r):
        points = []
        x, y = 0, r
        p = 3 - 2 * r
        while x <= y:
            points.extend([(xc + x, yc + y), (xc - x, yc + y), (xc + x, yc - y), (xc - x, yc - y),
                           (xc + y, yc + x), (xc - y, yc + x), (xc + y, yc - x), (xc - y, yc - x)])
            if p < 0: p += 4 * x + 6
            else: p += 4 * (x - y) + 10; y -= 1
            x += 1
        return points