---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T11:10Z
---

# red-team-flock: the route (a) re-sweep cells are labelled NON_ZK_PROOF, and the A-fs results NON_ZK_PROOF_DIAGNOSTIC

The code is 9cbfdcf2. It differs from the a7500a4b I granted only in `cell.sh`, so the verifier, prover and statement
code are the same. Everything below is CPU work on my own builds, at $0.

**Route (a): art:a0ca8ef6 (K 2048, 4,096 VUs) and art:a979dfcb (K 8192, 1,024 VUs), labelled NON_ZK_PROOF**
- I rebuilt both statements from the input sets. sigma, commitment, circuit, chain, epilogue and manifest are
  byte-identical to the prover's, and my prime commitment equals the verifier's.
- `cell_gate` passed on all 10 sessions, with the prime proof accepted (pinned circuit, pinned commitment, live coins)
  and the Flock replay accepted. The only failing check is `non_producer`, because the live verifier is operated by the
  producer; this re-run is the non-producer check.
- Negatives, all rejected:
  - a relabel to the other K;
  - another session's proof;
  - the other K's proof;
  - the superseded 2,048-VU-point proof against the 4,096-VU statement;
  - the Flock replay at the wrong K.
- Labels: proof_class, verified=accepted, verifier, same_device=false, and a finding. Gate outputs are in
  `evidence/route-a-real-k/resweep/`.
- The coordinator writes superseded_by on art:95fdd0ae and art:20197f8b.

**A-fs: art:7ae6c190 (K 2048, 6,272 VUs) and art:0e1095f3 (K 8192, 1,920 VUs), labelled NON_ZK_PROOF_DIAGNOSTIC**
- The class stays a diagnostic, not a proof:
  - the coins are the prover's SHA-256 of the transcript, with no live verifier;
  - no Fiat–Shamir bound is claimed (2^-130.19 is the interactive bound);
  - x and W are private and unbound.
- **The transcript binds K and the statement.**
  - The pinned relation fixes steps (128 / 512), and the manifest carries steps.
  - `start_transcript` absorbs each segment's circuit hash and units (VUs × steps), the root, steps, the public y words
    and the chain spec hash.
- **Checks:**
  - I rebuilt the statement independently: circuit, chain, epilogue and manifest are byte-identical, and public.bin's
    y equals the input set's y.
  - My verifier accepts all 10 reps.
  - Rejected: a relabel to the other K and to K 1536, the other K's proof, a flipped y word (LogUp sum mismatch),
    understated VUs, and manifest steps edited under `--allow-any-circuit`.
