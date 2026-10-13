# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import math

import pickle                 ## save world
from pathlib import Path      ## save world

import config
from simulation.particle import Particle

import sys
from tqdm import tqdm

import torch

class World:

    def __init__(self, particles):
        print("\nDetalls de la simulacio:")
        self.particles = particles
        self.integrator = config.INTEGRATOR   # Euler, Euler-Cromer, Verlet
        self.E_lost = 0.
        #self.forces = []
        self.const_ax = 0.0
        self.const_ay = 0.0
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

        self.checkdt = True   # Flag set in world.do_update to detect whether dt_sim may need to be re-scaled
        self.dt_test = 0      # Calculation of the time step that is actually needed to keep a good accuracy.
                              #   If considerably smaller than dt_sim re-scale dt_sim such that simplecticity is kept
                              #   in world.update

        self.terminal = sys.stderr.isatty()  # Is the simulation running on a terminal (True/False) ?


    def grav_fusion(self, used, to_merge, accs):
        surviving_particles = []
        new_accs = []
        # afegeix les paticules que no es fusionen
        for k, p in enumerate(self.particles):
            if k not in used:
                #print("particle ", k, " with mass: ", p.m, " survives")
                surviving_particles.append(p)
                new_accs.append(accs[k])

        # afegeix les fusionades
        for i, j in to_merge:
            #print("grav_fusion ", to_merge[0], " i ", i, " j ", j)
            # R_cm :
            m = self.particles[i].m + self.particles[j].m
            cfr = self.particles[i].cfr / (self.particles[i].m)**(1/3)
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
            print(f"Merged particle with mass: {m:.3e}  i canvi d'energia: {self.E_lost:.3e}, en aquest cas {thisE_lost:.3e}")

            # ATTENCIO : acceleracions propies no calculades !! mira la proposta: 
            #p.ax = (self.particles[i].m * self.particles[i].ax + self.particles[j].m * self.particles[j].ax) / (m_A + m_B)
            #p.ay = (self.particles[i].m * self.particles[i].ay + self.particles[j].m * self.particles[j].ay) / (m_A + m_B)

            p = Particle(x=x, y=y, vx=vx, vy=vy, m=m, cfr=cfr)
            surviving_particles.append(p)

            # Centre of mass acceleration: 
            # This is an approximation forces between the merged particles cancel but the external forces here used
            #   were calculated at slightly different positions. Since the fused particles are close to each other
            #   this should be a good approximation
            ax = (self.particles[i].m * accs[i][0] + self.particles[j].m * accs[j][0]) / m
            ay = (self.particles[i].m * accs[i][1] + self.particles[j].m * accs[j][1]) / m
            new_accs.append([ax, ay])


        #self.particles = []
        self.particles = surviving_particles
        print(f"# of resulting particles: {len(self.particles)}\n")

        return new_accs


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
                    #print(f"col.lisio: dist {dist:.3e}  rad.F.contact. {p1.cfr:.3e} v_rel*dt {dt*math.sqrt( dvx**2 + dvy**2 )} v_rel {v_rel}")                    


                    if v_rel < 0:   # S'apropen: força de contacte
#                    if v_rel < 0 and E_rel < 0:   # S'apropen: força de contacte
                        #gal=input("E")
                        pcr = min(p1.cr, p2.cr)   # Combinació dels coeficients de restitució  MILLORAR: afegir altres models
                        pj = -(1 + pcr) * v_rel
                        pj /= (1/p1.m + 1/p2.m)
                        #print(f"velocitats: {p1.vx:.3e} {p2.vx:.3e} {v_rel:.3e}")
                        p1.vx -= pj * nx / p1.m
                        p1.vy -= pj * ny / p1.m

                        p2.vx += pj * nx / p2.m
                        p2.vy += pj * ny / p2.m

                        dvx = p2.vx - p1.vx
                        dvy = p2.vy - p1.vy
                        v_rel = dvx*nx + dvy*ny
                        #print(f"noves velocitats: {p1.vx:.3e} {p2.vx:.3e} {v_rel:.3e}")
                        #print(f"Ara si {abs(r2):.3e} {dvx:.3e}, {pj:.3e} {pcr}")
                        #print(dx, dvx, v_rel, pcr)
                        #val = input("Enter your value: ")
                        
                        m = p1.m + p2.m
                        mu = (p1.m * p2.m) / m
                        E_rel = 0.5 * mu * (dvx**2  + dvy**2) - (config.GRAV_G * p1.m * p2.m / dist)

                        # Fusió:
                        # Si no hi ha gravetat segons la v_rel                     si n'hi ha segons E_rel
                        if (config.GRAV_G == 0 and abs(v_rel) < config.PART_FUS_VTHRE) or E_rel < 0:
                            to_merge.append((i, j))
                            used.add(i)
                            used.add(j)
                            fusion = True
                            print(f"FUSE! {i} {j}")
                            break

        if fusion:
            self.grav_fusion(used, to_merge)



    def grav_acceleration_cpu(self, particles, dt, allow_fusion=True):
        accs = [[0.0, 0.0] for _ in particles]
        r_min = float("inf")

        to_merge = []
        used = set()
        fusion = False

        for i in range(len(particles)):
            for j in range(i+1, len(particles)):
                p1 = particles[i]
                p2 = particles[j]

                dx = p2.x - p1.x
                dy = p2.y - p1.y

                r2 = dx*dx + dy*dy
                r = math.sqrt(r2)
                #if r_min > r: # if collisions are enabled check this when looking for collisions
                #    r_min = r
                inv_r3 = 1. / (r2 * r)

                fx = config.GRAV_G * dx * inv_r3
                fy = config.GRAV_G * dy * inv_r3

                # acc = F/m
                accs[i][0] += p2.m * fx
                accs[i][1] += p2.m * fy

                accs[j][0] -= p1.m * fx
                accs[j][1] -= p1.m * fy

#                print("R2: ", r2, " a[i]: ", accs[i][0], " ", accs[i][1], " a[j]: ", accs[j][0], " ", accs[j][1],)
#                print("")

                # Handle particle collisions if necessary
                merged = False
                # taken and unified from self.handle_collisions to avoid another O(N^2) loop:
                if allow_fusion and config.PART_COLL:
                    dist = r + 1e-12
                    # Comproba si hi ha força de contacte entre i-j
                    # r_min ~ v_rel * dt       r_min ~ max(v_rel * dt, 0.5 * a * dt**2)
                    # velocitat relativa:
                    dvx = p2.vx - p1.vx
                    dvy = p2.vy - p1.vy

                    #  mira si s'apropen o allunyen:
                    nx = dx / dist  # direcció normal de contacte component x
                    ny = dy / dist  # direcció normal de contacte component y
                    v_rel = (dvx * nx) + (dvy * ny)       

                    #print(f"v_rel: {v_rel} dist: {dist}")
                    # La distància < dt * (vel. rel.)         o  són molt a prop:
                    if (v_rel < 0 and dist < 2*abs(dt*v_rel) ) or (p1.cfr+p2.cfr) > dist:
##                    if dist < dt*math.sqrt( dvx**2 + dvy**2 ) or (p1.cfr+p2.cfr) > dist:
                    #if (p1.cfr+p2.cfr) > dist:  

                        #print(nx, " ", ny, "    ", dvx, " ", dvy)
                        #print(f"col.lisio: dist {dist:.3e}  rad.F.contact. {p1.cfr:.3e} v_rel*dt {dt*math.sqrt( dvx**2 + dvy**2 )} v_rel {v_rel}")                    


                        if v_rel < 0:   # S'apropen: força de contacte
#                        if v_rel < 0 and E_rel < 0:   # S'apropen: força de contacte
                            #gal=input("E")
                            pcr = min(p1.cr, p2.cr)   # Combinació dels coeficients de restitució  MILLORAR: afegir altres models
                            pj = -(1 + pcr) * v_rel
                            pj /= (1/p1.m + 1/p2.m)
                            #print(f"velocitats: {p1.vx:.3e} {p2.vx:.3e} {v_rel:.3e}")
                            p1.vx -= pj * nx / p1.m
                            p1.vy -= pj * ny / p1.m

                            p2.vx += pj * nx / p2.m
                            p2.vy += pj * ny / p2.m

                            dvx = p2.vx - p1.vx
                            dvy = p2.vy - p1.vy
                            v_rel = dvx*nx + dvy*ny
                            #print(f"noves velocitats: {p1.vx:.3e} {p2.vx:.3e} {v_rel:.3e}")
                            #print(f"Ara si {abs(r2):.3e} {dvx:.3e}, {pj:.3e} {pcr}")
                            #print(dx, dvx, v_rel, pcr)
                            #val = input("Enter your value: ")
                        
                            m = p1.m + p2.m
                            mu = (p1.m * p2.m) / m
                            E_rel = 0.5 * mu * (dvx**2  + dvy**2) - (config.GRAV_G * p1.m * p2.m / dist)

                            # Fusió:
                            # Si no hi ha gravetat segons la v_rel                     si n'hi ha segons E_rel
                            if (config.GRAV_G == 0 and abs(v_rel) < config.PART_FUS_VTHRE) or E_rel < 0:
                                to_merge.append((i, j))
                                used.add(i)
                                used.add(j)
                                fusion = True
                                merged = True
                                print(f"FUSE! {i} {j}")
                                break

                if merged == False and r_min > r:
                    r_min = r

        if fusion:
            #self.grav_fusion(used, to_merge, accs)
            accs = self.grav_fusion(used, to_merge, accs)

        return accs, r_min





    def grav_acceleration_gpu(self, particles, dt, allow_fusion=True):

        N = len(particles)

        # Transfer particle data CPU -> GPU
        n_data = 7 if config.PART_COLL else 3
        data_cpu = torch.empty((N, n_data), dtype=torch.float32)

        for i, p in enumerate(particles):
            data_cpu[i, 0] = p.x
            data_cpu[i, 1] = p.y
            data_cpu[i, 2] = p.m
            if config.PART_COLL:
                data_cpu[i, 3] = p.vx
                data_cpu[i, 4] = p.vy
                data_cpu[i, 5] = p.cfr
                data_cpu[i, 6] = p.cr

        data = data_cpu.to("cuda")

        x = data[:, 0] # Remeber these are (N,)
        y = data[:, 1]
        m = data[:, 2]

        # Pairwise distances             vector     vector
        dx = x[None, :] - x[:, None]   # column j - row i   
        dy = y[None, :] - y[:, None]   # (1, N)   - (N, 1)  --> (N, N) pytorch does broadcasting, anti-symmetric matrix

        r2 = dx*dx + dy*dy                                        # Hadamard product (element-wise) of the two matrices, symmetric matrix
        diag = torch.eye(N, dtype=torch.bool, device=data.device) # bool square matrix with "True" in the diagonal
        r2 = r2.masked_fill(diag, float("inf"))                   # Square matrix with inf values on the diagonal
        r = torch.sqrt(r2)                                        # distances (square) matrix between particles
        r_min = r.min()

        # Gravity
        inv_r3 = 1. / (r2 * r)     # (N, N) symmetric

        fx = config.GRAV_G * dx * inv_r3  # (N, N)  anti-symmetric from dx: dx_ij inv_r3^ji
        fy = config.GRAV_G * dy * inv_r3  # (N, N)  anti-symmetric from dy

        acc_x = (fx * m).sum(dim=1)  # fx_ij * m_j this is: fx (N, N) * m (N,)  --> (N,) 
        acc_y = (fy * m).sum(dim=1)
        
        accs = torch.stack((acc_x, acc_y), dim=1)
        #accs[:, 0] += acc_x  # if a global acceleration exists (or any other) it will added
        #accs[:, 1] += acc_y  #   to the gravitational one
        accs = accs.cpu().tolist()

        #############################3
        # Collisions
        if allow_fusion and config.PART_COLL:

            vx = data[:, 3]
            vy = data[:, 4]
            cfr = data[:, 5]
            cr = data[:, 6]

            dvx = vx[None, :] - vx[:, None]
            dvy = vy[None, :] - vy[:, None]

            inv_r = torch.rsqrt(r2)
            nx = dx * inv_r
            ny = dy * inv_r
            v_rel = (dvx * nx) + (dvy * ny)

            crossing = r < 2.0 * torch.abs(dt * v_rel)    # Bool 

            overlap = (cfr[:, None] + cfr[None, :]) > r

            collision = ( ((v_rel < 0) & crossing) | overlap )

            # Només una còpia de cada parella
            upper = torch.triu(torch.ones((N, N), dtype=torch.bool, device=data.device), diagonal=1)
            collision &= upper

            # Select non-overlapping collision pairs
            candidate = collision | collision.T

            idx = torch.arange(N, device=data.device)

            has_partner = candidate.any(dim=1)

            partner = torch.full( (N,), -1, dtype=torch.long, device=data.device )
            partner[has_partner] = ( candidate[has_partner].float().argmax(dim=1) )
            partner_safe = partner.clamp_min(0)

            mutual = ( has_partner & (partner[partner_safe] == idx) & (idx < partner) )
            ci = idx[mutual]
            cj = partner[mutual]

            # --------------------------------------------------------
            # Resolve collisions
            if ci.numel() > 0:

                vrel_pair = v_rel[ci, cj]

                nx_pair = nx[ci, cj]
                ny_pair = ny[ci, cj]

                cr_pair = torch.minimum( cr[ci], cr[cj])

                pj = -(1.0 + cr_pair) * vrel_pair
                pj /= (1.0 / m[ci] + 1.0 / m[cj])

                dvx_i = -pj * nx_pair / m[ci]
                dvy_i = -pj * ny_pair / m[ci]

                dvx_j = pj * nx_pair / m[cj]
                dvy_j = pj * ny_pair / m[cj]

                # Velocity after collision
                dvx_after = ( dvx[ci, cj] + dvx_j - dvx_i)

                dvy_after = ( dvy[ci, cj] + dvy_j - dvy_i)

                vrel_after = ( dvx_after * nx_pair + dvy_after * ny_pair)

                mu = (m[ci] * m[cj] / (m[ci] + m[cj]) )

                E_rel = ( 0.5 * mu * (dvx_after**2 + dvy_after**2)
                    - config.GRAV_G * m[ci] * m[cj] / r[ci, cj]    )

                if config.GRAV_G == 0:
                    fuse = ( vrel_pair < 0 ) & ( torch.abs(vrel_after) < config.PART_FUS_VTHRE )
                else:
                    fuse = ( vrel_pair < 0 ) & (E_rel < 0)

                # ----------------------------------------------------
                # Apply non-fusion collisions
                non_fuse = ~fuse

                new_vx = vx.clone()
                new_vy = vy.clone()

                ii = ci[non_fuse]
                jj = cj[non_fuse]

                new_vx.index_add_( 0, ii, dvx_i[non_fuse] )
                new_vy.index_add_( 0, ii, dvy_i[non_fuse] )

                new_vx.index_add_( 0, jj, dvx_j[non_fuse] )
                new_vy.index_add_( 0, jj, dvy_j[non_fuse] )

                # GPU -> CPU
                vel_cpu = torch.stack( (new_vx, new_vy), dim=1).cpu()

                for i, p in enumerate(particles):
                    p.vx = vel_cpu[i, 0].item()
                    p.vy = vel_cpu[i, 1].item()

                # ----------------------------------------------------
                # Fusion
                if fuse.any():

                    fuse_i = ci[fuse].cpu().tolist()
                    fuse_j = cj[fuse].cpu().tolist()

                    to_merge = list( zip(fuse_i, fuse_j) )

                    used = ( set(fuse_i) | set(fuse_j) )
                    
                    accs = self.grav_fusion( used, to_merge, accs )

        return accs, r_min




    def add_gravity(self, dt):                    # Se'n fa us a main.py: world.add_gravity(dt_sim)
        def force(particles, accs):              # Se'n fa us a update
            if config.GPU:
                return self.grav_acceleration_gpu(particles, dt)
            else:
                return self.grav_acceleration_cpu(particles, dt)
        #self.forces.append(force)

    def add_constant_acceleration(self, ax, ay):  # Se'n fa us a main.py: world.add_constant_acceleration(1.0, 0.0)
        self.const_ax = ax
        self.const_ay = ay
      #  def force(particles, accs):      # Se'n fa us a update
      #      for i in range(len(particles)):
      #          accs[i][0] += ax
      #          accs[i][1] += ay
      #      return accs, float("inf")
        #    return [(ax, ay) for _ in particles]
      #  self.forces.append(force)



    def do_update(self, dt):

        # Col.lisions:
        #if config.PART_COLL:
        #    self.handle_collisions(self.particles, dt)    Now collisions are in grav_acceleration_cpu

        accs = [[0.0, 0.0] for _ in self.particles]

        # si n'hi ha comença amb acceleració pròpia:
     #   if self.autoacc:
            #print("Auto acceleració")
     #       for i, p in enumerate(self.particles):
     #           accs[i][0] += p.ax
     #           accs[i][1] += p.ay

        # afegeix forces globals:
     #   for force in self.forces:           #   from: add_constant_acceleration and/or add_gravity
     #       accs, r = force(self.particles, accs)
        #    glob_accs, r = force(self.particles)
        #    for i in range(len(accs)):
        #        accs[i][0] += glob_accs[i][0]
        #        accs[i][1] += glob_accs[i][1]


        # acceleracions:     O(N^2)
        if config.GPU:
            accs, r_min = self.grav_acceleration_gpu(self.particles, dt)
        else:
            accs, r_min = self.grav_acceleration_cpu(self.particles, dt)

        ############################################
        # Integra:
        if config.INTEGRATOR == "euler" or config.INTEGRATOR == "cromer":
            for p, (ax, ay) in zip(self.particles, accs):
                ax += p.ax + self.const_ax    # acceleracio gravetat += propia + camp global
                ay += p.ay + self.const_ay    # acceleracio gravetat += propia + camp global

                if config.INTEGRATOR == "euler":     # Euler
                    p.x += p.vx * dt
                    p.y += p.vy * dt
                    p.vx += ax * dt
                    p.vy += ay * dt
                else:                                # "Euler-Cromer"
                    p.vx += ax * dt
                    p.vy += ay * dt
                    p.x += p.vx * dt
                    p.y += p.vy * dt
                    
        elif config.INTEGRATOR == "verlet":          # Verlet
#            print("Verlet")
            v_max = 0.
            r_min = float('inf')
            # 1. mig pas velocitat
            for p, (ax, ay) in zip(self.particles, accs):
                ax += p.ax + self.const_ax    # acceleracio gravetat += propia + camp global
                ay += p.ay + self.const_ay    # acceleracio gravetat += propia + camp global
                p.vx += 0.5 * ax * dt
                p.vy += 0.5 * ay * dt
                
            # actualitza posicions:    O(N)
            for p, (ax, ay) in zip(self.particles, accs):
                p.x += p.vx * dt #+ (0.5*ax*dt*dt)
                p.y += p.vy * dt #+ (0.5*ay*dt*dt)



            # 2. noves acceleracions:     O(N^2)
            if config.GPU:
                new_accs, r_min = self.grav_acceleration_gpu(self.particles, dt)
            else:
                new_accs, r_min = self.grav_acceleration_cpu(self.particles, dt)

            # 3. actualitza velocitats:   O(N)
#            print("noves vels")
            for p, (ax_new, ay_new) in zip(self.particles, new_accs):
                ax_new += p.ax + self.const_ax    # acceleracio gravetat += propia + camp global
                ay_new += p.ay + self.const_ay    # acceleracio gravetat += propia + camp global

                p.vx += 0.5*ax_new*dt  #(ax + ax_new)*dt
                p.vy += 0.5*ay_new*dt  #(ay + ay_new)*dt
                if v_max < math.hypot(p.vx, p.vy):
                    v_max = math.hypot(p.vx, p.vy)

            #a_max = max(math.hypot(anewx, anewy) for anewx, anewy in new_accs)
            self.dt_test = (config.SIM_DT_PARAM/100.) * (r_min / v_max if v_max > 0 else dt)
            if self.dt_test < dt:
                self.checkdt = True
            else:
                self.checkdt = False

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
        
        
############################
    def update(self, dt_sim):

        ret = True
        if self.checkdt:   # Verlet: It was detected in world.do_update that dt_sim may need to be re-scaled
                           # Euler/Cromer: always
            if config.INTEGRATOR == "euler" or config.INTEGRATOR == "cromer":
                # Get v_max and r_min and estimate whether time step has to be rescaled:
                v_max = max(math.hypot(p.vx, p.vy) for p in self.particles)
                #a_max = max(math.hypot(ax, ay) for ax, ay in accs)
                r_min = float('inf')
                for i in range(len(self.particles)):
                    for j in range(i+1, len(self.particles)):
                        p1 = self.particles[i]
                        p2 = self.particles[j]
                        if r_min > math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2):
                            r_min = math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)

            
                self.dt_test = (config.SIM_DT_PARAM/100.) * (r_min / v_max if v_max > 0 else dt_sim)
                #dt_test = (config.SIM_DT_PARAM/1000) * (r_min / v_max if v_max > 0 else dt_sim)
                print(f"\n v_max: {v_max:.3e} r_min: {r_min:.3e}      dt_test: {self.dt_test:.3e} {1/self.dt_test:.3e}")

            #elif config.INTEGRATOR == "verlet":   # Nothing needed. In this case "self.dt_test" was already set in world.update
            
            if self.dt_test < dt_sim:
                N = math.ceil(dt_sim / self.dt_test)
                dt_scaled = dt_sim / N   # There will be N sub-steps in time

#                print(f"Time will be rescaled: {N} times")
#                for _ in range(N):
#                    ret = self.do_update(dt_test)

                if self.terminal:
                    iterator = tqdm(range(N), desc="Time is being rescaled: ")
                else:
                    iterator = range(N)

                for i in iterator:
                    ret = self.do_update(dt_scaled)
                    if not self.terminal and (i + 1) % max(1, N // 10) == 0:
                        print(f"Time is being rescaled... {i+1}/{N}", flush=True)

                if not self.terminal: print("Done!")



            else:
                ret = self.do_update(dt_sim)
        else:    # This can be only in case of Verlet integrator
            ret = self.do_update(dt_sim)

        return ret

#    def save(self, time, dt_sim, timestamp, filename="world.pkl"):  # es recupera a particle.py
    def save(self, time, timestamp, filename="world.pkl"):  # es recupera a particle.py
        print(f"time {time}")
        data = {
            "time": time,            # total simulation time
            # "dt_sim": dt_sim,       # simulation time step   # es guarda/recupera a units.py/config.py
            "particles": [
                {
                    "x": p.x,
                    "y": p.y,
                    "vx": p.vx,
                    "vy": p.vy,
                    "ax": p.ax,
                    "ay": p.ay,
                    "m": p.m,
                    "cr": p.cr,
                    "cfr": p.cfr
                }
                for p in self.particles
            ],
        }

        directory = Path(timestamp)
        directory.mkdir(exist_ok=True)
        with open(directory / filename, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def set_dt_sim(self, dt_sim):
        self.dt_test = dt_sim