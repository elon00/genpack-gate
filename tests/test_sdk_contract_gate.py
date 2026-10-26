"""Adversarial tests of the actual local artifact integrity verifier."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sdk_contract_gate import GateError, verify_artifacts

GATE = Path(__file__).resolve().parents[1] / "sdk_contract_gate.py"


class ArtifactGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "artifacts"
        self.root.mkdir()
        self.target = self.root / "client.ts"
        self.target.write_bytes(b"export const n = 1;\n")
        self.manifest = self.base / "manifest.json"
        self.entries = [{"path": "client.ts", "sha256": hashlib.sha256(self.target.read_bytes()).hexdigest()}]
        self.write_manifest()

    def write_manifest(self):
        self.manifest.write_text(json.dumps({"files": self.entries}), encoding="utf-8")

    def test_valid_artifact(self):
        self.assertEqual(verify_artifacts(self.root, self.manifest), 1)

    def test_modified_artifact_rejected(self):
        self.target.write_bytes(b"tampered")
        with self.assertRaisesRegex(GateError, "mismatch"):
            verify_artifacts(self.root, self.manifest)

    def test_missing_artifact_rejected(self):
        self.target.unlink()
        with self.assertRaisesRegex(GateError, "missing"):
            verify_artifacts(self.root, self.manifest)

    def test_unlisted_artifact_rejected(self):
        (self.root / "extra.ts").write_text("extra", encoding="utf-8")
        with self.assertRaisesRegex(GateError, "enumerate"):
            verify_artifacts(self.root, self.manifest)

    def test_parent_traversal_rejected(self):
        self.entries[0]["path"] = "../manifest.json"
        self.write_manifest()
        with self.assertRaisesRegex(GateError, "unsafe"):
            verify_artifacts(self.root, self.manifest)

    def test_absolute_path_rejected(self):
        self.entries[0]["path"] = "/tmp/client.ts"
        self.write_manifest()
        with self.assertRaisesRegex(GateError, "unsafe"):
            verify_artifacts(self.root, self.manifest)

    def test_duplicate_path_rejected(self):
        self.entries.append(dict(self.entries[0]))
        self.write_manifest()
        with self.assertRaisesRegex(GateError, "duplicate"):
            verify_artifacts(self.root, self.manifest)

    def test_invalid_digest_rejected(self):
        self.entries[0]["sha256"] = "not-a-sha"
        self.write_manifest()
        with self.assertRaisesRegex(GateError, "SHA-256"):
            verify_artifacts(self.root, self.manifest)

    def test_empty_manifest_rejected(self):
        self.entries.clear()
        self.write_manifest()
        with self.assertRaisesRegex(GateError, "nonempty"):
            verify_artifacts(self.root, self.manifest)

    def test_symlink_rejected(self):
        link = self.root / "link.ts"
        try:
            link.symlink_to(self.target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(GateError, "symlink"):
            verify_artifacts(self.root, self.manifest)

    def test_cli_success_and_failure_exit_codes(self):
        args = [sys.executable, str(GATE), "--root", str(self.root), "--manifest", str(self.manifest)]
        ok = subprocess.run(args, capture_output=True, text=True, check=False)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("SDK correctness not assessed", ok.stdout)
        self.target.write_bytes(b"tampered")
        bad = subprocess.run(args, capture_output=True, text=True, check=False)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("FAILED", bad.stderr)


if __name__ == "__main__":
    unittest.main()
