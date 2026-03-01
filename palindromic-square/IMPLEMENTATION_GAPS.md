# PeakGuard v1 Remaining Gaps vs `docs/TECH_SPEC.md` (Post-Remediation Revalidation)

Assessment date: 2026-03-01  
Assessment basis: revalidation after code updates and new `docs/REMEDIATION_REPORT.md`.

## Scope Policy
- Include both code-level gaps and environment-dependent release-evidence gaps.
- Treat `TECH_SPEC.md` §12 and §15 as authoritative for release readiness.

## Status Legend
- `Open`: Requirement not fully satisfied.
- `Met`: Implemented and validated in current code/tests.
- `Environment-dependent`: Requires browser/device execution evidence.

## Executive Summary
Current state improved materially from the prior audit. Most previously-open implementation gaps are now closed.

Revalidation results:
- `npx pnpm@9 typecheck`: pass
- `npx pnpm@9 lint`: pass (0 errors, 2 warnings)
- `npx pnpm@9 test`: pass (167/167)
- `npx pnpm@9 build`: pass
- `npx pnpm@9 verify`: pass
- `npx pnpm@9 test:e2e`: fails in this environment due missing Playwright browser executables

Release readiness against `TECH_SPEC.md`: **Not ready** (remaining gaps listed below).

## Remaining Gaps Matrix (Open)
| Priority | TECH_SPEC Ref | Status | Evidence | Gap / Impact | Recommended Fix |
|---|---|---|---|---|---|
| P1 | §8.3 | Open | `src/math/square.ts:20-22`, `src/math/square.ts:39`, `src/app/App.tsx:296-321`, `src/math/square.ts:161` | Repunit fast-path is partially integrated, but contract is still incomplete. The helper is documented as O(1) and “without invoking O(n²) convolution,” yet calls `selfConvolution`. Also, explicit `Preview` requests can still return `indeterminate` for repunit inputs (preview path unchanged). | Enforce repunit exact classification in `handleCompute()` regardless of requested mode, and align fast-path implementation/comments with actual algorithm (true O(1) verdict path for classification). |
| P1 | §11.2, §12 | Open | `tests/e2e/determinism-evidence.spec.ts:45`, `tests/e2e/determinism-evidence.spec.ts:92-95`, `tests/e2e/determinism-evidence.spec.ts:103-106` | Cross-browser determinism evidence harness does not validate the TECH_SPEC digest contract. It captures rendered square text prefix + UI fields, not canonical SHA-256 digest of required exact fields. | Update cross-browser determinism spec to compute and compare the required digest payload/algorithm from §11.2 (canonical JSON, sorted keys, SHA-256, lowercase hex). |
| P2 | §12 | Open | `package.json:16-20` | Release-gate command wiring is still incomplete: `verify`/`verify:release` do not include cross-browser determinism checks required by §12. | Add a single release gate command (or CI workflow) that includes typecheck, lint, unit/property tests, E2E smoke, and cross-browser determinism checks. |
| P2 | §11.3 | Open | `tests/e2e/smoke.spec.ts:113-123`, `tests/e2e/smoke.spec.ts:154-168` | Smoke suite depth improved, but key assertions remain permissive for required scenarios (preview labeling / exact-action blocking). Tests can pass without proving preview state or blocked exports under preview. | Strengthen tests to deterministically enter preview mode and assert exact required outcomes (`Approximate` visible + export buttons disabled). |
| P3 | §10, §11.4, §12, §15 | Environment-dependent | `npx pnpm@9 test:e2e` failure: missing Playwright browser binaries; `evidence/` only contains template (`DEVICE_SMOKE_TEMPLATE.md`) | Final release evidence remains unproven in this environment: E2E execution, real-device smoke, and offline validation artifacts are not complete. | Install Playwright browsers, execute E2E + determinism runs, and produce dated iOS/Android/offline evidence artifacts. |

## Verified as Met (Current State)
- Preemption model upgraded to terminate-and-recreate on supersede with stale-result suppression (`src/worker/api.ts`).
- Startup recovery now has explicit user cleanup choices via modal (`src/features/recovery/StartupRecoveryModal.tsx`, `src/app/App.tsx`).
- Playwright server command no longer requires global `pnpm` (`playwright.config.ts`).
- Core remediation baseline remains healthy:
  - Auto-save timestamp preservation
  - Export blocking in preview mode
  - URL-state warning toasts
  - Migration scaffolding/tests
  - Determinism serializer and unit digest tests

## Validation Execution Snapshot (2026-03-01)
| Command | Result | Notes |
|---|---|---|
| `npx pnpm@9 typecheck` | Pass | 0 TypeScript errors |
| `npx pnpm@9 lint` | Pass with warnings | 0 errors, 2 warnings |
| `npx pnpm@9 test` | Pass | 167/167 tests |
| `npx pnpm@9 build` | Pass | Vite + PWA build successful |
| `npx pnpm@9 verify` | Pass | Local gate script completes |
| `npx pnpm@9 test:e2e` | Fail (environment) | Missing Playwright browser executable; requires install step |

## Environment-Dependent Release Evidence (Open)
- E2E smoke execution artifacts in a browser-installed environment.
- Cross-browser determinism evidence artifacts based on the §11.2 digest contract.
- Filled real-device smoke report (iOS Safari + Android Chrome).
- Filled offline launch validation evidence.

## Priority Remediation Order
1. Close determinism contract gap in cross-browser evidence tooling.
2. Complete repunit fast-path contract for explicit preview requests and align O(1) claim.
3. Strengthen E2E assertions for preview/blocked-export requirements.
4. Wire a complete release-gate command/CI path including cross-browser determinism.
5. Produce browser/device evidence artifacts.
