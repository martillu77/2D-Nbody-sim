# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import config

import math
import random

from pathlib import Path
import pickle

# --- Física ---
class Particle:
    def __init__(self, x=0, y=0, vx=0, vy=0, ax=0, ay=0, m=0.0, cfr=config.PART_CFR):
        self.x = x     # posicio inicial, component x
        self.y = y     # posicio inicial, component y
        self.vx = vx   # velocitat inicial, component x
        self.vy = vy   # velocitat inicial, component y
        self.ax = ax   # acceleracio constant propia, component x
        self.ay = ay   # acceleracio constant propia, component y
        self.m = m     # massa
        self.cr = config.PART_CR               # coeficient de restitució (0 = inelàstic, 1 = elàstic)
        self.cfr = (m**(1/3))*cfr              # radi efectiu foces de contacte (en unitats de càlcul)  m ~ phro * dr^3 => dr ~ m^(1/3)

        print(f"partícula de posició (x, y) = ({x}, {y}) velocitat (vx, vy) = ({vx:.3e}, {vy:.3e}) acceleració (ax, ay) = ({ax:.3e}, {ay:.3e}) massa: {m:.3e} cfr: {cfr:.3e}")
        
        
    @classmethod
    def generate_rotating_disk(cls, N, center, R, omega, mass=1.0, seed=config.SEED):
        particles = []
        cx, cy = center

        v_max = 0.
        random.seed(seed)
        if seed > 0:
            print(f"\n\nWARNING !!!  Randomize: seed: {seed}\n\n")
        else:
            print(f"Randomize: seed: {seed}")

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

            particles.append(cls(x, y, vx, vy, m=mass, cfr=0.5e-1))

        print("Velocitat màxima  generada: ", v_max)
        return particles

        
    @classmethod
    def generate_proto_disc(cls, N, center, R_outer, stellar_mass, omega, seed=config.SEED):
        """
        Genera un proto-disc circumestel·lar realista:
        - Estrella central massiva (Sol = 1 M☉)
        - Disc de gas i pols circumestel·lar (~0.01-1% de la massa total)
        - Velocitats keplerianes (v ∝ 1/√r) + baixa dispersió orbital
        - Distribució log-normal de masses
    
        Args:
            N: Nombre de partícules al disc
            center: Centre del sistema (x, y)
            R_outer: Radi exterior del disc (AU)
            stellar_mass: Massa de l'estrella central (M☉)
            omega: Velocitat angular de rotació global
            seed: Seed per a la generació aleatòria
    
        Returns:
            Llista amb l'estrella central + partícules del disc
        """
        from scipy.stats import lognorm
    
        random.seed(seed)
    
        # 1. Estrella central (centre massiu dominant)
        star = cls(center[0], center[1], 0.0, 0.0, 0., 0., m=stellar_mass, cfr=0.5e-1)
    
        particles = [star]
    
        # 2. Distribució log-normal de masses (comú en poblacions d'estrelles)
        # sigma ~ 1.5: dispersió moderada
        # scale ajustat per tenir la major part de la massa a l'exterior
        mass_dist = lognorm(s=1.5, scale=stellar_mass * 0.002)
    
        for _ in range(N):
            r = R_outer * math.sqrt(random.random())
            theta = 2 * math.pi * random.random()
        
            x = center[0] + r * math.cos(theta)
            y = center[1] + r * math.sin(theta)
        
            # Velocitat keplerià (v ∝ 1/√r)
            # Normalitzat: v_kepler(R_outer) = omega * R_outer
            v_kepler_local = omega * R_outer * math.sqrt(R_outer / r)
        
            vx = -v_kepler_local * math.sin(theta)
            vy =  v_kepler_local * math.cos(theta)
        
            # Dispersió orbital baixa (excentricitats ~5-10%)
            # Això permet col·lisions i accrecció gradual
            dispersion_fraction = 0.1
            vx += dispersion_fraction * v_kepler_local * (random.random() - 0.5)
            vy += dispersion_fraction * v_kepler_local * (random.random() - 0.5)
        
            # Massa segons distribució log-normal
            mass = mass_dist.rvs()
        
            # Coeficient de fricció ajustat per a partícules petites
            cfr = max(0.1e-1, mass ** (1/3) * 0.5e-1)
        
            particles.append(cls(x, y, vx, vy, ax=0, ay=0, m=mass, cfr=cfr))
    
        return particles


    @classmethod
    def generate_collapsing_cloud(cls, N, center, R_outer, cloud_mass, omega, rotational_bias, seed=config.SEED):
        """
        Genera un núvol molecular en col·lapse:
        - Cap estrella central dominant (massa distribuida)
        - Moviment gravitatori col·lectiu dominant
        - Velocitats no keplerianes (aleatòries)
        - Fase inicial de formació estel·lar
    
        Args:
            N: Nombre de partícules al núvol
            center: Centre del sistema (x, y)
            R_outer: Radi exterior del núvol (AU)
            cloud_mass: Massa total del núvol molecular (M☉)
            omega: Velocitat angular de rotació global
            rotational_bias: Biaix de rotació entre 0 i 1:
                0  : tothom sentit negatiu
                0.5: comportament simètric
                1  : tothom sentit positiu
            seed: Seed per a la generació aleatòria
    
        Returns:
            Llista amb partícules sense estrella central dominant
        """
        
        random.seed(seed)

        if not 0 <= rotational_bias <= 1:
            raise ValueError(f"rotational_bias ha de ser entre 0 i 1, rebéu: {rotational_bias}")
    
        # Normalitzador: massa per partícula si distribució uniforme
        mass_per_particle = cloud_mass / N  # Massa mitjana per partícula

        particles = []
    
        for _ in range(N):
            r = R_outer * math.sqrt(random.random())
            theta = 2 * math.pi * random.random()
        
            x = center[0] + r * math.cos(theta)
            y = center[1] + r * math.sin(theta)
        
            # Velocitats aleatòries (no keplerianes)
            # Distribució isotròpica amb dispersió moderada
            dispersion = omega * R_outer
            vx = (random.random() - rotational_bias) * dispersion
            vy = (random.random() - rotational_bias) * dispersion
        
            # Massa distribuida uniformement (o log-normal si es vol)
            mass = mass_per_particle * random.uniform(0.01, 2.0)
        
            # Coeficient de fricció ajustat per a partícules petites
            cfr = max(0.1e-1, mass ** (1/3) * 0.5e-1)
        
            particles.append(cls(x, y, vx, vy, ax=0, ay=0, m=mass, cfr=cfr))
    
        return particles




    @classmethod
    def generate_collapsing_cloud_lognormal(cls, N, center, R_outer, cloud_mass, omega, rotational_bias, sigma, seed=config.SEED):
        """
        Versió de generate_collapsing_cloud però amb distribució log-normal de masses (més realista)
        
        Additional Args:
            sigma: desviació estàndard de la distribució log-normal
        """
        from scipy.stats import lognorm
    
        random.seed(seed)

        if not 0 <= rotational_bias <= 1:
            raise ValueError(f"rotational_bias ha de ser entre 0 i 1, rebéu: {rotational_bias}")
        
        # Distribució log-normal normalitzada per a cloud_mass total
        # scale ajustat perquè la suma de masses ≈ cloud_mass
        mass_dist = lognorm(s=sigma, scale=cloud_mass * 0.01)  # Ajust del scale
    
        particles = []
    
        for _ in range(N):
            r = R_outer * math.sqrt(random.random())
            theta = 2 * math.pi * random.random()
        
            x = center[0] + r * math.cos(theta)
            y = center[1] + r * math.sin(theta)
        
            # Velocitats aleatòries
            dispersion = omega * R_outer
            vx = (random.random() - rotational_bias) * dispersion
            vy = (random.random() - rotational_bias) * dispersion
        
            # Massa segons distribució log-normal
            mass = mass_dist.rvs()
        
            cfr = max(0.1e-1, mass ** (1/3) * 0.5e-1)
        
            particles.append(cls(x, y, vx, vy, ax=0, ay=0, m=mass, cfr=cfr))
    
        return particles






    def resume(load_dir):
        with open(Path(load_dir) / "world.pkl", "rb") as f:  # es guarda a world.py
            data = pickle.load(f)

        time = data["time"]                  # total simulation time
        particles = []
        for p_data in data["particles"]:
            p = Particle(
                x=p_data["x"],
                y=p_data["y"],
                vx=p_data["vx"],
                vy=p_data["vy"],
                ax=p_data["ax"],
                ay=p_data["ay"],
                m=p_data["m"],
            )

            p.cr = p_data["cr"]
            p.cfr = p_data["cfr"]

            particles.append(p)

        return time, particles
