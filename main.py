# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import pygame
import sys
import math

import config

from simulation.particle import Particle
from simulation.world import World
from simulation.sampler import Sampler
from rendering.draw import draw_particles
from rendering.plots import draw_plots
from rendering.user_input import handle_input

# --- Inicialització ---
pygame.init()
config.init()

pygame.display.set_caption("2D simulation with stroboscopic view")
#pygame.display.set_caption("Simulació de partícules amb anotacions estroboscòpiques")
font = pygame.font.SysFont(None, 28)

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
clock = pygame.time.Clock()

sampler = Sampler(config.DT_SAMPLE)

dt_real = clock.tick(config.FPS) / 1000  # Per FPS = 60 --> dt_real = 0.016


# Posició al centre de la pantalla esquerra de simulació:
mid_x = config.LEFT_WIDTH/(2*config.LPIXELS_PER_UNIT)
mid_y = config.HEIGHT/(2*config.LPIXELS_PER_UNIT)


# Genera un disc de N particules dins d'un radi donat i petita rotació global (òmega):
particles = Particle.generate_disk(N=200, center=(mid_x, mid_y), R=50, omega=0.2)



# Partícules amb velocitats inicials i acceleracions
##particles = [
##    Particle(x=mid_x,       y=mid_y, vx=0, vy=0.,                               m=1),         # Sol
#    Particle(x=mid_x+3.9,   y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/3.9),     m=1.65e-7),   # Mercuri
##    Particle(x=mid_x+11.,   y=mid_y, vx=2, vy=0,   m=2),   # Venus
#    Particle(x=mid_x+10.0,  y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/10.0),    m=1),    # Terra
#    Particle(x=mid_x+10.0,  y=mid_y, vx=0, vy=math.sqrt(1200/10.0),    m=3.0e-6),
#    Particle(x=mid_x+15.2,  y=mid_y, vx=0, vy=math.sqrt(1200/15.2),    m=3.2e-7)
##]

# Sistema solar:
#particles = [
#    Particle(x=mid_x,       y=mid_y, vx=0, vy=0.,                               m=1),         # Sol
#    Particle(x=mid_x+3.9,   y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/3.9),     m=1.65e-7),   # Mercuri
#    Particle(x=mid_x+7.2,   y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/7.2),     m=2.45e-6),   # Venus
#    Particle(x=mid_x+10.0,  y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/10.0),    m=3.0e-6),    # Terra
#    Particle(x=mid_x+15.2,  y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/15.2),    m=3.2e-7),    # Mart
#    Particle(x=mid_x+52.0,  y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/52),      m=9.5e-4),    # Jupiter
#    Particle(x=mid_x+95.8,  y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/95.8),    m=2.86e-4),   # Saturn
#    Particle(x=mid_x+192.,  y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/192),     m=4.4e-5),    # Urà
#    Particle(x=mid_x+300.5, y=mid_y, vx=0, vy=math.sqrt(config.GRAV_G/300.5),   m=5.1e-5)     # Neptú
#]


# Defineix el "món":
world = World(particles)

# Camp global:
#world.add_constant_acceleration(0.0, 9.8)   # Descomenta per produir un camp de força global d'acceleració constant per tota partícula


##################
# Estimació de pas de temps per la simulació (dt_sim) òptim. El paràmetre SIM_DT_PARAM (veure config.py) ajuda l'usuari a regular-lo.
accs = world.grav_acceleration(world.particles, dt=1)
v_max = max(math.hypot(p.vx, p.vy) for p in world.particles)
a_max = max(math.hypot(ax, ay) for ax, ay in accs)
r_min = min(p.cfr for p in world.particles)

dt_sim = config.SIM_DT_PARAM * min(
    r_min / v_max if v_max > 0 else float('inf'),       math.sqrt(r_min / a_max) if a_max > 0 else float('inf')     )

DT = dt_sim                         # Guarda aquest temps per quan fas pausa                 
print(f"Simulation time step {dt_sim:.3e} (1/{int(1/dt_sim)})")
#print(f"Pas de temps de simulació {dt_sim:.3e} (1/{int(1/dt_sim)})")
##################


world.add_gravity(dt_sim)
flash_timer = 0

# --- Loop principal ---
t = 0
running = True

state = {
    "paused": False,
    "g_pressed": False,
    "r_screen_clear": False
}

while running:

    t += dt_sim
    #print("NOU pas de temps ", t)
    
    # Events d'usuari
    for event in pygame.event.get():
        running = handle_input(event, state)

        #if paused:
        if state["paused"]:
#            pygame.display.set_caption(f"Simulació 2D de partícules amb anotacions estroboscòpiques |  Pausa")
            pygame.display.set_caption(f"2D simulation with stroboscopic view |  Pause")
            dt_sim = 0
        else:
            pygame.display.set_caption(f"2D simulation with stroboscopic view")
            dt_sim = DT
        if state["r_screen_clear"]:
#            sampler.data.clear()               # Esborra tots els punts "estroboscòpics"
            sampler.data = sampler.data[-10:]   # Deixa els ùltims 10 punts "estroboscòpics"
            state["r_screen_clear"] = False


    if not running:
        print("Sortida")
        continue

    # --- Update física ---
    if not state["paused"]:
        running = world.update(dt_sim)
        if not running:
            running = False
#            print("Fora de limits: surt")
            print("Out of limits: surt")
            continue        
    else:
        continue
            
    # --- Sampling ---
    if sampler.trigger(dt_sim, dt_real):
        sampler.update(world.particles)
        flash_timer = config.DT_FLASH         # Duració flaix. Si dt_real = 0.016 i flash_timer?0.1 => el flaix dura uns 6 frames

    #print("      .")

    # --- Dibuix ---
#    screen.fill((20, 20, 20))

    # zona esquerra
    left_surface = pygame.Surface((config.LEFT_WIDTH, config.HEIGHT))
    left_surface.fill((50, 50, 50))

    # Particules (cercle)
    draw_particles(left_surface, world.particles)

    # flash
    if flash_timer > 0:
        overlay = pygame.Surface((config.LEFT_WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((255,255,255,120))
        left_surface.blit(overlay, (0,0))
        flash_timer -= dt_real

    screen.blit(left_surface, (0,0))

    # separador
    pygame.draw.line(screen, (200,200,200), (config.LEFT_WIDTH, 0), (config.LEFT_WIDTH, config.HEIGHT), 2)

    # zona dreta (plots)
    right_surface = pygame.Surface((config.RIGHT_WIDTH, config.HEIGHT))
    draw_plots(right_surface, sampler.data, font)
    
    screen.blit(right_surface, (config.LEFT_WIDTH, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()
