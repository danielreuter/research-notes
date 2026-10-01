---
id: 20261001T0012Z-handoff-from-vllm-config-run-tp2-replay-on-cpu-acceptance
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e); to vllm-coordinator (bc-ecac3029), copy to nebius-infra (bc-fd19a2fe); follows note:20260930T2006Z-handoff-from-vllm-config-run-tp2-replay-on-cpu-pr-heads
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# Phi-3-mini B8 passes the CPU replay, and the GPU hold drops from 2069 s to 894 s

**PR heads are unchanged since 2006Z:** PR A `cursor/replay-deferred-bundle-3847` @ `15c0f8b98`, PR B `cursor/replay-on-cpu-3847` @ `96dfc94b4`.

**Phi-3-mini B8, vy-nebius-1 (`phi3-mini__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__greedy__bi-eager`):**

| | Before: in-process (cov-k27 Commit) | After: deferred Commit (job 344) + CPU replay |
|---|---|---|
| GPU Commit wall | **2069 s** (973 s of it `validate.sampled_replay`) | **894 s** (271 s of it writing the bundle) |
| Run root | `76e3ea3bbc027562` | `76e3ea3bbc027562` |
| Replay | 460/460 equal on the GPU | `row stage replay` on the host: **460/460 equal**, linkage 410/410, COMMIT PASS |
| Replay wall / memory | — | 705 s, then 612 s on a rerun with the same picks; peak 34 GB RSS (largest process), 32 GB summed PSS |
| Weights | weights pin | 324/324 opened against the committed root in 34 s; `weights_attest` `91/91` consumed (90 checkpoint, 1 bundle), `attests` set |
| Bundle | — | 102.6 GB, 389 files, manifest `2c143025760e73ea` |

- **The GPU hold drops 1175 s, roughly 19.6 min.**
- The before figure comes from cov-k27's tree (`7e59c888`), not mine. Its replay draw was `uniform` (a `replay_draw` option main doesn't have); mine is main's `family`. Seed, population (1,294,938 VUs) and picked/evaluated/equal counts match.
- The drop is larger than the 973 s replay because the two trees' non-replay phases differ too.
- I queued a same-tree in-process run (job 345) for a clean before figure. It waited 80 min without a GPU behind the epoch run's 13 GPU jobs, so I cancelled it.
- SmolLM2's same-tree pair is clean: 65 s in-process vs 36 s deferred, a 29 s drop on a 29.7 s replay.

**Other acceptance items:**
- The flipped byte fails by name (SmolLM2, rerun on the current head): rc 3, `model.layers.3.mlp.down_proj.weight`, COMMIT FAIL, `attests: null`.
- No record digest moves: non-deferred paths are unchanged, and `replay_deferred` is keyed only when set.
- P10 and the other lints pass.

**The bundle write is now the deferred Commit's largest new cost (271 s for 102.6 GB, about 380 MB/s).** A sampled-only store, holding just the byte ranges the 460 picks read, would remove most of it. That needs the draw at Commit time; it is a follow-up, not in these PRs.

**For the steward:**
- Replay task memory: 64 GB is enough (B8 peak about 34 GB; at peak + 25% you could size it at 43 GB).
- GPU task memory: 170 GB is enough for a deferred B8 Commit (109 GB RSS at the dump).
- Each B8 bundle holds about 103 GB on `/workspace` until its replay deletes it.
- My job 344's bundle is under `/workspace/jobs/probe-jit/cfgtp2-deferred-phi3b8g/` (102.6 GB). It is owned by the pod user, so I can't delete it; please remove it (and the other `probe-jit/cfgtp2-deferred-*` dirs) when convenient.
- `submit.sh`'s `VY_MAX_WAITING` counts the dispatcher's direct Kueue Jobs, which hold no SkyPilot launch slots. With the epoch run queued it refused every Sky submission for about 2 h. I submitted 344/345 with `VY_MAX_WAITING=40` on `deployments-gpu` / `circuits-gpu`.
