# Copyright (c) 2026 Lluis Marti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

import config

class Sampler:
    def __init__(self, dt_sample=config.DT_SAMPLE):
        self.dt_sample = dt_sample
        self.timer = 0
        self.t = 0
        self.data = []    # [(t, x, y, vx, vy, E_kin...), ...]

    def trigger(self, dt, dt_real):
        self.timer += dt_real
        self.t += dt
        if self.timer >= self.dt_sample:
            self.timer = 0
            return True
        return False

    def update(self, particles):
        snapshot = []
        E_kin = 0.0
        Ep_grav = 0.0
        L_tot = 0.0
        m_max = 0.
        N = len(particles)
        
        for i in range(N):
            p1 = particles[i]
            
            snapshot.append((p1.x, p1.y, p1.vx, p1.vy))
            E_kin += 0.5 * p1.m * (p1.vx**2 + p1.vy**2)      # Energia cinètica
            L_tot += p1.m * (p1.x*p1.vy - p1.y*p1.vx)        # Moment angular (respecte el x, y = 0, 0 )
            m_max = max(m_max, p1.m)
            
            for j in range(i+1, N):
                p2 = particles[j]
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r = (dx*dx + dy*dy)**0.5 + 1e-6
                
                Ep_grav -= config.GRAV_G * p1.m * p2.m / r           # Energia potencial gravitatoria

        self.data.append((self.t, snapshot, E_kin, Ep_grav, L_tot, m_max))


    def downsample(self):
        if not self.data:
            return

        newdata = []
        d_min2 = 0.05**2

        print("Prune stroboscopic view points!")
        # primer punt sempre es queda
        newdata.append(self.data[0])

        for t, snapshot, E_kin, Ep_grav, L_tot, m_max in self.data[1:]:
            tp, snapshotp, *_ = newdata[-1]

            keep = False

            for (x, y, _, _), (xp, yp, _, _) in zip(snapshot, snapshotp):
                dx = x - xp
                dy = y - yp
                if dx*dx + dy*dy > d_min2:
                    keep = True
                    break

            if keep:
                newdata.append((t, snapshot, E_kin, Ep_grav, L_tot, m_max))

        self.data = newdata


