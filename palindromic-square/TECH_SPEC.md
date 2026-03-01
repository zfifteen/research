# TECH_SPEC: PeakGuard v1

## 1. Purpose
This document defines the implementation contract for v1.

Cross-links:
- Product framing: [README.md](./README.md)
- Math and algorithm correctness: [MATH.md](./MATH.md)
- App narrative: [APP_STORY.md](./APP_STORY.md)
- User journey and acceptance framing: [USER_STORY.md](./USER_STORY.md)

Source precedence for implementation conflicts:
1. `MATH.md`
2. `README.md`
3. `APP_STORY.md` and `USER_STORY.md`
4. `TECH_SPEC.md` (this file, for execution details)

## 2. v1 Scope
v1 must deliver the experience implied by `APP_STORY.md` and `USER_STORY.md`, with these hard constraints:
- No backend and no server-side persistence.
- Local-only data persistence.
- Installable PWA that works offline.
- Browser-first usage via localhost static serving.
- No telemetry or outbound analytics.
- Square-only workflow (`root^2`), not general multiplication.

## 3. Primary Stack and Alternatives
### 3.1 Primary (Required)
- Runtime/build: `Node.js` + `pnpm`
- App: `Vite` + `React` + `TypeScript` (`strict: true`)
- UI components: bespoke/custom design system (no heavy component library)
- State: `Zustand`
- Persistence: `IndexedDB` via `Dexie` (with versioned migrations)
- Compute isolation: `Web Worker` + `Comlink`
- Visualization: custom `SVG/Canvas` + D3-light (scales/layout/utilities only)
- PWA/offline: service worker + web app manifest
- Testing: `Vitest`, property tests, `Playwright`

### 3.2 Alternatives (Allowed if explicitly chosen later)
- UI framework: `Vue 3 + Vite + TypeScript + Pinia` (similar architecture)
- UI framework: `Svelte + Vite + TypeScript` (lighter runtime, different state model)
- Worker transport: raw `postMessage` (if Comlink is blocked)
- Storage: raw IndexedDB API (if Dexie is blocked)

Primary remains the default implementation target.

## 4. Functional Requirements
### 4.1 Core Math Experience
- Base range: `2..36`
- Root editing:
  - Default builder UX should favor sparse `0/1` workflows and presets.
  - Advanced mode must allow arbitrary digits `0..b-1`.
- Must compute and show:
  - convolution coefficients (pre-carry),
  - central peak,
  - carry normalization steps,
  - final square digits,
  - palindrome verdict.
- Must preserve canonical terminology from `MATH.md`.

### 4.2 Repunit Phase Transition
- Must clearly show cliff behavior:
  - pre-cliff: `n = b-1`
  - post-cliff: `n = b`
- Base-10 canonical examples must appear in built-in content:
  - `111111111^2 = 12345678987654321`
  - `1111111111^2 = 1234567900987654321`

### 4.3 Step-through Carry Animator (Required)
- Full timeline controls: play, pause, step forward/backward, restart, speed control.
- Highlight central overflow event and carry propagation path.
- In preview mode, animator must be visibly marked as approximate if exact steps are not ready.

### 4.4 Preview vs Exact
- Preview mode is allowed and required for large workloads.
- Any preview-derived output must be labeled `Approximate`.
- Final actions are blocked until exact computation completes:
  - theorem/snippet copy
  - final export artifacts
  - exact palindrome assertion

### 4.5 Gallery and First-run
- Include a built-in gallery of example families (including `10^k + 1` style and sparse patterns).
- First run must auto-load one gallery sample project.

### 4.6 Local Persistence
- Auto-save by default on meaningful change.
- Support multiple saved projects with names and timestamps.
- Data management UI must include:
  - per-project delete
  - clear all local data
  - "Refresh App (clear offline cache)"
- Startup must include corrupted-data recovery flow with cleanup options.

### 4.7 Local-only Export and Sharing
- No cloud sync, no backend storage, no import in v1.
- Required export/share actions:
  - `JSON` (project/result payload)
  - `SVG`
  - `PNG`
  - `Markdown` theorem/snippet text
  - shareable URL state (query/hash encoded)

## 5. Non-Functional Requirements
### 5.1 Offline and Self-contained
- After install, app must run with zero runtime network dependency.
- No CDN-hosted scripts/styles/fonts at runtime.
- PWA installability required.
- Must function offline once assets are cached.

### 5.2 No Telemetry
- No analytics, no crash reporting, no external logging endpoints.

### 5.3 Determinism
- Same input must produce identical exact outputs across supported browsers.
- Core math must use integer-safe operations only (`BigInt`/integer arrays).

### 5.4 Browser Support Matrix
- Desktop (guaranteed): latest 2 versions of Chrome, Edge, Firefox, Safari.
- Mobile (guaranteed): latest 2 versions of Chrome Android and Safari iOS.
- Others: best effort.

### 5.5 Accessibility
- v1 accessibility is best effort (not a formal WCAG compliance target).
- App should still honor OS/browser `prefers-reduced-motion`.
- No dedicated in-app reduce-motion toggle in v1.

## 6. Performance Model and Safety
### 6.1 Adaptive Profiles (Hard Requirement)
- Single codebase with runtime profiles:
  - Desktop profile
  - Mobile profile
- Profiles tune limits/defaults; they do not split product behavior.

### 6.2 Visual Priority
- If tradeoffs arise, preserve visual quality first.
- Use compute adaptation (preview, chunking, warnings, limits, cancellation) before degrading core visuals.

### 6.3 Compute Safety Controls (Required)
- Single active compute job (`latest wins`); cancel stale in-flight jobs.
- Manual override for safety limits with explicit warning/confirmation.
- Kill-switches:
  - user cancel button
  - worker max-time timeout
  - auto-abort on repeated frame-drop conditions

### 6.4 Performance Budget Table (v1 targets)
All values are targets with adaptive runtime tuning.

| Metric | Desktop Target | Mobile Target |
|---|---:|---:|
| Animation frame rate during active visuals | >= 45 FPS | >= 30 FPS |
| Input-to-preview latency (typical/safe range) | <= 150 ms | <= 300 ms |
| Exact compute soft budget (safe range) | <= 2.5 s | <= 5.0 s |
| Warning threshold before manual override prompt | predicted > 2.5 s | predicted > 5.0 s |
| Worker hard timeout per job | 15 s | 25 s |
| Auto-abort frame-drop trigger | < 20 FPS for >= 2 s | < 15 FPS for >= 2 s |

Digit limits must be adaptive and device-benchmarked:
- derive `safeDigitsExact` from startup benchmark and target time budget.
- expose current profile + limits in debug panel.
- allow manual override beyond soft cap.

## 7. Architecture
### 7.1 Repository Shape
Single-package repository (no monorepo/workspaces).

Suggested structure:

```text
palindromic-square/
  APP_STORY.md
  MATH.md
  README.md
  TECH_SPEC.md
  USER_STORY.md
  package.json
  pnpm-lock.yaml
  tsconfig.json
  vite.config.ts
  public/
    manifest.webmanifest
  src/
    app/
      App.tsx
      routes.tsx
    components/
    features/
      explorer/
      builder/
      animator/
      gallery/
      exports/
      data-management/
    math/
      types.ts
      repunit.ts
      convolution.ts
      carry.ts
      palindrome.ts
      square.ts
      invariants.ts
    worker/
      compute.worker.ts
      api.ts
      jobs.ts
    state/
      store.ts
      slices/
        projectSlice.ts
        computeSlice.ts
        uiSlice.ts
        profileSlice.ts
    storage/
      db.ts
      schema.ts
      migrations.ts
      repository.ts
    pwa/
      service-worker.ts
      cache-control.ts
    utils/
      encoding.ts
      timing.ts
  tests/
    unit/
    property/
    e2e/
```

### 7.2 State Model (Zustand)
Minimum slices:
- `projectSlice`: active project input, metadata, dirty state.
- `computeSlice`: job state, preview/exact status, approximation flags, cancellation.
- `uiSlice`: tabs/panels/animator controls/theme-level prefs.
- `profileSlice`: desktop/mobile profile, adaptive limits, benchmark results.

### 7.3 Storage Model (Dexie)
Required tables:
- `projects`
  - `id` (uuid)
  - `name`
  - `createdAt`
  - `updatedAt`
  - `base`
  - `rootDigits` (canonical encoding)
  - `settings` (JSON)
  - `cachedArtifacts` (optional JSON, exact/preview metadata)
- `appMeta`
  - singleton settings/preferences
  - schema/data version fields
  - first-run completion flag

Migration requirements:
- Versioned Dexie schema upgrades.
- Forward migration path must preserve existing projects.

## 8. Math and Compute Contract
### 8.1 Correctness
- `MATH.md` is the authoritative algorithm source.
- Exact mode must implement integer self-convolution + carry normalization.
- No floating-point path may determine exact digits or exact verdicts.
- No `any` types in core math/worker modules (`src/math/**`, `src/worker/**`).

### 8.2 Worker Contract
- Use Comlink RPC interface.
- Jobs must support cancellation and deterministic completion semantics.
- Output payload must include:
  - normalized digits
  - raw coefficients
  - peak
  - palindrome verdict
  - `isApproximate` flag
  - timing diagnostics

### 8.3 Preview Contract
- Preview can use truncated/chunked/sampled strategies.
- Preview must never be presented as exact.
- UI must prevent exact-only actions while `isApproximate=true`.

## 9. UI Requirements
Required screens/panels:
- Phase transition explorer
- Root builder (default sparse tools + advanced digit mode)
- Convolution/heatmap view
- Carry animator (full step-through controls)
- Example gallery
- Export/share panel
- Data management panel
- Debug panel (dev-only or explicit toggle)

Debug panel minimum fields:
- profile (desktop/mobile)
- safe/override limits
- active job timing
- queue depth (must remain 0/1 in latest-wins model)
- memory estimate (best-effort)

## 10. PWA and Offline Behavior
- Installable manifest required.
- Service worker required for offline app shell and static assets.
- No runtime dependency on remote resources after install.
- "Refresh App (clear offline cache)" must:
  - clear app caches,
  - unregister/reload as needed,
  - preserve or clearly warn about local project data handling.

Because this is local-only by design:
- update policy is manual/local deployment driven, not server-driven.

## 11. Validation and Test Plan
### 11.1 Unit and Property Tests
- Core invariants from `MATH.md` must be encoded as tests.
- Golden vectors required (base-10 `n=9`, `n=10`).
- Property tests for:
  - deterministic output for same input
  - carry normalization bounds (`0..b-1`)
  - palindrome verdict consistency
  - repunit cliff behavior across `b in [2,36]`

### 11.2 Cross-browser Determinism
- Same seeded input corpus must yield identical exact output digests across supported browsers.

### 11.3 E2E
- Playwright smoke suite for:
  - first-run gallery load
  - create/edit/save multiple projects
  - preview labeling and exact-action blocking
  - export flows
  - data clear and cache refresh flows
  - offline launch behavior

### 11.4 Real-device Smoke (Required)
- At least one real-device run on:
  - iOS Safari
  - Android Chrome

## 12. Quality Gates (Release Blocking)
All must pass:
- `pnpm typecheck`
- `pnpm lint`
- `pnpm test` (unit + property)
- `pnpm test:e2e` (core smoke matrix)
- Determinism digest checks across supported browsers for exact mode corpus

Suggested `pnpm verify` script:
- runs all release-blocking checks in order.

## 13. Phased Implementation Plan
### Phase 1: Foundation
Deliverables:
- Vite/React/TS strict setup
- Zustand scaffolding
- Dexie setup + initial schema
- Worker + Comlink skeleton
- PWA manifest/service worker baseline
Acceptance:
- App runs locally, installable, basic offline shell works.

### Phase 2: Core Math and Compute
Deliverables:
- exact square pipeline per `MATH.md`
- repunit fast verdict
- preview mode pipeline
- deterministic test vectors and invariants
Acceptance:
- Golden vectors pass and outputs are exact/deterministic.

### Phase 3: Core Experience
Deliverables:
- phase explorer
- builder (sparse + advanced digits)
- convolution/heatmap
- carry animator (full controls)
- gallery + first-run sample
Acceptance:
- End-to-end story flow from `USER_STORY.md` is demonstrable.

### Phase 4: Persistence, Export, Data Management
Deliverables:
- auto-save multiple projects
- recovery flow for corrupted records
- export JSON/SVG/PNG/Markdown
- shareable URL state
- clear/delete/cache-refresh actions
Acceptance:
- Local lifecycle is robust across app restarts and offline runs.

### Phase 5: Hardening and Performance
Deliverables:
- adaptive profile tuning
- performance budgets instrumentation
- kill-switches, latest-wins cancellation
- debug panel
- browser/device smoke coverage
Acceptance:
- Meets budget targets without freezing; release gates pass.

## 14. Out of Scope (v1)
- Backend APIs, cloud sync, auth/accounts
- Multi-user collaboration
- Import workflows
- General multiplication of two distinct roots
- Formal WCAG certification work
- Localization/i18n (English-only v1)

## 15. Definition of Done (v1)
v1 is done when:
- Required features in this spec are implemented.
- Behavior is consistent with `MATH.md`, `README.md`, `APP_STORY.md`, and `USER_STORY.md`.
- Offline installable PWA works with no backend.
- Local persistence and exports are operational.
- Quality gates and real-device smoke checks pass.
