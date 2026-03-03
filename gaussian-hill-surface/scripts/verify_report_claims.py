#!/usr/bin/env python3
import csv
import math
import pathlib
import sys

TOLERANCE = 1e-6


def fail(msg: str) -> None:
    print(f"[verify-claims] FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "").strip()
    if value == "":
        fail(f"Missing value for column '{key}' in row: {row}")
    try:
        return float(value)
    except ValueError as exc:
        fail(f"Invalid float for column '{key}': {value} ({exc})")


def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    csv_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "artifacts/results/phasewall_vs_vanilla_claims.csv"

    if not csv_path.is_file():
        fail(f"Claims CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        required = {
            "function",
            "dimension",
            "vanilla_median",
            "phasewall_median",
            "improvement_factor",
            "ratio_vs_vanilla",
            "p_value",
        }
        if reader.fieldnames is None:
            fail("CSV has no header")
        missing = required.difference(reader.fieldnames)
        if missing:
            fail(f"Missing required columns: {sorted(missing)}")

        total = 0
        for row in reader:
            total += 1
            vanilla = parse_float(row, "vanilla_median")
            phasewall = parse_float(row, "phasewall_median")
            improvement = parse_float(row, "improvement_factor")
            ratio = parse_float(row, "ratio_vs_vanilla")

            if vanilla == 0.0 or phasewall == 0.0:
                fail(f"Zero median not allowed for ratio math in row: {row}")

            expected_improvement = vanilla / phasewall
            expected_ratio = phasewall / vanilla

            if not math.isclose(improvement, expected_improvement, rel_tol=TOLERANCE, abs_tol=TOLERANCE):
                fail(
                    "Improvement mismatch for "
                    f"{row['function']} {row['dimension']}D: got {improvement}, expected {expected_improvement}"
                )

            if not math.isclose(ratio, expected_ratio, rel_tol=TOLERANCE, abs_tol=TOLERANCE):
                fail(
                    "Ratio mismatch for "
                    f"{row['function']} {row['dimension']}D: got {ratio}, expected {expected_ratio}"
                )

            if not math.isclose(improvement * ratio, 1.0, rel_tol=TOLERANCE, abs_tol=TOLERANCE):
                fail(
                    "Improvement/ratio reciprocal check failed for "
                    f"{row['function']} {row['dimension']}D"
                )

    if total == 0:
        fail("No data rows found")

    print(f"[verify-claims] PASS: validated {total} claim rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
