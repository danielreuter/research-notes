---
lane: coordinator
kind: report
title: Overnight 2 morning report — two-column Table 2 (bare | in-proof Poseidon2 hash), B-Ligero on the frozen tree 64c00bd
date: 2026-09-23T12:15Z
status: open
---

CHECKPOINT 39c5ee7a (04:05Z) [open] 04:08Z launched agkr-bound (local; integration of agkr-fp8+nvf4 then operand binding; $15, FINAL 12:00Z; worktree post-wave -> agkr-bound). TABLES.md: 'Same full relation' rule recorded. Circuit red-team waits for pin PR + A-GKR merge. Parity pass 2 running.
CHECKPOINT 14fc57e1 (04:04Z) [open] 04:03Z f24+f56 already on main (baeefd21). HOLD lane/vllm-rf-f3-integrated 68e75c14 (--no-ff) until gate (b) r20260925-034304-3b78 green is confirmed
CHECKPOINT none (04:02Z) [open] 04:05Z disk hit 3.1 GiB (swap files 16->20 GB + parity re-fetched blobs); evicted 78 R2-verified blobs 1.35 GiB -> 7.4 GiB; timers armed (sweep 30 min, digest 01:00Z); parity pass 2 started
CHECKPOINT baeefd21 (03:59Z) [open] 04:02Z merged vllm-rf-f24 e818a5d4 -> 24e3b391, vllm-rf-f56 a4b823a3 -> baeefd21 (--no-ff, integrations/vllm only, lints 41/41 on merged tree); pushed; cli moved
CHECKPOINT 3d48c00 (03:58Z) [open] 04:00Z standing rule: coordinator merges every PR (Daniel-commented PRs wait); #7 #8 #9 #10 already merged
CHECKPOINT 7b724ae2 (03:56Z) [open] 04:00Z merged #7 c67542be (pod registry, off on laptop) and #10 7b724ae2 (lease/liveness/service, opt-in); 106 tests pass incl rsync; cli+steward moved
CHECKPOINT none (03:48Z) [open] 03:58Z lanes FINAL: arith, agkr-fp8, agkr-nvf4, red-team-arith, red-team-lk, verify-po (pods gone). H100 FP8 A-GKR art:ad76c106 marked provisional; red-team-lk resumed for its statement check. Backlog += arith shared-memory opt-in; A-GKR integration after switch-over.
CHECKPOINT none (03:45Z) [open] 03:52Z verify-po released 6 labels; T2 A-GKR H100 FP8 4.4e7x, 4090 1.3e7x, 5090 1.8e7x; scoreboard re-rendered 8:52 PM PT
CHECKPOINT none (03:43Z) [open] 03:47Z parity pass 1 (with #8): exit 1, PARITY FAILED 10 unexplained: 9 Sep-22 attempts differ (remote copies carry extra fields: telemetry.resources / load_end; laptop copies older) + render 43 lines (A-GKR cells: verify-po labels written locally during the run, write-through off). JSON: Project store internal/parity-20260925T0315Z.json + notes campaigns/remote-state/assets/parity/. Pass 2 not run (runbook stops).
CHECKPOINT b84f11ea (03:19Z) [open] 03:20Z merged #8 6eb30ee8, #9 ca396d13 (conflict with #11 resolved: source_transport + custody private), lane/arith b84f11ea; cli 8:19 PM PT. red-team-arith + red-team-lk PASS -> verify-po told to release held labels; 5090 A-GKR no longer provisional. agkr-fp8 x agkr-nvf4 conflict in gpu/logup.py+prover.py (+nvf4 verifier Rust) -> integration lane after switch-over. Parity pass 1 running with #8.
CHECKPOINT bbbe936c (01:31Z) [open] 01:35Z merged PR #11 (run custody on R2, behind --custody-r2) ff main -> bbbe936c, pushed; cli+steward moved; laptop tests incl. rsync (test_pods_connect) pass
CHECKPOINT ab9573fd (01:06Z) [open] 01:10Z D4 parity on laptop FAILED TO COMPLETE: 2 attempts hung in R2 socket reads (17 min, 65 min; fresh store built 476 MB, then the compare/render phase stalled re-fetching evicted blobs); no JSON; /tmp cleaned. Sweep: disk 11 GiB, lanes alive
CHECKPOINT 4bd6c54c (01:03Z) [open] 01:02Z 6 PM digest rendered (baseline render/0100Z-*); changed list reset
CHECKPOINT 4bd6c54c (01:00Z) [open] 00:59Z user declined the security-matched 2^-100 drill-down: not run
CHECKPOINT 39c5ee7a (00:49Z) [open] 00:53Z 5090 A-GKR art:49757870 marked PROVISIONAL (scoreboard + TABLES.md) pending red-team-lk; verify-po told to hold labels on rewritten-statement A-GKR results (4090 0.490s art:45c5be4a held)
CHECKPOINT 3be6a35f (00:45Z) [open] 00:52Z agkr-fp8 4090 0.490s on merged-LK statement -> verify-po; launched red-team-lk (A-GKR circuit rewrites in agkr-fp8 + agkr-nvf4 incl. T2 cell art:49757870; $5, FINAL 03:30Z; worktree fill-dc -> red-team-lk)
CHECKPOINT f7e4709 (00:44Z) [open] 00:47Z notes seeded to github.com/danielreuter/research-notes (private): scan 0 key material / 4253 blobs; pushed main f7e4709 (404 commits, pack 13.5 MiB); sync stays off (no RESEARCH_NOTES_SYNC, watch uses --snapshot not --sync)
CHECKPOINT 95343488 (00:35Z) [open] 00:37Z T2: A-GKR 5090 1.4e8x->2.5e7x (art:49757870 verified); B-Ligero A100 5.9e6x, H100 BF16 8.9e6x, H100 FP8 1.1e7x (arith, verified); scoreboard re-rendered 5:37 PM PT
CHECKPOINT e1bcf472 (00:20Z) [open] 00:22Z sweep: disk 12 GiB; agkr-fp8 (4090 0.666s), agkr-nvf4 (5090 0.1905s), verify-po, red-team-arith (H100) alive; no idle pods; parity attempt 2 still running
CHECKPOINT 5034767f (00:18Z) [open] 00:20Z merged vllm-rf-a23b 9be6e462 --no-ff -> 932a4886; D3 rule (prefer separate-host live records) 4bd6c54c on main, cli moved 5:18 PM PT; scoreboard re-rendered; arith FINAL 92dab0ad (merge after red-team-arith + verify-po; harness commits accepted); d3-h100 FINAL; parity attempt 2 running
CHECKPOINT ab9573fd (23:45Z) [open] 23:47Z merged PRs #6 aceebe8a, #2 5a84adb4, #4 50b66973, #3 d0129d02 (pushed by me 4:41-4:42 PM PT), #5 a47a45bd (conflict in notes.py usage docstring resolved); cli+steward at a47a45bd 4:44 PM PT; store.toml write_through off; D4 parity running
CHECKPOINT ab57df0a (23:11Z) [open] 23:13Z sweep: disk 9.8 GiB; lanes alive (arith 5090 port, agkr-fp8/nvf4 hill-climbing, d3-h100 US-MO-1 prover+separate verifier, verify-po); reindex +16; Table 2 unchanged since 3:57 PM PT
CHECKPOINT e8503e2d (23:05Z) [open] 23:15Z ship-mtime audit (read-only): no table cell exposed; 1 recorded inversion (Sep 22 A-GKR CPU latency, not tabled); most Rust builds unrecorded -> producer self-check binaries unprovable; scripts in evidence/ship-mtime-*.py
CHECKPOINT 58e4c1aa (22:56Z) [open] 22:56Z merged lane/sp1-128 0e8cc6ea --no-ff -> main 58e4c1aa, pushed; cli moved; steward kickstarted; scoreboard re-rendered 3:55 PM PT (SP1 stock/precompile labels, D1 whole-proof security)
CHECKPOINT 048e6a41 (22:37Z) [open] 22:38Z sweep: disk 14 GiB; all lanes alive (arith on A100 port, agkr-fp8 H100, agkr-nvf4 5090 0.529s new, verify-po, d3-h100 starting); sp1-128 resumed for labels; no idle pods
CHECKPOINT 605b1bbb (22:32Z) [open] 22:33Z A-GKR on all 5 T2 rows (H100 FP8 1.1e8x art:2e7baba7 verified verdict art:ccafc0f7); reindex --remote pulled 57; scoreboard re-rendered 3:31 PM PT
CHECKPOINT 1d9c3198 (22:29Z) [open] 22:30Z sp1-128 FINAL d1111579 (A100 raised-query 21.05s, achieved -95.46, art:e8c7c331; pod gone ~$2.10) but missed 2222Z handoff -> resumed for SP1 stock/precompile labels + whole-proof D1 wording; merge after. Verify request at verify-po.
CHECKPOINT 1d9c3198 (22:25Z) [open] 22:35Z scoreboard re-rendered: T2 A-GKR 4090 FP8 3.0e7x + 5090 NVFP4 1.4e8x (gaps filled, verified), B-Ligero 4090 2.4e6->2.2e6x; run-folder eviction 1.14 GiB (disk 13 GiB); d3-h100 bc-9be44216 launched ($4, FINAL 01:30Z); LANE-CONTRACT 1.3 verity-agents rule; TABLES.md SP1 stock/precompile; sp1-128 told D1 whole-proof wording + labels
CHECKPOINT 1d9c3198 (22:10Z) [open] 22:12Z merged lane/vllm-rf-a1-rebased bcbec401 --no-ff -> main 1d9c3198 (tests-only, tree == bcbec401), pushed; cli moved; steward kickstarted
CHECKPOINT none (21:46Z) [open] 21:47Z sweep: evicted 196 R2-verified store blobs (4.79 GiB, log evidence/20260924T2120Z-eviction-log.tsv), disk 10 GiB; 0 run dirs qualified (71 blocked by local-only preserved.json); lanes alive (arith+agkr-fp8 on H100s now); agkr-fp8 4090 cell art:1b4fd4a1 forwarded to verify-po; SP1 D1 field-bound text on lane/sp1-128 0783fe6e, lands at its merge
CHECKPOINT 21688b01 (21:42Z) [open] 21:45Z merged PR #1 (drop veritor runtime deps) ff main ab9573fd->21688b01, pushed; cli moved; steward kickstarted; test_pods_connect+test_notes 57 passed. 4 pre-existing failures noted on backlog
CHECKPOINT 07a8edd6 (21:12Z) [open] 21:18Z sweep: disk 7.0 GiB; 4 lanes alive (pods arith/agkr-fp8/agkr-nvf4/sp1-128-a100 busy); arith's 'verified' is producer-only -> launched verify-po bc-591a01c2 (non-producer verifier, worktree moved verify-night->verify-po, FINAL 03:45Z, $6); lanes told to send verify requests there
CHECKPOINT 3510b39a7 (20:37Z) [open] 20:47Z sweep: disk 5.9 GiB; lanes arith/agkr-fp8/agkr-nvf4/sp1-128 alive, pods vy-arith vy-agkr-fp8 vy-agkr-nvf4 busy; sp1-128 2040Z: SP1 cannot reach 2^-128 by params (field-bound terms ~2^-100..-112) -> option 2 (A100 D2 row, <=$5), other rows stopped; option 3 (grinding/bigger field) asked of Daniel
CHECKPOINT ab9573fd (20:29Z) [open] 20:45Z scoreboard doc live; launched agkr-fp8 bc-c0324f23, agkr-nvf4 bc-581636de, sp1-128 bc-d7883bfb (FINAL 03:30Z); backlog in state note; timers: 6PM PT digest + 30-min sweep; R2 hash check done
CHECKPOINT ab9573fd (20:11Z) [open] 20:15Z main ff 22741456->ab9573fd (lane/verifier-cost: D3 12/12, D2 verified-first, D1 A-GKR fix, vocab included-hash-shared), pushed; cli moved; steward kickstarted. Open: H100 D3 rows used loopback verifier (separate-host rerun ~$2.5?); finish-check exit 3 = laptop catalog misses pod-side puts.
CHECKPOINT 6da1b430 (20:08Z) [open] 20:10Z verifier-cost FINAL ab9573fd pushed (D3 12/12, custody art:d841eb56, verifier pod gone) -> merge next; arith alive (4090 arith .0477->.0417); remote-state handoff 2012Z declined per Daniel (separate workstream owns it); stale overnight lanes not yet closed.
CHECKPOINT 22741456 (19:04Z) [open] 19:08Z launched verifier-cost (agent bc-e9e42c6a, pod vy-live2b-verifier-ro keep until sessions preserved; registered in machines.toml) + arith (bc-da525da2, own GPU pod, guard=90), base main 22741456, $10 each, FINAL 01:10Z. vyv-rf-* = vllm coordinator's, not ours.
CHECKPOINT f210f65 (19:00Z) [open] project coordinator took over
CHECKPOINT none (17:58Z) [open] 18:02Z merge-postwave FINAL -> main 22741456 (ff) pushed; cli moved; steward.toml source -> cli; render from main = 15:40Z except T1 A-GKR SHA-512 (campaigns/afternoon/render/1800Z-*). vy-live2b-verifier-ro NOT terminated: holds 5.0 GB of live verifier sessions (/workspace/live/sessions) = D3 raw data; hand to the verifier-cost lane (preserve to R2, extract verify cpu, reuse as live verifier). drilldown.py follow-ups for that lane: A-GKR rows stale (SHA-256/2^-127.7/'Table 1 says BLAKE3'), D2 picks unverified fastest (0a66c35e). Pre-existing: test_label_keys_are_the_store_vocabulary (included-hash-shared missing from vocab).
CHECKPOINT f08314ae (17:25Z) [open] 17:33Z pod-runs merged (6d7728d5) + origin vllm-cleanup-2 (72884c8a) -> main f08314ae pushed; cli moved; watcher restarted. guard = 90 on vy-merge-postwave (opt-in; never on control/verifier pods). merge-postwave told to merge main f08314ae. Disk 16 GiB after deleting stale Rust targets (~/projects/sp1, openvm, openvm-tc-bench; Sep 7). User considering Cursor Projects for lanes: switch after merge lands; needs notes remote, secrets, store access.
CHECKPOINT e7d4a978 (16:49Z) [open] 16:58Z user decisions: research after merge = verifier cost (D3) + arithmetic hill-climb; all variants same security (2^-128 gate stays; SP1 out of T2 until a 128-bit run; SP1-128 lane after merge if disk allows); Table 1 A-GKR hash -> SHA-512 (in merge lane). Cursor DB NOT fixed (77 GB, still growing). Launched merge-postwave (5bc1502a, FINAL 18:15Z, brief campaigns/afternoon/BRIEF.md). Then: ff main, push, move cli, steward.toml source -> cli, re-render; merge pod-runs; launch research lanes on main.
CHECKPOINT 0b0768ed (06:19Z) [open] 06:20Z tables-fix FINAL b11809c1 merged to lane/post-wave with fused-phases 9989797f + wave-5090 d30c32f6 -> 1b3c7be6 (pushed). Launched fill-dc, fill-consumer, verify-night (base 1b3c7be6). Inbox: tables-fix art:68466c4a decision -> verify-night task 1; sp1-table 100-bit -> frozen rule stands, D1/D2 only, user decides in AM (replied); fused-phases fill-go -> launched; contract-result stays post-wave. wave-a100-2 died 04:57Z -> wave-a100-3 (reg.sh run_id fix sent). For AM report: Table 1 says A-GKR BLAKE3 Merkle but code uses SHA-256 (D1 notes it; Table 1 frozen, user to decide).
CHECKPOINT 0b0768ed (05:18Z) [open] 05:35Z morning-tables launched: tables-fix, fused-phases, agkr-table, sp1-table, sp1-tcdot; fill-* + verify-night on fused-phases handoff; render 12:30Z
# Overnight 2 (Sep 23, 05:45Z → 12:15Z) — morning report

User decisions honoured (05:39Z): every target gets two columns — (1) the **bare relation** (`authentication = excluded`) and
(2) **ZK-friendly hashes as part of the proof** (`authentication = included-hash`: Poseidon2-BabyBear hashing of the operand rows
inside the proof, digests bound to the Merkle roots; x and W private). Interactive ZK only, 2^-128, **live verifier** (no
Fiat–Shamir runs anywhere), K = 1536, B = 4096 VUs, frozen instance sets. No algebraic leaf/v2, no re-randomization.

## 1. Table 2 as it renders now (main cc885b2 = frozen 64c00bd + post-freeze + post-freeze-2, ff'd 13:12Z / 13:24Z after H100 and 4090 validation; renders byte-identically)

Every populated cell was accepted by the LIVE verifier (its own coins; session recorded) AND re-verified by me on the laptop with
the Rust `ligero-verify` built from 64c00bd (custody-checked dump trees, `batch --target-bits 128`, system PINNED; verdict
artifacts `verification-verdict/v1`, labels `verified=accepted --by coordinator`). ALL FIVE TARGETS' cells are now today's
live-verified runs (dev-h100-2 re-measured the four H100 cells 12:38–12:43Z against a 30–38 ms US-KS-2 verifier at depth 4;
yesterday's local-coin H100 cells 0.727 / 0.397 are superseded and remain as also-valid rows).

~~~
| Device | Datatype / target | Native peak, spec | measured | B-Ligero (bare) | B-Ligero + in-proof hash |
| --- | --- | --- | --- | --- | --- |
| NVIDIA A100 SXM4 80GB | BF16 sm80.mma.m16n8k16.bf16 | 312 T | 284 T (0.91) | 1.9e7× — 0.781 s [2] (a3 replicate; 0.795 first run) | 5.2e7× — 2.104 s (+169 %) [3] |
| NVIDIA H100 SXM5 80GB | BF16 sm90.mma.m16n8k16.bf16 | 989 T | 722 T (0.73) | 5.2e7× — 0.665 s [5] (live 0.886; local-coin control 0.268–0.306) | 7.5e7× — 0.951 s (+43 %) [6] |
| NVIDIA H100 SXM5 80GB | E4M3 sm90.wgmma.m64n8k32.e4m3 | 1979 T | 1125 T (0.57) | 5.6e7× — 0.356 s [8] (live 0.639; local-coin control 0.108–0.183) | 8.3e7× — 0.527 s (+48 %) [9] |
| NVIDIA GeForce RTX 4090 | E4M3 sm89.mma.m16n8k32.e4m3 | 330 T | 306 T (0.93) | 6.6e6× — 0.252 s [11] | 1.8e7× — 0.693 s (+175 %) [12] |
| NVIDIA GeForce RTX 5090 | E2M1 sm120.mma.m16n8k64.e2m1.nvf4 | 1676 T | 1283 T (0.77) | 9.5e6× — 0.0714 s [14] | — (fp4 hashing not composed, §3.4) |
~~~

Cells: [2] art:d8809c11 (r20260923-105825-b97b) · [3] art:574b41c5 (105944-8701) · [5] art:5807c8b9 (031611-55f1) · [6] art:0ffdb2e9
(110625-36c2) · [8] art:4729f223 (031830-65d9) · [9] art:61c5c0be (111406-14ab) · [11] art:cc59294a (104729-92cb) · [12] art:4ab22886
(104925-7636) · [14] art:318eed1c (110113-b79a). Render: `uv run python -m verity_numerical.bench.tables` on lane/post-freeze.

**Bare column, yesterday → today (frozen tree = hp2-host device witness/tests + enc-hopper encoder + pipelining):**
A100 1.78 → 0.795 s (2.2×) · 4090 2.246 → 0.252 s (8.9×; also a reference 24 GiB board on a Ryzen 7950X host instead of the
48 GiB variant) · 5090 1.636 → 0.0714 s (22.9×; fp4-fast's device hint generator) · H100 bf16 0.727 → **0.665 s live cell**
(dev-h100-2, depth 4 on 11c7075 with the pipe-race fix; local-coin control on the same pod/tree 0.268 s = 2.7× yesterday) ·
H100 fp8 0.397 → **0.356 s live cell** (local-coin control 0.108 s = 3.7×). The H100 cells are now bounded by the live-session
tax (§3b dev-h100-2 (a)), not by the prover. Best overhead: 5090 NVFP4 9.5e6× (1.76e8 proved FLOP/s).

**Committed column (worst case: every VU hashes its own x row + W column, no row sharing):** +169 % (A100), +175 % (4090),
H100 +43 % (bf16) / +48 % (fp8) — the H100 ratios are compressed because both columns there carry the same live-session tax. The hash-relation lane's Poseidon2 witness hook (staged
post-freeze, not in the frozen tree) cuts committed fp8-ada 0.861 → 0.764 s on a 4090; real row sharing via a LogUp table
(64×64 tile: +3–5 % instead of +65–72 % rows) is designed but NOT built — that is the column-2 hill-climb for today.

## 2. What was staged on lane/post-freeze (11c7075) — VALIDATED on an H100 by dev-h100-2 and ff'd into main 13:12Z; post-freeze-2 (cc885b2, §3b) still staged

hash-relation d7141ec (Poseidon2 witness hook) + a844398 fingerprint fix (hashed runs no longer say "privacy is vacuous"; ZK_HASHED_NOTE)
+ hp2-host FINAL 9268cc4 (v4 Montgomery test kernels, register witness, no 440 MB zero fill) + enc-hopper 0da4b1b (encoder n/l ∈
{2,4,8}) + merkle.py loud warning on a cupy host without backends/shared (LIGERO_GPU_STRICT=1 raises) + privsel import fix
(_clamp_table restored) + **pipe-race 5a569ab** (§3.1) + **tables 50c6782** (two-column Table 2). Laptop tests green (bench 157,
research 178); ligero GPU tests cannot run on the laptop → lane **dev-h100-2** (launched 12:05Z) runs them + gates on an H100 and,
if green, measures the four H100 cells at depth 4 with a same-DC verifier. If it reports ff-safe: `git -C ~/projects/verity-main-wt/main
merge --ff-only lane/post-freeze && git push`.

## 3. Findings

1. **`--pipeline 4` (run.py default) produced honest proofs the verifier REJECTED** (dev-4090: 5/6 attempts lost 1–2 of 13
   sub-batches; dev-h100: rejected twice at l=16384). Root cause (pipe-race): the SIMT encoder's per-CTA global scratch
   (`encode_simt.py` `cf_scratch`/`stg`) was one buffer per encoder object, and `encoder_for()` caches one object per (l, n, t_pad,
   device) — concurrent sub-batches on different streams wrote the same scratch words (~1 % of codeword rows corrupted). Fix:
   per-launch stream-ordered scratch (torch allocator; private pool under graph capture); transcript unchanged; kernel repro
   20/20 → 0/20; 0 rejections in 143 depth ≥ 3 sub-batches by Rust + 780 by the prover's verifier; depth-4 bytes == depth-1 bytes.
   Depth 4 is ~37 % faster than depth 2 (0.201–0.208 vs 0.328 s on the 4090). All Table 2 cells tonight are depth ≤ 2 and
   all-accepted.
2. **A cross-continent live verifier inflates `t.total` 2.2–4×.** dev-h100 (US-MO-1) → verifier (EU-RO-1): RTT 135–300 ms, ~32 Mbps
   single flow; `t.total = t.total_live − net.wait_seconds` subtracts only the socket wait for coins, while the ~195 MB/rep of
   prover messages and the pipeline stalls they induce land in the timed phases (`split.openings_seconds` 0.40–1.42 s). Same
   pod, same tree, local coins: 0.254 s vs 0.847 s live. Same-DC pairs (4090/5090 in EU with the EU verifier) show
   t.total_live ≈ t.total + 0.03 s. Fix is deployment, not code: verifier in the prover's DC (dev-h100-2 does this). The
   measurement contract should also move the proof transmit off the timed path (open item, live-verifier follow-up).
3. **Row reduction:** relmin-lookup's v2 relations (8–18× fewer rows) move the selection of public operands to the verifier
   (~30× native FLOPs recomputed) → private-operand-UNSAFE, drill-down only (fp8-ada-v2 0.114 s on the 4090); relmin-private
   found a completeness gap in v2's normalisation (exact-zero sums, honest units rejected; fp8-hopper-v2 in main affected).
   relmin-private's v3 (private-operand-safe) = 2.0–2.2× fewer rows/unit, but its differential tests are still red on main
   (fp8-hopper-v3 failed at 1e5 units; graph-replay crash in privsel/hints.py) → not in Table 2. Lane still working (pod up).
4. **Column 2 for NVFP4 is empty:** hashing fp4 operands needs an in-circuit decode layer (~900 rows/unit + 24-bit-lane packing +
   a component chain end in statement v5) — 6–8 h (hash-compose §6 has the design).
5. **Instance-set "drift" — CORRECTED 12:25Z (dev-h100 final):** the off-manifest results (fa22f077…, 15655c01…) are the `-v2`
   public-selection DRILL-DOWNS (runs 5c19/9a71), not Table 2 cells: a different relation builds its own instance set while
   inheriting the base dataset/tier string, so the renderer (rightly) rejects them as cells, and the drill-down mechanism also
   loses them (it compares instances too) — a renderer follow-up. All four dev-h100 Table 2 cells and the depth-4 fp8 run 1373
   carry the frozen manifests. My 11:47Z coordinator verification of run 1373's proofs had been recorded against the WRONG result
   artifact (the v2 drill-down art:e516454e): those four labels were retracted (files removed, catalog reindexed), the verdict
   art:7c6b2e72 is labelled SUPERSEDED, and both fp8-hopper bare runs are now verified against their own results (1373 →
   art:f85b1129, verdict art:d60e6bae; headline 114946-e45e → art:b966b33b, verdict art:7b0b045f; 13/13 each, 2^-128.32).
   dev-h100's fp8-hopper bare headline is **0.526 s live (depth 2) / 0.235 s prover-only**; bf16-hopper 0.847 live / 0.356
   prover-only (3 reps) — inflation 2.2–2.4× from the cross-continent verifier, so yesterday's 0.727 / 0.397 cells stand until
   dev-h100-2 delivers same-DC numbers.
6. **A100 bare path is `vu.py` = sequential** (`--pipeline` is a no-op there; l=32768 is a knee: encode 2.47 s vs 0.17 s); the generic
   runner's `bf16-ampere` bare line at depth 2/4 would be the like-for-like number (dev-a100 ran out of time; §6 of the brief).
7. Store/tooling: `research data fetch` twice failed on a shared object that another lane's concurrent eviction/pull had removed
   (retry succeeded) → the honing branch's `evict` must respect shared objects; labels are still local-only until the honing
   merge (`labels-sync`); `data pull` of thousands of per-proof JSONs is slow (tar them); laptop Data volume ~99 % full from OTHER
   projects (~/projects 95 GB) — eviction of the store cannot fix that.

## 3b. Lane finals that landed after the first draft (12:05Z)

* **live-pipeline** (620e7316, in 64c00bd): `--pipeline N --verifier` now overlap (non-blocking coin Futures + a HELLO `window` so
  the verifier commits N sub-batches ahead). At 70 ms RTT, 49 sub-batches: sequential-live 7.4 s → depth 2/3/4 **3.87 / 2.66 /
  2.04 s** t.total_live (wait ≈ 49/N · 2·RTT), 147/147 accepted, byte-identical non-ZK bytes. CAVEAT that explains tonight's live
  numbers: the gain needs the VERIFIER restarted on ≥ 620e7316 — the shared EU verifier ran main's older server, whose control
  loop serialises the openings (7.15 s floor whatever the prover overlaps). dev-h100-2's own verifier is built from 11c7075.
  `vu.py` (A100 bf16 bare) has no `--pipeline`, so its live path stays sequential. $1.47.

* **EU live verifier retired 12:27Z** (vy-live-verifier, 06:36Z–11:50Z, 183 sessions, 23 GB): proof-free custody bundle
  preserved as art:a8004556 (index.jsonl, every session's hello.json, verifier-drawn `sub_*.coins`, `rust_sub_*.json` verdicts,
  sha256 manifest of all excluded .stmt/.proof/system.bin — 10 938 files, 60 MB). The Table 2 sessions were additionally recorded
  by their lanes via `live record`. enc-hopper's "missing blobs" run-files art:b634b6c0 is intact on R2 (605 objects PRESERVED,
  `data verify` 12:15Z) — it was a laptop-local eviction, not a loss.

* **relmin-lookup FINAL (12:15Z, $3.41).** Checkpoint 2ef2409 (in main) = the four `-v2` public-selection relations,
  7.8–18.4× fewer rows (bf16-hopper 3292→282, bf16-ampere 3516→449, fp8-hopper 3396→185, fp8-ada 3769→337); committed
  elements per FLOP bf16-hopper 103→8.8. Post-checkpoint **`-v2x4` fold** (6b79b06/87c94b6, four instruction steps per
  column: 1045/1717/647/1255 rows, 24/24/12/12 columns per VU; GPU gates 0 failures; Rust-pinned) — same 4090, fp8-ada
  int-ZK 4096 VUs at l=16384: **v1 0.490 → v2 0.329 → v2x4 0.162 s** (3.48e6× with whole sub-batches); proof 66→31→12 MB;
  verifier 0.355→0.148 s. THE FINDING: 10× fewer rows bought only 1.6×, the fold another 2× — the v2 prover is ~95 %
  per-sub-batch fixed cost (arithmetic tests ~13 ms/sub-batch, serialisation, openings) and the sub-batch count is
  `VUs × columns/VU ÷ l`, independent of rows. **Columns per VU is the lever nobody named**; hint generation (0.05 s flat)
  is now a third of the x4 prover. v2/v2x4 stay drill-downs (verifier recomputes the public half, ~30× native; useless for
  private operands). Spec errors they flagged: "2^16 lookups are cheap" is false in this compiler (one selector row per
  distinct output group); "prover ∝ rows × n/l" holds for encode/Merkle/proof size, not wall time.
* **relmin-private FINAL (12:15Z, 3.75 h).** Four `-v3` PRIVATE-operand-safe relations at 78daae8: bf16-hopper 1519,
  bf16-ampere 1629, fp8-hopper 1673, fp8-ada 1806 rows (2.03–2.17×; operands stay committed witness bound by word pins),
  GPU gates 0 failures, 1e5 differentials, Rust-pinned (`Decode::PrivSel`), 33 batch verdicts. Same 4090 fp8-ada int-ZK
  l=4096: 0.686 → 0.593 s (proof 181→103 MB); at l=16384 1.84–1.90× faster than v1 across three relations. Two findings:
  (a) a completeness gap for exactly-cancelling sums with a large group maximum — main's `fp8-hopper-v2` rejects the same
  honest unit (one-quadratic fix in v3; pubsel one-liner spelled out in their report — apply before v2 is ever a headline);
  (b) they measured main 02c3321's encoder ~15× slower at n=65536 on their 4090 (encode 1.83 s) — **NOT reproduced**:
  dev-4090 on 64c00bd (same commits, reference part) measured fp8-ada v1 l=16384 encode 0.070 s / t.total 0.252 s at the
  same hour; their l=16384 numbers are on a pod-specific degraded path (their l=4096 numbers are fine). Treat (b) as an
  environment caveat, not a regression.
* **dev-a100 FINAL (12:14Z, $2.47):** cells as in §1 (bare 0.795 s, clean replicate 0.781; committed 2.104 s); 75/75 live
  + my Rust 25/25 each. Their action items: pytest collection on frozen main breaks on the privsel import (fixed on
  post-freeze a618793); `--batch 32768` is 2.5–2.8× WORSE on the A100 for both columns (encoder knee) — keep 16384;
  `--pipeline` is a no-op on the `vu.py` bare path; duplicate snapshot art:13e48b06 labelled DUPLICATE (canonical
  art:e10634d4).
* **Staging:** `lane/post-freeze-2` = cc885b2 (worktree ~/projects/verity-main-wt/post-freeze-2) = post-freeze 11c7075 +
  relmin-private 78daae8 + relmin-lookup x4 (87c94b6); conflicts were all additive (relation.rs 17 pins, run.py choices,
  D12 stub addendum); Rust 22+7+16 tests green, laptop Python baseline unchanged (12 passed / 8 torch-only collection
  errors; bench+research 162). **GPU-validated by fold-private D0 (13:05Z: 5 gates 0 failures, pytest 195 passed, fp8-ada v1 bare
  depth 4 t.total 0.179 s on the 4090, Rust 13/13) → ff'd into main 13:24Z, pushed.**

* **dev-h100-2 FINAL (13:09Z, ~$4.0 of $6).** post-freeze 11c7075 validated on an H100 (pytest 147/0 incl. pipeline_race_test
  6/6, four gates 0 failures, depth 4 clean in 316/316 live sub-batches) → **ff'd into main 13:12Z, pushed.** Four H100 cells
  re-measured at `--batch 16384 --pipeline 4` against a US-KS-2 verifier (30–38 ms RTT; RunPod has NO routable same-DC
  pod-to-pod path — the only DC with both an H100 and a cpu3m returns EHOSTUNREACH): bf16 bare **0.665 s** (live 0.886),
  bf16 hash **0.951 s** (live 2.874), fp8 bare **0.356 s** (live 0.639), fp8 hash **0.527 s** (live 1.401); 75/75, 75/75,
  39/39, 39/39 live-accepted; my Rust re-verification 25/25, 25/25, 13/13, 13/13 (verdicts art:9a03bd0d, art:c84dab2b,
  art:16002c77, art:dde4677b). Snapshot dev-h100-2-v1 art:4cdf9e13. TWO FINDINGS: (a) the **live tax is ~2× inside `t.total`
  even at 30 ms** — local-coin controls on the same pod/tree are bf16 0.268–0.306 s and fp8 0.108–0.183 s; the extra lands in
  `split.openings_seconds` and `t.arithmetic` (transmit contention on the prover host: 586 / 309 MB out per 3 reps) and does not
  shrink with RTT → the next lever is moving the prover's transmit off the compute critical path (sender thread / stream-ordered
  copies), not a closer verifier. (b) **bf16-hopper at `--pipeline 2` against this verifier is a reproducible 27–28 s session**
  (opening RTT 380–430 ms median, p90 2.3–2.6 s) while depths 1 and 4 are 35 ms and fp8 depth 2 is clean — a live-path pathology
  specific to depth 2 on this pair; depth 2 is NOT the safe fallback. Unowned (live-verifier lane is done); run ids + verifier
  log in their report. Also: dev-h100's off-manifest runs came from a different `n`, not a re-seed.

* **fold-private FINAL (14:47Z, $1.71; 5d88d70 ff'd into main 14:55Z, pushed; Table 2 cells unchanged).** Eight folded
  private-safe relations (`fp8-ada-x4`, `fp8-hopper-x4`, `bf16-hopper-x4`, `bf16-ampere-x4`, and the `-v3x4` four; x8 registered
  for fp8-ada), all gates 0 failures, 1e5-chain differential 0 mismatches, Rust pins (25), folded-boundary negatives, D15.
  **The prediction in §5(0) was wrong for v1/v3:** rows per VU are FLAT under the fold (fp8-ada 3724 → 14830/4 = 99.6 %;
  Ampere v1 even 103.6 % super-linear) because v1/v3 do not share an accumulator decode the way v2 does — the fold only cuts the
  sub-batch count, and v1's prover is not fixed-cost dominated. Measured (4090, int-ZK, medians, all Rust-accepted): fp8-ada v1
  l=16384 p4 **0.170 s** vs -x4 0.195 (1-VU tail) / **0.150 with whole packing (4095 VUs)**; l=4096: 0.181 vs 0.167 / 0.152;
  bf16-hopper v1 0.267 vs -x4 0.282 / 0.242 (4092 VUs); l=4096 0.309 vs 0.260. So −8…−16 %, not 2×. Two real findings:
  (a) `--pipeline 4` at l=16384 OOMs the 24 GB part for every x4 relation (22.9 GB), depth 2 loses encode overlap; (b) **the v3
  relations fail the pipelined prover's self-check at any depth > 1 on cc885b2, unfolded too** (reproducer in their note), so v3
  runs pipeline-1 — and at pipeline 1 **v3 is slower in wall time than v1 at depth 4** (fp8-ada-v3 0.829 s vs v1 0.170 s;
  bf16-hopper-v3 1.074 vs 0.267): the 2× row reduction does not pay while the arithmetic phase (0.498 s) is serialised. Net:
  **v1 + hp2-host/pipe-race pipelining at depth 4 is the fastest private-operand-safe prover we have** (4090 fp8-ada 0.170 s,
  H100 fp8 local-coin 0.108 s). Their ranked remaining: v3 pipelined bug; per-slot CUDA-graph pools to restore depth 4 for folds;
  x8 registration (450 s compile); `marshal()` id()-keyed bundle cache (test hazard: stale-bundle replay made a negative "accept").
  Snapshot fold-private-v1 art:91008763 (19 members). Their `push --pending` was spinning on the OTHER session's 259k-file vllm
  fixture (46 GB, local=0) — killed 14:53Z after confirming every fold-private artifact is remote.

* **HONING MERGED 15:00Z (lane/honing-code 77033bf → main e0cf2cd, pushed; 183 research+bench tests green; Table 2 cells
  byte-identical before/after).** Runbook executed: catalog migrated v0→v1 (`research data catalog`: schema v1, current;
  pre-merge worktrees keep working — they never read user_version); `reindex` (3456 artifacts / 1035 attempts / 8552 labels);
  **labels are now durable: `labels-sync --push-only` put all 8552 local assertions on R2** (was 0 remote); `vocab-check`: 1509 of
  8547 files off-vocabulary (626 unknown keys, mostly lane shorthand like row/tree/same_device — harmless to the tables; vocabulary
  decision for the user); off-enum `proof_class` corrections written by the coordinator for the 5 fp8-proof runs, mirroring each
  run's own fingerprint (NON_ZK_PROOF_DIAGNOSTIC ×4, COMPLETE_HVZK_BACKEND ×1; r20260922-183111-3c01 has no result → no label);
  b-sweep's `verified=ligero-verify` ×31 left as-is (the verify lane's labels supersede them). `research data evict` found 0
  evictable blobs after reindex — the store's 6 GB of objects were (a) a 2.4 GB orphaned `.tmp` partial write by the killed
  fold-private push (removed) and (b) a 3.0 GB blob of the OTHER session's unpushed vllm fixture art:346f958a (left alone: remote=0).
  Per-target dossier published to Notion (child of the decision record): https://app.notion.com/p/3e4399515d9e818fb9c4d5041eaa0d4e
* **DISK (tell the user):** Data volume at 3 GB free / 460 GB. `~/.research` is 9.4 GB (store objects 3.4 after cleanup + runs 2.9 of
  pre-store Sep 21-22 run dirs with no run-files artifacts → not evictable by policy). The hog is Cursor's
  `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` = **59 GB**, plus ~/projects (~95 GB: veritor 14, os 10,
  sp1 9.9, openvm-fv 7.6, proofs 7.4) and the other session's 26 worktrees. The disk watchdog (/tmp/disk_watch.sh) can only evict
  verified store blobs and there are none left to evict.

* **hp2-host** (final 9268cc4, staged post-freeze): on one H100 (Xeon 8480+ host), like-for-like vs main 6babe27 at
  `--batch 16384 --pipeline 4`: **bf16-hopper 0.752 → 0.2525 s (3.0×), fp8-hopper 0.443 → 0.1342 s (3.3×)**; transcripts 187/187
  byte-identical, 7/7 gates, Rust ACCEPT; the prover is now GPU-bound at depth 4 (host 4.1 ms busy per sub-batch). One more
  commit **e689b72** (four-step CUDA NTT, −7.4 % → 0.2337 s, bit-exact) is only 2/7-gated (pods terminated) → NOT staged;
  dev-h100-2 may gate it opportunistically (§6 12:20Z). Lane overspent ($15.5 vs $12). Encode + Merkle (5.4 of ≈ 8.8 ms GPU per
  sub-batch) are now the floor (≈ 0.12 s for the bf16 row).
* **enc-hopper** (final 0da4b1b, staged post-freeze): encode + Merkle on H100 bf16-hopper 0.158 → 0.072 s (2.19×; target 0.05 not
  reached — the encoder is barrier/smem-pass-bound, not DRAM-bound, so the "1 TB/s" framing of the spec was wrong); n/l ∈ {2,4,8}
  encoder (torch fallback 25–81 ms → 1–3.6 ms). 62/62 transcript files identical, 6 gates, Rust ACCEPT. $21.5.
* **fp4-fast** (a2089ac; everything but a reverted pair is in 64c00bd): NVFP4 on the 5090 0.788 s (main 6babe27, same pod) →
  **0.062 s pipelined / 0.058 s on frozen main with local coins** (13.6×; 28× vs the spec's 1.636 s); 32/32 rows Rust-accepted,
  byte-identical transcripts. The live Table 2 cell (0.0714 s) is the SEQUENTIAL fp4 runner: `fp4/chain.py:713` keeps live
  sub-batches sequential (the `--pipeline` flag is inert under `--verifier`) → a 0.039–0.048 s cell is available once the fp4
  runner takes live coins per sub-batch (live-pipeline scope). The 4-VU tail sub-batch costs ~23 % of the fp4 row (B = 4092
  diagnostic 0.053 s); `--tail-l natural` was a negative result (Rust reject, reverted).
* **pipe-race** ($0.46): as §3.1. Caveat: the prover-level rejection never fired on its EPYC 7402 host even unfixed (0/429 at depth
  4) — overlap is host-timing-dependent; dev-h100-2's depth-4 runs on the fixed tree are the field test.
* **dev-5090** ($1.36): headline moved to the depth-1 run r20260923-113505-0474 (0.0722 / live 0.106 s, identical within noise to
  0.0714); `--reps 1` sweeps are misleading for fp4 (rep 1 carries ~0.37 s of graph capture).
* Disk: enc-hopper found Cursor's `state.vscdb` at 58 → 62 GB on the laptop — that, not the store, is the disk hog; `research run`
  launches failed once with `No space left on device`.

## 4. Lanes, pods, money

Wave 1: hp2-host, enc-hopper, relmin-lookup, fp4-fast, live-verifier, hash-relation, honing-code, hash-compose, live-pipeline,
merge-val — all FINAL, all merged into 64c00bd or staged on post-freeze (honing-code NOT merged: needs zero store writers,
runbook in its note §2). Wave 2: dev-4090, dev-a100, dev-5090, dev-h100 FINAL (all pods terminated by 12:00Z); pipe-race FINAL.
Running at 12:15Z: **dev-h100-2** (H100 + same-DC cpu3m verifier, ≤ $6, deadline 13:40Z), **relmin-private** (4090, v3 tests).
Pods still up: vy-dev-a100 (finishing snapshot; the lane terminates it), vy-relmin-priv, vy-live-verifier (EU; off when
dev-h100-2 has its own), vy-control. RunPod balance **$202.11 at 12:05Z** ($296.21 at 12:00Z Sep 22 → ~$94 for the two
campaigns incl. the other session's vyv-* pods; ours tonight ≈ $45).

## 5. Next hill-climbs

**(0) [DONE by fold-private, result −8…−16 %, NOT 2× — see §3b; rows/VU flat for v1/v3] Fold the PRIVATE-safe units.** relmin-lookup showed
the prover is ~95 % per-sub-batch fixed cost and the fold cuts sub-batches 4× at sub-linear row growth (fp8-ada-v2 0.329
→ v2x4 0.162 s). The same `_folded(rel, m)` construction applies to any relation whose chain state is the FP32
accumulator — v1 and v3 included — with NO change to the claim (same VU, same y16) and no public selection. Predicted:
fp8-ada v3x4 ≈ 0.25–0.3 s on a 4090 (vs 0.252 s v1 today) with private operands intact; m = 8 is one line more. Plus the
two fixed-cost items it exposes: fused per-group hint kernel (0.05 s flat), and `protocol.py` per-sub-batch test INTTs /
syncs / serialisation.
 (for the user to rank)

(a) LogUp row sharing for column 2 (64×64 tile; +3–5 % rows target) — the biggest single win on the committed column.
(b) fp4 committed column (decode layer, 6–8 h).
(c) relmin-private v3 to green (2× fewer rows, private-safe) then re-measure every bare cell.
(d) Same-DC verifier + depth 4 everywhere (post-freeze tree): expect H100 bf16 ≈ 0.25 s, fp8 < 0.2 s → overheads ~2e7×.
(e) Move proof transmit off the timed path in the live protocol; report t.total (prover), t.total_live (session), bytes.
