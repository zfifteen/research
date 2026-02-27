import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Assumption ledger (edit these)
# -----------------------------
T_TARGET = 100.0          # desired improvement eta_nano/eta_macro
f = 1e4                   # switching frequency [Hz]
tau = 1.0 / (2.0 * f)     # active time per cycle [s]

# Geometry / scale
A_total = 1e-4            # total active area [m^2] (e.g., 1 cm^2)
d_macro = 1e-6            # macro gap [m]
d_list = np.logspace(-9, -7, 200)  # nano gaps from 1 nm to 100 nm [m]

# Casimir force per area (ideal parallel plates): F/A = (pi^2 ħ c)/(240 d^4)
HBAR = 1.054_571_817e-34
C = 299_792_458.0
CASIMIR_K = (np.pi**2 * HBAR * C) / 240.0  # [N*m^2]
def casimir_pressure(d):
    return CASIMIR_K / (d**4)  # [N/m^2]

# Device "unknown physics": net impulse rectification factor kappa in [0,1]
# We will solve for kappa required to hit the target improvement.
# Energy per cycle per unit area (drive/maintenance), treated as a knob:
Ecycle_area_nano = 1e-6   # [J/m^2 per cycle]  <-- edit this
Ecycle_area_macro = 1e-6  # [J/m^2 per cycle]  <-- edit this

# Cooling ceilings (optional): cap average power density [W/m^2]
# Use np.inf to disable.
Pcool_nano = np.inf       # [W/m^2]
Pcool_macro = np.inf      # [W/m^2]

# -----------------------------
# Derived quantities
# -----------------------------
# Forces for same total active area
F_macro = casimir_pressure(d_macro) * A_total
F_nano = casimir_pressure(d_list) * A_total

# Average drive power (same area), capped by cooling ceilings if enabled
P_macro = np.minimum(Ecycle_area_macro * A_total * f, Pcool_macro * A_total)
P_nano  = np.minimum(Ecycle_area_nano  * A_total * f, Pcool_nano  * A_total)

# Net force from pulsing: F_net = (kappa * F * tau) * f = kappa * F * (tau*f) = kappa*F/2
# (because tau = 1/(2f)). If you have a different duty cycle, change tau.
duty = tau * f
Fnet_macro_per_kappa = F_macro * duty
Fnet_nano_per_kappa  = F_nano  * duty

eta_macro_per_kappa = Fnet_macro_per_kappa / P_macro
eta_nano_per_kappa  = Fnet_nano_per_kappa  / P_nano

ratio_per_kappa = eta_nano_per_kappa / eta_macro_per_kappa

# kappa required to reach target improvement (if ratio scales linearly with kappa, it cancels)
# Here kappa cancels out because both sides use same kappa.
# If you believe kappa depends on scale (key claim!), add kappa_nano(d) vs kappa_macro.
print("NOTE: With identical kappa for nano and macro, kappa cancels in the ratio.")
print("To encode your hypothesis, define kappa_nano(d) > kappa_macro or different Ecycle scaling.\n")

# Plot ratio vs gap
plt.figure()
plt.loglog(d_list * 1e9, ratio_per_kappa)
plt.axhline(T_TARGET, linestyle="--")
plt.xlabel("Nano gap d [nm]")
plt.ylabel("eta_nano / eta_macro")
plt.title("Conditional scaling: nano pulsed array vs macro (same total area)")
plt.tight_layout()
plt.show()