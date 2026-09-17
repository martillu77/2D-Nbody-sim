License: GNU GPL v3.0
LICENSE: GNU GPL v3.0
This project is licensed under the GNU General Public License v3.0.

Versió en català: README_cat.md

---------------------------------------------------------------------
SUMMARY: This is a 2D N-body simulator. It opens a window divided into two parts: the left side shows the simulation “world” at the current simulation time, and a subwindow on the right displays different results at fixed time intervals, as if a stroboscopic light captured snapshots of the system.

Goal: to interactively explore the dynamics of particle systems with or without gravity, various force fields, and collisions.

Run: 
    `python main.py`
Saved simulation: 
    `python main.py "name of the directory where it was saved"`

(see also below in "OTHERS" and "Controls")
---------------------------------------------------------------------
## SIMULATION FEATURES:

### Particles with individual forces (vehicles)
Particles can have their own constant individual acceleration defined at the beginning of the simulation, as well as initial velocities. This mode simulates simple vehicles or, if no acceleration is present, ideal particles in a box. Example in main.py when defining a particle:
        Particle(x=103.9,   y=35, vx=0,    vy=10.3,  ax=1.5,  ay=3,    m=1.65e-7)
                 pos_x      pos_y vel_x   vel_y     acc_x    acc_y    mass

### GLOBAL uniform force field (gravity at the surface of a planet, uniform gravitational field)
A global force field can also be defined for all particles as a constant acceleration. This allows simulating objects at the surface of the Earth. Example:
    world.add_constant_acceleration(0.0, 9.8)

### UNIVERSAL GRAVITY (NEWTON)
Gravitational interactions can also be included. In this case particles must have mass (see above) and the gravitational constant in the simulation must be non-zero (config.py variable GRAV_G). An example with Solar System planets can be found in main.py.

The simulator includes three different integrators for the equations of motion (from lower to higher numerical stability): Euler, Cromer and Verlet. Controlled via the parameter INTEGRATOR.

### COLLISIONS
Particles can collide if enabled (config.py variable PART_COLL = True). In this case particles have a finite interaction radius defined by PART_CFR. When a collision occurs, it is handled using a coefficient of restitution (PART_CR) between 0 and 1 (0 = inelastic, 1 = elastic).

### OTHERS
The right window shows positions (top) and velocities (bottom) at fixed time intervals (DT_SAMPLE). It also displays kinetic energy, gravitational potential energy, total energy, and total angular momentum (with respect to the origin x, y = 0, 0) at the top.

The simulation can be paused with the "space" key or exited with "ESC".

OTHER KEYS: there is a summary at below

---------------------------------------------------------------------
## PEDAGOGICAL INTEREST

It is interesting to observe how quantities such as energy and angular momentum behave depending on the particle system and the integrator. For example, depending on particle density, masses, etc.

From a programming perspective, it is also useful to see how small changes in the implementation of the equations can improve results (Euler → Cromer). A substantial improvement can also be observed with a more refined approach (Verlet integrator).

Examples can be easily found in main.py, including a Solar System setup or a set of N=200 pseudo-random particles simulating a proto-solar system.

In complex particle systems (e.g. N=200), different types of interactions can be observed: formation of binary systems, ejection of bodies through orbital energy transfer, etc.

Since it supports collisions with different elasticity and a large number of particles, this simulation allows experimenting with many types of systems and helps develop intuition about the underlying physics.

Press the S key to save the current configuration and other variables. In the terminal it will be shown the name of the directory where it has been saved (see SUMMARY to see how to run it)

---------------------------------------------------------------------
## LIMITATIONS (known and incomplete)

- 2D simulation
- Energy is not exactly conserved (depends on the integrator and timestep)
- Collisions and fusions are approximations
- Internal structure of bodies is not modeled, nor associated effects:
  tides, deformations, internal friction or realistic energy dissipation
- Fusions and collisions effectively dissipate energy:
  internal energy (heat, deformation, etc.) is not explicitly modeled
- In a fusion, gravitational potential energy and part of the kinetic energy
  disappear from the effective system (not converted into modeled internal energy)

---------------------------------------------------------------------
## CODE STRUCTURE


```text
project/
├── main.py
├── simulation/
│   ├── particle.py
│   ├── world.py
│   ├── sampler.py
│   └── units.py
│
├── rendering/
│   ├── draw.py
│   ├── plots.py
│   └── user_input.py
└── config.py          <---- parameters controlling simulation and visualization (with detailed comments)
```

---------------------------------------------------------------------
## Controls - KEYS

### Simulation
- `SPACE` — Pause / resume the simulation.
- `ESC` — Exit the simulation.
- `S` — Save the current simulation.

### Left panel
- `T` — Zoom in.
- `B` — Zoom out.
- arrows — Move the view.
- `F` — Show velocity and acceleration vectors during the stroboscopic flashes.

### Right panel — position
- `Y` — Zoom in.
- `N` — Zoom out.
- Hold `R` + arrows — Move the position plot.

### Right panel — velocity
- `U` — Zoom in.
- `M` — Zoom out.

### Zoom
- Hold `G` — Increase/decrease zoom by a factor of 10 instead of the normal factor.

### Stroboscopic points
- `C` — Clear the stroboscopic points, keeping the last 10.
- `X` — Prune stroboscopic points according to their spatial separation.
- `Z` — Remove 50% of the stroboscopic points.


Contact: lluis.marti_at_gmx.net



