/**
 * Determinism digest test corpus with snapshot assertions.
 * Per TECH_SPEC Section 11.2 — verifies that computeDeterminismDigest
 * produces correct, canonical, reproducible SHA-256 digests.
 */
import { describe, it, expect } from 'vitest';
import { computeDeterminismDigest, canonicalJSON } from '../../src/math/invariants';

describe('canonicalJSON', () => {
  it('sorts keys lexicographically', () => {
    const obj = { z: 1, a: 2, m: 3 };
    expect(canonicalJSON(obj)).toBe('{"a":2,"m":3,"z":1}');
  });

  it('sorts nested object keys', () => {
    const obj = { b: { z: 1, a: 2 }, a: 3 };
    expect(canonicalJSON(obj)).toBe('{"a":3,"b":{"a":2,"z":1}}');
  });

  it('handles arrays (no sorting of elements)', () => {
    const obj = { b: [3, 1, 2], a: 1 };
    expect(canonicalJSON(obj)).toBe('{"a":1,"b":[3,1,2]}');
  });

  it('handles primitives', () => {
    expect(canonicalJSON('hello')).toBe('"hello"');
    expect(canonicalJSON(42)).toBe('42');
    expect(canonicalJSON(true)).toBe('true');
    expect(canonicalJSON(null)).toBe('null');
  });

  it('produces no insignificant whitespace', () => {
    const obj = { base: 10, isPalindrome: true, rootDigits: '111111111' };
    const result = canonicalJSON(obj);
    expect(result).not.toContain(' ');
    expect(result).not.toContain('\n');
    expect(result).not.toContain('\t');
  });

  it('matches the TECH_SPEC digest input format', () => {
    const obj = {
      base: 10,
      isPalindrome: true,
      normalizedSquareDigits: '12345678987654321',
      peak: '9',
      rootDigits: '111111111',
      schemaVersion: 'v1'
    };
    const expected = '{"base":10,"isPalindrome":true,"normalizedSquareDigits":"12345678987654321","peak":"9","rootDigits":"111111111","schemaVersion":"v1"}';
    expect(canonicalJSON(obj)).toBe(expected);
  });
});

describe('computeDeterminismDigest', () => {
  // Snapshot corpus: each entry defines a known input and its expected SHA-256 digest.
  // These digests were produced from canonical JSON with sorted keys.

  it('base-10 repunit n=9 (palindrome) produces stable digest', async () => {
    const digest = await computeDeterminismDigest(
      10,
      '111111111',
      '12345678987654321',
      9n,
      true
    );
    // Digest of: {"base":10,"isPalindrome":true,"normalizedSquareDigits":"12345678987654321","peak":"9","rootDigits":"111111111","schemaVersion":"v1"}
    expect(digest).toBe('77d51be88d965877972bc2556da45a269719f00a035f0c8f4617a346d2906b85');
    expect(digest).toHaveLength(64);
    expect(digest).toMatch(/^[0-9a-f]{64}$/);
  });

  it('base-10 repunit n=10 (not palindrome) produces stable digest', async () => {
    const digest = await computeDeterminismDigest(
      10,
      '1111111111',
      '1234567900987654321',
      10n,
      false
    );
    expect(digest).toBe('16d7a6aa98e4b50d0542d5daaf25fe168ff99fbf696eca624dcdbc9601ecd6fe');
    expect(digest).toHaveLength(64);
    expect(digest).toMatch(/^[0-9a-f]{64}$/);
  });

  it('base-2 repunit n=2 (palindrome) produces stable digest', async () => {
    const digest = await computeDeterminismDigest(
      2,
      '11',
      '1001',
      2n,
      true
    );
    expect(digest).toBe('8113ca9b10b98f13acc9897f9512b6ad7d08d465ad668f240a5727c9251e45e2');
    expect(digest).toHaveLength(64);
    expect(digest).toMatch(/^[0-9a-f]{64}$/);
  });

  it('different inputs produce different digests', async () => {
    const digest1 = await computeDeterminismDigest(10, '111111111', '12345678987654321', 9n, true);
    const digest2 = await computeDeterminismDigest(10, '1111111111', '1234567900987654321', 10n, false);
    const digest3 = await computeDeterminismDigest(2, '11', '1001', 2n, true);

    // All three should differ
    expect(digest1).not.toBe(digest2);
    expect(digest1).not.toBe(digest3);
    expect(digest2).not.toBe(digest3);
  });

  it('same inputs produce identical digests (determinism)', async () => {
    const a = await computeDeterminismDigest(10, '111111111', '12345678987654321', 9n, true);
    const b = await computeDeterminismDigest(10, '111111111', '12345678987654321', 9n, true);
    expect(a).toBe(b);
  });

  it('base-16 sparse pattern digest', async () => {
    const digest = await computeDeterminismDigest(
      16,
      'A0B',
      '6472E479',
      260n,
      false
    );
    expect(digest).toBe('3e52670ebe7a0787b2aeb8c5263e406b0ff79f954dedf0eef23f04726f0fa9e2');
    expect(digest).toHaveLength(64);
    expect(digest).toMatch(/^[0-9a-f]{64}$/);
  });
});
