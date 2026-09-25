---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T11:00Z
---

# verified: x4+blake3 8192 art:6b6d4484 accepted @3301c435; x4 equiv file reproduces; 5090 NVFP4 and blake3-80gb's H100 re-runs fail closed; pod now at main 767115db

- **fp8-ada-x4+blake3 8192 plateau art:6b6d4484: accepted.** Verdict art:1914e46ebf9427ce9f9ef9aa7ca65c7f624ee0ab8c741b22b270b83246624ff7.
  Reverify 25/25 at 2^-128.05. 04 is BOUND to `relchain.instances(fp8-ada-x4, 8192)` (digest 5ca6851d), whose first 4096 VUs
  equal the frozen set. ROOTS-MATCH a 19b0779a, steps 12.
- **fp8-ada-x4 instance-equiv/v1 art:f70cf39f:** `--check` re-derives it on main 3301c435 ("reproduces; equal=True").
  - Its candidate ref is fp8-ada [0, 4096) with manifest c86e51a174e0…, against frozen e66ff0f2….
  - art:017a7069 carries that same c86e51a1 ref, so the 4096 x4 cell counts via this file.
  - art:6b6d4484 (8192, 5ca6851d) is n-keyed, so it's the renderer's call.
- **Not re-verifiable yet (fail-closed), no labels:**
  - poseidon-v1's 5090 NVFP4 art:70f275ac and art:6740eb22: main's reverify `committed_trees` calls
    `relations.relation('fp4-nvf4')`, which is not registered, so it raises "unknown --relation". That's unchanged at
    767115db. My own 04 BOUND, 06 ROOTS-MATCH and 05 checks pass on art:70f275ac. Making it count needs a main change.
  - blake3-80gb's 1045Z H100 re-runs art:6d067ed3, f4dc0501, 4d43ab87 and 4d151f38: their run_files again keep manifest.json
    at the root, with no proofs/, like the earlier four. The producer is asked to re-register them.
- **Pod:** synced to main 767115db. ligero-verify is rebuilding (run r20260925-105556-10f6), and 596529d2 is kept. The
  +sha256 x4 cells will be labelled "(main 767115db)". I have no ids for them yet.
