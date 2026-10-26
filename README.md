# Genpack Gate — SDK Artifact Integrity Checks

This repository is the **tests** component of QMOOSA-0880 (SDK generator family).
It currently implements a **local file-integrity gate**, not a full SDK generator, blockchain relayer, x402 settlement system, PQC verifier, or production-ready service.

## What is implemented

`sdk_contract_gate.py` validates a JSON manifest of generated SDK artifacts. Each entry has a relative POSIX `path` and lowercase SHA-256 `sha256`. The gate rejects path traversal, absolute paths, symlinks, duplicate paths, invalid hashes, missing files, unlisted files, and modified contents. It does **not** validate generated SDK API semantics, provenance of the generator, signature authenticity, or supply-chain trust.

Example manifest:

```json
{"files":[{"path":"client.ts","sha256":"<64 lowercase hex characters>"}]}
```

Run on a real artifact directory and manifest:

```bash
python sdk_contract_gate.py --root path/to/artifacts --manifest path/to/manifest.json
python tests/reality_check_harness.py
python -m compileall -q sdk_contract_gate.py tests
cargo test
```

The test suite creates temporary local artifacts and runs positive and adversarial cases against the real gate. It does not connect to any RPC, spend funds, or deploy. GitHub Actions runs these tests and Python CodeQL analysis. A passing workflow establishes only the checked scope at that commit.

## Unresolved blockers

- No independently verified SDK-generation engine integration or semantic contract tests.
- No signed build provenance or trusted artifact origin attestation.
- No independent security audit, FIPS certification, production deployment, or readiness approval.
- Rust binary is an informational scaffold, not an SDK generator.

The original `100/100`, connected-RPC, and FIPS claims were unsupported and are not acceptance evidence.
