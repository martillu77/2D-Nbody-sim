# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import config
import pygame

# --- Funcions de dibuix ---

def draw_plots(surface, SamplerDatasets, font):
    surface.fill((30, 30, 30))

    mid_y = config.HEIGHT // 2
    pygame.draw.line(surface, (200,200,200), (0, mid_y), (config.RIGHT_WIDTH, mid_y), 1)

    c_vx = config.RIGHT_WIDTH // 2 # config.TYPICAL_VEL
    c_vy = 3* config.HEIGHT // 4   #4*config.TYPICAL_VEL // 3

    #print(c_vx, " ", c_vy)

    colors_pos = [(255,100,100), (100,255,100), (255,255,100)]
    colors_vel = [(100,200,255), (200,100,255), (100,255,255)]


    # Mostra alguns valors importants per pantalla:
    if SamplerDatasets:
        t, snapshot, E_kin, Ep_grav, L_tot, m_max = SamplerDatasets[-1]

        E_tot = E_kin + Ep_grav
        text = font.render(f"E_kin = {E_kin:.3e}  Ep = {Ep_grav:.3e}  E_tot = {E_tot:.3e}  L_tot = {L_tot:.3e} m_max = {m_max}", True, (255,255,255))
        surface.blit(text, (10, 5))
        text_t = font.render(f"t = {t:.2f}", True, (200,200,200))
        surface.blit(text_t, (10, 30))


    text_t = font.render(f"Posició", True, (200,200,200))
    surface.blit(text_t, (10, mid_y-20))

    text_t = font.render(f"Velocitats", True, (200,200,200))
    surface.blit(text_t, (10, config.HEIGHT-20))

    #print( " ", config.RIGHT_X, " ", config.RPIXELS_PER_UNIT)
    #print( " RIGHT_VX: ", config.RIGHT_VX, " RPIXELS_PER_UNIT_V: ", config.RPIXELS_PER_UNIT_V)

    t = pygame.time.get_ticks()
    colour = (255,255,255) if (t // 500) % 2 else (0,0,0)
    pygame.draw.circle(surface, colour, (config.RIGHT_X, config.RIGHT_Y), 2)
    pygame.draw.circle(surface, colour,  (   c_vx  * config.RPIXELS_PER_UNIT_V + config.RIGHT_VX,     c_vy  * config.RPIXELS_PER_UNIT_V + config.RIGHT_VY), 2)
    pygame.draw.circle(surface, colour, ((1+c_vx) * config.RPIXELS_PER_UNIT_V + config.RIGHT_VX , (1+c_vy) * config.RPIXELS_PER_UNIT_V + config.RIGHT_VY), 2)

    for data in SamplerDatasets:
        t, snapshot, E_kin, Ep_grav, L_tot, m_max = data
        for particle_idx, (x, y, vx, vy) in enumerate(snapshot):
            color_p = colors_pos[particle_idx % len(colors_pos)]
#            color_v = colors_vel[particle_idx % len(colors_vel)]

            # posició
            x_plot = int((x * config.RPIXELS_PER_UNIT) + config.RIGHT_X)
            y_plot = int((y * config.RPIXELS_PER_UNIT) + config.RIGHT_Y)

            if y_plot < config.HEIGHT/2:
                pygame.draw.circle(surface, color_p, (x_plot, y_plot), 2)
            #print(x, x_plot, "   ", y, y_plot)

            # velocitat
            x_plot = int( ((vx) * config.RPIXELS_PER_UNIT_V) + config.RIGHT_VX)
            y_plot = int( ((vy) * config.RPIXELS_PER_UNIT_V) + config.RIGHT_VY)
            if y_plot > config.HEIGHT/2:
                pygame.draw.circle(surface, color_p, (x_plot, y_plot), 2)
        #print("....")
    #print("out")





