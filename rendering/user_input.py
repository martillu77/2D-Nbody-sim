# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import pygame

import config

def handle_input(event, state):

    oldLPIXELS_PER_UNIT = config.LPIXELS_PER_UNIT
    oldRPIXELS_PER_UNIT = config.RPIXELS_PER_UNIT
    oldRPIXELS_PER_UNIT_V = config.RPIXELS_PER_UNIT_V
    
    
    if event.type == pygame.QUIT:         # Click a X de la finestra
        return False  # aturar simulació
   
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:   # Espai per fer pausa
            state["paused"] = not state["paused"]
        elif event.key == pygame.K_ESCAPE:  # ESC per sortir
            return False  # aturar simulació


        if event.key == pygame.K_LEFT:
            config.LEFT_X -= 10
        elif event.key == pygame.K_RIGHT:
            config.LEFT_X += 10
        elif event.key == pygame.K_UP:
            config.LEFT_Y -= 10
        elif event.key == pygame.K_DOWN:
            config.LEFT_Y += 10


        if event.key == pygame.K_g:
            state["g_pressed"] = True

########################
####    Pantalla esquerra
####
        if event.key == pygame.K_c:    # Tecla "c"   neteja els plots pantalla dreta
            state["r_screen_clear"] = True


        if event.key == pygame.K_t or event.key == pygame.K_b:    # Tecla "t" Zoom in      # Tecla "b" Zoom out
            factor = 10 if state["g_pressed"] else 1.1
            if event.key == pygame.K_t:
                config.LPIXELS_PER_UNIT *= factor
            else:
                config.LPIXELS_PER_UNIT /= factor

            cx = config.LEFT_WIDTH // 2
            cy = config.HEIGHT // 2
            config.LEFT_X = cx - (config.LPIXELS_PER_UNIT / oldLPIXELS_PER_UNIT) * ( cx - config.LEFT_X )
            config.LEFT_Y = cy - (config.LPIXELS_PER_UNIT / oldLPIXELS_PER_UNIT) * ( cy - config.LEFT_Y )
            print(f"LPIXELS_PER_UNIT: {config.LPIXELS_PER_UNIT}")


########################
####    Pantalla dreta
####
####        Posicions:
        if event.key == pygame.K_u or event.key == pygame.K_m:    # Tecla "u" Zoom in       # Tecla "m" Zoom out
            factor = 10 if state["g_pressed"] else 1.1
            if event.key == pygame.K_u:
                config.RPIXELS_PER_UNIT *= factor
            else:
                config.RPIXELS_PER_UNIT /= factor

            cx = config.RIGHT_WIDTH // 2
            cy = config.HEIGHT // 4
            config.RIGHT_X = cx - (config.RPIXELS_PER_UNIT / oldRPIXELS_PER_UNIT) * ( cx - config.RIGHT_X )
            config.RIGHT_Y = cy - (config.RPIXELS_PER_UNIT / oldRPIXELS_PER_UNIT) * ( cy - config.RIGHT_Y )
            print(f"RPIXELS_PER_UNIT: {config.RPIXELS_PER_UNIT} {config.RIGHT_X} {config.RIGHT_Y}")

####        Velocitats:
        if event.key == pygame.K_i or event.key == pygame.K_l:    # Tecla "i" Zoom in       # Tecla "l" Zoom out
            factor = 10 if state["g_pressed"] else 1.1
            if event.key == pygame.K_i:
                config.RPIXELS_PER_UNIT_V *= factor
            else:
                config.RPIXELS_PER_UNIT_V /= factor

            cx = config.RIGHT_WIDTH // 2
            cy = 3 * config.HEIGHT // 4
            if (cx - config.RIGHT_VX) == 0 or (cy - config.RIGHT_VY) == 0: # a la primera iteració són zero per definició
                cx -= 50;  cy -= 50
            config.RIGHT_VX = cx - (config.RPIXELS_PER_UNIT_V / oldRPIXELS_PER_UNIT_V) * ( cx - config.RIGHT_VX )
            config.RIGHT_VY = cy - (config.RPIXELS_PER_UNIT_V / oldRPIXELS_PER_UNIT_V) * ( cy - config.RIGHT_VY )
            print(f"cx: {cx}    RPIXELS_PER_UNIT_V: {config.RPIXELS_PER_UNIT_V}   oldRPIXELS_PER_UNIT_V {oldRPIXELS_PER_UNIT_V}    config.RIGHT_VX {config.RIGHT_VX}")

            
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_g:      # Els Zooms magnifiquen en un factor x10 més
            state["g_pressed"] = False

    return True







