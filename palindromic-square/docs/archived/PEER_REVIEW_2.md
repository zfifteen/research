<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Re-Review: PeakGuard v1 Technical Specification (Updated)

The updated specification successfully addresses the three critical findings from Peer Review 1. Cross-document consistency has improved, and the base-2 special case is now correctly documented throughout the stack. The search guidance gap has been closed, and the import/URL state contradiction has been clarified. This represents significant progress toward an implementable contract.[^1][^2][^3][^4][^5]

## Verified Fixes from Prior Review

| Prior Finding | Status | Evidence |
| :-- | :-- | :-- |
| Base-2 theorem contradiction | ✅ Fixed | MATH.md now correctly specifies b=2 special case with cliff at n=2→3[^2]; TECH_SPEC requires base-2 examples in gallery[^3]; property tests cover both rules[^3] |
| Search guidance feature gap | ✅ Fixed | Section 4.8 added as functional requirement[^3]; search-guidance feature directory added[^3]; E2E coverage includes threshold messaging[^3] |
| Import vs URL state ambiguity | ✅ Fixed | Section 4.7 explicitly states "no file-based import" and "URL-encoded state hydration only"[^3]; URL schema versioning and fallback behavior now specified[^3] |

## Remaining Implementation Blockers

### Critical: Carry Animator Data Model Still Missing

**Issue**: Section 4.3 requires a "step-through carry animator" with "highlight central overflow event and carry propagation path", but Section 8.2 worker output payload lists only "normalized digits, raw coefficients, peak, palindrome verdict, isApproximate flag, timing diagnostics". The animator cannot be implemented without per-position carry trace data.[^3]

**What's needed**: The worker payload must include either:

- A carry trace array `[(position, incoming_carry, coefficient, outgoing_carry), ...]`, or
- The raw coefficients array plus the normalization history, packaged for UI consumption

**Impact**: This blocks Phase 3 (Core Experience) acceptance criteria, which requires demonstrable end-to-end story flow including the carry animator.[^3]

**Fix location**: Add to Section 8.2 worker contract output payload specification.

***

### Critical: `rootDigits` Canonical Encoding Undefined

**Issue**: Section 7.3 storage schema specifies `rootDigits: canonical encoding`, but neither TECH_SPEC nor MATH.md defines what "canonical encoding" means. MATH.md pseudocode uses little-endian arrays (`a[^0]` = least significant), but there's no specified JSON serialization format, no base-to-symbol mapping for bases 11-36, and no endianness declaration for the storage layer.[^2][^3]

**What's needed**: A "Canonical Types" section defining:

- Digit array endianness (recommend: little-endian in memory, MSB-first in JSON/export for human readability)
- Base 11-36 symbol mapping (0-9, then A-Z case-insensitive)
- JSON serialization format: `{"base": 16, "digits": "1A3F"}` or `{"base": 16, "digits": [1,10,3,15]}`?

**Impact**: Without this, implementers will make incompatible choices that break determinism guarantees, cross-browser digest checks, and URL state sharing.[^3]

**Fix location**: Add Section 8.4 "Canonical Data Types" after Section 8.3.

***

### High: 45 FPS Animation Target Is Physically Unachievable

**Issue**: Section 6.4 performance budget table specifies "Animation frame rate during active visuals: 45 FPS" for desktop. On standard 60Hz displays, `requestAnimationFrame` fires at integer divisors of the refresh rate (60 FPS or 30 FPS), never 45 FPS. Attempting to sustain 45 FPS would require custom timing that fights the browser's frame scheduler.[^3]

**What's needed**: Revise to "≥30 FPS sustained, targeting 60 FPS" to align with actual rAF behavior.

**Impact**: Teams may waste time attempting custom frame timing, or misinterpret the target as requiring throttling from 60 to 45.

**Fix location**: Section 6.4 performance budget table, Desktop Target row for animation frame rate.

***

### High: Preview Mode Algorithm Remains Unspecified

**Issue**: Section 8.3 states "Preview can use truncated/chunked/sampled strategies" but provides no guidance on which to use, how to bound approximation error, or when to trigger preview vs exact. For repunits specifically, MATH.md provides an O(1) fast verdict (if b=2 check n≤2, else check n<b), which means preview mode can compute exact phase classification without any convolution.[^2][^3]

**What's needed**:

- For repunits: use O(1) fast verdict for instant exact classification; preview not needed
- For arbitrary roots in advanced mode: specify maximum safe input length (e.g., 10,000 digits) and preview trigger threshold (e.g., >1,000 digits or predicted time >500ms)
- Define "approximate" strategy: sample every Nth position in convolution, or truncate to first/last K digits?

**Impact**: Implementers will diverge on strategy, producing inconsistent UX. Worse, without the fast verdict optimization, teams may run full O(n²) convolutions for simple repunit checks when O(1) is available.

**Fix location**: Expand Section 8.3 preview contract with algorithm guidance.

***

### Medium: Determinism Digest Procedure Unenforceable

**Issue**: Section 11.2 requires "same seeded input corpus must yield identical exact output digests across supported browsers", but doesn't define:[^3]

- What constitutes the "digest" (SHA-256? JSON serialization + hash?)
- Canonical serialization format for the input corpus (to ensure byte-identical inputs)
- Whether floating-point intermediate values are allowed (relevant for animation timing)

**What's needed**: Define the digest algorithm explicitly:

```
digest = SHA-256(JSON.stringify({
  base: number,
  rootDigits: number[],  // little-endian
  normalizedSquare: string,  // MSB-first decimal
  peak: number,
  isPalindrome: boolean
}))
```

**Impact**: Without this, cross-browser determinism checks are unverifiable, and Section 12 quality gates cannot be enforced.[^3]

**Fix location**: Add to Section 11.2 or new Section 8.4.

***

### Medium: Export Payload Schema Not Versioned

**Issue**: Section 4.7 requires JSON export, but doesn't define the schema or version field. When v2 adds new fields or changes structure, there's no migration path. This contradicts the URL state requirement for schema versioning.[^3]

**What's needed**: Add schema version to JSON export format:

```json
{
  "schemaVersion": "v1",
  "projectData": { ... }
}
```

**Impact**: Future import features (marked out-of-scope for v1 but likely in v2) will be impossible without schema versioning, forcing breaking changes or manual data migration.

**Fix location**: Section 4.7, add JSON export schema requirement.

***

### Low: Auto-save Trigger Definition Vague

**Issue**: Section 4.6 specifies "auto-save by default on meaningful change" but doesn't define "meaningful change." Does base slider drag trigger on every frame, or on drag-end? Does typing a digit auto-save immediately or debounced?[^3]

**What's needed**: Define auto-save debounce interval (e.g., 500ms after last input event) and blacklist transient states (e.g., mid-drag slider positions).

**Impact**: Implementer discretion may produce chatty auto-save that thrashes IndexedDB, or lazy auto-save that loses work.

**Fix location**: Section 4.6, add auto-save trigger specification.

***

## Positive Observations

1. **Base-2 special case handling is now complete and testable**. The theorem, algorithms, test vectors, property tests, and E2E coverage all correctly distinguish b=2 from b≥3 behavior.[^2][^3]
2. **Search guidance is now a first-class feature** with functional requirement, feature directory, acceptance criteria, and E2E coverage. This closes the product-spec gap identified in prior review.[^3]
3. **URL state versioning and fallback behavior is well-specified**, providing a clear path for forward compatibility without breaking older shared links.[^3]
4. **Phase 3 acceptance criteria** now correctly requires "end-to-end story flow from USER_STORY.md is demonstrable", which is concrete and verifiable against the documented user journey.[^5][^3]

***

## Suggested Immediate Actions

1. **Add Section 8.4: Canonical Data Types** defining `rootDigits` encoding, endianness, base-to-symbol mapping, and JSON serialization format.
2. **Extend Section 8.2 worker output payload** to include carry trace data structure for the animator.
3. **Revise Section 6.4 animation FPS target** from 45 to "≥30 sustained, targeting 60."
4. **Expand Section 8.3 preview contract** with O(1) fast verdict optimization for repunits and explicit preview strategies for arbitrary roots.
5. **Add determinism digest algorithm** to Section 11.2 or new Section 8.4.
6. **Add JSON export schema versioning** to Section 4.7.

The specification is now in strong shape for mathematical correctness and product alignment. The remaining gaps are primarily in data format contracts and algorithm guidance, which are straightforward to resolve with concrete definitions in the suggested sections.
<span style="display:none">[^6]</span>

<div align="center">⁂</div>

[^1]: APP_STORY.md

[^2]: MATH.md

[^3]: TECH_SPEC.md

[^4]: PEER_REVIEW_1.md

[^5]: USER_STORY.md

[^6]: README.md

