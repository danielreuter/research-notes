---
id: 20261001T1502Z-handoff-from-proofs-checkable-rows-core-first-verifiers-wait
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Checkable rows: prototype core's side first; Rust and Lean wait for Daniel

to: proofs-flock-fp. Re note:proofs-flock-fp/20261001T1459Z-handoff-from-red-team-proofs-554-core-checkable-rows-requirements.

Red-team's design review shows the rows need new core protocol:
- SHA-512 row schemas for NVFP4, MXFP4 and FP8;
- `frame-v3-sha512` admitting element rows;
- a hiding-leaf schema per row kind.

They also need changes to the Flock verifier of record, in Rust and Lean. New core protocol is Daniel's to agree. I've put it
on his morning list, recommending yes and mirroring §4a. So the scope tonight, still CPU-only on your own branch with no PR, is:

1. **Core's side first, as red-team asks:**
   - in `verity.commitments.rowleaf`, the prefix, the layout and the digest from codes and scales with range checks;
   - the §6 text beside §4a, with conformance vectors and a core test;
   - the coincidence enumeration test across the new, default and packed frames.
2. **Flock's stager uses core's function** for the prefixes, behind a new switch. With the switch unset, the default and
   packed frames stay byte-identical, and the per-cell CPU stage-only table gives digests for default, packed and new.
3. **Not tonight:** edits to `circuit.rs`, `Flock.HmRow` or any `lean-audit.json` record. Instead, write down what each
   would change, so red-team can review it with the rest.

The item-1 profile is unaffected: one GPU job on node 1, under the cap. Send your review request to
`lanes/red-team-proofs-554/` when 1 and 2 are pushed.
