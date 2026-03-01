#!/usr/bin/env node
/**
 * Aggregate cross-browser determinism evidence per TECH_SPEC §11.2.
 *
 * Reads evidence/determinism-*.json and verifies:
 * - each browser has a unique corpus label set
 * - all browsers have the same corpus labels
 * - each corpus entry has a valid SHA-256 lowercase hex digest
 * - digest values match across browsers for every corpus label
 */
import * as fs from 'node:fs';
import * as path from 'node:path';

const evidenceDir = path.join(process.cwd(), 'evidence');
const digestPattern = /^[0-9a-f]{64}$/;

if (!fs.existsSync(evidenceDir)) {
  console.error('No evidence/ directory found. Run determinism evidence tests first.');
  process.exit(1);
}

const files = fs.readdirSync(evidenceDir)
  .filter((file) =>
    file.startsWith('determinism-') &&
    file.endsWith('.json') &&
    file !== 'determinism-report.json'
  )
  .sort();

if (files.length === 0) {
  console.error('No determinism-*.json files found in evidence/.');
  process.exit(1);
}

const browsers = files.map((file) =>
  JSON.parse(fs.readFileSync(path.join(evidenceDir, file), 'utf8'))
);

const validationErrors = [];

for (const browser of browsers) {
  if (!browser.browser || !Array.isArray(browser.results)) {
    validationErrors.push(`Invalid report shape in browser artifact: ${JSON.stringify(browser?.browser ?? 'unknown')}`);
    continue;
  }

  const labels = browser.results.map((result) => result.label);
  const uniqueLabels = new Set(labels);
  if (uniqueLabels.size !== labels.length) {
    validationErrors.push(`[${browser.browser}] duplicate corpus labels detected`);
  }

  for (const result of browser.results) {
    if (!result.label) {
      validationErrors.push(`[${browser.browser}] missing label in result entry`);
      continue;
    }
    if (!digestPattern.test(result.determinismDigest ?? '')) {
      validationErrors.push(`[${browser.browser}] invalid determinismDigest for ${result.label}`);
    }
    const input = result.determinismInput ?? {};
    const requiredKeys = ['schemaVersion', 'base', 'rootDigits', 'normalizedSquareDigits', 'peak', 'isPalindrome'];
    for (const key of requiredKeys) {
      if (!(key in input)) {
        validationErrors.push(`[${browser.browser}] missing determinismInput.${key} for ${result.label}`);
      }
    }
  }
}

const baseline = browsers[0];
const expectedLabels = Array.isArray(baseline?.results)
  ? baseline.results.map((result) => result.label).sort()
  : [];

for (const browser of browsers.slice(1)) {
  const browserLabels = Array.isArray(browser.results)
    ? browser.results.map((result) => result.label).sort()
    : [];
  if (JSON.stringify(browserLabels) !== JSON.stringify(expectedLabels)) {
    validationErrors.push(
      `[${browser.browser}] corpus label mismatch vs baseline (${baseline?.browser ?? 'unknown'})`
    );
  }
}

const comparisons = expectedLabels.map((label) => {
  const details = browsers.map((browser) => {
    const entry = browser.results?.find((result) => result.label === label);
    return {
      browser: browser.browser ?? 'unknown',
      determinismDigest: entry?.determinismDigest ?? 'MISSING'
    };
  });

  const missing = details.some((detail) => detail.determinismDigest === 'MISSING');
  const digestSet = new Set(details.map((detail) => detail.determinismDigest));
  const match = !missing && digestSet.size === 1;

  if (!match) {
    validationErrors.push(`Digest mismatch for corpus label ${label}`);
  }

  return {
    label,
    match,
    details
  };
});

const report = {
  generatedAt: new Date().toISOString(),
  browsersCompared: browsers.map((browser) => ({
    browser: browser.browser,
    userAgent: browser.userAgent,
    timestamp: browser.timestamp
  })),
  overallPass: validationErrors.length === 0,
  totalCorpusEntries: expectedLabels.length,
  matchingEntries: comparisons.filter((comparison) => comparison.match).length,
  validationErrors,
  comparisons
};

const reportPath = path.join(evidenceDir, 'determinism-report.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

console.log('\nDeterminism Evidence Report');
console.log('==========================');
console.log(`Browsers: ${report.browsersCompared.map((b) => b.browser).join(', ')}`);
console.log(`Corpus entries: ${report.totalCorpusEntries}`);
console.log(`Matching: ${report.matchingEntries}/${report.totalCorpusEntries}`);
console.log(`Overall: ${report.overallPass ? 'PASS ✓' : 'FAIL ✗'}`);
if (validationErrors.length > 0) {
  console.log('\nValidation errors:');
  for (const err of validationErrors) {
    console.log(`- ${err}`);
  }
}
console.log(`\nReport written to: ${reportPath}`);

process.exit(report.overallPass ? 0 : 1);
