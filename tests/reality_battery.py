"""Additional source-coupled failure cases for the local SDK artifact gate."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sdk_contract_gate import GateError, verify_artifacts


class ManifestFailureTests(unittest.TestCase):
    def test_malformed_json_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "out"
            root.mkdir()
            manifest = Path(d) / "manifest.json"
            manifest.write_text("{", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                verify_artifacts(root, manifest)

    def test_unknown_manifest_fields_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "out"
            root.mkdir()
            manifest = Path(d) / "manifest.json"
            manifest.write_text('{"files":[],"certified":true}', encoding="utf-8")
            with self.assertRaisesRegex(GateError, "only a files array"):
                verify_artifacts(root, manifest)

    def test_backslash_path_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "out"
            root.mkdir()
            manifest = Path(d) / "manifest.json"
            manifest.write_text(json.dumps({"files":[{"path":"..\\escape","sha256":"0"*64}]}), encoding="utf-8")
            with self.assertRaisesRegex(GateError, "invalid relative path"):
                verify_artifacts(root, manifest)
