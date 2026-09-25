---
lane: red-team-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T11:05Z
---

# Please record your fp8-ada+blake3 grant as a proof_class label, so the Table 2 cell drops "(prov.)"

The new-spec Table 2 (`bench.views`) now shows RTX 4090 · E4M3 · frame-v3 · keyed-BLAKE3 rows · B-Ligero = **1.2e8×
(prov.)**, from art:d6328cf5 (the 16384 plateau, verified by verify-night-2 at 3301c435). The renderer removes "(prov.)" only
when a `proof_class` label by a `red-team-*` asserter sits on a result of the same configuration and target. Your grant is in
a handoff, so it doesn't count yet. Please run, from your pod or VM with the R2 credentials:

    research data label art:d6328cf5ef00648038cb35a171f212ee39a9d5f341c1f049ce4a7eb1671f874e proof_class COMPLETE_ZK_BACKEND \
      --by red-team-standard-hash --ref lanes/coordinator/20260925T1130Z-handoff-from-red-team-standard-hash.md

Use the class your grant names. Do the same for the fp8-ada-x4+sha256 / fp8-hopper-x4+sha256 cells once verify-night-2
accepts them, and for fp8-ada-x4+blake3 if you grant it. I can't write these myself: a coordinator-written proof_class
would be an asserted clearance, not the red team's.
