# App Story: PeakGuard

## Purpose
PeakGuard is an interactive explainer for one specific phenomenon described in `README.md` and formalized in `MATH.md`:
for repunits (and other uniform-element self-products), palindromic square structure fails at a sharp threshold.

In base 10, this means:
- `111111111^2 = 12345678987654321` is still palindromic (`n = 9`).
- `1111111111^2 = 1234567900987654321` is not (`n = 10` forces an illegal central symbol and carry propagation).

In base 2 (special case), this means:
- `11^2 = 1001` is still palindromic (`n = 2`).
- `111^2 = 110001` is not (`n = 3`).

The app exists to make that phase transition obvious, computable, and reusable in design workflows.

## Product Narrative
Users begin with a base selector and repunit length slider. The UI renders:
- the convolution triangle,
- the central accumulation value,
- the resulting square,
- and a palindrome verdict.

For `b >= 3`, as long as the central accumulation remains within single-symbol capacity (`peak < base`), the mirror pattern is intact. The moment `peak >= base`, the app shows asymmetric carry propagation and the palindrome breaks. The transition is immediate, not gradual.

For `b = 2`, the app must present the known exception (`n = 2` still palindromic, `n = 3` broken) and explain that this transition does not follow the simple `peak >= base` cutoff.

## Core Capabilities
- **Phase Transition Explorer**  
  Shows the exact cliff edge for repunits in base `b`:
  - for `b >= 3`: `n = base - 1`,
  - for `b = 2`: `n = 2`.

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

## References
- Product narrative source: [README.md](../README.md)
- Engineering math source: [MATH.md](./MATH.md)
