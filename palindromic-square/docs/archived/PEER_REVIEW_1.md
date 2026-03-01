# Peer Review 1: Cross-Document Consistency and Math Correctness

## Scope
Reviewed:
- `README.md`
- `APP_STORY.md`
- `USER_STORY.md`
- `MATH.md`
- `TECH_SPEC.md`

This review focuses on correctness risks and implementation-blocking ambiguities.

## Findings (Ordered by Severity)

### 1) Critical: Core theorem is false for base 2, but v1 scope requires base 2 support

**Evidence**
- `MATH.md` states `b >= 2` and claims:
  - safe at `n = b-1` and failure at `n = b` (`MATH.md:21`, `MATH.md:45-47`)
  - rule `n <= b-1` is pre-cliff, else post-cliff (`MATH.md:64-66`)
- `TECH_SPEC.md` requires base range `2..36` (`TECH_SPEC.md:49`) and phase behavior at `n=b-1`/`n=b` (`TECH_SPEC.md:63-64`).
- `README.md`, `APP_STORY.md`, and `USER_STORY.md` repeat the unconditional cliff claim (`README.md:12-14`, `APP_STORY.md:24`, `USER_STORY.md:19-20,27`).

**Counterexample**
- Base 2, repunit length 2: `11₂^2 = 1001₂`, which is palindromic.
- This directly contradicts "post-cliff at `n = b`" for `b = 2`.

**Impact**
- The product will misclassify valid palindromic results.
- Property tests in `TECH_SPEC.md:319` cannot pass under current theorem text.
- Acceptance criteria are mathematically incorrect for part of declared scope.

**Required fix**
- Choose one:
  1. Restrict supported bases to `3..36` across all documents and tests, or
  2. Keep `2..36` and update theorem/rules to include base-2 exception.
- Update all narrative/acceptance language that currently says failure is guaranteed immediately above `b-1`.

Suggested corrected fast verdict for repunits:
- If `b == 2`: pre-cliff for `n <= 2`, post-cliff for `n >= 3`.
- If `b >= 3`: pre-cliff for `n <= b-1`, post-cliff for `n >= b`.

### 2) High: Product story requires "Search Guidance", but TECH_SPEC omits it

**Evidence**
- `APP_STORY.md` declares **Search Guidance** as a core capability (`APP_STORY.md:32-34`).
- `USER_STORY.md` acceptance criteria requires a guidance section (`USER_STORY.md:31`).
- `TECH_SPEC.md` required panels do not include any guidance panel (`TECH_SPEC.md:281-290`).

**Impact**
- Implementation can pass the tech spec while failing product/user-story intent.
- High risk of scope drift and review churn late in delivery.

**Required fix**
- Add a functional requirement for guidance behavior (inputs, outputs, wording constraints).
- Add a corresponding UI panel/section under required screens.
- Add E2E coverage for guidance rendering and correctness messaging.

### 3) Medium: "No import in v1" is ambiguous against required URL state sharing

**Evidence**
- `TECH_SPEC.md` says "no import in v1" (`TECH_SPEC.md:96`).
- Same section requires shareable URL state (`TECH_SPEC.md:102`), which is an inbound state load path.

**Impact**
- Teams may block URL hydration as "import", or implement ad hoc exceptions.
- Risk of inconsistent behavior and review disagreement.

**Required fix**
- Clarify scope language:
  - "No file-based import in v1" (JSON/SVG/PNG not re-ingested),
  - "URL-encoded state hydration is allowed."
- Define URL payload versioning and fallback behavior for unknown versions.

## Open Questions
1. Do you want to keep base 2 in scope, or narrow to `3..36`?
2. Should Search Guidance be a required panel for v1, or moved out of scope in upstream docs?

## Summary
The biggest blocker is mathematical correctness at base 2. Resolve that first, then align story/spec coverage for Search Guidance and clarify import semantics around URL state.
