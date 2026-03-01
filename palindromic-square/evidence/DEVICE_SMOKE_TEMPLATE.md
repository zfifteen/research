# PeakGuard v1 — Real-Device & Offline Smoke Evidence Template

> Per TECH_SPEC §10, §11.4, §12, §15: final release requires documented
> real-device smoke and offline launch validation artifacts.

## Instructions

1. Fill in the **Environment** section for each device tested.
2. Walk through every checklist item.
3. Mark each item ✅ Pass, ❌ Fail, or ⚠️ Partial.
4. Capture screenshots where indicated.
5. Save this completed file as `evidence/device-smoke-YYYY-MM-DD.md`.

---

## Test Run Metadata

| Field                | Value                           |
|---------------------|---------------------------------|
| Date                | YYYY-MM-DD                      |
| Tester              |                                 |
| App Version / Build | PeakGuard v1 (commit: _______)  |
| Deployment URL      |                                 |

---

## iOS Safari Smoke

### Environment

| Field          | Value          |
|---------------|----------------|
| Device         |                |
| iOS Version    |                |
| Safari Version |                |

### Checklist

| #  | Test                                         | Status | Notes / Screenshot |
|----|----------------------------------------------|--------|--------------------|
| 1  | App loads without errors in Safari           |        |                    |
| 2  | Header shows "PeakGuard"                     |        |                    |
| 3  | Auto-compute triggers, result summary appears |       |                    |
| 4  | Tab navigation works (all 8 tabs)            |        |                    |
| 5  | Compute Exact produces definitive verdict    |        |                    |
| 6  | Preview mode shows Approximate badge         |        |                    |
| 7  | Export buttons disabled in preview mode       |        |                    |
| 8  | Export JSON works in exact mode               |        |                    |
| 9  | URL share link copies to clipboard            |        |                    |
| 10 | Gallery tab shows examples                    |        |                    |
| 11 | Debug panel shows mobile profile              |        |                    |
| 12 | No console errors visible                     |        |                    |

---

## Android Chrome Smoke

### Environment

| Field            | Value          |
|-----------------|----------------|
| Device           |                |
| Android Version  |                |
| Chrome Version   |                |

### Checklist

| #  | Test                                         | Status | Notes / Screenshot |
|----|----------------------------------------------|--------|--------------------|
| 1  | App loads without errors in Chrome           |        |                    |
| 2  | Header shows "PeakGuard"                     |        |                    |
| 3  | Auto-compute triggers, result summary appears |       |                    |
| 4  | Tab navigation works (all 8 tabs)            |        |                    |
| 5  | Compute Exact produces definitive verdict    |        |                    |
| 6  | Preview mode shows Approximate badge         |        |                    |
| 7  | Export buttons disabled in preview mode       |        |                    |
| 8  | Export JSON works in exact mode               |        |                    |
| 9  | URL share link copies to clipboard            |        |                    |
| 10 | Gallery tab shows examples                    |        |                    |
| 11 | Debug panel shows mobile profile              |        |                    |
| 12 | No console errors visible                     |        |                    |

---

## Offline Launch Validation

### Instructions

1. Load PeakGuard in the browser (first visit to install service worker).
2. Wait at least 5 seconds for SW to finish precaching.
3. Enable Airplane Mode / disable network.
4. Close and re-open the browser tab / navigate to the PeakGuard URL.
5. Verify the app loads and functions.

### iOS Safari Offline

| #  | Test                                          | Status | Notes / Screenshot |
|----|-----------------------------------------------|--------|--------------------|
| 1  | App shell loads offline (header visible)      |        |                    |
| 2  | Cached result/project loads if saved          |        |                    |
| 3  | Tab navigation works offline                  |        |                    |
| 4  | Compute Exact works offline (local compute)   |        |                    |
| 5  | No uncaught errors                            |        |                    |

### Android Chrome Offline

| #  | Test                                          | Status | Notes / Screenshot |
|----|-----------------------------------------------|--------|--------------------|
| 1  | App shell loads offline (header visible)      |        |                    |
| 2  | Cached result/project loads if saved          |        |                    |
| 3  | Tab navigation works offline                  |        |                    |
| 4  | Compute Exact works offline (local compute)   |        |                    |
| 5  | No uncaught errors                            |        |                    |

---

## Summary

| Platform       | Online Smoke | Offline Launch | Overall |
|---------------|-------------|----------------|---------|
| iOS Safari     |             |                |         |
| Android Chrome |             |                |         |

### Sign-off

| Role     | Name | Date |
|----------|------|------|
| Tester   |      |      |
| Reviewer |      |      |
