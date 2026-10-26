# Genpack Gate — Verified Scope and Architecture Roadmap

Canonical system ID: **QMOOSA-0880**. Component role: **TESTS**.

## Current implementation

A Python local SDK artifact integrity verifier (`sdk_contract_gate.py`) checks manifest enumeration, relative-path safety, SHA-256 content integrity, symlink rejection, and unexpected files. The regression suite runs positive and adversarial tests against that implementation. Rust remains an informational scaffold.

## Planned, not implemented or certified

SDK generator engine integration, generated API semantics, package signing, reproducible provenance, cross-chain RPC, x402 settlement, Conway automation, PQC/FIPS cryptography, autonomous AI agents, and tokenomics are **not verified** by this component.

## Acceptance gates

1. Real generator output is exercised end-to-end by this gate and semantic SDK tests.
2. Supply-chain provenance and signature verification are implemented and independently reviewed.
3. CI passes at the relevant current commit, including negative tests and CodeQL.
4. Security review approves the exact shipped implementation.

No mainnet/testnet deployment, gas/cycles spending, or cryptographic certification is authorized by these checks.
