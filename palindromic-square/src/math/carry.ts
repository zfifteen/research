/**
 * Carry normalization per MATH.md Algorithm B steps 3-4.
 * Converts raw convolution coefficients to base-b digit representation.
 */
import type { Base, DigitsLE, CarryTraceEntry } from './types';

export interface CarryResult {
  /** Normalized digits in LE order */
  digitsLE: DigitsLE;
  /** Full carry trace for animator */
  carryTrace: CarryTraceEntry[];
  /** Whether carry trace was omitted for size reasons */
  carryTraceOmitted: boolean;
  carryTraceOmissionReason: string | null;
}

const CARRY_TRACE_MAX_BYTES = 5 * 1024 * 1024; // 5 MB threshold

/**
 * Normalize raw coefficients to base-b digits with full carry propagation.
 * Implements MATH.md pseudocode exactly.
 */
export function carryNormalize(raw: bigint[], base: Base, collectTrace: boolean = true): CarryResult {
  const b = BigInt(base);
  const estimatedTraceSize = raw.length * 80; // rough estimate per entry
  const shouldCollectTrace = collectTrace && estimatedTraceSize < CARRY_TRACE_MAX_BYTES;

  const digitsLE: DigitsLE = [];
  const carryTrace: CarryTraceEntry[] = [];
  let carry = 0n;

  for (let k = 0; k < raw.length; k++) {
    const rawCoeff = raw[k]!;
    const t = rawCoeff + carry;
    const digitOut = Number(((t % b) + b) % b); // ensure non-negative
    const outgoingCarry = t / b; // BigInt division truncates toward zero

    digitsLE.push(digitOut);

    if (shouldCollectTrace) {
      carryTrace.push({
        position: k,
        rawCoefficient: rawCoeff,
        incomingCarry: carry,
        digitOut,
        outgoingCarry
      });
    }

    carry = outgoingCarry;
  }

  // Append remaining carry digits
  while (carry > 0n) {
    const digitOut = Number(carry % b);
    const outgoingCarry = carry / b;

    digitsLE.push(digitOut);

    if (shouldCollectTrace) {
      carryTrace.push({
        position: digitsLE.length - 1,
        rawCoefficient: 0n,
        incomingCarry: carry,
        digitOut,
        outgoingCarry
      });
    }

    carry = outgoingCarry;
  }

  return {
    digitsLE,
    carryTrace: shouldCollectTrace ? carryTrace : [],
    carryTraceOmitted: !shouldCollectTrace,
    carryTraceOmissionReason: shouldCollectTrace
      ? null
      : `Carry trace omitted: estimated size ${estimatedTraceSize} bytes exceeds 5 MB threshold`
  };
}
