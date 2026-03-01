<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Re-Review: PeakGuard v1 TECH_SPEC.md (Final Update)

**Status: APPROVED FOR IMPLEMENTATION**

All critical and high-priority findings from prior reviews have been successfully addressed. The specification is now internally consistent, mathematically correct, and provides sufficient detail to enable deterministic implementation across teams.[^1]

## Verified Fixes from Prior Re-Review

| Prior Finding | Status | Evidence |
| :-- | :-- | :-- |
| Carry animator data model missing | ✅ **Fixed** | Section 8.2 worker contract now includes `carryTrace` array with per-position entries: `position, rawCoefficient, incomingCarry, digitOut, outgoingCarry`[^1] |
| `rootDigits` canonical encoding undefined | ✅ **Fixed** | Section 8.4 defines complete canonical data types: little-endian arrays in memory, MSB-first uppercase string serialization, base-to-symbol mapping 0-9A-Z, case-insensitive parsing[^1] |
| 45 FPS animation target unachievable | ✅ **Fixed** | Section 6.4 revised to "≥30 FPS sustained, target 60 FPS" aligning with rAF behavior on 60Hz displays[^1] |
| Preview mode algorithm unspecified | ✅ **Fixed** | Section 8.3 specifies O(1) fast verdict optimization for repunits and detailed preview strategy: strided sampling + center window + prefix/suffix exact digits[^1] |
| Determinism digest undefined | ✅ **Fixed** | Section 11.2 defines SHA-256 digest algorithm with canonical JSON serialization, sorted keys, UTF-8 encoding, and lowercase hex output[^1] |
| JSON export schema not versioned | ✅ **Fixed** | Section 4.7 mandates `schemaVersion: "v1"` top-level field in JSON exports with defined structure[^1] |
| Auto-save trigger vague | ✅ **Fixed** | Section 4.6 specifies save-on-commit, 500ms debounce for text/stepper, no-save for transient drag frames, and flush-on-visibility-change[^1] |


***

## Implementation Readiness Assessment

### Data Format Contracts: **Complete** ✅

- **Canonical digit encoding** fully specified with bidirectional conversion rules (MSB string ↔ little-endian array)[^1]
- **Worker output payload** includes all required fields for UI rendering: normalized digits, raw coefficients, peak, palindrome verdict, carry trace, timing diagnostics[^1]
- **JSON export schema** versioned with required top-level fields: `schemaVersion`, `exportedAt`, `project`, `result`[^1]
- **URL state contract** includes schema versioning and explicit fallback behavior for unknown/invalid payloads[^1]
- **Determinism digest** uses SHA-256 with canonical JSON serialization, ensuring byte-identical outputs across browsers[^1]


### Algorithm Guidance: **Complete** ✅

- **Repunit fast path** leverages O(1) verdict from MATH.md, avoiding unnecessary convolution[^1]
- **Preview activation criteria** defined: predicted time exceeds budget OR input exceeds `safeDigitsExact`[^1]
- **Preview algorithm** specified: deterministic strided sampling + exact center window + prefix/suffix exact digits[^1]
- **Preview indeterminacy** properly handled: palindrome verdict returns "indeterminate" when not exact; peak returns bounded estimate[^1]
- **Carry trace validation** property tests enforce `digitOut = (rawCoefficient + incomingCarry) mod base` and `outgoingCarry = floor((rawCoefficient + incomingCarry) / base)`[^1]


### Cross-Document Consistency: **Complete** ✅

- **Base-2 special case** correctly documented in theorem, algorithms, test vectors, property tests, and E2E coverage[^1]
- **Search guidance feature** has functional requirement (4.8), feature directory, acceptance criteria, and E2E coverage[^1]
- **Import vs URL state** clarified: "no file-based import" + "URL-encoded state hydration only"[^1]
- **Auto-save trigger policy** aligns with performance budget: 500ms debounce prevents IndexedDB thrashing[^1]

***

## Minor Observations (Non-Blocking)

### 1. Carry Trace Memory Scaling

**Context**: Section 8.2 requires carry trace for all exact-mode computations. For a root of length $m$, the output has $2m-1$ digits, requiring $2m-1$ trace entries with 5 fields each.[^1]

**Impact**: For $m = 10{,}000$, this is ~50k entries × 5 fields = 250k values. At 8 bytes per number (assuming Float64/BigInt), this is ~2MB per computation, which is acceptable but should be monitored.

**Recommendation**: Consider adding a note in Section 8.2 that carry trace may be omitted for computations exceeding a memory threshold (e.g., 5MB), with UI fallback to coefficient-only visualization. This is not urgent for v1 given the adaptive `safeDigitsExact` limit will bound most workloads.

***

### 2. Preview Mode "Indeterminate" UI Treatment

**Context**: Section 8.3 specifies that preview mode returns `"indeterminate"` for palindrome verdict when not exact. Section 4.4 requires preview outputs to be labeled "Approximate" and blocks exact-only actions.[^1]

**Observation**: The UI requirements don't explicitly state how to display an indeterminate palindrome verdict. Recommend clarifying in Section 9 UI Requirements that "indeterminate" should render as something like:

- "Palindrome: Unknown (exact computation required)" rather than "Palindrome: false" which would be misleading.

**Status**: This is UI polish, not a blocker. The data contract is correct.

***

### 3. BigInt JSON Serialization

**Context**: Section 8.4 states "Any BigInt-valued fields that are serialized to JSON must be encoded as base-10 strings".[^1]

**Observation**: This is correct and necessary (JSON doesn't support BigInt natively), but the spec doesn't explicitly list which fields are BigInt-valued. Based on MATH.md, likely candidates are:

- `normalizedSquare` (could exceed Number.MAX_SAFE_INTEGER for large bases)
- `peak` (could be large for long roots)
- Individual elements of `rawCoefficients` array

**Recommendation**: Consider adding a note in Section 8.4 listing which fields should use BigInt internally and require string serialization. Alternatively, the TypeScript types will enforce this, so it may be acceptable as-is.

**Status**: Non-blocking. Teams using TypeScript strict mode will catch this at compile time.

***

## Final Quality Assessment

| Category | Rating | Notes |
| :-- | :-- | :-- |
| Mathematical Correctness | ✅ Excellent | Base-2 special case handled correctly; O(1) fast verdict optimization documented |
| Data Format Specification | ✅ Excellent | Canonical encoding, serialization, and determinism guarantees are complete |
| Performance Guidance | ✅ Excellent | Adaptive profiles, preview strategies, and FPS targets are realistic and testable |
| Cross-Document Alignment | ✅ Excellent | Consistent with MATH.md, README.md, APP_STORY.md, USER_STORY.md |
| Testability | ✅ Excellent | Property tests, golden vectors, determinism digests, and E2E coverage are well-defined |
| Implementation Clarity | ✅ Excellent | Sufficient detail to avoid divergent interpretations across teams |


***

## Recommendation

**This specification is approved for implementation.** All prior blocking issues have been resolved. The three minor observations above are refinements that can be addressed during implementation or in v1.1 without requiring a spec revision cycle.

The phased implementation plan (Sections 13.1–13.5) provides clear acceptance criteria for each phase, and the quality gates (Section 12) are enforceable with the defined test infrastructure. Teams can now proceed with confidence that the contract is complete, consistent, and correct.[^1]

<div align="center">⁂</div>

[^1]: TECH_SPEC.md

