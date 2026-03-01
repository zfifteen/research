/**
 * Unit tests for encoding utilities — TECH_SPEC Section 8.4.
 */
import { describe, it, expect } from 'vitest';
import { parseMSBtoLE, serializeLEtoMSB, encodeURLState, decodeURLState } from '../../src/utils/encoding';

describe('parseMSBtoLE', () => {
  it('parses simple decimal string', () => {
    expect(parseMSBtoLE('123', 10)).toEqual([3, 2, 1]);
  });

  it('parses single digit', () => {
    expect(parseMSBtoLE('5', 10)).toEqual([5]);
  });

  it('parses hex string case-insensitive', () => {
    expect(parseMSBtoLE('FF', 16)).toEqual([15, 15]);
    expect(parseMSBtoLE('ff', 16)).toEqual([15, 15]);
  });

  it('throws on invalid digit for base', () => {
    expect(() => parseMSBtoLE('A', 10)).toThrow();
  });

  it('throws on empty string', () => {
    expect(() => parseMSBtoLE('', 10)).toThrow();
  });

  it('parses all-ones repunit', () => {
    expect(parseMSBtoLE('111', 10)).toEqual([1, 1, 1]);
  });
});

describe('serializeLEtoMSB', () => {
  it('serializes LE to MSB', () => {
    expect(serializeLEtoMSB([3, 2, 1], 10)).toBe('123');
  });

  it('trims leading zeros', () => {
    expect(serializeLEtoMSB([1, 2, 0, 0], 10)).toBe('21');
  });

  it('canonical zero', () => {
    expect(serializeLEtoMSB([0], 10)).toBe('0');
  });

  it('empty array returns 0', () => {
    expect(serializeLEtoMSB([], 10)).toBe('0');
  });

  it('hex digits are uppercase', () => {
    expect(serializeLEtoMSB([15, 10], 16)).toBe('AF');
  });

  it('roundtrip parse-serialize', () => {
    const original = '12345';
    const le = parseMSBtoLE(original, 10);
    const msb = serializeLEtoMSB(le, 10);
    expect(msb).toBe(original);
  });
});

describe('URL state encoding', () => {
  it('roundtrip encode-decode', () => {
    const encoded = encodeURLState(10, '111111111');
    const decoded = decodeURLState(encoded);
    expect(decoded).toEqual({ base: 10, rootDigits: '111111111' });
  });

  it('returns null for invalid base64', () => {
    expect(decodeURLState('not-valid-base64!!!')).toBeNull();
  });

  it('returns null for unknown version', () => {
    const payload = btoa(JSON.stringify({ v: 999, b: 10, r: '111' }));
    expect(decodeURLState(payload)).toBeNull();
  });

  it('returns null for invalid base', () => {
    const payload = btoa(JSON.stringify({ v: 1, b: 100, r: '111' }));
    expect(decodeURLState(payload)).toBeNull();
  });

  it('returns null for invalid digits', () => {
    const payload = btoa(JSON.stringify({ v: 1, b: 2, r: '999' }));
    expect(decodeURLState(payload)).toBeNull();
  });
});
