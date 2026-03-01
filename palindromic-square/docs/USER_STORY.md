# User Story: Predicting the Repunit Palindrome Cliff

As an algorithm designer,
I want to see when repunit-square palindromes must fail in a given base,
so that I can stop impossible searches early and focus on constructions with viable symmetry.

References:
- Product framing: [README.md](../README.md)
- Math/algorithm contract: [MATH.md](./MATH.md)

## Scenario
1. I open PeakGuard and choose a base `b`.
2. I move a repunit-length slider `n`.
3. The app shows:
   - the convolution triangle,
   - the central accumulation (`peak = n` for repunits),
   - the computed square,
   - and whether the result is palindromic.
4. For `b >= 3`, at `n = b - 1`, the square is still palindromic.
5. For `b >= 3`, at `n = b`, the center requires a symbol outside the base, carries propagate asymmetrically, and palindrome symmetry breaks.
6. For `b = 2`, `n = 2` is still palindromic but `n = 3` is not.

## Example (Base 10)
- `n = 9`: `111111111^2 = 12345678987654321` (palindromic)
- `n = 10`: `1111111111^2 = 1234567900987654321` (not palindromic)

## Example (Base 2 Special Case)
- `n = 2`: `11^2 = 1001` (palindromic)
- `n = 3`: `111^2 = 110001` (not palindromic)

## Acceptance Criteria
- The app marks repunit squares using the math contract:
  - for `b >= 3`: palindromic exactly up to `n = b - 1`, and not beyond,
  - for `b = 2`: palindromic up to `n = 2`, and not beyond.
- The failure explanation explicitly references the README/MATH model:
  for `b >= 3`, central accumulation exceeds symbol capacity and carries propagate asymmetrically;
  for `b = 2`, the UI presents the documented special-case transition at `n = 2 -> 3`.
- The UI frames the behavior as a sharp phase transition, not gradual degradation.
- The guidance section warns that linear (or faster) peak growth implies a finite symmetry ceiling.
