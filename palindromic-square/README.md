# Palindromic Square Cliff (Repunits)

## Document Roles
- `README.md` is the product-level narrative source of truth.
- `MATH.md` is the implementation-math source of truth (definitions, theorems, algorithms, test vectors).
- `APP_STORY.md` and `USER_STORY.md` must stay consistent with both.

See: [MATH.md](./MATH.md)
Related: [APP_STORY.md](./APP_STORY.md), [USER_STORY.md](./USER_STORY.md)

## Core Claim
The palindromic square pattern from repunits (111...1)^2 breaks at exactly n=(base-1) digits because squaring a repunit is equivalent to convolving a uniform sequence with itself, producing a triangular distribution whose peak value equals n, and when this peak meets or exceeds the base radix, it triggers a carry that propagates asymmetrically and irreversibly destroys the palindromic structure.

The breakdown is not gradual deterioration but a sharp phase transition: one digit below the threshold produces perfect symmetry, one digit above guarantees failure.

This reveals that the pattern's fragility is not about computational complexity or "too many carries" in the aggregate sense, but about a single critical digit position (the center) attempting to represent a value outside the symbol set, forcing information to spill asymmetrically into neighboring positions.

The convolution lens predicts that any similar pattern based on uniform-element multiplication will exhibit identical phase behavior: stable palindromes exist only while the central accumulation stays within single-symbol capacity, regardless of how many other positions experience carries.

In base 10, the ninth repunit (111,111,111) sits exactly at the cliff edge where the central digit tries to become "9," still legal, but the tenth repunit demands a central "10," which cannot exist as a single symbol and must decompose, breaking the mirror.

This implies we should search for palindromic squares by first checking whether the root's digit structure produces linear or sublinear peak growth under self-multiplication; superlinear or even linear growth with sufficient length always terminates in symmetry collapse at a computable threshold.

For algorithm designers seeking to exploit palindromic properties in number-theoretic constructions, this sets an absolute ceiling on pattern availability, not a probabilistic one: beyond length (base-1), the mathematical structure forbids palindromic repunit squares by necessity, not by chance.
