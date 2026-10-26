"""Local SDK artifact integrity gate; not a proof of SDK correctness or certification."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


class GateError(ValueError):
    """A generated artifact set failed validation."""


def verify_artifacts(root: Path, manifest: Path) -> int:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise GateError("artifact root is not a directory")
    document = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or set(document) != {"files"}:
        raise GateError("manifest must contain only a files array")
    entries = document["files"]
    if not isinstance(entries, list) or not entries:
        raise GateError("files must be a nonempty array")

    declared = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise GateError("each entry requires path and sha256")
        rel, expected = entry["path"], entry["sha256"]
        if not isinstance(rel, str) or not rel or "\\" in rel or ":" in rel:
            raise GateError("invalid relative path")
        parts = rel.split("/")
        if any(part in ("", ".", "..") for part in parts) or rel.startswith("/"):
            raise GateError("unsafe relative path")
        if rel in declared:
            raise GateError("duplicate manifest path")
        declared.add(rel)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise GateError("invalid SHA-256 digest")
        candidate = root.joinpath(*parts)
        if any(p.is_symlink() for p in [candidate, *candidate.parents] if p != root):
            raise GateError("symlinked artifact or parent is not allowed")
        if not candidate.is_file() or not candidate.resolve().is_relative_to(root):
            raise GateError("missing or escaped artifact")
        digest = hashlib.sha256()
        with candidate.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != expected:
            raise GateError("artifact SHA-256 mismatch")

    actual = set()
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise GateError("symlinks are not allowed in artifact root")
        if candidate.is_file():
            actual.add(candidate.relative_to(root).as_posix())
    if actual != declared:
        raise GateError("manifest does not enumerate exactly the artifact files")
    return len(declared)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a local SDK artifact file manifest")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    try:
        count = verify_artifacts(args.root, args.manifest)
    except (OSError, ValueError) as exc:
        print(f"artifact verification FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"local artifact integrity verified for {count} file(s); SDK correctness not assessed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
