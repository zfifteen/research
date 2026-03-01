# User Story: Predicting the Repunit Palindrome Cliff

As an algorithm designer,
I want to see when repunit-square palindromes must fail in a given base,
so that I can stop impossible searches early and focus on constructions with viable symmetry.

## Scenario
1. I open PeakGuard and choose a base `b`.
2. I move a repunit-length slider `n`.
3. The app shows:
   - the convolution triangle,
   - the central accumulation (`peak = n` for repunits),
   - the computed square,
   - and whether the result is palindromic.
4. At `n = b - 1`, the square is still palindromic.
5. At `n = b`, the center requires a symbol outside the base, carries propagate asymmetrically, and palindrome symmetry breaks.

## Example (Base 10)
- `n = 9`: `111111111^2 = 12345678987654321` (palindromic)
- `n = 10`: `1111111111^2 = 1234567900987654321` (not palindromic)

## Acceptance Criteria
- The app marks repunit squares as palindromic exactly up to `n = b - 1`, and not beyond.
- The failure explanation explicitly references the README model:
  central accumulation exceeds symbol capacity, causing asymmetric carry propagation.
- The UI frames the behavior as a sharp phase transition, not gradual degradation.
- The guidance section warns that linear (or faster) peak growth implies a finite symmetry ceiling.
