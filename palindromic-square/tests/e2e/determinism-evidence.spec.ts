/**
 * Cross-browser determinism verification per TECH_SPEC §11.2.
 *
 * This spec computes the required SHA-256 digest from exact-mode payload fields:
 * schemaVersion, base, rootDigits, normalizedSquareDigits, peak, isPalindrome.
 * Digest input serialization uses canonical key-sorted JSON, output lowercase hex.
 */
import { test, expect, type Page } from '@playwright/test';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { createHash } from 'node:crypto';

const CORPUS = [
  { label: 'b10_111', base: 10, root: '111' },
  { label: 'b10_12321', base: 10, root: '12321' },
  { label: 'b10_99', base: 10, root: '99' },
  { label: 'b16_FF', base: 16, root: 'FF' },
  { label: 'b2_1011', base: 2, root: '1011' },
  { label: 'b10_1', base: 10, root: '1' },
  { label: 'b10_repunit_9', base: 10, root: '111111111' },
  { label: 'b10_repunit_10', base: 10, root: '1111111111' },
  { label: 'b36_ZZ', base: 36, root: 'ZZ' },
] as const;

interface ExportPayload {
  schemaVersion: string;
  project: {
    base: number;
    rootDigits: string;
  };
  result: {
    mode: 'preview' | 'exact';
    isApproximate: boolean;
    normalizedSquareDigits: string;
    peak: string;
    isPalindrome: boolean | 'indeterminate';
  };
}

interface DeterminismInput {
  schemaVersion: 'v1';
  base: number;
  rootDigits: string;
  normalizedSquareDigits: string;
  peak: string;
  isPalindrome: boolean;
}

interface CorpusResult {
  label: string;
  base: number;
  root: string;
  determinismInput: DeterminismInput;
  determinismDigest: string;
}

interface BrowserResult {
  browser: string;
  userAgent: string;
  timestamp: string;
  results: CorpusResult[];
}

function encodeState(base: number, root: string): string {
  return Buffer.from(JSON.stringify({ v: 1, b: base, r: root }), 'utf8').toString('base64');
}

function canonicalJSON(obj: unknown): string {
  if (obj === null || obj === undefined) return JSON.stringify(obj);
  if (typeof obj !== 'object') return JSON.stringify(obj);
  if (Array.isArray(obj)) {
    return '[' + obj.map(canonicalJSON).join(',') + ']';
  }
  const record = obj as Record<string, unknown>;
  const sortedKeys = Object.keys(record).sort();
  const pairs = sortedKeys.map((key) => JSON.stringify(key) + ':' + canonicalJSON(record[key]));
  return '{' + pairs.join(',') + '}';
}

function computeDigest(input: DeterminismInput): string {
  const canonical = canonicalJSON(input);
  return createHash('sha256').update(Buffer.from(canonical, 'utf8')).digest('hex');
}

async function readDownloadAsText(page: Page): Promise<string> {
  const exportButton = page.locator('button:has-text("Export JSON")');
  await expect(exportButton).toBeEnabled({ timeout: 15000 });

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    exportButton.click()
  ]);

  const stream = await download.createReadStream();
  if (stream) {
    const chunks: Buffer[] = [];
    for await (const chunk of stream) {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    }
    return Buffer.concat(chunks).toString('utf8');
  }

  const downloadPath = await download.path();
  if (!downloadPath) {
    throw new Error('Could not access downloaded JSON payload');
  }
  return fs.readFileSync(downloadPath, 'utf8');
}

test.describe('Cross-browser determinism evidence', () => {
  test('compute determinism corpus and record digests', async ({ page, browserName }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toHaveText('PeakGuard');
    await expect(page.locator('.result-summary')).toBeVisible({ timeout: 15000 });

    const userAgent = await page.evaluate(() => navigator.userAgent);

    const browserResult: BrowserResult = {
      browser: browserName,
      userAgent,
      timestamp: new Date().toISOString(),
      results: []
    };

    for (const entry of CORPUS) {
      const payload = encodeState(entry.base, entry.root);
      // URL-state hydration is processed at app startup, so force a full remount.
      await page.goto('about:blank');
      await page.goto(`/#state=${payload}`);

      await expect(page.locator('h1')).toHaveText('PeakGuard');
      await expect(page.locator('.result-summary')).toBeVisible({ timeout: 15000 });
      await expect(page.locator('.result-summary .summary-item').first()).toContainText(entry.root.toUpperCase());

      // Force exact mode so digest input always follows TECH_SPEC §11.2 exact contract.
      await page.click('button:has-text("Compute Exact")');
      await expect(page.locator('.result-summary .approx-badge')).toHaveCount(0, { timeout: 15000 });

      await page.click('button[role="tab"]:has-text("Export")');
      const exportText = await readDownloadAsText(page);
      const exported = JSON.parse(exportText) as ExportPayload;

      expect(exported.schemaVersion).toBe('v1');
      expect(exported.project.base).toBe(entry.base);
      expect(exported.project.rootDigits).toBe(entry.root.toUpperCase());
      expect(exported.result.mode).toBe('exact');
      expect(exported.result.isApproximate).toBe(false);
      expect(typeof exported.result.isPalindrome).toBe('boolean');

      const determinismInput: DeterminismInput = {
        schemaVersion: 'v1',
        base: exported.project.base,
        rootDigits: exported.project.rootDigits,
        normalizedSquareDigits: exported.result.normalizedSquareDigits,
        peak: exported.result.peak,
        isPalindrome: exported.result.isPalindrome as boolean
      };

      const determinismDigest = computeDigest(determinismInput);
      expect(determinismDigest).toMatch(/^[0-9a-f]{64}$/);

      browserResult.results.push({
        label: entry.label,
        base: entry.base,
        root: entry.root,
        determinismInput,
        determinismDigest
      });
    }

    expect(browserResult.results).toHaveLength(CORPUS.length);
    expect(new Set(browserResult.results.map((r) => r.label)).size).toBe(CORPUS.length);

    const reportDir = path.join(process.cwd(), 'evidence');
    fs.mkdirSync(reportDir, { recursive: true });
    fs.writeFileSync(
      path.join(reportDir, `determinism-${browserName}.json`),
      JSON.stringify(browserResult, null, 2)
    );

    console.log(`[determinism] ${browserName}: ${browserResult.results.length} corpus entries recorded`);
  });
});
