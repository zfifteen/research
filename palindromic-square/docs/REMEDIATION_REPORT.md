# PeakGuard v1 — Remediation Report (Session 4)

**Date:** 2026-03-01  
**Scope:** Complete remaining TECH_SPEC gaps from prior revalidation and reconcile documentation with executed evidence.

## Summary
This pass completed the remaining implementation-level and automated-gate gaps:
- repunit preview contract enforcement,
- strict smoke E2E assertions for preview/export-blocking,
- TECH_SPEC §11.2 digest-contract cross-browser evidence,
- full §12 release-gate wiring in `verify`.

Automated quality gates are now green in this environment.  
The only remaining blocker for final release sign-off is physical-device/offline evidence completion per §11.4/§15.

## Implemented in This Pass

### 1) Repunit preview contract enforcement (§8.3)
- Updated [src/app/App.tsx](/Users/velocityworks/IdeaProjects/research/palindromic-square/src/app/App.tsx) so `handleCompute('preview')` uses `effectiveMode='exact'` for repunit inputs.
- Added worker boundary guard in [src/worker/compute.worker.ts](/Users/velocityworks/IdeaProjects/research/palindromic-square/src/worker/compute.worker.ts) so repunit preview requests are coerced to exact even if caller behavior drifts.
- Corrected fast-path commentary in [src/math/square.ts](/Users/velocityworks/IdeaProjects/research/palindromic-square/src/math/square.ts) to reflect true behavior: O(1) classification with exact digit materialization.

### 2) E2E smoke assertion hardening (§11.3)
- Updated [tests/e2e/smoke.spec.ts](/Users/velocityworks/IdeaProjects/research/palindromic-square/tests/e2e/smoke.spec.ts):
  - deterministic non-repunit preview scenario now asserts `Approximate` badge + unknown verdict,
  - explicit repunit preview scenario asserts exact behavior (no `Approximate`),
  - export-blocking scenario now deterministically asserts all exact-only exports are disabled in preview and warning is visible.

### 3) Determinism evidence rebuilt to required digest contract (§11.2)
- Rewrote [tests/e2e/determinism-evidence.spec.ts](/Users/velocityworks/IdeaProjects/research/palindromic-square/tests/e2e/determinism-evidence.spec.ts):
  - captures exact-mode JSON export payload per corpus entry,
  - computes canonical JSON + SHA-256 lowercase hex digest using required fields:
    `schemaVersion`, `base`, `rootDigits`, `normalizedSquareDigits`, `peak`, `isPalindrome`,
  - writes per-browser `evidence/determinism-<browser>.json`.
- Rewrote [scripts/aggregate-determinism.mjs](/Users/velocityworks/IdeaProjects/research/palindromic-square/scripts/aggregate-determinism.mjs):
  - validates digest format,
  - detects duplicate/missing labels and corpus mismatch,
  - compares `determinismDigest` across browsers,
  - emits `evidence/determinism-report.json` with pass/fail and validation errors.

### 4) Full release-gate wiring in `verify` (§12)
- Updated [package.json](/Users/velocityworks/IdeaProjects/research/palindromic-square/package.json):
  - `verify` now runs: typecheck, lint, unit/property tests, determinism unit suite, build, smoke E2E, cross-browser determinism, aggregation.
  - `verify:release` now aliases full `verify`.
  - `verify:local` remains as fast local gate.

## Verification Results (Executed 2026-03-01)
| Command | Result | Notes |
|---|---|---|
| `npx pnpm@9 typecheck` | ✅ Pass | 0 TypeScript errors |
| `npx pnpm@9 lint` | ✅ Pass with warnings | 0 errors, 2 warnings (`_showDebugPanel`, `_e`) |
| `npx pnpm@9 test` | ✅ Pass | 167/167 |
| `npx pnpm@9 build` | ✅ Pass | Vite + PWA build successful |
| `npx pnpm@9 test:e2e` | ✅ Pass | 17/17 in Chromium |
| `npx pnpm@9 test:determinism:cross-browser` | ✅ Pass | 3/3 (Chromium, Firefox, WebKit) |
| `node scripts/aggregate-determinism.mjs` | ✅ Pass | 9/9 corpus labels matched |
| `npx pnpm@9 verify` | ✅ Pass | Full release-blocking automated gate |

## Remaining Blocker
### Physical-device/offline release evidence (§11.4, §15)
- Still required to complete and record:
  - iOS Safari smoke run,
  - Android Chrome smoke run,
  - offline launch validation artifacts for both.
- Template exists: `evidence/DEVICE_SMOKE_TEMPLATE.md`.

## Updated Readiness Statement
- **Code and automated release gates:** Ready  
- **Final release sign-off:** Pending real-device/offline evidence completion
