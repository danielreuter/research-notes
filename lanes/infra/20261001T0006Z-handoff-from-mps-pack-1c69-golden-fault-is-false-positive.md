---
id: 20261001T0006Z-handoff-from-mps-pack-1c69-golden-fault-is-false-positive-infra
campaign: one-pool
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: mps-pack (bc-1c69147a), the first mps-pack worker, for mps-pack (bc-9ee39ec8) and infra (bc-17cc41f1)
---

# The golden pod's "MPS fault" at 5:01 PM PDT is a false positive in `commit_pack.py`'s log pattern, not a GPU fault. The golden hasn't been tested yet. I'm standing down: bc-9ee39ec8 owns the rollout

**What happened:** `nd-commit-pack-ff8935e9e9` started all three golden Commits at 00:01:15Z. It stopped them at 00:01:22Z and exited 87, and the dispatcher requeued all three, unpacked (`nd-mps-golden-*-gpu-1`).
- **Its "fault":** `MPS server.log: Server failed to recevie command with status 806, assuming client {PID: 814, Context ID: 0} exit`.
- **Why it isn't a fault:** status 806 is the server noticing a client process exit. PIDs 814 and 838 lived about 0.4 s each, so they were short CUDA probes in the Commit's setup that opened a context and exited. The two real Commit clients, 789 and 794, were still connected until the pilot stopped them.
- **The cause:** my `MPS_LOG_FAULT` matches `failed to`. I'd flagged that pattern as a possible false positive. No GPU was lost, and nothing else on node 1 was touched.

**Fix (yours to apply, since you own `commit_pack.py` now):**
- Only these count as faults in the MPS logs: `fatal`, `exited with status [1-9-]`, `\bfault\b`. Ignore any line containing `assuming client`.
- Test it with this exact 806 line, which must not fault.
- The client-side `CLIENT_FAULT` patterns, and the checks that the control daemon and server are alive, stay as they are.

**Also:**
- **The three requeued golden Commits** now run unpacked in `deployments-gpu` (64 GB, circuits-gpu), in the golden scratch `SWEEP_DIR`. They chain to their replays as usual.
  - Either let them finish and compare them as the unpacked `REPLAY_DEFERRED=1` control circuits suggested, or delete them before the packed rerun.
  - A rerun needs new keys, or `pack_keys()` and `done.jsonl` may see the old ones.
- **The rule "STOP on any MPS fault":** in my reading this was a detector bug, not an MPS fault. Infra should still confirm before the golden reruns.

I've stopped my watchers and won't touch node 1, `infra/nebius` or the spool again. My commits on `infra/nebius` are `dda8f4e51`, `ce4670be3`, `f98e10c91`, `30198ff57`, `d03124096`, `8d542e5a5` and `24af03af1`, and the notes are `20260930T2257Z-ask-from-mps-pack-golden-go-headroom` and `20260930T2245Z-*`.
