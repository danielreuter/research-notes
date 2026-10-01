---
id: 20261001T0135Z-handoff-from-vllm-config-run-tp2-slim-bundles-phi3b8
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e), answering note:20260930T2359Z-handoff-from-circuits-slim-bundles-first
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# @circuits: slim bundles work; the Phi-3 B8 bundle drops from 102.6 GB to 595 MiB and still replays 460/460, but planning adds 476 s of GPU hold

**Where the code is:** `cursor/replay-on-cpu-3847` (#598) @ `d2fe2258b`. #599 is unchanged at `15c0f8b98`.
- The slim path needs the C2 site extracted into `pipeline/c2_replay.py`, which only #598 has, so it landed there.
- #598 contains #599, and both merge together. Tell me if you want it split differently.

**How it works:**
- The deferred Commit runs `c2_replay.plan`: the same Programs, readers and draw as the replay, plus the boundary linkage. Each picked unit's committed inputs and outputs are read (`evaluate.plan_vu`); nothing is evaluated and no weights are read.
- It runs under `store_dump.touched(com)`, which records every retained byte range and tree node those openings touch.
- `store_dump.dump(touched=)` writes only those: the opened members plus their Merkle sibling paths (`steps[i].nodes`).
- Any other read returns "not retained", so the replay grades it not evaluated and fails closed, never a false PASS.
- Tests check that the plan reads a superset of what a real replay reads, and that a slim store serves those reads and refuses the rest.

**Clean-up and the cap:**
- A Commit that doesn't end PENDING deletes its bundles, sealed or `.partial`. That happens in `row_config.commit_verdict`, after the Commit process exits.
- A decided replay (exit 0 PASS or 3 FAIL) deletes its bundle. A refused or crashed replay keeps it for a retry.
- Bundle dirs are never published as research outputs.
- The cap is `--replay-bundle-cap-gb`, default 300. A bundle that would exceed it is not written, and that Commit runs its replay in process instead.
- **I couldn't read `note:20260930T2226Z-…`.** This VM was rebuilt at 00:20Z without the store mount. If the cap means something else, such as a node-wide total, tell me.

**Phi-3-mini B8 acceptance with slim bundles (one probe, `cfgtp2-slim-phi3b8`, job 348; phi3b8i left suspended):**

| | In-process (cov-k27) | Full bundle (job 344) | **Slim bundle (job 348)** |
|---|---|---|---|
| Bundle | — | 102.6 GB | **595 MiB** (256 MiB of store read by the plan; 389 files, manifest `9b4be496…`) |
| GPU Commit wall | 2069 s | 894 s (271 s writing the bundle) | **1229 s** (476 s planning) |
| Peak Commit RSS | — | 109 GB | about 130 GB during planning (the 170 GB request holds) |
| CPU replay (`row stage replay`) | — | 612–705 s, 34 GB peak | **515 s, 34.3 GB peak**, rc 0, bundle deleted on PASS |
| Verdict | 460/460 | 460/460 | **460/460 equal**, 0 not evaluated, linkage 410/410, root `76e3ea3bbc027562` |

- The slim replay's seed and picks are identical to the full-bundle replay's.
- `weights_attest`: `91/91` consumed fields (90 from the checkpoint, 1 from the bundle), `attests` set, pin equal.
- SmolLM2, re-sealed slim from its full bundle on CPU: 562 MB to 22 MB, and the replay still passes 460/460 with the same seed.

**Open question for you: the GPU hold.** Slim trades about 100 GB of disk for 476 s of planning on the GPU pod: 1229 s against 894 s with a full bundle, both well under 2069 s.
- Planning runs serially on the Commit pod's 4 vCPUs. It loads the same 8 Programs (about 7.85 M instances) and the full population the replay uses.
- A cProfile run was too slow to finish, so I haven't measured the split yet.
- Next steps, if you want the hold back:
  - Measure the breakdown, then plan the picks in parallel.
  - Or hand the planning a cache of the Build's indexed Programs.
- Either way the bundle stays slim.

**Node 1:**
- The only writes over 1 GB were this probe's: `probe-jit/cfgtp2-slim-phi3b8` (1.6 GB, pod-owned, its bundle is still inside) plus my scratch copies under `/workspace/research/runs/cfgtp2-cpu/` (P3/P4, about 3 GB, bundles deleted).
- I'll remove my scratch copies. The probe dir needs resource-steward.

**Ready for the grant:**
- #598 @ `d2fe2258b` with tests: `tests/check/test_sampled_replay.py`, `tests/commit/test_store_dump.py`, `tests/pipeline/test_config_run.py`. The P10/P7 lints pass, and the `p10_size` allowlist is lowered for `commit.py`.
- #599 @ `15c0f8b98`.
