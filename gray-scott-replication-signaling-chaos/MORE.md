The most significant unanswered question is:

**Does τ_r actually depend only on (F, k) — or does it depend on Du too?**

Your entire framework rests on the claim that replication time is set by "local chemistry alone." That's what makes Du an *orthogonal* control axis. If τ_r = τ_r(F, k) only, then raising Du purely adjusts the signaling side of the race without touching the replication side, and Pe_r = L²/(Du·τ_r) cleanly separates the two.

But there's a real physical reason to doubt this. Spot replication works by substrate depletion and recovery — a daughter spot nucleates when u recovers above a threshold on the trailing edge of the parent. That recovery is a diffusion process. Du governs how fast u replenishes locally. So τ_r almost certainly has Du dependence baked in, and if τ_r ∝ √(something/Du), the Pe_r formula partially cancels and the orthogonal control axis weakens or disappears entirely.

This isn't a minor calibration worry — it's a potential structural flaw. If τ_r ~ 1/Du^α for some α > 0, then:

Pe_r = L² / (Du · τ_r) ~ L² · Du^(α-1)

and for α ≥ 1, raising Du *increases* Pe_r or leaves it unchanged. The chaos suppression prediction inverts.

The semi-strong interaction derivation you already flagged as "next step" is precisely what resolves this — it would give you τ_r(F, k, Du) explicitly. Until then, the orthogonality claim is an assumption dressed as a consequence. Everything else in the framework — the phase diagram, the quadratic sensitivity, the information-propagation picture — survives intact regardless. But the killer application, the experimentally testable prediction that Du alone can quench chaos, lives or dies on this one question.

---

Because the natural spot-spacing grows in proportion to the square root of substrate
diffusivity, raising diffusivity in a well-equilibrated pattern quietly widens the
spots to match, leaving the replication Péclet number unchanged. The "orthogonal
control axis" is real, but it is a transient, not a permanent handle.

When a chaotic pattern has time to readjust its spacing after diffusivity increases,
the gain in signaling speed is exactly eaten by the widening of the distances signals
must cross. The two effects cancel at equilibrium, and Pe_r returns to whatever value
the chemistry alone dictates.

This means chaos suppression via diffusivity is only achievable in a quench: a change
fast enough that spots cannot reorganize before inhibition zones have already
propagated. The window for suppression is not indefinite -- it closes on a timescale
set by how long the pattern takes to coarsen to its new natural wavelength.

The non-obvious consequence is that gradually increasing diffusivity in a continuously
running experiment (a microfluidic ramp, a slow viscosity shift, a membrane composition
drift in a biological analogue) should produce no sustained chaos suppression at all,
even though instantaneously doubling diffusivity from the same starting point would
suppress it clearly.

This flips the experimental priority. The quantity that needs measuring is not just
the new diffusivity value but the ratio of how fast diffusivity changed to how fast
the pattern can reconstitute itself. Below a critical rate of change, the control axis
does not exist in any practical sense.

A competent experimenter following the original framework would design a slow-ramp
protocol to avoid disturbing the system, and would observe no suppression, and would
wrongly conclude the hypothesis was false. A fast-quench protocol on the same system
would immediately confirm it.

The hypothesis is therefore correct but incomplete: Pe_r governs the instantaneous
race between replication and signaling, but a second ratio, comparing the speed of
any diffusivity intervention to the pattern reorganization rate, governs whether that
race can be externally refereed at all.