#!/usr/bin/env python3
import hashlib
import pathlib
import sys


def fail(msg: str) -> None:
    print(f"[verify-hashes] FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest_line(line: str) -> tuple[str, str]:
    line = line.strip()
    if not line or line.startswith("#"):
        return "", ""
    parts = line.split(None, 1)
    if len(parts) != 2:
        fail(f"Malformed manifest line: {line}")
    expected_hash, rel_path = parts
    rel_path = rel_path.strip()
    if rel_path.startswith("*"):
        rel_path = rel_path[1:]
    return expected_hash, rel_path


def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    manifest_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "artifacts/SHA256SUMS"

    if not manifest_path.is_file():
        fail(f"Manifest not found: {manifest_path}")

    checked = 0
    with manifest_path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            expected_hash, rel_path = parse_manifest_line(raw_line)
            if not expected_hash:
                continue

            file_path = repo_root / rel_path
            if not file_path.is_file():
                fail(f"Missing file listed in manifest: {rel_path}")

            actual_hash = sha256_file(file_path)
            if actual_hash.lower() != expected_hash.lower():
                fail(
                    "Hash mismatch for "
                    f"{rel_path}: expected {expected_hash.lower()} got {actual_hash.lower()}"
                )
            checked += 1

    if checked == 0:
        fail("Manifest contained no file entries")

    print(f"[verify-hashes] PASS: validated {checked} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
