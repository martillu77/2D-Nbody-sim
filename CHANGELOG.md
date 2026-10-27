License: GNU GPL v3.0
LICENSE: GNU GPL v3.0
This project is licensed under the GNU General Public License v3.0.

Contact: lluis.marti_at_gmx.net



#######################################
##   VERSION			v.1.1.1      ##
#######################################

Rotational_bias did not generate a global rotation in "generate_collapsing_cloud" and "generate_collapsing_cloud_lognormal". This is now corrected.

Other small changes/improvements:
   - Checks for incoming parameters of particle generating modules
   - Random generator usage and seed set valid in the particle generating modules AND not affecting other parts of the code (if implemented)
   - Remove a non-essential N loop (small but still an improvement) for Verlet integrator in the half-step of the velocities and updating positions 

#######################################
##   VERSION			v.1.1.0      ##
#######################################

Removed one remaining non-essential N^2 loop and left the only one needed for an "exact" simulation
Besides the already existing "generate_rotating_disk" method to initialise particle settings 3 new methods were added:
	- generate_proto_disc                  : massive central mass + keplerian velocity and log-normal masses distrib.
	- generate_collapsing_cloud            : no massive mass + all masses equal + no keplerian velocities
	- generate_collapsing_cloud_lognormal  : basically same as previous but with with log-normal masses distrib.
If GPU is available, calculations are done there using PyTorch (needs to be installed). Note: for now if you try to
simulate too many particiles it will crash
Corrected bug in kinetic energy calculation during collisions.

#######################################
##   VERSION			v.1.0.1      ##
#######################################

Removed an unnecessary N^2 loop for the Verlet integrator

#######################################
##   VERSION			v.1.0.0      ##
#######################################


Version v.1.0.0 summary:

Added the possibility to save the simulation with the "s" key. The name of the directory where the simulation is saved is shown in the terminal, and the simulation can be resumed later.
For more details see the README.md file.
Other simulation parameters are also saved along with the simulation state.
Other minor bugs corrected, eg.:
	kinetic energy in collisions

################################################################################
## Version v.0.2.0 summary:

--------------------------
* Scaling and Units:
Automatic conversion from user units to internal simulation units. This allows to get a normalization to G=1.
This includes a consistent scaling of: positions, velocities, masses and length parameters (cfr)

--------------------------
* Time Integration
In v.0.1.0 a physical criterion for the passage of time was already introduced:

dt∼min(r_min/v_max, SQRT(r_min/a_max) )

Now, it besides time control by: SIM_DT_PARAM (precision) a new time control variable was introduced:
SIM_DT_MAX (upper limit to avoid too slow simulations)

Besides, local time processing was added. This is an automatic substepping in situations of:
- Close encounters
	or
- High accelerations

Preservation of temporal coherence with the global step so as to keep the simulation's simplecticity (better energy and angular momentum conservation) 

* Overall behaviour after v.0.2.0
Significant improvement in:
	- Orbital stability
	- Close encounter handling
	- Accuracy–performance balance
	​

################################################################################
--------------------------
​* User control

In v.0.1.0 the user could control the visualization with the following keys:

	"t" and "b" to zoom in and out the simulation window (left window)
	"y" and "n" to zoom in and out the stroboscopic position window (upper-right window)
	"u" and "m" to zoom in and out the stroboscopic velocity window (lower-right window)
	"g"  to increase the zoom powers of the keys above by a factor x10
	Arrow keys to move the simulation window, AND "r" + arrow keys to move the stroboscopic position window
	
Because long simulations add many innecessary points to the stroboscopic view, this loads the running machine and slows down the simulation. The following keys were added:
	"x" which removes stroboscopic points (position and velocity) that are spatially close.
	"z" which removes ~50% of stroboscopic points.

To improve the understanding of the system being simulated and its didactic value another key was added:
	"f" which shows velocity (blue) and acceleration (red) vectors in the simulation window


--------------------------


