fn main() {
    println!("Genpack Gate: local SDK artifact integrity verifier");
    println!("Run: python sdk_contract_gate.py --root ARTIFACT_DIR --manifest MANIFEST.json");
    println!("Scope: file enumeration, path safety, SHA-256 integrity only.");
    println!("Not an SDK correctness check, cryptographic certification, or production approval.");
}
