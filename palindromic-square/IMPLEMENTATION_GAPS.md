# PeakGuard v1 Implementation Gaps vs `docs/TECH_SPEC.md`

Assessment date: 2026-03-01  
Assessment basis: static code review of `src/`, `tests/`, config files, and project structure.

Runtime validation note:
- Full release-gate execution was not possible in this environment because `pnpm` is not installed and network access is restricted (so `corepack` cannot fetch `pnpm`).

## Status Legend
- `Met`: Implemented and evidenced in code.
- `Partial`: Implemented in part, but does not fully satisfy the spec contract.
- `Missing`: Not implemented.
- `Unverified`: Could not be validated from available execution environment/evidence.

## Executive Summary
Release readiness against current TECH_SPEC: **Not ready**.

Primary blockers:
1. Compute safety controls are not preemptive in practice (worker cancellation/timeout and latest-wins semantics break down for long synchronous jobs).
2. Required validation gates are incomplete (no E2E suite, no real-device smoke evidence, incomplete `verify` script, no determinism cross-browser checks).
3. Several contract-level mismatches remain (canonical determinism JSON sort requirement, metadata persistence correctness, and exact-only action blocking behavior).

## Gap Matrix
| TECH_SPEC Reference | Status | Evidence | Gap / Impact | Recommended Fix |
|---|---|---|---|---|
| 6.3, 8.2: cancellation + latest-wins + worker timeout | Partial | `src/worker/compute.worker.ts:15-41`, `src/worker/api.ts:36-53`, `src/math/convolution.ts:23-29` | Worker compute path is synchronous O(n^2). `cancel()` and timeout flag cannot interrupt hot loops mid-job. Long jobs can block cancellation and degrade latest-wins semantics. | Make compute chunked/cooperative (periodic cancellation checks) or adopt interruptible strategy; enforce timeout by terminating worker if budget exceeded. |
| 6.3: auto-abort on repeated frame drops | Missing | No FPS monitoring/auto-abort logic in app; debug only displays configured thresholds in `src/features/data-management/DebugPanel.tsx:51-53` | Required kill-switch is not implemented. | Add runtime frame-drop detector and cancel/abort policy tied to profile thresholds. |
| 8.3: preview activation condition (time budget OR safeDigitsExact) | Partial | Auto compute uses only digit-count threshold in `src/app/App.tsx:229-237`; predicted time is computed but not used for auto preview (`src/app/App.tsx:184`) | Spec requires activation when predicted time exceeds budget even under `safeDigitsExact`. Current logic can still auto-run exact unnecessarily. | Gate auto exact on both `safeDigitsExact` and predicted-time budget (`limits.inputToPreviewMs`). |
| 4.6: project timestamps semantics | Partial | Autosave always writes `createdAt: now` in `src/app/App.tsx:127-133` and `src/app/App.tsx:156-163` | Existing projects lose original creation time on autosave. Timestamp integrity for project metadata is broken. | Preserve `createdAt` for existing projects; only set on first creation. |
| 4.4: exact-only action blocking | Partial | JSON/Markdown are blocked in preview (`src/features/exports/ExportPanel.tsx:160-170`), but SVG/PNG remain enabled in preview (`src/features/exports/ExportPanel.tsx:173-186`) | Spec language calls for blocking final export artifacts until exact completion; current behavior allows preview exports for SVG/PNG. | Clarify artifact policy and enforce exact-only gating consistently if intended by spec. |
| 4.7: URL invalid/unknown payload UX fallback | Partial | Decode returns `null` and logs warning (`src/utils/encoding.ts:65-67`, `src/app/App.tsx:85-87`) | Fallback is non-crashing, but no user-visible non-blocking error message is shown. | Add transient UI notice/toast for invalid/unsupported URL state. |
| 7.3: forward migration path | Partial | Dexie has only v1 schema (`src/storage/schema.ts:30-33`), no migration handlers | Versioning exists, but explicit forward migration path preservation is not yet demonstrated. | Add migration scaffolding/tests for v2+ schema upgrades with data-preservation checks. |
| 9: debug panel safe/override limits | Partial | Safe limits shown in debug panel (`src/features/data-management/DebugPanel.tsx:31-53`), no explicit override state surfaced | Minimum fields request "safe/override limits"; override value/state is not represented. | Track override mode/threshold in state and render in debug panel. |
| 11.2: canonical determinism digest serialization | Partial | Utility exists (`src/math/invariants.ts:67-90`) but uses plain `JSON.stringify(obj)` (`src/math/invariants.ts:84`) | Spec requires lexicographically sorted keys canonical JSON; insertion-order serialization is not explicit canonicalization. | Implement key-sorted canonical serializer and add deterministic tests. |
| 11.2: cross-browser determinism checks | Missing | No determinism digest test corpus or browser-run harness found; utility is not referenced by tests (`rg` only finds definition). | Required cross-browser determinism gate is absent. | Add corpus + digest snapshots and cross-browser automation/report. |
| 11.3: Playwright E2E smoke suite | Missing | `tests/e2e/` has zero files, `count=0`; script exists in `package.json:14` but no test implementation | Required E2E scenarios are not implemented. | Add Playwright setup and smoke tests for all required flows. |
| 3.1, 11.3: Playwright toolchain presence | Partial | `package.json:14` includes `playwright test`; no Playwright dependency in `package.json:27-45` | E2E command is declared but dependency/tooling appears incomplete. | Add `@playwright/test` and config; wire into CI/local docs. |
| 11.4: real-device smoke (iOS Safari + Android Chrome) | Missing | No evidence/log artifacts in repo | Mandatory real-device validation is undocumented/unmet. | Execute and document smoke results (device/OS/browser/version/date). |
| 12: quality gates in `verify` | Partial | `verify` runs `typecheck`, `lint`, `test`, `build` (`package.json:15`) | Missing required `test:e2e` and determinism digest checks from release gate list. | Update `verify` to include all release-blocking gates in TECH_SPEC §12. |
| 10, 12, 15: offline and release validation evidence | Unverified | PWA configuration exists (`vite.config.ts:8-28`, `src/main.tsx:6-13`) | Offline launch/install behavior and full gate pass status cannot be confirmed from current environment. | Run and capture install/offline smoke + full verify artifacts in a network-enabled dev/CI environment. |

## Areas Largely Aligned (No Major Gap Found in Static Review)
- Core stack and architecture baseline: Vite + React + TS strict + Zustand + Dexie + Worker/Comlink are present (`tsconfig.json:14`, `src/state/store.ts`, `src/storage/schema.ts`, `src/worker/api.ts`).
- Core math pipeline and canonical examples are implemented (`src/math/square.ts`, `src/math/repunit.ts`, `src/features/gallery/galleryData.ts:10-45`).
- Required UI panels are present (explorer, builder, heatmap, animator, guidance, gallery, export, data, debug) via app tab routing in `src/app/App.tsx:23-343`.
- Approximate labeling and indeterminate palindrome wording are implemented (`src/app/App.tsx:250-257`, `src/features/explorer/ConvolutionHeatmap.tsx:30`, `src/features/animator/CarryAnimator.tsx:82-87`).
- Unit/property math tests are substantial and align with many §11.1 expectations (`tests/unit/square.test.ts`, `tests/property/invariants.test.ts`).

## Priority Remediation Order
1. Fix worker preemption model (cancellation/timeout/latest-wins) and add frame-drop auto-abort.
2. Implement E2E suite and real-device smoke evidence.
3. Complete determinism contract (canonical JSON sort + cross-browser digest checks).
4. Correct autosave metadata handling (`createdAt`) and clarify/export exact-only policy.
5. Align `verify` with full TECH_SPEC quality gates.

