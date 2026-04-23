# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import math

WIDTH = None
HEIGHT = None
LEFT_WIDTH = None
RIGHT_WIDTH = None

# Visualization parameters:
TYPICAL_DIST = 50
TYPICAL_VEL = 10

# Window layout (simulation display)
LEFT_PERCENTAGE = 0.5     # Fraction of screen width used for the "world" (left panel)
HIGHT_PERCENTAGE = 0.7    # Fraction of screen height used
LEFT_X = 0
LEFT_Y = 0

RIGHT_X = 0
RIGHT_Y = 0
RIGHT_VX = 0
RIGHT_VY = 0

# General visualization parameters
FPS = 60             
DT_SAMPLE = 2.            # Real time between stroboscopic snapshots
DT_FLASH = 0.1            # Duration of the flash (real time)
PARTICLE_RAD = 0.1        # Particle radius on screen (not physical). See draw.py (currently unused)

# Particle configuration:
PART_CFR = 0.1            # Contact interaction radius (in simulation units)
PART_CR = 1.              # Coefficient of restitution (0 = inelastic, 1 = elastic)
PART_COLL = True          # Enable/disable collisions
PART_FUS_VTHRE = 2.       # Relative velocity threshold for fusion (with gravity, relative energy condition is used instead)

# "World" configuration:
INTEGRATOR = "verlet"     # Integrators: "euler", "cromer", "verlet" (from worse to better)
SIM_DT_PARAM = 0.02       # Simulation timestep factor (smaller means smaller timestep)

GRAV_G = 4*100*math.pi**2    # Gravitational constant (G = 0 disables gravity)

WALLS = False    # If True, particles bounce off boundaries
BOUNDS = None    # = None or True
                 # BOUNDS = None -> particles can escape the simulation window
                 # BOUNDS = True -> simulation window acts as boundary
                 #   if WALLS = True → particles bounce
                 #   if WALLS = False → simulation stops when a particle exits

                 # NOTE: WALLS = True && BOUNDS = None is equivalent to WALLS = False

def init():
    print("")
    import pygame
    info = pygame.display.Info()

    global WIDTH, HEIGHT, LEFT_WIDTH, RIGHT_WIDTH,    LPIXELS_PER_UNIT, RPIXELS_PER_UNIT, RPIXELS_PER_UNIT_V, BOUNDS, RIGHT_X, RIGHT_Y, RIGHT_VX, RIGHT_VY  # DT_SAMPLE, FPS

    WIDTH = info.current_w - 100
    HEIGHT = int(info.current_h * HIGHT_PERCENTAGE)

    LEFT_WIDTH = int(WIDTH * LEFT_PERCENTAGE)
    RIGHT_WIDTH = WIDTH - LEFT_WIDTH

    # Left panel zoom
    LPIXELS_PER_UNIT = int(LEFT_WIDTH/(3*TYPICAL_DIST))   # 1 simulation unit = this many screen pixels
    if LPIXELS_PER_UNIT < 1:
        print("WARNING:  LPIXELS_PER_UNIT set to 1")
        LPIXELS_PER_UNIT = 1

    # Right panel zoom (positions)
    RPIXELS_PER_UNIT = int(RIGHT_WIDTH/(6*TYPICAL_DIST))
    if RPIXELS_PER_UNIT < 1:
        print("WARNING:  RPIXELS_PER_UNIT set to 1")
        RPIXELS_PER_UNIT = 1
    RIGHT_X = RIGHT_WIDTH // 4

    # Right panel zoom (velocities)
    RPIXELS_PER_UNIT_V = int(RIGHT_WIDTH/(5*TYPICAL_VEL))
    if RPIXELS_PER_UNIT_V < 1:
        print("WARNING:  RPIXELS_PER_UNIT (velocities) set to 1")
        RPIXELS_PER_UNIT_V = 1
    RIGHT_VX = RIGHT_WIDTH // 2 
    RIGHT_VY = 3* HEIGHT // 4

    # Particle display size (deprecated)
    PARTICLE_RAD = int(PART_CFR * LPIXELS_PER_UNIT)
    if PARTICLE_RAD < 1:
        print("PART_CFR too small to be visible: PARTICLE_RAD set to 1")
        PARTICLE_RAD = 1


    print("")
    print("Screen width: ", WIDTH, " and height: ", HEIGHT)
    print("Left screen width: ", LEFT_WIDTH)
    
    print(f"Pixels per unitat als càlculs: {LPIXELS_PER_UNIT}, Radi part. a la pantalla: {PARTICLE_RAD} Radi forces de contacte (als càlculs): {PART_CFR:.3e}")







