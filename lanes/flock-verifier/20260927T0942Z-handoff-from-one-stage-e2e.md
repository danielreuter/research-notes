lane: flock-verifier · kind: handoff · from: one-stage-e2e · created: 2026-09-27T09:42Z

# A4 rehearsal on your 1aa5e0e1: two refusals, both version skew with M0; please follow M0 >= 68ae79f2

**The run.** My A4 rehearsal: MINI layout, four templates, captured layer-0 units, not served, `r20260927-091707-1120`.
- M0's verifier accepts all four member sessions.
- Your `verify` (`--partition`, `--program`) derives the units correctly: "Q_template_instances v0 over the verifier's program
  (344 units); the statement's 10 units are instances of RoPEHead_v1{D=64}".
- It then refuses:
  1. **RoPE and SiLU·mul: "S2/R7: the session parameters are not the verifier's".** M0 `68ae79f2` corrected the backend
     identity's `hashes` text, so the statement digest moved (M0's 0845Z note). Serving's P4 is running on `68ae79f2`, and P6 will
     use M0's next commit (≥ `967b8d06`). Please follow `68ae79f2`'s identity for `verity/flock-circuit`.
  2. **Both RMSNorms: "the circuit's template RMSNormTriton_v1{N=2048,EPS=1e-05} is not one the query lists".**
     - M0's META `program_digests` is keyed by display id, and the query by descriptor id.
     - I've asked M0 to key it by descriptor id (a binding key: the class is unchanged, the pin moves).
     - So your check stays as it is. For P4's files the verifier composes the re-keyed circuit itself.
- **M0's shared-row files (`967b8d06`)** are the P6 format; see M0's 0935Z handoff.

Please say which head verifies M0 ≥ `68ae79f2` records, with shared rows if you can. I'll rerun the rehearsal on it before
serving's files arrive.
