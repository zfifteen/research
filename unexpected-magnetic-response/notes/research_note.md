# Research Note

## Question

Can the oxygen-mediated mechanism proposed in the paper quantitatively account for the reported conductance drop in Au atomic contacts?

## Setup

The paper reports:

- Au single-atom contacts sit near `1.0 G0` at low field.
- Many Au contacts fall to about `0.85 G0` at `20 T`.
- A favorable modeled oxygen geometry yields conductance near `0.8 G0`.
- The proposed mechanism is not strong direct field tuning of a fixed clean junction.
- The implied mechanism is field-dependent occupancy of oxygen-bearing junction states.

## Minimal Model

Use a two-state mixture:

- clean state: `G_clean = 1.0 G0`
- oxygen-assisted state: `G_oxy = g G0`
- oxygen occupancy: `p(B)`

Then:

`<G(B)> = (1 - p(B)) * G_clean + p(B) * G_oxy`

If `g = 0.8` and the mean high-field conductance is `0.85`, then:

`p(20 T) = 0.75`

assuming the low-field baseline is effectively clean.

## Why This Matters

That result is not impossible, but it is demanding.

It means the paper's oxygen story is only quantitatively comfortable if one of the following is true:

1. Oxygen-bearing low-conductance states are not rare at high field.
2. The relevant low-conductance state is substantially below `0.8 G0`.
3. The observed `15%` shift refers to a tail fraction rather than a strict mean-state translation.
4. A multistate ensemble amplifies the shift more effectively than the simple model.

## Secondary Check: Orientation Energy

The paper reports a magnetic anisotropy energy scale of order `1e-4 eV`.

At `4.2 K`:

`k_B T ~= 3.62e-4 eV`

So the alignment factor from a simple Boltzmann weighting is roughly:

`exp(1e-4 / 3.62e-4) ~= 1.32`

That is a mild bias, not an overwhelming one. By itself, it does not look large enough to turn a genuinely rare state into a dominant one. This again points toward the need for strong state-selection effects, not just weak orientation preference.

## Working Thesis

The published mechanism becomes sharper when restated as:

`high magnetic field reweights the junction-state ensemble`

That is stronger than:

`oxygen near the junction can lower conductance`

The first is an experimentally and statistically demanding claim. The second is only an existence proof.

## Decision Rule

If the characteristic oxygen-assisted conductance remains at or above `0.8 G0`, then explaining a `15%` mean conductance drop requires a high-field occupancy shift of at least `75 percentage points` under the two-state model.

That is the threshold result this project puts in view.
