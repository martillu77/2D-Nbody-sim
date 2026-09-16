
This README is available in English. See README.md
Llicència: GNU GPL v3.0
Aquest projecte està llicenciat sota la GNU General Public License v3.0.


---------------------------------------------------------------------
RESUM: Aquest és un simulador 2D de N-partícules. Obre una finestra que es divideix en dues parts, l'esquerra on es mostra el "món" de la simulació en el moment "real" de la simulació, i una subfinestra a la dreta que mostra diferents resultats en intervals de temps constants com si una llum estroboscòpica capturés instantànies del sistema.

Objectiu: explorar de manera interactiva la dinàmica de sistemes de partícules amb o sense gravetat, diversos camps de força i col·lisions.

Execució: python main.py
Si es vol continuar una simulacio guardada: python main.py "nom del directory on s'ha guardat"   (més indicacions a "ALTRES" i a "Controls")

---------------------------------------------------------------------
POSSIBILITATS DE SIMULACIÓ:

	Partícules amb força pròpia (vehicles)
Les partícules poden tenir una acceleració pròpia i individual constant definida al principi de la simulació, així com velocitats inicials. Aquesta modalitat simula vehicles simples o, si no hi ha cap acceleració, partícules ideals en una capsa. Exemple a main.py quan es defineix una partícula:
	    Particle(x=103.9,   y=35, vx=0,    vy=10.3,  ax=1.5,  ay=3,    m=1.65e-7)
	             pos_x      pos_y veloc_x  veloc_y   accel_x  accel_y  massa

	CAMP DE FORÇA GLOBAL uniforme (gravetat a la superfície d'un planeta, camp gravitatori uniforme)
També es pot definir un camp de força global per a totes les partícules en forma de acceleració constant. D'aquesta manera es poden simular objectes a la superfície de la Terra. Exemple:
	world.add_constant_acceleration(0.0, 9.8)

	GRAVITACIÓ UNIVERSAL (NEWTON)
També es poden incloure interaccions gravitacionals. En aquest cas les partícules han de tenir massa (vegeu a dalt) i la constant de la gravitació universal a les simulacions ha de ser diferent de zero (config.py variable GRAV_G). Un exemple amb planetes del sistema solar es pot trobar a main.py

Inclou tres tipus diferents de integradors de les equacions de moviment (de menor a major estabilitat numèrica): Euler, Cromer i Verlet. Es controla amb el paràmetre INTEGRATOR. 

	COL·LISIONS
Les partícules poden col·lisionar si així es vol. Es pot activar a config.py variable PART_COLL = True. En aquest cas les partícules tenen un radi determinat per PART_CFR. Quan hi ha una col·lisió el xoc es calcula mitjançant un coeficient de restitució (PART_CR) que pot prendre valors entre 0 i 1 (on: 0 = inelàstic, 1 = elàstic)

	ALTRES
La finestra de la dreta mostra posicions a dalt i velocitats a baix en intervals de temps constants (DT_SAMPLE). També es mostren les energies cinètica, potencial gravitatòria, energia total i moment angular total (des del punt x, y = 0, 0) a dalt de tot.

La simulació es pot pausar amb la tecla "espai" o sortir d'ella amb "ESC".

ALTRES TECLES: hi ha un resum de les tecles i el que fan cap al final d'aquest document.

---------------------------------------------------------------------
INTERÈS PEDAGÒGIC

Es interessant veure com es comporten valors com energia i moment angular segons el sistema de partícules i el integrador. Per exemple, si les partícules són més o menys juntes, massives, etc. 

Des del punt de vista de la programació és també interessant veure com petits canvis a la implementació de les equacions poden millorar els resultats (integrador Euler -> Cromer). També pot observar-se una millora substancial de la implementació amb un càlcul més refinat (integrador "Verlet").

Al codi main.py es poden trobar fàcilment exemples pel sistema solar o fins i tot un conjunt de N=200 partícules pseudoaleatòries que simulen un proto-sistema solar.

Els sistemes de partícules complexos (exemple N=200) es poden veure diferents tipus de interaccions: creació de sistemes binaris, ejecció d'un cos mitjançant transferència d'energia orbital d'altres cossos, etc.

Donat que permet col·lisions de diferent grau d'elasticitat i un número alt de partícules aquesta simulació permet experimentar amb molts tipus de sistemes amb el que permet guanyar una intuïció de la física simulada.

Amb la tecla S es pot guardar la configuració actual de partícules i altres variables. Al terminal s'indica el directori on es guarda (a RESUM podeu veure com executar-ho)

---------------------------------------------------------------------
LIMITACIONS (conegudes i en qualsevol cas incompleta)

- Simulació 2D
- No conserva exactament l’energia (depèn de l’integrador i del pas de temps)
- Les col·lisions i fusions són aproximacions
- No es modela l’estructura interna dels cossos ni efectes associats:
  marees, deformacions, fricció interna o dissipació realista d’energia.
- Les fusions i col·lisions dissipen energia de manera efectiva:
  l’energia interna (calor, deformació, etc.) no es modela explícitament.
- En una fusió, l’energia potencial gravitatòria i part de l’energia cinètica
  desapareixen del sistema efectiu (no es transformen en energia interna modelada).

---------------------------------------------------------------------
ESTRUCTURA GENERAL DEL CODI

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
└── config.py          <---- paràmetres que controlen la simulació i la visualització. Inclou molts comentaris sobre com fer-ho anar.


---------------------------------------------------------------------
## Controls - Tecles

### Simulació
- `ESPAI` — Pausa / reprèn la simulació.
- `ESC` — Surt de la simulació.
- `S` — Desa la simulació actual.

### Panell esquerre
- `T` — Apropa la vista.
- `B` — Allunya la vista.
- fletxes — Mou la vista.
- `F` — Mostra els vectors de velocitat i acceleració durant els flaixos estroboscòpics.

### Panell dret — posició
- `Y` — Apropa la vista.
- `N` — Allunya la vista.
- Mantén premut `R` + fletxes — Mou la gràfica de posicions.

### Panell dret — velocitat
- `U` — Apropa la vista.
- `M` — Allunya la vista.

### Zoom
- Mantén premut `G` — Augmenta o redueix el zoom per un factor 10 en lloc del factor normal.

### Punts estroboscòpics
- `C` — Esborra els punts estroboscòpics, conservant-ne els 10 últims.
- `X` — Redueix els punts estroboscòpics segons la seva separació espacial.
- `Z` — Elimina el 50 % dels punts estroboscòpics.


Contacte: lluis.marti_at_gmx.net
