---
cursor:
  subagentId: "bc-150e567c-6652-5d27-9a27-b9a4e1254c45"
lane: coordinator
kind: handoff
from: renderer (bc-150e567c)
created: 2026-09-25T22:15Z
---

# Route (a) config is merge-ready (PR #38, branch cursor/route-a-config-4c45 @ 6e833e1a). Merging alone does NOT fill art:4b52879f's cell: the record as registered still fails F and M. Decision or re-registration needed before 00:15Z.

**Merge-ready.** [PR #38](https://github.com/danielreuter/verity/pull/38) is based on main `1fdcc268` and is still current with it.
- **Adds route (a) to the drill-down:** a variant that recognises it by the backend name, which names route (a) or both Flock and the sigma link.
- **Adds the Table 1 configuration** `A-GKR route (a): prime + Flock rows + sigma link`: FULL, `frame-v3/blake3-row`, SHA-256, keyed BLAKE3 and SHA-512, NON_ZK_PROOF, 2^-130.19, live coins, decision 57.
- **Payload envelopes:** the spec views now read a result registered with its envelope as payload (art:4b52879f is registered that way; before, the views never saw it). The legacy rules still read meta only.
- **Checks:** the bench suite passes (288), `--parity` is ok (15/15), and the spec render has 15 cells, the same as main.
- **Tests:** route (a) fills the A-GKR column; plain A-GKR GPU still reads "weaker statement".

**What the render will say after merge** (store refreshed at about 22:05Z): the A100 · BF16 · keyed-BLAKE3 A-GKR cell stays `—`, now with "no admissible result; first reasons R×32, U×3, F×2". art:4b52879f is recognised as route (a) and rejected with:
- **F:** no proof dump named. Its manifest refs are `gates` and `supersedes` only; there is no `run_files` or `proof` ref and no producing attempt.
- **M:** "protocol not recorded". The envelope has `sessions: 5` and `warmup: 1`, but:
  - no `protocol` block with a contention verdict;
  - no `sweep` block with `plateau: true` (a single 4,096 point);
  - no `commit.seconds`.

**To fill the cell, re-register with a `cell.py rederive` that adds:**
1. `refs.run_files` (or `refs.proof`): the preserved dump of prover run r20260925-201056-1018 (its run-files artifact), with a remote replica.
2. `protocol: {"warm": true, "runs": 5, "statistic": "median", "contended": false}`. `contended` needs the timing guard's verdict for those sessions; I can't infer it.
3. `sweep: {"id": …, "point": …, "plateau": true}`. **Decision needed:** 4,096 is the only point, and the plateau rule (a cell is the maximal-batching plateau) says a single point isn't a plateau. Either sweep, or rule that a single point may be published as provisional.
4. `commit.seconds`. **Decision needed:** the record has `commit.serving_seconds` = 38.97 s (CPU reference committer, outside `t.total`). The spec's P counts commitment, which makes the cell about 55.6 s (12.59 + 4.076 + 38.97), not the ~16.67 s the brief expects (t.total + 4,076 × 1 ms). A GPU committer's time would be the fair `commit.seconds`.

The interaction check is not the blocker. Since bf024564 it uses the run's measured RTT, and this record passes it (−3%).
