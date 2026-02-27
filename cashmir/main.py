import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Physical constants
hbar = 1.0546e-34   # J·s
c    = 3.0e8        # m/s
kT   = 4.1e-21      # J (room temperature ~300 K)

# Casimir force per unit area: F/A = pi^2 * hbar * c / (240 * d^4)
def casimir_force_per_area(d):
    return (np.pi**2 * hbar * c) / (240.0 * d**4)

# Device parameters
A_total = 1e-4   # m^2 (1 cm^2 total active area)
d_macro = 1e-6   # m  (1 um macroscale reference gap)
d_cross = 100e-9 # m  (100 nm thermal crossover)

# Thermal power model
# Above d_cross: volume-dominated scaling (d^3)
# Below d_cross: surface-dominated scaling (d^2)
def thermal_power(d):
    P_ref = 1e-3  # 1 mW at crossover
    return np.where(
        np.asarray(d) > d_cross,
        P_ref * (d / d_cross)**3,
        P_ref * (d / d_cross)**2
    )

# Momentum per cycle: dp = F * A * (1 / 2f)
def momentum_per_cycle(d, f):
    return casimir_force_per_area(d) * A_total / (2.0 * f)

# Core efficiency metric: eta = (dp * f) / P_thermal
def eta(d, f):
    return (momentum_per_cycle(d, f) * f) / thermal_power(d)

# Simulation ranges
d_range      = np.logspace(-9, -5, 500)         # 1 nm to 10 um
f_fixed      = 10.0                              # Hz
f_range      = np.logspace(0, 4, 300)            # 1 Hz to 10 kHz
d_nano_range = np.logspace(-9, np.log10(d_cross), 200)

# Compute
eta_vs_d     = eta(d_range, f_fixed)
eta_nano_f   = eta(50e-9, f_range)
eta_macro_f  = eta(1e-6,  f_range)
eta_macro_ref = float(eta(d_macro, f_fixed))
ratio_scan   = eta(d_nano_range, f_fixed) / eta_macro_ref

# Style constants
BG    = '#0d1117'
PANEL = '#111827'
GRID  = '#1e2d3d'
TEXT  = '#e0e0e0'
C1    = '#00d4ff'
C2    = '#ff6b35'
C3    = '#39ff14'

def style_ax(ax, title, xlabel, ylabel):
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=TEXT, fontsize=11, pad=8)
    ax.set_xlabel(xlabel, color=TEXT, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT, fontsize=9)
    ax.tick_params(colors=TEXT, labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID)
    ax.grid(True, color=GRID, linewidth=0.5, alpha=0.8)

fig = plt.figure(figsize=(16, 10), facecolor=BG)
gs  = GridSpec(2, 2, figure=fig, hspace=0.50, wspace=0.38)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, :])

# Plot 1: eta vs gap size
style_ax(ax1, 'eta vs Gap Size  (f = 10 Hz)', 'Gap d  [nm]', 'eta  [dimensionless]')
ax1.loglog(d_range * 1e9, eta_vs_d, color=C1, linewidth=2)
ax1.axvline(d_cross * 1e9, color=C2, linestyle='--', linewidth=1.5,
            label='Thermal crossover (100 nm)')
ax1.axhline(1e-4, color=C3, linestyle=':', linewidth=1.2,
            label='eta = 1e-4 decision threshold')
peak_idx = np.argmax(eta_vs_d)
ax1.annotate(
    f'Peak eta ~ {eta_vs_d[peak_idx]:.1e}\n@ d ~ {d_range[peak_idx]*1e9:.1f} nm',
    xy=(d_range[peak_idx]*1e9, eta_vs_d[peak_idx]),
    xytext=(d_range[peak_idx]*1e9 * 8, eta_vs_d[peak_idx] * 0.05),
    color=TEXT, fontsize=7.5,
    arrowprops=dict(arrowstyle='->', color=TEXT, lw=1.0)
)
ax1.legend(fontsize=7.5, facecolor=PANEL, labelcolor=TEXT, edgecolor=GRID, loc='lower left')

# Plot 2: eta vs switching frequency
style_ax(ax2, 'eta vs Switching Frequency', 'Frequency f  [Hz]', 'eta  [dimensionless]')
ax2.loglog(f_range, eta_nano_f,  color=C1, linewidth=2, label='Nano   d = 50 nm')
ax2.loglog(f_range, eta_macro_f, color=C2, linewidth=2, label='Macro  d = 1 um')
ax2.axhline(1e-4, color=C3, linestyle=':', linewidth=1.2, label='eta = 1e-4 threshold')
ax2.legend(fontsize=7.5, facecolor=PANEL, labelcolor=TEXT, edgecolor=GRID)

# Plot 3: falsifiability ratio test
style_ax(ax3,
         'Falsifiability Test: eta_nano / eta_macro  (f = 10 Hz)\nPrediction: ratio > 100x for d < 100 nm',
         'Nanoscale emitter gap d  [nm]',
         'eta_nano / eta_macro  [ratio]')
ax3.semilogx(d_nano_range * 1e9, ratio_scan, color=C1, linewidth=2.5)
ax3.axhline(100, color=C2, linestyle='--', linewidth=1.8, label='100x prediction threshold')
ax3.axhline(10,  color=C3, linestyle=':',  linewidth=1.2, label='10x falsification boundary')
ax3.axvline(d_cross * 1e9, color='#888888', linestyle='--', linewidth=1.2,
            label='Scaling crossover (100 nm)')
confirmed = ratio_scan >= 100
ax3.fill_between(d_nano_range * 1e9, ratio_scan, 100,
                 where=confirmed, alpha=0.15, color=C2,
                 label='Prediction confirmed zone')
ax3.legend(fontsize=8.5, facecolor=PANEL, labelcolor=TEXT, edgecolor=GRID, loc='upper left')

fig.suptitle(
    'Casimir Propulsion Efficiency: Pulsed Nanoscale Arrays vs Static Macroscale Gaps\n'
    'Core Insight: eta scales favorably below the 100 nm thermal crossover.',
    color=TEXT, fontsize=11, y=1.02
)

plt.savefig('casimir_insight.png', dpi=150, bbox_inches='tight', facecolor=BG, edgecolor='none')
print("Saved: casimir_insight.png")

# Console summary
print()
print("=" * 55)
print("SIMULATION RESULTS  [model, not measured data]")
print("=" * 55)
print(f"Macro ref  d=1um,  f=10Hz :  eta = {eta(d_macro, f_fixed):.2e}")
print(f"Nano       d=50nm, f=10Hz :  eta = {eta(50e-9,   f_fixed):.2e}")
print(f"Ratio (nano / macro)      :  {eta(50e-9, f_fixed) / eta(d_macro, f_fixed):.2e}x")
if np.any(confirmed):
    print(f"Prediction (>100x) holds for d < {d_nano_range[confirmed][-1]*1e9:.0f} nm")
if np.any(ratio_scan >= 10):
    print(f"Falsification boundary       d < {d_nano_range[ratio_scan>=10][-1]*1e9:.0f} nm")
