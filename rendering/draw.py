# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import config
import pygame

def draw_particles(left_surface, particles):
    colors_pos = [(255,100,100), (100,255,100), (255,255,100)]
    #print(len(particles))

    #print("draw ", config.LEFT_X, " ", config.LPIXELS_PER_UNIT)
    for particle_idx, p in enumerate(particles):
        #x, y = particle
        x_screen = int(p.x * config.LPIXELS_PER_UNIT + config.LEFT_X)
        y_screen = int(p.y * config.LPIXELS_PER_UNIT + config.LEFT_Y) # + (config.HEIGHT // 2)

#        if particle_idx == 0:
#            color_p = colors_pos[particle_idx % len(colors_pos)]
        color_p = colors_pos[1] #int(p.m)]
        pygame.draw.circle(left_surface, color_p, (x_screen, y_screen), max(1, int(p.cfr*config.LPIXELS_PER_UNIT)) )
#        else:
#            pygame.draw.circle(left_surface, (255,255,0), (x_screen, y_screen), config.PARTICLE_RAD)
