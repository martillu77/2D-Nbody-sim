License: GNU GPL v3.0
LICENSE: GNU GPL v3.0
This project is licensed under the GNU General Public License v3.0.

Contact: lluis.marti_at_gmx.net

#######################################
##   VERSION			v.0.2.0      ##
#######################################

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
	​
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
* Overall behaviour after v.0.2.0
Significant improvement in:
	- Orbital stability
	- Close encounter handling
	- Accuracy–performance balance

