# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import config

import math
import random

# --- Física ---
class Particle:
    def __init__(self, x=0, y=0, vx=0, vy=0, ax=0, ay=0, m=0.0):
        self.x = x     # posicio inicial, component x
        self.y = y     # posicio inicial, component y
        self.vx = vx   # velocitat inicial, component x
        self.vy = vy   # velocitat inicial, component y
        self.ax = ax   # acceleracio constant propia, component x
        self.ay = ay   # acceleracio constant propia, component y
        self.m = m     # massa
        self.cr = config.PART_CR               # coeficient de restitució (0 = inelàstic, 1 = elàstic)
        self.cfr = (m**(1/3))*config.PART_CFR  # radi efectiu foces de contacte (en unitats de càlcul)  m ~ phro * dr^3 => dr ~ m^(1/3)

        print(f"partícula de posició (x, y) = ({x}, {y}) velocitat (vx, vy) = ({vx}, {vy}) acceleració (ax, ay) = ({ax}, {ay}) i massa: {m}")
        
        
    @classmethod
    def generate_disk(cls, N, center, R, omega, mass=1.0):
        particles = []
        cx, cy = center

        v_max = 0.
        particles.append(cls(cx, cy, 0.0, 0.0, m=10))   # llavor al centre
        for _ in range(N):
            # --- posició (disc uniforme en àrea) ---
            r = R * math.sqrt(random.random())
            theta = 2 * math.pi * random.random()

            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)

            # --- velocitat: rotació global ---
            vx = -omega * (y - cy)
            vy =  omega * (x - cx)

            # --- petit soroll ---
            vx += 0.1 * (random.random() - 0.5)
            vy += 0.1 * (random.random() - 0.5)

            v_max = max(v_max, math.sqrt(vx**2 + vy**2))

            particles.append(cls(x, y, vx, vy, m=mass))

        print("Velocitat màxima  generada: ", v_max)
        return particles
        

        
