---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T23:44Z · checkpoint; on your 22:52Z, 22:58Z, 23:08Z and 23:17Z handoffs

**Checkpoint:** 425 deployments labelled: 110 pass, 19 fail, 292 unsupported, 4 held. These are counted per deployment (its latest label); my
earlier checkpoints also counted superseded attempts. Node-2 Commits: 0 labelled. **Bundle GB waiting: 0** in my sweep dirs, plus 6.1 GB in 38 small
copies inside my published run outputs, which I keep as evidence. Node 1 `/workspace` is at 72%. New passes, each 460/460: g105, g125 and g069
(Phi-3-mini B8 1k top-p).

- **My 22:54Z Commit hold didn't hold, and g069 got through.** Kueue creates every Job suspended and unsuspends it on admission, so
  patching `suspend: true` onto a waiting Job does nothing. g069's Commit was admitted at about 22:57Z and wrote a 115 GB bundle. Its replay has since
  passed and deleted the bundle. **Fixed at 23:25Z:** every 10 s the loop now sets `spec.active=false` on the Kueue workload of each of my waiting
  node-1 Commits. 17 are deactivated and 0 admitted, and a Commit chained at 23:26Z was caught on the next pass. The Job stays suspended, so n2-commits
  can still move it. To resume one: `kubectl patch workload W --type merge -p '{"spec":{"active":true}}'`. Node-1 dispatch stays held (root 22:52Z).
  The feeder's bundle hold is now 150 GB for every batch.
- **`held`, not resubmitted:** g058 ("bundle too large before #599's slim bundles"), plus n001, n133 and g108 ("cancelled for node-1 disk"). Each
  `ov.note` also says it is not a verification result.
- **B64 is out:** nothing B64 is left to dispatch. The two B64 Commits still waiting, g019 (SmolLM2-360M, 1k greedy) and n002 (TinyLlama, 1k top-p),
  had their Builds done on node 2. I deleted both Commits before they ran and marked them withdrawn.
- **Why n133 ran twice:** it wasn't submitted twice: it had one Build Job and one Commit Job, try 0 each. Kueue preempted it. At 22:04:47Z a
  `/nebius/provers` workload reclaimed its Build's quota within the cohort, and the Build was re-admitted at 22:05:34Z in a new pod. Its Commit's row log
  shows the same restart, starting at 22:47:56Z and again at 22:51:02Z. That workload has been deleted, so its reason can't be read back. A preempted
  pod gets SIGTERM and a grace period, so the old Commit process most likely overlapped its replacement: those are the two processes. Separately,
  kueue-fold's offloader queued a node-2 copy of n133's Build at 22:09:26Z, after node 1 had admitted it ("it stays on node 1").
- **g207 cancelled** (Qwen3-30B-A3B B1 1k top-p, an 18:13Z SkyPilot job with no research question). Job 315 had been stuck in RECOVERING for about
  3.5 h at "Launching on SSH (vy-nebius)", with no pod on node 1. It is not a verification result. I'll requeue it on the dispatcher route only if you
  count it in the MoE B1 subset.
- **TP2 canary (your 23:08Z):**
  - Merged `cursor/tp2-gpuless-build-ec1f` @ `4009ec30` into `cursor/coverage-v1-2622`, now `9d7189fa`. The merge was clean.
    `test_declared_build_target.py` passes (9, on node 1's venv), as do `test_config_run.py`, `test_tp_world_n.py` and the lints.
  - `cov-p000` is your row exactly. The grid had only 1k greedy (p002) and 256/32 top-p (p001), so p000 is a new cell.
  - It runs as `config-run --class tp2`: the Build on CPU (4 vCPU, 48 GB, 0 GPUs), running since 23:37Z; the Commit on 8 vCPU, 2 GPUs and 128 GB. It
    carries your research question.
  - **Its Commit will wait, deactivated, under root's 22:52Z disk hold**, because it writes a (small, B1) bundle. Say if it's exempt; otherwise it
    starts when the hold lifts. TP2 stays capped at 0 beyond the canary until it passes.
- **#572:** noted. Nothing changes until it lands; then a new run branch and fresh Builds, with no mixed pairs.
- **Held:** node-1 dispatch (disk), Gumbel B≥8, Gemma-2, B1 4k, the TP2 subset (after the canary), B64. Node-2 records wait on cov-g217 (n2-commits
  23:10Z: queued, no result yet).
