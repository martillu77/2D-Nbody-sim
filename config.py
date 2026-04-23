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

# Per la visualització:
TYPICAL_DIST = 50
TYPICAL_VEL = 10

# Mides de les finestres de la visualització de la simulació
LEFT_PERCENTAGE = 0.5     # Percentatge de la amplada de la pantalla que es fa servir per visualitzar el "món" (pantalla de la esquerra)
HIGHT_PERCENTAGE = 0.7    # Percentatge de la alçada de la pantalla que es fa servir
LEFT_X = 0
LEFT_Y = 0

RIGHT_X = 0
RIGHT_Y = 0
RIGHT_VX = 0
RIGHT_VY = 0

# Paràmetres de visualització general
FPS = 60             
DT_SAMPLE = 2.            # Temps real (no de simulació) entre flaxos estroboscòpics
DT_FLASH = 0.1            # Duració en temps real del flaix
PARTICLE_RAD = 0.1        # Radi del les partícules a la pantalla, no es un paràmetre físic. Veure draw.py (ara en desús)

# Configuració de les partícules:
PART_CFR = 0.1            # Radi de les forces de contacte (en unitats de càlcul)
PART_CR = 1.             # coeficient de restitució (0 = inelàstic, 1 = elàstic)
PART_COLL = True         # Col.lisions amb coef. de restitució PART_CR permès sí (True) o no (False).
PART_FUS_VTHRE = 2.      # Velocitat relativa per fusionar dues partícules  -> amb gravetat fem servir la condició amb E_rel

# Configuració del "món":
INTEGRATOR = "verlet"     # Integradors : "euler", "cromer", "verlet"   (de pitjors a millors).
SIM_DT_PARAM = 0.02        # Aquest paràmetre controla el pas del temps als càlculs de la simulació: +petit = pas més curt

GRAV_G = 4*100*math.pi**2      # Constant de la gravitació universal. Si G = 0 no hi ha gravetat

WALLS = False   # Si hi ha parets aleshores les partícules reboten: True or False
BOUNDS = None   # = None o True
                # BOUNDS = None -> Les partícules poden escapar la finestra de simulació
                # BOUNDS = True -> Les partícules tenen la finestra de simulació com a límit. 
                #                  Si hi ha parets (WALLS = True), les partícules reboten com si la finestra de simulació tingués parets.
                #                  Si no n'hi ha (WALLS = False), la simulació s'atura quan una partícula surt de la finestra.

                # ATENCIÓ: WALLS = True && BOUNDS = None és equivalent a WALLS = False

def init():
    print("")
    import pygame
    info = pygame.display.Info()

    global WIDTH, HEIGHT, LEFT_WIDTH, RIGHT_WIDTH,    LPIXELS_PER_UNIT, RPIXELS_PER_UNIT, RPIXELS_PER_UNIT_V, BOUNDS, RIGHT_X, RIGHT_Y, RIGHT_VX, RIGHT_VY  # DT_SAMPLE, FPS

    WIDTH = info.current_w - 100
    HEIGHT = int(info.current_h * HIGHT_PERCENTAGE)

    LEFT_WIDTH = int(WIDTH * LEFT_PERCENTAGE)
    RIGHT_WIDTH = WIDTH - LEFT_WIDTH

    # Zoom pantalla esquerra
    LPIXELS_PER_UNIT = int(LEFT_WIDTH/(3*TYPICAL_DIST))   # 1 unitat de longitud en el càlculs, equival a PIXELS_PER_UNIT a la pantalla
    if LPIXELS_PER_UNIT < 1:
        print("ATENCIÓ:  LPIXELS_PER_UNIT fixat a 1")
        LPIXELS_PER_UNIT = 1

    # Zoom pantalla dreta posicions
    RPIXELS_PER_UNIT = int(RIGHT_WIDTH/(6*TYPICAL_DIST))
    if RPIXELS_PER_UNIT < 1:
        print("ATENCIÓ:  RPIXELS_PER_UNIT fixat a 1")
        RPIXELS_PER_UNIT = 1
    RIGHT_X = RIGHT_WIDTH // 4

    # Zoom pantalla dreta velocitats
    RPIXELS_PER_UNIT_V = int(RIGHT_WIDTH/(5*TYPICAL_VEL))
    if RPIXELS_PER_UNIT_V < 1:
        print("ATENCIÓ:  RPIXELS_PER_UNIT (velocitats) fixat a 1")
        RPIXELS_PER_UNIT_V = 1
    RIGHT_VX = RIGHT_WIDTH // 2 
    RIGHT_VY = 3* HEIGHT // 4

    # Grandaria de les particules (en desus)
    PARTICLE_RAD = int(PART_CFR * LPIXELS_PER_UNIT)
    if PARTICLE_RAD < 1:
        print("PART_CFR massa petit pel que es pot veure per pantalla: PARTICLE_RAD fixat a 1")
        PARTICLE_RAD = 1


    print("")
    print("Screen width: ", WIDTH, " and height: ", HEIGHT)
    print("Left screen width: ", LEFT_WIDTH)
    
    print(f"Pixels per unitat als càlculs: {LPIXELS_PER_UNIT}, Radi part. a la pantalla: {PARTICLE_RAD} Radi forces de contacte (als càlculs): {PART_CFR:.3e}")







