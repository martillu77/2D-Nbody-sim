# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import config
import pickle
from pathlib import Path

def compute_scales(particles):  # called by natural_units below
    # posicions i masses en unitats de l’usuari
    import math

    # escala espacial
    L = max((p.x**2 + p.y**2)**0.5 for p in particles)

    V = max((p.vx**2 + p.vy**2)**0.5 for p in particles)

    # massa total
    M = sum(p.m for p in particles)

    return L, V, M
    
    
# Recalculate particle values (pos, vel, size, mass) with more natural units:
def natural_units(particles):
    config.TYPICAL_DIST, config.TYPICAL_VEL, config.TYPICAL_M = compute_scales(particles)
    config.TYPICAL_T = (config.TYPICAL_DIST**3 / (config.GRAV_G * config.TYPICAL_M))**0.5

    print(f"\nDist. típica: {config.TYPICAL_DIST} Massa típica: {config.TYPICAL_M} Temps típic: {config.TYPICAL_T}")

    for p in particles:
            p.x=p.x / config.TYPICAL_DIST
            p.y=p.y / config.TYPICAL_DIST
            p.vx=p.vx * config.TYPICAL_T / config.TYPICAL_DIST
            p.vy=p.vy * config.TYPICAL_T / config.TYPICAL_DIST
            p.cfr=p.cfr / config.TYPICAL_DIST
            p.m=p.m / config.TYPICAL_M

    # Left panel zoom
    L, V, M = compute_scales(particles)
    config.LPIXELS_PER_UNIT = int(config.LEFT_WIDTH/(3*L))   # 1 simulation unit = this many screen pixels
    if config.LPIXELS_PER_UNIT < 1:
        print("WARNING:  LPIXELS_PER_UNIT set to 1")
        config.LPIXELS_PER_UNIT = 1

    # Right panel zoom (positions)
    config.RPIXELS_PER_UNIT = int(config.RIGHT_WIDTH/(6*L))
    if config.RPIXELS_PER_UNIT < 1:
        print("WARNING:  RPIXELS_PER_UNIT set to 1")
        config.RPIXELS_PER_UNIT = 1

    # Right panel zoom (velocities)
    config.RPIXELS_PER_UNIT_V = int(config.RIGHT_WIDTH/(5*V))
    if config.RPIXELS_PER_UNIT_V < 1:
        print("WARNING:  RPIXELS_PER_UNIT (velocities) set to 1")
        config.RPIXELS_PER_UNIT_V = 1

    print(f"LPIXELS_PER_UNIT: {config.LPIXELS_PER_UNIT}  RPIXELS_PER_UNIT: {config.RPIXELS_PER_UNIT}   RPIXELS_PER_UNIT_V: {config.RPIXELS_PER_UNIT_V} ")

    # Particle display size (deprecated)
    config.PARTICLE_RAD = int(config.PART_CFR * config.LPIXELS_PER_UNIT)
    if config.PARTICLE_RAD < 1:
        print("PART_CFR too small to be visible: PARTICLE_RAD set to 1")
        config.PARTICLE_RAD = 1

    print(f"Pixels per unitat als càlculs: {config.LPIXELS_PER_UNIT}, Radi part. a la pantalla: {config.PARTICLE_RAD} Radi forces de contacte (als càlculs): {config.PART_CFR:.3e}")

    return particles


def save_units(timestamp, dt_sim, filename="units.pkl"):    # recuperats a config.py
    data = {
        "GRAVITY": config.GRAVITY,
        "GRAV_G": config.GRAV_G,
        "LPIXELS_PER_UNIT": config.LPIXELS_PER_UNIT,
        "RPIXELS_PER_UNIT": config.RPIXELS_PER_UNIT,
        "RPIXELS_PER_UNIT_V": config.RPIXELS_PER_UNIT_V,
        "TYPICAL_DIST": config.TYPICAL_DIST,
        "TYPICAL_VEL": config.TYPICAL_VEL,
        "TYPICAL_M": config.TYPICAL_M,
        "TYPICAL_T": config.TYPICAL_T,
        "SIM_DT_PARAM": config.SIM_DT_PARAM,
        "SIM_DT_MAX": config.SIM_DT_MAX,
        "dt_sim": dt_sim
    }
    directory = Path(timestamp)
    directory.mkdir(exist_ok=True)
    with open(directory / filename, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def user_units(particles, L, T):   # no la fa servir ningu
    return [
        Particle(
            x=p.x * L,
            y=p.y * L,
            vx=p.vx * L / T,
            vy=p.vy * L / T,
            m=p.m   # ja estava normalitzada; normalment no cal tornar
        )
        for p in particles
    ]
