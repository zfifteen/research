# App Story: PeakGuard

## Purpose
PeakGuard is an interactive explainer for one specific phenomenon described in `README.md`:
for repunits (and other uniform-element self-products), palindromic square structure fails at a sharp threshold when the central convolution peak reaches the base.

In base 10, this means:
- `111111111^2 = 12345678987654321` is still palindromic (`n = 9`).
- `1111111111^2 = 1234567900987654321` is not (`n = 10` forces an illegal central symbol and carry propagation).

The app exists to make that phase transition obvious, computable, and reusable in design workflows.

## Product Narrative
Users begin with a base selector and repunit length slider. The UI renders:
- the convolution triangle,
- the central accumulation value,
- the resulting square,
- and a palindrome verdict.

As long as the central accumulation remains within single-symbol capacity (`peak < base`), the mirror pattern is intact. The moment `peak >= base`, the app shows asymmetric carry propagation and the palindrome breaks. The transition is immediate, not gradual.

## Core Capabilities
- **Phase Transition Explorer**  
  Shows the exact cliff edge at `n = base - 1` for repunits in base `b`.

- **Convolution-First View**  
  Visualizes coefficients so users see that the peak grows with length and directly drives the break condition.

- **Carry Breakdown Trace**  
  Explains failure as a representational limit at the center (value outside symbol set), followed by asymmetric information spill.

- **Search Guidance**  
  Helps users prioritize candidates by projected peak growth under self-multiplication, matching README guidance:
  linear growth eventually hits a finite ceiling; sublinear/bounded growth is where longer-lived symmetry can exist.

## Promise
PeakGuard does not present palindromic behavior as luck.  
It presents it as a structural constraint with a computable threshold.
