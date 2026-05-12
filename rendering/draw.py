# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
import math
import pygame

import config
#from simulation.world import World

def draw_particles(left_surface, world, particles, show_vectors=False):
    accs = []
    if show_vectors:
        accs, r = world.grav_acceleration(world.particles, dt=1)
        
        v_max = max(math.hypot(p.vx, p.vy) for p in particles)
        a_max = max(math.hypot(ax, ay) for ax, ay in accs)
    
    colors_pos = [(255,100,100), (100,255,100), (255,255,100)]
    #print(len(particles))

    #print(f"draw LEFT_X {config.LEFT_X} config.LEFT_Y {config.LEFT_Y}   LPIXELS_PER_UNIT {config.LPIXELS_PER_UNIT}")
    for particle_idx, p in enumerate(particles):
        x_screen = int(p.x * config.LPIXELS_PER_UNIT + config.LEFT_X)
        y_screen = int(p.y * config.LPIXELS_PER_UNIT + config.LEFT_Y)

#        if particle_idx == 0:
#            color_p = colors_pos[particle_idx % len(colors_pos)]
        color_p = colors_pos[1] #int(p.m)]
        pygame.draw.circle(left_surface, color_p, (x_screen, y_screen), max(1, int(p.cfr*config.LPIXELS_PER_UNIT)) )
#        else:
#            pygame.draw.circle(left_surface, (255,255,0), (x_screen, y_screen), config.PARTICLE_RAD)
        if show_vectors:
            ax, ay = accs[particle_idx]

            # velocitat (blau)
            pygame.draw.line(left_surface, (100,100,255), 
            (x_screen, y_screen), 
            (x_screen + int(p.vx*config.LPIXELS_PER_UNIT / v_max),     y_screen + int(p.vy*config.LPIXELS_PER_UNIT / v_max)), 2 )

            # acceleració (vermell)
            pygame.draw.line(left_surface, (255,100,100), 
            (x_screen, y_screen), 
            (x_screen + int(ax * config.LPIXELS_PER_UNIT/a_max),       y_screen + int(ay * config.LPIXELS_PER_UNIT/a_max)), 2 )
