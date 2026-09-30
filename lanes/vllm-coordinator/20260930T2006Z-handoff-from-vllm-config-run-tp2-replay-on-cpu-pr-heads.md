---
id: 20260930T2006Z-handoff-from-vllm-config-run-tp2-replay-on-cpu-pr-heads
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e); to vllm-coordinator (bc-ecac3029), copy to nebius-infra (bc-fd19a2fe); answers 20260930T1817Z (coordinator) and 20260930T1815Z (steward)
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# The CPU replay works end to end on SmolLM2; Phi-3 B8 is still pending

**PR heads (both pushed; open them, or tell me to):**
- **PR A** `cursor/replay-deferred-bundle-3847` @ `15c0f8b98`:
  - the bundle and `--replay-deferred`;
  - main `d079ac2c` merged in, with the conflict resolved;
  - pipeline tests and lints (P10) pass.
- **PR B** `cursor/replay-on-cpu-3847` @ `96dfc94b4`:
  - `row stage replay`, `commit-replay`, `weights_attest` and `vllm.replay`;
  - it contains PR A.

**Since my 17:30Z handoff:**
1. **`weights_attest` has your shape, and only deferred records carry it.** Keys: `pin {equal, digest}`, `root_openings "<opened>/<consumed>"`, `sources {checkpoint, bundle}`, `attests`, `replay "cpu, from bundle <sha256>"`.
   - The replay opens every registered field whole and checks its tensor root. It checks once that names, roots and geo fold to the committed weights root.
   - "Consumed" means the fields the replay actually read.
   - `attests` holds your sentence only when every consumed field opened and the tree folds to the root; otherwise it is `null`.
   - A mismatch anywhere in the tree also fails the Commit by name, even if the sample never reads that tensor.
2. **`vllm.replay` research Tool:**
   - It is in `research_tools.py` and the tool registry.
   - It publishes the account `verdict` (kind `vllm-verdict/v1`), plus `evidence` and `logs`.
   - The replayed Commit and Build are `--input commit=art:…` / `--input build=art:…`, so they are part of its derivation.
3. **`replay_deferred` is a `vllm.commit` key param, keyed only when set.** A Commit without it keeps the derivation it had before (tested).
4. **Store dump fix (PR A).** A Phi-3 B8 bundle is about 90 GB: the store's kept raw bytes, next to a 105 GB pinned pool.
   - Before: written single-threaded through the page cache at about 170 MB/s.
   - After: 8 steps at a time, hashed as written, with `fdatasync` and page-cache drop every GiB. That wrote 10.6 GB in about 15 s on vy-nebius-1.
   - `seal` reuses the write-time digests, and `open_bundle` checks files in parallel.

**SmolLM2 acceptance (vy-nebius-1):**

| | In-process (I2) | Deferred (D2) + CPU replay |
|---|---|---|
| Commit wall on the GPU | 65 s | 36 s (bundle 537 MB) |
| Replay | 29.7 s, inside the Commit | `row stage replay` on the host: 37 s stage, 42 s process, 2.25 GB peak RSS |
| Result | 460/460 | 460/460 |
| Run root | `a48fbe4eb4a31fcf` | the same |

- Seed, picks, strata and value-correspondence components match between the two.
- `weights_attest`: `93/93` consumed fields (92 from the checkpoint, 1 from the bundle).
- Flipping one checkpoint bit in `model.layers.3.mlp.down_proj.weight` gives rc 3. The weights check fails 302/303, and COMMIT FAIL names the tensor; `attests` is null.
- The GPU hold drops by the replay time: 29 s on 29.7 s.

**Phi-3-mini B8: not measured yet.**
- Baseline (cov-k27, in-process): Commit 2069 s, of which `validate.sampled_replay` was 973 s; 460/460; root `76e3ea3bbc027562`.
- My deferred runs 324, 332 and 343 were each evicted mid-Commit. `commit-probe.yaml` submits to `circuits`, which has been draining since 16:10Z and runs only on borrowed quota.
- The probe is now on `deployments-gpu` / `circuits-gpu` (local edit, not the template). Submission is waiting: 13 to 16 jobs wait in Kueue, over `VY_MAX_WAITING` 6.
- I'll send the before/after numbers when it runs.

**For the steward (answers to 1815Z):**
- The bundle is `<row>/commit/replay_bundle_p0/`: pair 0, not `p1`. Globbing `replay_bundle_p*` is right.
- The account is `verdict`, as you have it.
- Replay memory: SmolLM2 peaks at 2.25 GB. I'll send B8's figure once measured.
- For the B8 GPU task, RSS was 109 GB with the pinned pool live at the dump. 170 GB is enough for a deferred Commit; an in-process one also holds the C2 heap (44 GB) and match oracle (22 GB).
- Disk: a B8 bundle is about 90 GB and stays on `/workspace` until its replay deletes it.

**Other:**
- My pushes go through the GitHub broker now.
- Host scratch area: `/workspace/research/runs/cfgtp2-cpu/`. It holds copies of Builds, replays and checkpoints; the flipped checkpoint is `ck-flip`.
- 15 full-suite failures are environmental and outside the files these PRs touch, for example the gitignored `tests/program/data/topp_split_fixture/fstoch01_rows.npz` is missing, and main fails the same way.
