#!/usr/bin/env node
/**
 * Aggregate cross-browser determinism evidence into a single report.
 *
 * Reads per-browser JSON files from evidence/ directory and produces
 * a consolidated evidence/determinism-report.json with:
 *   - Per-browser results
 *   - Cross-browser digest comparison
 *   - Pass/fail determination
 *
 * Usage:
 *   node scripts/aggregate-determinism.mjs
 *
 * Prerequisite: run the cross-browser determinism test first:
 *   npx pnpm@9 build
 *   npx playwright test --config=playwright.determinism.config.ts
 */
import * as fs from 'node:fs';
import * as path from 'node:path';

const evidenceDir = path.join(process.cwd(), 'evidence');

if (!fs.existsSync(evidenceDir)) {
  console.error('No evidence/ directory found. Run the determinism tests first.');
  process.exit(1);
}

const files = fs.readdirSync(evidenceDir).filter(f => f.startsWith('determinism-') && f.endsWith('.json'));
if (files.length === 0) {
  console.error('No determinism-*.json files found in evidence/.');
  process.exit(1);
}

const browsers = [];
for (const f of files) {
  const data = JSON.parse(fs.readFileSync(path.join(evidenceDir, f), 'utf8'));
  browsers.push(data);
}

// Compare digests across browsers
const labels = browsers[0].results.map(r => r.label);
const comparisons = [];
let allMatch = true;

for (const label of labels) {
  const entries = browsers.map(b => {
    const r = b.results.find(x => x.label === label);
    return {
      browser: b.browser,
      squareDigestPrefix: r?.squareDigestPrefix ?? 'MISSING',
      isPalindrome: r?.isPalindrome ?? 'MISSING',
      peak: r?.peak ?? 'MISSING'
    };
  });

  // Check if all browsers agree
  const digests = new Set(entries.map(e => e.squareDigestPrefix));
  const palindromes = new Set(entries.map(e => e.isPalindrome));
  const peaks = new Set(entries.map(e => e.peak));

  const match = digests.size === 1 && palindromes.size === 1 && peaks.size === 1;
  if (!match) allMatch = false;

  comparisons.push({
    label,
    match,
    details: entries
  });
}

const report = {
  generatedAt: new Date().toISOString(),
  browsersCompared: browsers.map(b => ({ browser: b.browser, userAgent: b.userAgent, timestamp: b.timestamp })),
  overallPass: allMatch,
  totalCorpusEntries: labels.length,
  matchingEntries: comparisons.filter(c => c.match).length,
  comparisons
};

const reportPath = path.join(evidenceDir, 'determinism-report.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

console.log(`\nDeterminism Evidence Report`);
console.log(`==========================`);
console.log(`Browsers: ${browsers.map(b => b.browser).join(', ')}`);
console.log(`Corpus entries: ${labels.length}`);
console.log(`Matching: ${comparisons.filter(c => c.match).length}/${labels.length}`);
console.log(`Overall: ${allMatch ? 'PASS ✓' : 'FAIL ✗'}`);
console.log(`\nReport written to: ${reportPath}`);

process.exit(allMatch ? 0 : 1);
