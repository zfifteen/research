# Palindromic Square Math Spec

## Purpose
This file is the engineering math reference for the app.  
Use it for implementation decisions, correctness checks, and tests.

## Scope
This spec covers the model stated in `README.md`:
- repunit squares in base `b`,
- convolution-driven peak growth,
- carry-triggered symmetry breaking at a sharp threshold.

## Canonical Terms
- `base` or `b`: radix of positional representation.
- `symbol capacity`: valid single-digit range `0..b-1`.
- `repunit length` or `n`: number of ones in `111...1` (base `b`).
- `central accumulation` or `peak`: maximum raw convolution coefficient before carry normalization.
- `phase transition`: immediate behavior change at threshold crossing.

## Definitions
Let `b >= 2`.

Repunit of length `n` in base `b`:

`R_n = sum_{i=0}^{n-1} b^i`

Digit-vector view:

`R_n` corresponds to vector `a = [1, 1, ..., 1]` (length `n`).

Raw square coefficients are self-convolution:

`c_k = sum_{i=0}^{n-1} a_i * a_{k-i}`, for `k = 0..2n-2`.

For repunits this is the triangular sequence:

`c_k = min(k+1, 2n-1-k)`

So the peak is:

`peak = max_k c_k = n`

## Project Theorem (Canonical)
For repunits under this project model:
- at `n = b-1`, palindromic square structure is still valid,
- at `n = b`, central accumulation reaches/exceeds symbol capacity and carry propagation breaks the mirror,
- therefore the cliff edge is `n = b-1`.

Equivalent threshold form:
- safe side: `peak < b`
- failure side: `peak >= b`

## Proof Sketch (Implementation-Level)
1. Repunit squaring is self-convolution of a uniform vector.
2. Self-convolution yields a symmetric triangle with center value `n`.
3. When `n < b`, center can be represented as one symbol, so no forced center overflow.
4. When `n >= b`, center is not representable as one symbol and must decompose via carry.
5. Carry introduces asymmetric spill relative to the mirror axis in this model, so palindrome structure is lost.

## Algorithms
### A. Fast Verdict for Repunits
Input: `base b`, `length n`.

Rule:
- if `n <= b-1`: classify as pre-cliff (palindrome side),
- else: classify as post-cliff (broken side).

Time: `O(1)`.

### B. General Square Pipeline (Any Root)
Input: digit array `a[0..m-1]` in little-endian (`a[0]` least significant), base `b`.

1. Compute raw self-convolution:
`raw[k] = sum_i a[i] * a[k-i]`
2. Compute `peak_raw = max(raw)`.
3. Carry-normalize to base `b`:
   - `t = raw[k] + carry`
   - `out[k] = t % b`
   - `carry = t // b`
4. Append remaining carry digits.
5. Palindrome check on normalized digits (after trimming leading zeros at MSB side).

Pseudocode:

```text
function square_digits_with_peak(a, b):
    m = len(a)
    raw = array_of_zeros(2*m - 1)
    for i in 0..m-1:
        for j in 0..m-1:
            raw[i + j] += a[i] * a[j]

    peak_raw = max(raw)

    out = []
    carry = 0
    for k in 0..len(raw)-1:
        t = raw[k] + carry
        out.append(t % b)
        carry = t // b

    while carry > 0:
        out.append(carry % b)
        carry = carry // b

    trim_msb_zeros(out)  # if representation allows them
    pal = (out == reverse(out))
    return out, peak_raw, pal
```

Time: `O(m^2)` with naive convolution.

## Test Vectors
### Base 10 (Canonical Product Example)
- `n = 9`:
  - root: `111111111`
  - square: `12345678987654321`
  - classification: pre-cliff
- `n = 10`:
  - root: `1111111111`
  - square: `1234567900987654321`
  - classification: post-cliff

## Engineering Notes
- Use integer-safe arithmetic (`BigInt`/big integers) for rendered full values.
- Keep both representations:
  - coefficient-space (pre-carry, for theorem/visualization),
  - normalized digits (post-carry, for displayed number/palindrome check).
- UI language should preserve canonical terms from this file.
