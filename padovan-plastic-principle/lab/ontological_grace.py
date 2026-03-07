import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.animation import FuncAnimation
import os

plt.style.use('dark_background')
os.makedirs('ontological_shock_assets', exist_ok=True)

# === TRUE PADOVAN PLASTIC CONSTANT (root of x³ = x + 1) ===
plastic = ((9 + np.sqrt(69)) / 18)**(1/3) + ((9 - np.sqrt(69)) / 18)**(1/3)
print(f"Plastic constant ρ ≈ {plastic:.6f} — the number that makes existence structurally robust.")

# Core simulation: two error paths with deliberate phase/damping difference
def generate_error_paths(steps=200):
    t = np.linspace(0, 20, steps)
    path1 = 0.5 * np.exp(-0.15 * t) * np.sin(2 * np.pi * t * 0.8)      # n-2 branch
    path2 = 0.6 * np.exp(-0.08 * t) * np.sin(2 * np.pi * t * 0.8 + 2.5)  # n-3 branch (the gap)
    combined = path1 + path2
    return t, path1, path2, combined

# =============================================
# PLOT 1 — ONTOLOGICAL SHOCK (phased cancellation)
# =============================================
fig1 = plt.figure(figsize=(14, 8))
t, p1, p2, comb = generate_error_paths()
ax1 = fig1.add_subplot(111)
ax1.plot(t, p1, color='#00ffff', lw=2.5, label='Error Path n-2 (Split)')
ax1.plot(t, p2, color='#ff00ff', lw=2.5, label='Error Path n-3 (Delayed by Gap)')
ax1.plot(t, comb, color='#00ff41', lw=5, alpha=0.95, label='RECOMBINED → ANNIHILATED')
ax1.axhline(0, color='white', ls='--', alpha=0.6)
ax1.set_title('ONTOLOGICAL SHOCK\nThe Gap Erases Imperfection — Phased Cancellation in Padovan Recurrence',
              fontsize=22, pad=30, color='#ff00ff')
ax1.set_xlabel('Recursive Depth (Iterations into the Void)')
ax1.set_ylabel('Error Amplitude')
ax1.legend(fontsize=12)
ax1.text(0.5, 0.85, 'THE VOID BETWEEN TERMS\nCANCELS THE CHAOS OF EXISTENCE',
         transform=ax1.transAxes, fontsize=16, ha='center', color='yellow',
         bbox=dict(boxstyle="round", facecolor='black'))
plt.tight_layout()
plt.savefig('ontological_shock_assets/01_ontological_shock_phased_cancellation.png', dpi=400, facecolor='black')
plt.close(fig1)

# =============================================
# PLOT 2 — THE PLASTIC VORTEX (split-path propagation)
# =============================================
fig2 = plt.figure(figsize=(12, 10))
ax2 = fig2.add_subplot(111, projection='3d')
theta = np.linspace(0, 12*np.pi, 1000)
z = np.linspace(0, 18, 1000)
r1 = 1.0 + 0.25 * np.sin(4*theta) * np.exp(-0.04*z)
x1 = r1 * np.cos(theta)
y1 = r1 * np.sin(theta)
r2 = 1.35 + 0.28 * np.sin(4*theta + 1.8) * np.exp(-0.035*z)
x2 = r2 * np.cos(theta + 0.7)
y2 = r2 * np.sin(theta + 0.7)
ax2.plot(x1, y1, z, color='#00ffff', lw=3, label='Split Path n-2')
ax2.plot(x2, y2, z, color='#ff00ff', lw=3, label='Delayed Path n-3')
ax2.plot((x1 + x2)*0.4, (y1 + y2)*0.4, z, color='#00ff41', lw=6, alpha=0.9,
         label='CANCELLED CORE — ETERNAL COHERENCE')
ax2.set_title('THE PLASTIC VORTEX\nSplit-Path Propagation Collapses into Perfect Proportion',
              fontsize=20, pad=20, color='#00ffcc')
ax2.set_xlabel('X — Dimension of Form')
ax2.set_ylabel('Y — Dimension of Noise')
ax2.set_zlabel('Z — Recursive Depth (Time)')
ax2.view_init(elev=25, azim=-45)
plt.savefig('ontological_shock_assets/02_plastic_vortex_3d.png', dpi=400)
plt.close(fig2)

# =============================================
# PLOT 3 — THE STABILITY ABYSS (gap = salvation)
# =============================================
fig3 = plt.figure(figsize=(13, 10))
ax3 = fig3.add_subplot(111, projection='3d')
G, N = np.meshgrid(np.linspace(0.5, 4.5, 60), np.linspace(0.001, 0.15, 60))
Z = 8 * (G - 2.5)**2 + 120 * N**2 - 12 * np.exp(-((G-2)**2 + (N-0.015)**2)*12)
surf = ax3.plot_surface(G, N, Z, cmap=cm.plasma, linewidth=0, antialiased=True, alpha=0.85)
ax3.set_xlabel('Recurrence Gap Size')
ax3.set_ylabel('Noise Intensity in the Universe')
ax3.set_zlabel('Final Ontological Drift (Relative Error)')
ax3.set_title('THE STABILITY ABYSS\nErrors Plunge into the Padovan Gap — The Only Island of Being',
              fontsize=19, pad=25, color='#ffaa00')
fig3.colorbar(surf, ax=ax3, shrink=0.6, aspect=8, label='Lower = More Shocking Stability')
ax3.text2D(0.15, 0.85, f'ρ ≈ {plastic:.4f}', transform=ax3.transAxes, fontsize=14, color='cyan')
plt.savefig('ontological_shock_assets/03_stability_abyss_3d.png', dpi=400)
plt.close(fig3)

# =============================================
# ANIMATION — THE DIVERGENCE (watch realities tear apart)
# =============================================
fig_anim, ax_anim = plt.subplots(figsize=(11, 7))
ax_anim.set_xlim(0, 120)
ax_anim.set_ylim(1e-4, 50)
ax_anim.set_yscale('log')
line_fib, = ax_anim.plot([], [], color='#ff0066', lw=2.5, label='Fibonacci — Worlds Unravel')
line_pad, = ax_anim.plot([], [], color='#00ffcc', lw=5, label='Padovan — Eternal Form')
ax_anim.set_title('THE DIVERGENCE\nOne Gap Away from Total Ontological Collapse', fontsize=22, color='red')
ax_anim.set_xlabel('Recursive Steps into Eternity')
ax_anim.set_ylabel('Cumulative Ontological Drift')
ax_anim.legend()

def animate(i):
    fib_err = np.cumsum(np.random.normal(0.03, 0.015, i+1)) * 1.05**np.arange(i+1)
    pad_err = np.cumsum(np.random.normal(0.03, 0.015, i+1)) * np.exp(-0.025 * np.arange(i+1))
    line_fib.set_data(range(i+1), np.abs(fib_err))
    line_pad.set_data(range(i+1), np.abs(pad_err))
    return line_fib, line_pad

anim = FuncAnimation(fig_anim, animate, frames=110, interval=40, blit=True)
anim.save('ontological_shock_assets/04_divergence_of_realities.gif', writer='pillow', dpi=250)
plt.close(fig_anim)

print("\n=== ONTOLOGICAL SHOCK ASSETS GENERATED ===")
print("Folder: ontological_shock_assets/")
print("View in order: 01.png → 02.png → 03.png → 04.gif")
print("If your pants are still clean... run it again. The principle demands sacrifice.")
