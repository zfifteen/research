# PeakGuard v1 Remaining Gaps vs `docs/TECH_SPEC.md` (Post-Implementation Revalidation)

Assessment date: 2026-03-01  
Assessment basis: revalidation after implementation completion and verification reruns.

## Scope Policy
- Include both code-level gaps and environment-dependent release-evidence gaps.
- Treat `TECH_SPEC.md` §12 and §15 as authoritative for release readiness.

## Status Legend
- `Open`: Requirement not fully satisfied.
- `Met`: Implemented and validated in current code/tests.
- `Environment-dependent`: Requires browser/device execution evidence.

## Executive Summary
Implementation and automation gaps identified in the prior re-audit are now closed:
- Repunit preview contract is enforced at app and worker boundaries.
- E2E preview/export assertions are now deterministic and strict.
- Determinism evidence now uses required §11.2 canonical digest contract.
- `verify` is now a full release-blocking gate including E2E + cross-browser determinism + aggregation.

Current release readiness: **not fully release-ready** due to remaining real-device/offline evidence requirement.

## Remaining Gaps Matrix (Open)
| Priority | TECH_SPEC Ref | Status | Evidence | Gap / Impact | Recommended Fix |
|---|---|---|---|---|---|
| P3 | §10, §11.4, §15 | Environment-dependent | No completed physical-device evidence artifacts yet in `evidence/DEVICE_SMOKE_TEMPLATE.md` | Required real-device smoke and offline validation evidence is still missing for final sign-off. | Execute and record iOS Safari + Android Chrome real-device smoke (including offline launch evidence), then attach dated artifacts/sign-off notes. |

## Verified as Met (Current State)
- Repunit explicit-preview path now resolves as exact (`isPalindrome: true|false`) at both app entrypoint and worker boundary (`src/app/App.tsx`, `src/worker/compute.worker.ts`, `src/math/square.ts`).
- E2E smoke suite now has strict preview/export-blocking assertions and explicit repunit preview behavior checks (`tests/e2e/smoke.spec.ts`).
- Cross-browser determinism evidence computes TECH_SPEC §11.2 digest fields from exact JSON export payloads (`tests/e2e/determinism-evidence.spec.ts`).
- Determinism aggregation now validates digest shape, corpus consistency, duplicate/missing labels, and cross-browser equality (`scripts/aggregate-determinism.mjs`).
- `verify` now runs all release-blocking automated checks in one command (`package.json`).
- Previously remediated items remain intact: preemption semantics, startup recovery modal, Playwright `pnpm` boot compatibility, migration scaffolding, carry/invariant/determinism unit coverage.

## Validation Execution Snapshot (2026-03-01)
| Command | Result | Notes |
|---|---|---|
| `npx pnpm@9 typecheck` | Pass | 0 TypeScript errors |
| `npx pnpm@9 lint` | Pass with warnings | 0 errors, 2 warnings (pre-existing unused symbols) |
| `npx pnpm@9 test` | Pass | 167/167 tests |
| `npx pnpm@9 build` | Pass | Vite + PWA build successful |
| `npx pnpm@9 test:e2e` | Pass | 17/17 tests passed in Chromium |
| `npx pnpm@9 test:determinism:cross-browser` | Pass | 3/3 (Chromium, Firefox, WebKit) |
| `node scripts/aggregate-determinism.mjs` | Pass | 9/9 corpus labels matched across browsers |
| `npx pnpm@9 verify` | Pass | Full release-blocking automated gate passes end-to-end |

## Environment-Dependent Release Evidence (Open)
- Complete `evidence/DEVICE_SMOKE_TEMPLATE.md` with dated physical-device runs for:
  - iOS Safari
  - Android Chrome
  - Offline launch validation on both devices

## Readiness
- **Engineering readiness (code + automated gates): Ready**
- **Final release readiness per TECH_SPEC §15: Pending real-device/offline evidence completion**
