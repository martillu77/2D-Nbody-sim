# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import math

import config
from simulation.particle import Particle

class World:

    def __init__(self, particles):
        print("\nDetalls de la simulacio:")
        self.particles = particles
        self.integrator = config.INTEGRATOR   # Euler, Euler-Cromer, Verlet
        self.E_lost = 0.
        self.forces = []
#        self.walls = config.WALLS # if there are walls, bounce the particles.
#        self.bounds = bounds  # (xmin, xmax, ymin, ymax) o None
        print(" Integrador usat: ", config.INTEGRATOR)
        print(" Numero de partícules: ", len(self.particles))
        if config.WALLS:
            print(" El simulador considera que hi ha parets ", config.BOUNDS)
            if config.BOUNDS != None:
                print("  Limits: ", config.BOUNDS)
        else:
            print(" El simulador considera que no hi ha parets\n")

        # Tenen les partícules acceleració pròpia? (es comporten com "vehicles"?)
        self.autoacc = False
        for p in particles:
            if abs(p.ax) > 0. and abs(p.ay) > 0.:
                self.autoacc = True



    def grav_fusion(self, used, to_merge):
        surviving_particles = []
        # afegeix les que no es fusionen
        for k, p in enumerate(self.particles):
            if k not in used:
                #print("particle ", k, " with mass: ", p.m, " survives")
                surviving_particles.append(p)

        # afegeix les fusionades
        for i, j in to_merge:
            #print("grav_fusion ", to_merge[0], " i ", i, " j ", j)
            # R_cm :
            m = self.particles[i].m + self.particles[j].m
            x = (self.particles[i].m*self.particles[i].x + self.particles[j].m * self.particles[j].x)/m
            y = (self.particles[i].m*self.particles[i].y + self.particles[j].m * self.particles[j].y)/m
            # V_cm :
            vx = (self.particles[i].m * self.particles[i].vx + self.particles[j].m * self.particles[j].vx)/m
            vy = (self.particles[i].m * self.particles[i].vy + self.particles[j].m * self.particles[j].vy)/m

            # Energia perduda d'auto-interacció:
            mu = (self.particles[i].m * self.particles[j].m) / m
            dist = math.sqrt((self.particles[i].x - self.particles[j].x)**2 + (self.particles[i].y - self.particles[j].y)**2)
            thisE_lost = 0.5 * mu * ( (self.particles[i].vx - self.particles[j].vx)**2 + (self.particles[i].vy - self.particles[j].vy)**2 )  # Kin_rel
            thisE_lost -= (config.GRAV_G * self.particles[i].m * self.particles[j].m) / dist                                                 # U_grav
            self.E_lost += thisE_lost
            print(f"Merged particle with mass: {m}  i canvi d'energia: {self.E_lost:.3e}, en aquest cas {thisE_lost:.3e}")
            p = Particle(x=x, y=y, vx=vx, vy=vy, m=m)
            surviving_particles.append(p)

        self.particles = []
        self.particles = surviving_particles
        print(f"# of resulting particles: {len(self.particles)}\n")




    def handle_collisions(self, particles, dt):

        to_merge = []
        used = set()
        fusion = False
        for i in range(len(particles)):
            p1 = particles[i]
            for j in range(i+1, len(particles)):
                p2 = particles[j]
                
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r2 = dx*dx + dy*dy
                dist = math.sqrt(r2) + 1e-12
                # Comproba si hi ha força de contacte entre i-j
                # r_min ~ v_rel * dt       r_min ~ max(v_rel * dt, 0.5 * a * dt**2)
                # velocitat relativa:
                dvx = p2.vx - p1.vx
                dvy = p2.vy - p1.vy

                #  mira si s'apropen o allunyen:
                nx = dx / dist  # direcció normal de contacte component x
                ny = dy / dist  # direcció normal de contacte component y
                v_rel = dvx*nx + dvy*ny


                #print(f"v_rel: {v_rel} dist: {dist}")
                # La distància < dt * (vel. rel.)         o  són molt a prop:
                if (v_rel < 0 and dist < 2*abs(dt*v_rel) ) or (p1.cfr+p2.cfr) > dist:
##                if dist < dt*math.sqrt( dvx**2 + dvy**2 ) or (p1.cfr+p2.cfr) > dist:
                #if (p1.cfr+p2.cfr) > dist:  

                    #print(nx, " ", ny, "    ", dvx, " ", dvy)
                    print(f"col.lisio: dist {dist}  rad.F.contact. {p1.cfr} v_rel*dt {dt*math.sqrt( dvx**2 + dvy**2 )} v_rel {v_rel}")                    


                    if v_rel < 0:   # S'apropen: força de contacte
#                    if v_rel < 0 and E_rel < 0:   # S'apropen: força de contacte
                        #gal=input("E")
                        pcr = min(p1.cr, p2.cr)   # Combinació dels coeficients de restitució  MILLORAR: afegir altres models
                        pj = -(1 + pcr) * v_rel
                        pj /= (1/p1.m + 1/p2.m)
                        print("velocitats: ", p1.vx, p2.vx, v_rel)
                        p1.vx -= pj * nx / p1.m
                        p1.vy -= pj * ny / p1.m

                        p2.vx += pj * nx / p2.m
                        p2.vy += pj * ny / p2.m

                        dvx = p2.vx - p1.vx
                        dvy = p2.vy - p1.vy
                        v_rel = dvx*nx + dvy*ny
                        print("velocitats: ", p1.vx, p2.vx, v_rel)
                        print("Ara si: ", abs(r2), p1.vx, p2.vx, dvx, pj, pcr)
                        #print(dx, dvx, v_rel, pcr)
                        #val = input("Enter your value: ")
                        
                        m = p1.m + p2.m
                        mu = (p1.m * p2.m) / m
                        E_rel = 0.5 * mu * (dvx + dvy) - (config.GRAV_G * p1.m * p2.m / dist)

                        # Fusió:
                        # Si no hi ha gravetat segons la v_rel                     si n'hi ha segons E_rel
                        if (config.GRAV_G == 0 and abs(v_rel) < config.PART_FUS_VTHRE) or E_rel < 0:
                            to_merge.append((i, j))
                            used.add(i)
                            used.add(j)
                            fusion = True
                            print("FUSE!")
                            break

        if fusion:
            self.grav_fusion(used, to_merge)



    def add_constant_acceleration(self, ax, ay):  # Se'n fa us a main.py: world.add_constant_acceleration(1.0, 0.0)
        def force(particles):      # Se'n fa us a update
            return [(ax, ay) for _ in particles]
        self.forces.append(force)




    def grav_acceleration(self, particles, dt):
        accs = [[0.0, 0.0] for _ in particles]
        for i in range(len(particles)):
            for j in range(i+1, len(particles)):
                p1 = particles[i]
                p2 = particles[j]

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                r2 = dx*dx + dy*dy
                r = math.sqrt(r2)
                inv_r3 = 1 / (r2 * r)

                fx = config.GRAV_G * dx * inv_r3
                fy = config.GRAV_G * dy * inv_r3

                # acc = F/m
                accs[i][0] += p2.m * fx
                accs[i][1] += p2.m * fy

                accs[j][0] -= p1.m * fx
                accs[j][1] -= p1.m * fy
#                print("R2: ", r2, " a[i]: ", accs[i][0], " ", accs[i][1], " a[j]: ", accs[j][0], " ", accs[j][1],)
#        print("")
        return accs
                    
    def add_gravity(self, dt):
        def force(particles):      # Se'n fa us a update
            return self.grav_acceleration(particles, dt)
        self.forces.append(force)



############################
    def update(self, dt):

        # Col.lisions:
        if config.PART_COLL:
            self.handle_collisions(self.particles, dt)


        accs = [[0.0, 0.0] for _ in self.particles]

        # comença amb acceleració pròpia:
        if self.autoacc:
            #print("Auto acceleració")
            for i, p in enumerate(self.particles):
                accs[i][0] += p.ax
                accs[i][1] += p.ay

        # afegeix forces globals:
        for force in self.forces:           #   de: add_constant_acceleration O add_gravity
            glob_accs = force(self.particles)
            for i in range(len(accs)):
                accs[i][0] += glob_accs[i][0]
                accs[i][1] += glob_accs[i][1]

        # integra:
        if config.INTEGRATOR == "euler" or config.INTEGRATOR == "cromer":
            for p, (ax, ay) in zip(self.particles, accs):
                if config.INTEGRATOR == "euler":
                    p.x += p.vx * dt
                    p.y += p.vy * dt
                    p.vx += ax * dt
                    p.vy += ay * dt
                else:              # "Euler-Cromer"
                    p.vx += ax * dt
                    p.vy += ay * dt
                    p.x += p.vx * dt
                    p.y += p.vy * dt
                    
        elif config.INTEGRATOR == "verlet":
#            print("Verlet")
            # 1. mig pas velocitat
            for p, (ax, ay) in zip(self.particles, accs):
                p.vx += 0.5 * ax * dt
                p.vy += 0.5 * ay * dt
                
            # actualitza posicions:    O(N)
            for p, (ax, ay) in zip(self.particles, accs):
                p.x += p.vx * dt #+ (0.5*ax*dt*dt)
                p.y += p.vy * dt #+ (0.5*ay*dt*dt)
                
            # noves acceleracions:     O(N^2)
#            print("noves accs")
            new_accs = self.grav_acceleration(self.particles, dt)
            
            # actualitza velocitats:   O(N)
#            print("noves vels")
            for p, (ax, ay), (ax_new, ay_new) in zip(self.particles, accs, new_accs):
                p.vx += 0.5*ax_new*dt  #(ax + ax_new)*dt
                p.vy += 0.5*ay_new*dt  #(ay + ay_new)*dt
#                print("vx: ", p.vx, " vy: ", p.vy)
#            print("")
        else:
            print("Integrador desconegut")

        if config.WALLS:
            return self.handle_walls()
        else:
            return self.handle_limits()


############################
    def handle_walls(self):
        if config.BOUNDS == None:
            return True

        xmin, xmax, ymin, ymax = 0, config.LEFT_WIDTH/config.LPIXELS_PER_UNIT, 0, config.HEIGHT/config.LPIXELS_PER_UNIT

        for p in self.particles:
            if p.x < xmin:
                p.x = xmin
                p.vx *= -1
            elif p.x > xmax:
                p.x = xmax
                p.vx *= -1
            elif p.y > ymax:
                p.y = ymax
                p.vy *= -1
            elif p.y < ymin:
                p.y = ymin
                p.vy *= -1
        return True


############################
    def handle_limits(self):
        if config.BOUNDS == None:
            return True

        xmin, xmax, ymin, ymax = 0, config.LEFT_WIDTH/config.LPIXELS_PER_UNIT, 0, config.HEIGHT/config.LPIXELS_PER_UNIT
        #print(xmin, xmax, ymin, ymax)
        for p in self.particles:
            #print(" ", p.x, p.y)
            if p.x < xmin or p.x > xmax or p.y < ymin or p.y > ymax:
                return False     # Atura la simulació
        return True              # Continua la simulació
        
        
        
        
