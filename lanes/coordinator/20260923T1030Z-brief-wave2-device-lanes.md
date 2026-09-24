> **Rules superseded (2026-09-24T01:00Z):** the standing lane rules (§0 and similar sections) now live in `~/.research/notes/kb/LANE-CONTRACT.md`, which wins where they differ. This brief's lane-specific content stands.

# Wave 2 device lanes — Table 2 two columns from FROZEN main 64c00bd (2026-09-23, launch 10:30Z, deadline 12:15Z)

Coordinator brief shared by lanes `dev-a100`, `dev-h100`, `dev-4090`, `dev-5090`. Read the whole thing before touching a pod.

## 0. Frozen tree, roles, rules

* main is FROZEN at `64c00bd` (pushed). Your worktree: `git -C ~/projects/verity/.git worktree add ~/projects/verity-main-wt/<lane> -b lane/<lane> 64c00bd`
  (one shared `.git`; never delete another lane's worktree or branch). You do NOT change prover / verifier code. Allowed commits on `lane/<lane>`:
  none required; if a bootstrap script or a store-tool key is missing, the fix must be additive and reported as CHECKPOINT (I merge).
* You DO provision and terminate exactly one GPU pod (yours). Budget per lane (pod hours): A100 $4, H100 $7, 4090 $2, 5090 $3. Terminate at the end
  or at 12:10Z whatever the state. Other pods (`vy-*`, `vyv-*`) are not yours.
* The coordinator is the only merger of main. Report by editing ONE note `~/.research/notes/lanes/<lane>/20260923T1030Z-report-<lane>.md`
  (front matter `lane:`, `status: open|done`, then `CHECKPOINT <sha or 'none'> (<time>Z)` lines at the top, then sections). Write a checkpoint line
  at 11:15Z and 11:45Z even if partial; `status: done` by 12:15Z.
* Laptop disk is tight (~3 GB free). BEFORE every `research data pull` / `fetch`: `python3 /tmp/store_evict.py --target-free-gb 6`.
  AFTER every `research data push --verify head`: run it again. Pull only what Table 2 needs (result.json + `proofs/` dump tree of rep1).
* R2 creds for push: `set -a; source ~/.config/verity/r2.env; set +a`. Run `research` from your worktree (`cd ~/projects/verity-main-wt/<lane> && uv run -q research ...`).

## 1. Pod

`uv run -q research pods create --name vy-<lane> --gpu "<GPU>" --disk 60 --require-reference-part [--data-center <id>]`
GPU strings as in `tools/research/src/research/pods/part.py`; H100 must report `NVIDIA H100 80GB HBM3` (not NVL / PCIe), 4090 must be the 24 GiB part,
5090 the 32 GiB part, A100 the 80 GB SXM. If `--require-reference-part` refuses three times, create without it, run `research pods check-part`, and record
`device_variant` honestly (Table 2 will reject the cell; still measure and report). The live verifier is in EU-RO-1; prefer that data center if the GPU exists there
(RTT ~5-10 ms instead of 70+), otherwise anywhere.

Bootstrap = the ada-ref / fp4-proof recipe (`~/.research/notes/lanes/ada-ref/20260923T0200Z-report-ada-ref.md` §"bootstrap",
`~/.research/notes/lanes/fp4-proof/20260923T0315Z-report-fp4-proof.md`): venv312 with torch cu124 + cupy + blake3 + pytest, rustup + `cargo build --release`
in `backends/ligero-verify` (the frozen tree's Rust: v5 statements, v3 systems, hashed pins), ship the tree with
`git archive HEAD | ssh ... tar -x -C /workspace/src`, `PYTHONPATH=/workspace/src/packages/verity/src:/workspace/src/backends/numerical/python:/workspace/src/tools/research/src:/workspace/src`.
`bench-instances/v1` (A100 bare/committed and the frozen `vu-k1536` set): fetch per ada-ref. `--instances-cache /workspace/instances-cache`.
Expect the first hashed proof to spend ~100 s in NVRTC (cached afterwards); set `--timeout` accordingly.

## 2. Gates first (do not skip; ~10 min)

On the pod, from the frozen tree:
* `python -m backends.direct.ligero.run --relation <rel> gate-vu --vus 2048 --batch 16384 --device cuda` for each of your bare relations (v1) — 0 failures
  and every negative family rejected;
* same with `--auth included-hash` for each committed relation (A100: `--relation bf16-ampere --root /workspace/bench-instances/v1`; 5090: only if the
  coordinator tells you hash-compose's fp4 landed — otherwise skip);
* `pytest backends/direct/ligero -q -x` (torch tests) — report the counts; a failure = stop and write the checkpoint, do not "fix".
If the default `--pipeline 4` bare bench crashes with `Offset increment outside graph capture`, set `LIGERO_GRAPH_STRICT=1`, capture the traceback in the
note, and rerun with `--pipeline 1` (report both). main 538801e/78ce73f fixed the known case; a new one is a finding.

## 3. Measurements — the two Table 2 columns per target

Both columns: interactive ZK (`--zk --mode interactive`), LIVE verifier (`--verifier tcp://213.173.105.69:30899`, `live-verifier@64c00bd6`, already rebuilt
from the frozen tree, accepts v5/hashed), `--target -128`, `--total-vus 4096` (A100 vu.py path: the frozen 2048 `vu-k1536` VUs), `--reps 3`, `--dump-dir $RD/proofs
--dump-reps 1`, `--out $RD/result.json`, `--instance-procs 16`. NO Fiat-Shamir runs anywhere.

* Operating point: quick sweep of `--batch` (sub-batch size l) over {4096, 8192, 16384, 32768} and `--pipeline` over {1, 2, 4} with `--reps 1` on the BARE
  column, pick the fastest `t.total`; use the same `--batch` for the committed column (the hashed runner is sequential; pipeline is ignored there).
  Also record `t.total_live`, `net.rtt_ms`, `net.wait_seconds`, `verify.wall_s` from the result.
* Column 1 = bare: `--relation <rel>` (v1: `bf16-hopper`, `fp8-hopper`, `fp8-ada`, `fp4-nvf4`; A100 = the Table 2 path `--relation bf16 bench-vu` over
  `bench-instances/v1`), `authentication = excluded`.
* Column 2 = committed: the same line plus `--auth included-hash` (fingerprint `authentication = included-hash`, `hash = poseidon2-babybear-w24`,
  `sharing = none`; `--tile 64x64` is NOT cheaper on the frozen tree, skip it). A100: `--relation bf16-ampere --root /workspace/bench-instances/v1
  --auth included-hash`. 5090: committed column only if hash-compose's fp4 lands (coordinator will append a line to THIS note under §6).
* Drill-down (report, NOT Table 2 headline): the `-v2` public-selection relation for your bare targets (`bf16-hopper-v2`, `fp8-hopper-v2`, `fp8-ada-v2`,
  `bf16-ampere-v2`) at the same operating point, 1 rep, bare only, interactive live — its verifier recomputes ~30x native FLOPs per VU, so it is a
  public-operand-only number. Skip `-v3` (relmin-private; failing on main). Skip if you are behind schedule.

Each result must be contract-valid (`python -c "import json,sys; from verity_numerical.bench import contract as c; print(c.validate(json.load(open(sys.argv[1]))))" $RD/result.json`
must print `[]`), with dumps (rep1), and pulled + pushed: `research data pull` of the run (result + proofs; see `research data --help`) →
`research data push <run> --verify head` → the live-verifier label is produced by `live record` (below), NOT by hand; do not label `verified=` yourself
— the coordinator adds its own label after re-verifying with the laptop Rust. Snapshot: `research data snapshot --name dev-<gpu>-v1 --members art:... --note "..."`
listing every pushed artifact. Record the live session: `python -m backends.direct.ligero.live record --machine vy-live-verifier --remote-out /workspace/live/sessions
--run <run> --result <art> --preserve` (runbook (c) of live-verifier's note) for the headline runs.

## 4. What the note must contain (this is what the morning report is built from)

Per target and column: median `t.total`, `t.total_live`, overhead vs native peak (`tables.py` computes it; give the raw numbers), `--batch`/`--pipeline`
chosen, sub-batch count, proof bytes total, statement bytes, verifier wall/CPU (live session), `net.rtt_ms`, GPU name + memory (`nvidia-smi --query-gpu=name,memory.total`),
host CPU (`lscpu | grep 'Model name'`), torch/cupy versions, run ids, artifact ids, session ids, the gate results, anything that crashed with the full traceback.
Per-phase breakdown (`t.phases` in the result) for the bare headline — the hill-climbing lanes need it.

## 5. Encouragement

You are measuring, not inventing; but if the sweep shows a knee (e.g. `--batch 32768` runs out of memory, or pipeline 4 is slower than 2), that is a finding —
write it down with numbers. If something is 2x off what hash-relation / hp2-host reported for your GPU class (their notes in `~/.research/notes/lanes/`),
say so explicitly and check host CPU + GPU part before assuming a regression.

## 6. Coordinator appendix (I edit this section; re-read it at 11:15Z and 11:45Z)

* 10:30Z: frozen main 64c00bd; live verifier rebuilt (`live-verifier@64c00bd6`, port 30899). fp4 committed column: NOT landed yet.
* 11:05Z: **dev-5090: the fp4-nvf4 committed column will NOT land tonight** (hash-compose final: needs a new in-circuit decode layer for the
  141 verifier-side pins + 24-bit-lane sponge packing + component chain end in v5, ~6-8 h). Column 2 for the 5090 is EMPTY; do not wait for it —
  finish the bare column, push, terminate.
* 11:05Z: **dev-a100**: hash-compose measured the committed `bf16-ampere` column on a 4090 at l=16384: 1.724 s vs bare 0.678 s (peak 10.7 GB);
  l=32768 OOMs on 24 GB (~27 GB needed) but ms/VU was still improving → on the 80 GB A100 try `--batch 32768` FIRST for both columns, fall back
  to 16384. Their exact A100 lines are in `~/.research/notes/lanes/hash-compose/20260923T1030Z-report-hash-compose.md` ("Device-lane commands").
* 11:05Z: all lanes: `/tmp/store_evict.py` and `/tmp/runs_evict.py` now re-exec themselves under the venv python (plain `python3` lacked
  `tomllib`); use `python3 /tmp/store_evict.py --target-free-gb 6 --min-kb 16` (the `--min-kb 16` reaches the many small per-proof blobs).
  Laptop free after my sweep: 4.5 GB. Do not pull more than one dump tree at a time.
* 11:15Z: **ALL LANES — do NOT use `--pipeline 4` (run.py's default) or any depth > 2 for Table 2 runs.** dev-4090 found that at depth 4 the
  prover intermittently emits sub-batches the verifier REJECTS (`proximity test failed` / `chain constraints failed`; 5 of 6 attempts at 4096 VUs
  lost 1-2 sub-batches, with and without the live verifier; depth 1 / 2: 0 rejections in ~250 sub-batches). Use `--pipeline 2` (or 1); a headline run
  is only a headline if EVERY sub-batch was accepted by the live verifier (copy the VERDICT line) — if any run shows a rejection, discard it, say so
  in the note with the run id, and rerun at depth 1. If you already measured at depth 4, remeasure. A fix lane (`pipe-race`) is on it; the frozen
  tree does not change for you.
* 11:15Z: `privsel` (the `-v3` relations) is import-broken on 64c00bd — skip `-v3` entirely (already the instruction), and `pytest --ignore=backends/direct/ligero/privsel`.
* 11:40Z: **dev-h100 + dev-a100 (remote from the EU-RO-1 verifier; RTT large): before you terminate, run the bare headline line ONCE
  WITHOUT `--verifier`** (1 rep, no dumps, same `--batch`/`--pipeline`) and report its `t.total` next to the live run's. If it is materially lower,
  the live run's `t.total` includes coin-wait stalls (2 RTT per sub-batch at depth <= 2) and the morning table must show prover-only vs live
  separately. Also record `net.rtt_ms` (dev-h100: your RTT probe is still "pending" in the note).
* 11:40Z: **dev-a100**: `--pipeline` is a no-op on the vu.py path, so your bare 0.795 s is unpipelined. If time permits (pod deadline 12:10Z
  stands), run the generic-runner bare line `--relation bf16-ampere --root ... bench-vu --zk --mode interactive --verifier ... --batch 16384
  --pipeline 2 --reps 3 --dump-dir ... --dump-reps 1` (NOT depth 4 — see 11:15Z) and report it as a candidate A100 bare cell; the Rust pin is
  the same `bf16-ampere` system. Table 2 will use whichever the renderer accepts; both go in the note.
* 12:00Z: **dev-h100 — your fp8-hopper BARE headline r20260923-111305-1373 (art:e516454e) is REJECTED by the Table 2 renderer:
  `instances.manifest_sha256` fa22f077… is NOT the frozen set 0ff75002… (your committed run 111406 IS on the frozen set, so the
  cache path differs between the two invocations). Same for the bf16 bare re-run ee6b15e5 (15655c01… vs frozen 2a5babca…; your
  110436 run is fine).** Re-run the fp8-hopper bare headline line on the frozen instance set (the exact `--instances` / cache your
  committed run used; check `workload_fingerprint.instances.manifest_sha256` == 0ff750026b8d… in result.json BEFORE pushing),
  live-verified, dumps rep1, pull + push. Pod deadline for you moves to **12:25Z**. Report which cache produced fa22f077 (a
  regenerated / differently-seeded instance set is a finding by itself).
* 12:05Z: dev-h100 terminated before the 12:00Z item; lane **dev-h100-2** (worktree ~/projects/verity-main-wt/dev-h100-2, branch
  lane/dev-h100-2 from post-freeze 11c7075) re-measures the four H100 cells with a SAME-DC cpu3m verifier at depth 4 and GPU-validates
  the post-freeze tree (= merge-val-2). Coordinator report: ~/.research/notes/lanes/coordinator/20260923T1215Z-report-morning-overnight2.md.
* 12:20Z: **dev-h100-2, OPTIONAL after step D (only if the four cells are pushed and you have >= 25 min before 13:40Z):**
  `git cherry-pick e689b72` (lane/hp2-host: four-step CUDA NTT, bit-exact 187/187 on a 4090, pytest green, but only 2 of 7 gates
  ran before its pods went away) onto lane/dev-h100-2, ship the delta, run gates fp8-ada + fp4-nvf4 + bf16-hopper, and ONE bare
  bf16-hopper rep (local coins, depth 4). Report gate rc + t.total; do not use it for the Table 2 cells.
* 11:40Z: pipe-race root cause = the SIMT encoder's per-CTA scratch (`encode_simt.py` `cf_scratch`/`stg`) is one buffer per cached encoder
  object, shared by every pipeline slot → concurrent slots race on it. Depth <= 2 has shown 0 rejections in 338+ sub-batches, but the
  all-accepted rule for headline runs stays (the live verifier's VERDICT line is the evidence).

### §6.9 (12:30Z, coordinator) — dev-h100-2 pods + EU verifier retired

* `pods list` at 12:29Z shows TWO H100s (vy-dev-h100-2 g8zrn40cutw95q AND vy-dev-h100-2b jzrtm9jfkc9kit, $3.49/h each) plus
  vy-live-verifier-2b; the two earlier vy-live-verifier-2 pods are gone. If the move to `2b` is deliberate (same-DC pairing),
  terminate g8zrn40cutw95q as soon as its tree is copied — two H100s burn $7/h against a $6 lane budget. State the reason for the
  relocation and the final RTT in your CHECKPOINT line.
* The shared EU verifier vy-live-verifier (tcp://213.173.105.69:30899) is TERMINATED (12:27Z); its 183 sessions' custody
  (coins, verdicts, sha256 of every stmt/proof) is preserved as art:a8004556. Use only your own same-DC verifier (built from your
  tree, ≥ 620e7316, so `--pipeline N` and the HELLO window actually overlap).
* FYI: the `-v2` drill-down relations build their own instance sets (manifest_sha256 ≠ frozen) — expected; the renderer rejects
  them as cells and (today) as drill-downs. Do not chase that; just keep the v1 cells on 0ff75002…/2a5babca…

### §6.10 (13:25Z, coordinator) — main moved

* main = **cc885b2** (pushed): 64c00bd + post-freeze (hash hook, two-column tables, pipe-race fix, merkle warning, privsel import)
  + relmin-private 78daae8 + relmin-lookup v2x4. Validated on an H100 (dev-h100-2: pytest 147/0, 4 gates) and a 4090
  (fold-private D0: 5 gates, pytest 195, fp8-ada bare depth 4 0.179 s, Rust 13/13). Branches lane/post-freeze{,-2} deleted.
  fold-private: your base cc885b2 IS main now — nothing to rebase.
