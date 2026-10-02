---
id: 20260930T2205Z-report-resource-steward
campaign: verity
lane: resource-steward
kind: report
status: open
repo: danielreuter/verity
origin: resource-steward (bc-b154b9ef-b9e0-560b-857b-56c2d5530ead), worker of the infra coordinator (bc-17cc41f1)
---

# resource-steward: disk, RAM and cache policy for vy-nebius-1 and vy-nebius-2

The steward's only job is keeping disk, RAM and other resources on the two GPU nodes from being overwhelmed (Daniel's ruling,
2:52 PM PDT 30 Sep). It owns disk, cache and RAM policy on both nodes. It runs until the nodes stop at 7 Oct 14:55Z
(7:55 AM PDT). It is woken by a 20-minute timer, by top-level posts in `#agent-alerts`, and by `*alert*` notes in
`lanes/infra/`, `lanes/node2-ops/` and `lanes/resource-steward/`. It stays silent unless a threshold is crossed or it acts.

## 1. Policy

### Delete without asking
Only with no open files (`lsof +D`), and only at `nice 19 ionice -c3`:
- check scratch untouched for more than 2 h: `~/.cache/verity-check/lean-audit-scratch-*`, other scratch a finished check
  left, and `/tmp/pytest-of-research/*` (20 GB on node 1's root disk now);
- benchmark scratch (`/workspace/research/tmp-bench` and the like);
- LRU entries of regenerable caches, only while their filesystem is over its watermark, oldest first, down to 5 points under
  it: `~/.cache/uv`, `/workspace/cache/uv`, `/workspace/jobs/cache/{uv,triton}`, `~/.triton`, `~/.cache/vllm`, and
  harness venvs under `/workspace/cache`. Never `~/.cache/verity-check/lean-deps` or `circuit-check` (check's verdict caches;
  their owner is the check, and run `r20260930-213917-d6b3` is moving them to `/workspace`);
- shipped source trees `/workspace/research/src/<sha>` older than **6 h** that no running run references (Daniel's ruling on
  card `01933aa8`, 6:58 PM PDT 30 Sep; it was 24 h), and that hold nothing outside their commit besides build caches and
  registered fixtures: a tree with other files may hold a run's output, so it waits on its owner (§5). `tools/sweep.sh`
  (§2) checks every request not yet finished (a dead runner's doesn't count), Kueue workloads and pods not finished, fill
  jobs queued or running, and every process's cwd, root, open files, maps, argv and environment. A tree whose ship is reused
  keeps its first mtime, so its age is from when it was shipped; a deleted tree is re-shipped from the node's bare repo.
- node 1's infra job trees in `/workspace/jobs/src` older than 6 h (Daniel's ruling on card `396420c8`, 8:59 PM PDT 1 Oct,
  with infra's two rules). This covers per-pod copies (`<hostname>`, `pod-<hostname>`, `*-head`) whose pod is not live,
  and content copies (`<id16>`, aged by the newest `by-pod/*` file naming them) that no live pod names. A copy without
  `.copied` is kept. The pass renames each copy into `jobs/src/.trash`, re-checks, and puts back anything named since.
  `sweep.sh` runs it on node 1 only (`node-sweep.sh --jobs-src`).

Every deletion is logged in §4 (path, size, age). Slack hears of it only if it frees over 50 GB.

### Ask the owner first
The steward asks on Slack `--as infra`, prefixed "resource-steward:", tags the owning handle, and waits for a yes:
- weights in `/workspace/hf` and `/workspace/jobs/hf` (@circuits, @proofs, @compute-accounting);
- replay bundles, sealed or `.partial` (@circuits);
- `/workspace/pouw/*` (@compute-accounting);
- `/workspace/research/runs/*` entries, preserved or not (the owning lane, through its coordinator);
- anything else it isn't sure of.

Anything destructive beyond this policy goes to Daniel as a blocking `#ask-daniel` card.

### Hard stops
- Node 2's `/workspace` at 55%: no new jobs start. node2-ops' runner enforces it; the steward only verifies it. Verified
  22:10Z: `fill_runner.py` refuses new **Verity guest** jobs at `FILL_VERITY_DISK_PCT` = 55. PoUW's own fill isn't under
  that stop, so at 55% the steward asks @compute-accounting to hold new PoUW fill that writes to disk.
- Node 1's `/workspace` at 85%: the steward asks kueue-fold, the nebius-infra steward and @circuits to hold new Builds and Commits.
- Root disk under 45 GB free: no new check starts (check's own preflight floor, `tools/check/preflight.py`, is the same 45 GB).
- Replay RAM is reserved before a Commit is admitted: the steward flags any node where the replay RAM to come is over half of
  its available RAM (after `/workspace/ramlock` reservations).
- Never delete unpreserved run outputs. Never touch `/workspace/pouw/gpu3-fp8`. Nothing runs on node 2 while
  `/workspace/pouw/fill/status.txt` says `timed True` (the tick skips node 2's probe then).

### Thresholds (the probe's watermarks)
| metric | node 1 | node 2 |
|---|---|---|
| `/workspace` used | alert 80%, hard 85% | alert and hard 55% |
| root free | alert < 60 GB, hard < 45 GB | same |
| inodes used, either filesystem | 80% | 80% |
| inode growth, either filesystem | > 100k files/h | same |
| RAM available | < 10% | < 10% |
| replay RAM to come | > ½ available | > ½ available |
| GPU memory at 0% util | > 20 GiB for 15 min | same |
| finished runs without custody, older than 1 h | > 10 | > 10 |

Replay RAM to come is counted differently on each node. On node 1 it is Kueue's pending `*-replay-*` Workloads, each at
max(its memory request, 90 GB). On node 2 it is the queued `verity-replay-*` fill jobs at max(`mem_gb`, 90 GB), plus each
running `verity-commit-*` at 90 GB, since each queues a replay when it ends; a queued Commit reserves nothing until it runs.
The 90 GB floor is a Phi-3/Mistral batch-8 bundle; the requests (64 GB) are lower. GPU idle comes from node 1's Prometheus
(DCGM) and from node 2's sampler JSONL, never from NVML. A run has custody on its node when it has `.custody`, `.fetched`
or `preserved.json`.

### Overlaps: one owner
- Disk, cache and RAM decisions on both nodes: **resource-steward**.
- Enforcement: node2-ops keeps its OOM guard (`node_ops.py`) and its job-start disk stop (the fill runner), but hands disk and
  cleanup decisions to the steward.
- The nebius-infra steward's node-1 disk reporting folds into the steward.
- GPU idle-in-lease and unleased GPUs as job norms stay with node2-ops and kueue-fold (`publish_pool.py`, `pool_n1.py`).
  The steward's 15-minute, 20 GiB rule is about memory held; it doesn't re-alert a GPU those monitors already flagged.
- Handoffs: `note:20260930T2205Z-handoff-from-resource-steward` in `lanes/node2-ops/` and `lanes/nebius-infra/`.

### Daily
At 8 AM PDT (15:00Z), a summary in `#agent-coordination` (`--as infra`, "resource-steward:"): headroom per node and
resource, what was deleted, what waits on an owner, and trends (from each node's `~/.local/state/resource-steward/history.jsonl`).

## 2. Probe
- `tools/research/src/research/pods/nebius/resource_probe.py` on `infra/nebius` (`233f451f2`, then `7bcf2fc5f`: inode growth
  is measured against a base reading at least 15 min old), with its test `tools/research/tests/test_nebius_resource_probe.py`
  (12 tests).
- Deployed at `~/resource-steward/bin/resource_probe.py` on both nodes (sha256 `18d5fde99a73…`, `infra/nebius` `f2d8decc9`,
  1 Oct 07:45Z; 14 tests), by install and rename.
- The tick is `lanes/resource-steward/tools/tick.sh`: the probe on both nodes (node 2 only while `fill/status.txt` says `timed
  False`; a missing or unreadable status skips it, as does a timed window), plus new
  resource `*alert*` notes. It exits 1 only for a new kind of breach, a HARD stop, a failed probe or a new alert note; a known
  breach prints as `known:` and exits 0. `tools/bootstrap.sh` restores the agent VM after a reset (no secrets).
- The sweep is `lanes/resource-steward/tools/sweep.sh` (every 6 h at :30, timer `resource-steward-sweep`): it installs
  `tools/node-sweep.sh` on each node and runs it as root at `nice 19 ionice -c3`, node 2 only while its status says `timed
  False`. It
  deletes exactly the policy's source trees (`--src-age-h`, 24 by default) and check scratch (`/tmp/pytest-of-research/pytest-*`,
  `lean-audit-scratch-*`), keeps anything something live names, and logs every line to `~/resource-steward/deletions.log`. A
  tree is renamed into `src/.trash/` before it is deleted and put back if a scan after the rename finds a reference, so the
  launcher never sees a half-deleted ready tree. `--dry-run` lists without deleting. Exit 1 means something was deleted.
  Each node writes every line to its own `~/resource-steward/node-sweep.log` before printing it, and finishes when its ssh
  drops, so that log is the record of a sweep whose ssh dropped. `sweep.sh` skips a node where a sweep is still running. A
  refused request (`runs/<id>/refused.json`) doesn't hold its tree: it never runs.
- It reads statvfs, `/proc/meminfo`, the ramlock dir, Kueue (node 1) or the fill queue (node 2), Prometheus (node 1) or the
  sampler JSONL (node 2), and the run dirs. It takes 0.1–0.8 s at `nice 19`, and never deletes, stops a process or touches NVML.
- Exit codes: 0 means all clear, 1 a breach (one line each), 2 a failed source (never read as all clear).
- Each node keeps its state and history in `~/.local/state/resource-steward/`.

## 3. Baseline (30 Sep 2:55–3:05 PM PDT, 21:55–22:05Z)
| | node 1 (vy-nebius-1) | node 2 (vy-nebius-2) |
|---|---|---|
| root | 155 GB free of 265 (42%), inodes 5% | 199 GB free (26%), inodes 3% |
| `/workspace` | **71%**, 1.58 TB free of 5.39 TB, inodes 35% | **36%**, 3.46 TB free, inodes 11% |
| RAM available | 1,308 GB of 1,800 (73%); shmem 91 GB | 1,531 GB (85%) |
| ramlock reservations | none | none |
| replay RAM to come | 4 pending replay Workloads × 64 GB request (360 GB at the floor), ½ available = 654 GB: OK | 0 (14 Commits queued, none running): OK |
| GPUs holding memory at 0% | GPU 0 (53 GB) and GPU 2 (49 GB), 15 min+, both `nd-vllm-epoch-run-*-gpu-0` in `deployments-gpu`; `pool_n1` flags them too | none |
| runs without custody, > 1 h | 1 (`r20260930-080414-bae0`, failed) | **13**: see §5 |
| `~/.cache/verity-check` | 35 GB (lean-deps 34, circuit-check 0.9); no scratch | 35 GB (lean-deps 34); no scratch |
| uv / Triton / vLLM caches | `~/.cache/uv` 1.0 GB, `/workspace/cache` 26.5 GB, `/workspace/jobs/cache` 20.0 GB | `/workspace/cache` 29.1 GB, `/workspace/jobs/cache` 0.5 GB, `~/.cache/vllm` 44 MB |
| weights | `/workspace/hf` 2.92 TB | `/workspace/hf` 175 GB, `/workspace/jobs/hf` 121 GB |
| `/workspace/research/runs` | 57 GB (344 dirs) | 122 GB (572) |
| `/workspace/research/src` | 162 GB (181 trees, oldest 05:22Z) | 38 GB (272) |
| `/workspace/research/trees` | 62 GB | — |
| `/workspace/jobs` | **517 GB** (runs 149, flock-sweep2 87, probe-jit 80, cov 76, store 38, src 34, flock-v2 19, flock-m0 18, venv312 11) | 140 GB |
| `/workspace/pouw` | — | 1.36 TB |
| `/tmp` (root disk) | 21 GB, 20 GB of it `pytest-of-research` | 3 GB |
| replay bundles found | 1 × 0.56 GB (`research/runs/cfgtp2-cpu`); the 60 GB and 11 GB `.partial` bundles in `probe-jit` are gone | none |

Node 1's `/workspace` has grown from 69% at 2:24 PM PDT to 71%, and `/workspace/jobs` from 398 GB to 517 GB. At 1.58 TB
free, it reaches the 80% alert after about 0.48 TB more. The trend line starts with the next ticks.

## 4. Deletions
- 04:03Z (9:03 PM PDT), node 1, check scratch under `/tmp/pytest-of-research` (policy: untouched for more than 2 h, no open
  files; each directory re-checked for both just before `rm`): 15 directories, 226,587 files, 14.6 GB.

  | directory | files | MB | newest file (UTC) |
  |---|---:|---:|---|
  | `pytest-1` | 15,178 | 2,084 | 09-30 06:01 |
  | `pytest-23` | 17,759 | 414 | 09-30 07:50 |
  | `pytest-24` | 17,741 | 414 | 09-30 07:50 |
  | `pytest-25` | 17,868 | 414 | 09-30 07:50 |
  | `pytest-51` | 19,419 | 1,950 | 09-30 07:35 |
  | `pytest-52` | 19,348 | 1,181 | 09-30 07:35 |
  | `pytest-53` | 24,007 | 2,412 | 09-30 07:44 |
  | `pytest-239` | 16 | 1 | 09-30 12:14 |
  | `pytest-310` | 365 | 1,703 | 09-30 14:37 |
  | `pytest-388` | 115 | 570 | 09-30 15:43 |
  | `pytest-402` | 15,773 | 2,913 | 09-30 16:06 |
  | `pytest-489` | 76,834 | 508 | 09-30 18:45 |
  | `pytest-509` | 2,100 | 19 | 09-30 19:15 |
  | `pytest-835` | 58 | 3 | 10-01 01:46 |
  | `pytest-844` | 6 | 1 | 10-01 01:46 |

  Root went from 74 GB to 60 GB used and from 808k to 582k inodes. Kept: `pytest-945` onward (written within 2 h;
  `pytest-948` held open), and `/tmp/sm120-base-*`, `/tmp/sb*` (about 47k files, owner unknown, not check scratch).
- 05:42Z (10:42 PM PDT), first `tools/sweep.sh` (policy: source trees over 24 h that nothing live names; check scratch):
  - node 1, 6 source trees, 27,033 files, 489 MB. Two of them (`b82f1dd2`, `6d7e2998`) were named only by five requests
    from 30 Sep 05:21–05:29Z whose runners died at launch (`PermissionError: '/root/dm'`, no `status.json`).

    | tree | files | MB | age |
    |---|---:|---:|---|
    | `4464033f046872a02bb182b07326bd00c53d50ac` | 4,422 | 78 | 24 h |
    | `5f740e972d79fdbd7021b4fb7374568f6dcb728b` | 4,918 | 99 | 24 h |
    | `6d7e2998642f2b87de6de9f6992a3f961a18cd68` | 4,422 | 78 | 24 h |
    | `b82f1dd2be55056823e295b088524777a287eaa6` | 4,419 | 78 | 24 h |
    | `fa6190a020a35ad1e2f681648239822d2b62a9bb` | 4,427 | 78 | 24 h |
    | `fd47cdd1b8e2a012a30bd9dcf7ae59642dcdafb1` | 4,425 | 78 | 24 h |
  - node 2, `/tmp/pytest-of-research/pytest-104`, 258 files, 12 MB, 8 h. Kept `pytest-120` and `pytest-165`, both untouched
    for 2 h but held open by a live `python`.
- 06:25–08:00Z (11:25 PM–1:00 AM PDT), the first 6 h sweep (policy: Daniel's 6 h ruling; source trees over 6 h that nothing
  live names and that hold nothing outside their commit), in two runs: **481 source trees, 5.73M files, 281 GB** (MB from
  `du -m`), plus node 1's `/tmp/pytest-of-research/pytest-945` (613 files, 1,557 MB, untouched 4 h). The list of every
  tree deleted or kept, with its reason, is `art:0e02599e4fcd2a49ee1f4b6bdc2591cbc67be3642c345fd9f4a21054833ee099`.

  | | trees | files | MB |
  |---|---:|---:|---:|
  | node 1, run 1 (from 06:25Z), printed | 37 | 866,247 | 49,469 |
  | node 1, run 1, after its ssh dropped (sizes from the 06:20Z dry run) | 24 | 297,166 | 13,667 |
  | node 1, run 2 (07:56–08:00Z) | 136 | 2,821,372 | 156,675 |
  | node 2, run 1 | 283 | 1,738,283 | 60,892 |
  | node 2, run 2 | 1 | 4,649 | 261 |
  | **total** | **481** | **5,727,717** | **280,964** |

  - Run 1's ssh to node 1 dropped ("server not responding") during node 1's load spike (§6). The node went on deleting
    without printing, 24 trees in sha order from `34c1f5ec…` to `51318a6e…`, until a write to the closed pipe stopped it
    before the check scratch; `src/.trash` was empty. They are found as the dry run's candidates that are neither printed
    nor still on disk.
  - After: node 1 has 62 trees (38 GB), `/workspace` at 35% space and 37% inodes (47% before run 2); node 2 has 45 trees,
    `/workspace` at 38% and 12%.
  - Kept: 12 trees that hold files outside their commit (deleted at 08:28Z once their owners said yes, below); trees a live process, fill job or open request names
    (node 2: seven); node 1's `16b6f334`, `3604bf9e` and `6043b4b6`, named only by refused requests, which the scan now
    ignores (they go at the 12:30Z sweep); node 2's `pytest-120` and `pytest-165` (held open).
- 08:27–08:28Z (1:27–1:28 AM PDT), `sweep.sh --src-age-h 6 --approved` (policy: the owner-asked trees of §5 once their
  owners said yes, checked as below; the rest by the 6 h rule and the 2 h scratch rule): 35 entries, 777k files, 51.4 GB.
  - Owner-approved, 12 trees, 329,594 files, 17,144 MB. Node 1: `9b88cb01` (302,515 files, 16,594 MB, 19 h), `29f691be`,
    `c379497f`, `ddeabc86`, `e3238d3c`, `b84e85ef` (about 4,450 files and 79 MB each, 23–25 h). Node 2: `0555d893` (4,510
    files, 131 MB, 26 h), `1fbf4fbd`, `2dfaf436`, `7d9c944b`, `80a4c8ff`, `adb66134` (47 files and 4–7 MB each, 25–26 h).
  - 6 h rule, 20 trees, 447,390 files, 23,263 MB. Node 1, 13: `0e4cd04e`, `11b1c45f`, `16b6f334` (11 h), `2ebe0d68`,
    `3604bf9e` (18 h), `4860d817`, `551a6cdd`, `6043b4b6` (26 h), `8ce49ec0`, `8fb77458`, `a406b12d`, `c22a06d9`,
    `c4c5ba9d`. Node 2, 7: `0e0f9678`, `209cce5a`, `5b4815a6`, `6a1a051f` (24 h), `784471db`, `7a853670`, `c354ca9e`. The
    rest were 6 h old, 4,600–29,900 files and 84–1,697 MB each.
  - Check scratch on node 1, 151,747 files, 11,039 MB: `lean-audit-scratch-lwqhx813` (142,654 files, 9,324 MB),
    `/tmp/pytest-of-research/pytest-1092` (9,024 files, 1,714 MB) and `pytest-1093` (69 files, 1 MB), all untouched 2 h.
  - After: node 1 has 50 trees, `/workspace` at 36% space and 35% inodes; node 2 has 40 trees, at 40% and 13%.
- 11:15Z (4:15 AM PDT), node 1, check scratch under `/tmp/pytest-of-research`: 4 directories, 17,841 files, 4.65 GB. The
  policy allowed it: each was untouched for over 2 h, had no open files, and the PID in its pytest `.lock` was dead.
  `pytest-1094` (245 files, 1,702 MB, last written 06:35Z), `pytest-1122` (251 files, 11 MB, 06:30Z), `pytest-1194` (16,438
  files, 2,915 MB, 08:15Z) and `pytest-1245` (907 files, 22 MB, 08:43Z). Root free went from 160 to 164 GB.
- 12:38–12:39Z (5:38–5:39 AM PDT), the 6 h sweep (`sweep.sh --src-age-h 6`): 39 entries, 778,039 files, 40.8 GB.
  - Node 1, 26 trees, 578,825 files, 30,255 MB: `016d97bd`, `0423128a`, `0e991d9d`, `22fe745f`, `4fc658ce`, `53cc3d99`,
    `59eedcc0`, `6221a271`, `6454cc3a`, `67f82b87`, `68e7d205`, `6db2c066`, `72aacf9b`, `780673e7`, `7c80f77e`,
    `a905d170`, `ad9f93b0`, `ae902546`, `b08e5e6b`, `b3e7e093`, `b7dd48f0`, `c8442c22`, `df081875`, `ee7b8c26` (10 h),
    `fb8f525c`, `fc8eac5a`. The rest were 6–8 h old, 4,848–30,039 files and 87–1,701 MB each.
  - Node 2, 9 trees, 194,298 files, 10,453 MB: `036fe6f9`, `2b2aa982` (15 h), `4df4bfea`, `815bc58e` (14 h), `947f1de2`,
    `ee47ec2c` (14 h), `efd5739b`, `f50b7605`, `fbce5a2f`. The rest were 6–8 h old.
  - Check scratch, 4 directories, 4,916 files, 66 MB: node 1 `pytest-1329` and `pytest-1336`, node 2 `pytest-120` and
    `pytest-165`.
  - Kept, 10 trees, all on node 2.
    - Seven are named by live processes, by fill queue entries, or by request `r20260930-112057-cff1`.
    - Three (`8aa9452d`, `b3b268ca`, `f6b39a2b`, 140 MB each, shipped 04:41–06:35Z) hold two generated files outside
      their commit, under `integrations/vllm/out/gen/r9/cmt-hidden/src/`. They are too small to ask about.
  - After: node 1 has 68 trees, with `/workspace` at 38% space and 39% inodes and root at 193 GB free. Node 2 has 77
    trees, at 48% space and 10% inodes.
- 18:17–18:20Z (11:17–11:20 AM PDT), `sweep.sh --src-age-h 6`, run from the 18:06Z tick's inode HARD line (§6) instead of
  waiting for the 18:30Z timer: 127 entries, 1,850,993 files, 92.3 GB.
  - Node 1, 67 trees, 1,079,105 files, 53,454 MB: `04af3429`, `063d6d2b`, `08a869fc`, `127fb3cc`, `15159f7d`, `21a3d38d`
    (10 h), `23f2018c`, `291877ee`, `2b52f034`, `2fdd1105` (11 h), `31ef5e28`, `33e10236`, `34eb7edc`, `35d14750`,
    `36102418` (10 h), `3b6653dd`, `3c81408b` (11 h), `4127073f`, `43d7e430`, `443538fe`, `46c768b2` (10 h), `4e2a7abc`
    (11 h), `4f1fd43d`, `4ff29e61`, `5d90708f` (10 h), `63f836e2`, `67c2055f`, `6f8da256`, `71eca2f7`, `734ed97b`,
    `77a7b6dc`, `8150148d`, `88930666` (11 h), `8c2c9c21` (11 h), `8d3a0046`, `8d4b9f30`, `92849f82` (11 h), `97c7ed11`,
    `9d19a91d` (10 h), `9ec8b794` (10 h), `a009c1cb`, `aac15370` (10 h), `abfbbc9c`, `ac502b63` (10 h), `aeee0d32`
    (10 h), `b06cf4ae`, `b737755b`, `b9b27dc2`, `bdedc145`, `c0097b93`, `c07b1d4c` (11 h), `c0d8216d` (10 h), `c2cc505b`
    (11 h), `d7691fc6` (10 h), `d9e9ba1e`, `dfc7cc21`, `e272fb46`, `e79b4aee`, `ea8cc26a`, `eb8cb916`, `eb995b2c`,
    `ef6a3e74`, `f2a572cf`, `f49f0415`, `f6697c66`, `f7c0bd24` (10 h), `fdb178ee`. The rest were 6–9 h old, 4,863–30,412
    files and 88–1,712 MB each.
  - Node 2, 50 trees, 423,508 files, 15,781 MB: `064d1522` (11 h), `09c81e87`, `116d8590`, `14c4a047`, `1fa67c4b` (10 h),
    `1ff24ad5`, `223e3e0e`, `25d54031`, `301c31d1`, `36584b4b` (10 h), `37008e8a` (15 h), `377b7c48` (10 h), `408a7470`,
    `43dc9fe2` (10 h), `43e8dc44`, `453abfb0`, `4dd558a5`, `51a7a69b`, `553a1b49` (17 h), `5776475f`, `5a7f8aff` (11 h),
    `678b7d29` (10 h), `6c983266` (10 h), `6e5b9c70`, `7777c3d9`, `8150148d`, `86351426` (10 h), `8e91aeb6`, `923b5acb`
    (11 h), `9abbecb0`, `9bea11bf`, `9ec8b794` (10 h), `a371a25d`, `a3fa6642`, `a4e2e108`, `b737755b`, `b79830ad`,
    `bdedc145`, `be89244f`, `c2cc505b` (11 h), `c382dd84`, `d664e854`, `d91928ee`, `dfc7cc21`, `e5b6661a`, `eb6b83a5`,
    `ecf7d9e3`, `ef1042a0`, `f9b0d16d` (11 h), `fb2ec7d8`. The rest were 6–9 h old, 4,844–30,351 files and 87–1,711 MB.
  - Check scratch, node 1, 348,153 files, 23,012 MB: `lean-audit-scratch-f7jkfxj1` (321,002 files, 19,771 MB, last
    written about 14:11Z; left by a `check` that ended without its `finally`, since `lean_audit.py` removes its scratch
    otherwise), and `/tmp/pytest-of-research/pytest-1454`, `-1489`, `-1491`, `-1631`, `-1635` (16,812 files, 3,071 MB),
    `-1678` and `-1700`. Node 2: `pytest-567` and `pytest-614` (227 files, 3 MB).
  - Kept, 24 trees, all on node 2:
    - five are named by live processes, fill queue entries or request `r20260930-112057-cff1`;
    - four hold the two generated `integrations/vllm/out/gen/r9/cmt-hidden/src/` files: `8aa9452d`, `b3b268ca`,
      `f6b39a2b` (as before) and `375a32bd`;
    - fifteen have no `READY.json`, or no `.git` and a commit the bare repo lacks (`5f21ea3d`). All are 88 MB, shipped
      07:25–11:38Z, 1.3 GB together. They are too small to ask about.
  - After: node 1 has 32 trees, `/workspace` at 44% space and 43% inodes (47% before), root 181 GB free. Node 2 has 48
    trees, at 52% space and 10% inodes, root 184 GB free.
- 18:38–18:42Z (11:38–11:42 AM PDT), the 6 h sweep (`sweep.sh --src-age-h 6`): 8 entries, 23,016 files, 7.1 GB.
  - Node 1, check scratch, 4,862 files, 3,916 MB: `/tmp/pytest-of-research/pytest-1798` (422 files, 1,601 MB),
    `-1799` (244 files, 328 MB), `-1801` (305 files, 1,601 MB) and `-1803` (3,891 files, 386 MB), all 2 h old.
  - Node 2, 2 trees, 9,945 files, 179 MB: `888c8aed` (4,966 files, 89 MB, 6 h) and `d099b8f3` (4,979 files, 90 MB, 6 h).
    Check scratch: `pytest-615` (5,952 files, 3,024 MB) and `pytest-616` (2,257 files, 12 MB), both 2 h old.
  - Kept: the same 24 node 2 trees as at 18:17Z.
- 20:08–20:13Z (1:08–1:13 PM PDT), the 6 h sweep run from the 20:03Z tick (`sweep.sh --src-age-h 6`): 25 entries,
  774,936 files, 43.5 GB.
  - Node 1, 10 trees, 190,880 files, 9,871 MB, 6–7 h old: `27f6a0a0`, `31c1117c`, `4d44830f` (7 h), `55aebcc5` (8,499
    files, 311 MB each), `4473e281` (30,276 files, 1,709 MB), `86d68c2d` (29,405 files, 1,669 MB), `b27b69c1` (7 h,
    30,737 files, 1,720 MB), `b3b4c843` (30,735 files, 1,720 MB), `b3f1912a` (30,666 files, 1,718 MB), `da9a9cfe` (5,065
    files, 91 MB).
  - Node 1, check scratch, 507,650 files, 31,552 MB, both 2 h old: `lean-audit-scratch-otchoghv` (493,976 files, 28,716
    MB, last written 18:08:18Z, an orphan of a cancelled `check`) and `/tmp/pytest-of-research/pytest-1865` (13,674
    files, 2,836 MB).
  - Node 2, 12 trees, 76,406 files, 2,118 MB: `05f8d08a` (7 h), `28710983`, `87510450`, `c38a5bd9` (8,501–8,504 files,
    311 MB each), `06cf2201` (5,192 files, 94 MB), `087f33d5` (4,905 files, 88 MB), `2e1a9268`, `dabb17c0` (4,968 files,
    89 MB each), `b3f1912a` (5,415 files, 98 MB), `7aa3abf6` (21 h, 5,653 files, 139 MB), `9d5abb09` (33 h, 5,644 files,
    138 MB), `bf77c948` (25 h, 5,648 files, 139 MB); the rest 6 h old.
  - Kept, 25 node 2 trees: `1503e18c` (request `r20260930-112057-cff1`), `91af9a6b` (a live python3), the four
    `cmt-hidden` trees, fifteen without `READY.json` and four with no `.git` and a commit the bare repo lacks (`0d1cc2ef`,
    `335d1f20`, `41a4eeb9`, `5f21ea3d`).
  - After: node 1 has 31 trees, `/workspace` at 45% space and 48% inodes (9.80M; 10.37M at 20:03Z), root 186 GB free.
    Node 2 has 36 trees, at 45% space and 10% inodes.
- 22:16–22:23Z (3:16–3:23 PM PDT), the 6 h sweep run from the 22:15Z tick (`sweep.sh --src-age-h 6`): 14 entries,
  959,384 files, 54.3 GB.
  - Node 1, 6 trees, 132,135 files, 7,073 MB: `2a06c1eb` (7 h, 29,944 files, 1,698 MB), `2d4008ea` (30,748 files, 1,721
    MB), `41157ff3` (30,623 files, 1,715 MB), `b9ec4b1b` (5,475 files, 144 MB), `d784c58e` (5,417 files, 98 MB),
    `de74f334` (7 h, 29,928 files, 1,697 MB); the rest 6 h old.
  - Node 1, check scratch, 771,725 files, 45,088 MB: `lean-audit-scratch-lkzyik2u` (770,175 files, 45,034 MB, last
    written 19:07:22Z, 3 h; an orphan of a cancelled `check`) and `/tmp/pytest-of-research/pytest-1979` (1,550 files,
    54 MB, 2 h).
  - Node 2, 6 trees, 55,524 files, 2,166 MB: `0d2ff8b6` (7 h, 4,865 files, 88 MB), `2a06c1eb` (7 h, 4,992 files, 90 MB),
    `69a2fcdd` (7 h, 4,970 files, 89 MB), `89e87f9e` (4,970 files, 89 MB), `a8ae60ff` (30,735 files, 1,720 MB),
    `de74f334` (7 h, 4,992 files, 90 MB); the rest 6 h old.
  - Kept, 26 node 2 trees: as at 20:08Z, plus `bb934d59` (no `READY.json`; sixteen such now).
  - After: node 1 has 35 trees, `/workspace` at 47% space and 45% inodes (9.20M; 10.03M at 22:15Z), root 190 GB free.
    Node 2 has 32 trees, at 44% space and 10% inodes, root 187 GB free.
- 00:32–00:40Z (5:32–5:40 PM PDT), the scheduled 6 h sweep (`sweep.sh --src-age-h 6`): 17 entries, 321,234 files,
  19.1 GB.
  - Node 1, 13 trees, 291,687 files, 15,628 MB, 6–8 h old: `1f201190` (7 h, 30,759 files, 1,721 MB), `5fd4715d` (8 h,
    28,124 files, 1,627 MB), `6a0818b8` (29,693 files, 1,675 MB), `7597f7db` (8 h, 28,093 files, 1,626 MB), `8ceb3a47`
    (8 h, 30,606 files, 1,714 MB), `9890ad47` (5,441 files, 99 MB), `9cf20f6f` (30,707 files, 1,719 MB), `b455b194` (8 h,
    5,417 files, 98 MB), `c2ba8c7f` (7 h, 30,692 files, 1,719 MB), `c3624304` (30,674 files, 1,718 MB), `e06d821c`
    (30,623 files, 1,715 MB), `ec6db628` (7 h, 5,441 files, 99 MB), `fb524e14` (8 h, 5,417 files, 98 MB); the rest 6 h.
  - Node 1, check scratch, 18,352 files, 3,244 MB, both 2 h old: `/tmp/pytest-of-research/pytest-2207` (17,040 files,
    3,236 MB) and `pytest-2227` (1,312 files, 8 MB). No orphaned Lean scratch this time.
  - Node 2, 2 trees, 11,195 files, 204 MB: `9cf20f6f` (7 h, 5,456 files, 99 MB) and `cd884174` (6 h, 5,739 files,
    105 MB).
  - Kept: the same 26 node 2 trees as at 22:16Z. No `STUCK` lines.
  - After: node 1 has 49 trees, `/workspace` at 57% space and 48% inodes (9.86M), root 188 GB free, `jobs/src` at 850
    copies. Node 2 has 32 trees, at 38% space and 10% inodes, root 184 GB free.
- 03:01–03:08Z (8:01–8:08 PM PDT), the 6 h sweep run from the 03:00Z tick (`sweep.sh --src-age-h 6`): 17 entries,
  344,615 files, 17.9 GB.
  - Node 1, 14 trees, 328,809 files, 17,585 MB, 6–8 h old: `213f4361`, `30344d13`, `32396cc4`, `e925be34` (6 h),
    `6f371128`, `789f4257`, `bab22b23` (7 h), `8ce87f6f`, `cbda4b67`, `d23f7936` (8 h), each 30,631–30,746 files and
    1,716–1,721 MB; `33f2b1d3`, `7f019198`, `d8e1a566` (8 h) and `85778c4d` (7 h), 5,417–5,466 files and 98–99 MB each.
  - Node 2, 3 trees, 15,806 files, 287 MB: `3403247f` (6 h, 5,471 files, 100 MB), `6d76e5e8` (7 h, 5,438 files, 99 MB),
    `b959acdf` (8 h, 4,897 files, 88 MB).
  - Kept: the same 26 node 2 trees as at 22:16Z. No check scratch was old enough, and no `STUCK` lines.
  - After (03:08Z): node 1 has 58 trees, `/workspace` at 60% space and 52% inodes (10.52M; both live audits had
    finished), root 192 GB free.
- 06:09Z (11:09 PM PDT), the 6 h sweep run early from the 06:07Z tick's HARD line (`sweep.sh --src-age-h 6`): node 1
  only, 26 trees, 606,594 files, 32.1 GB. Node 2 was not swept: I edited `sweep.sh` while it ran, bash read a fragment
  (`ntf: command not found`) and stopped on a syntax error. `sweep.sh` now runs as one function, so a later edit cannot
  reach a running sweep.
  - 14 trees 6 h old: `4ddd7a5a`, `9e2ca94d`, `a72455b8`, `aa2dd5dc`, `d9c5b0f3`, `fc9b4029` (30,686–30,768 files,
    1,719–1,722 MB each), `210d32e1` (25,066 files, 1,079 MB), `cb3bd6c6` (25,195 files, 1,213 MB), and `06fa0be0`,
    `2f6d09ac`, `455a0104`, `4f96f82a`, `73041968`, `998ac159` (5,457–5,472 files, 99–100 MB each).
  - 7 h: `50fdfe55`, `51069d4a`, `68f4f081` (30,700–30,714 files, 1,719–1,720 MB), `7af1b472` (27,357 files, 1,596 MB),
    `3cd1e329` (5,474 files, 100 MB). 8 h: `0bacf0ca`, `402c53cb`, `524c1282`, `d93e796e`, `e823817d` (30,677–30,780
    files, 1,717–1,722 MB), `18e9fbe1` (29,866 files, 1,680 MB). 9 h: `53eb34e8` (30,716 files, 1,719 MB).
  - Kept: `62e3c42b` (419 files outside its commit). Node 1 went from 59% to 55% inodes (11.25M).
- 06:16–06:23Z (11:16–11:23 PM PDT), the first sweep with `jobs/src` (`sweep.sh --src-age-h 6`, `--jobs-src` on node
  1): 841 entries, 4,146,357 files, 79.1 GB.
  - Node 1 `jobs/src`, 836 entries, 4,071,533 files, 75,455 MB, 6–41 h old: 665 per-pod copies (3,187,404 files,
    57,384 MB; `nd-proofs-bf16-hi-*`, `nd-proofs-flock-f-*`, `nd-assumption-swe-*`, `nd-backend-sweep-*` and the Sep 30
    `*-head` ones) and 171 content copies (884,129 files, 18,071 MB). The per-entry lines are in node 1's
    `~/resource-steward/node-sweep.log` and this VM's `~/resource-steward/deletions.log`. Nothing was put back, nothing
    `STUCK`. Afterwards all 14 live pods with a `by-pod` file still had their copy, with `.copied`.
  - Node 1 source trees: `3e44638d` (6 h, 27,357 files, 1,596 MB) and `d2b57788` (6 h, 30,775 files, 1,722 MB).
  - Node 2 source trees: `3ae34fb0` (7 h, 5,438 files, 99 MB), `97e90885` (8 h, 5,782 files, 105 MB), `fa3c22ed` (7 h,
    5,472 files, 100 MB). Kept: the same 26 node 2 trees.
  - After: node 1 `/workspace` at 36% inodes (7.40M), `jobs/src` down to 175 entries.

- 06:30–06:33Z (11:30–11:33 PM PDT), the scheduled 6 h sweep (`sweep.sh --src-age-h 6`, `--jobs-src` on node 1): 6
  entries, 55,814 files, 2.2 GB, all on node 1 and all 6 h old.
  - Source tree `7392c51c` (30,748 files, 1,721 MB).
  - `jobs/src`: content copy `21e1a5a3ab7af866` (5,446 files, 99 MB), and per-pod copies
    `nd-circuits-ed4f8b2204-prover-d-0-dq67n` (5,484 files, 100 MB), `nd-proofs-bf16-hi-0a8d1797a7-prover-b-0-s787j`,
    `-29417a4eac-prover-b-0-nc7cg` and `-7dd07e18c4-prover-b-0-gqgxf` (4,700–4,718 files, 84 MB each).
  - Kept: `62e3c42b` on node 1 and the same 26 node 2 trees. No `STUCK` lines.

- 08:21–08:23Z (1:21–1:23 AM PDT), the sweep a one-off timer ran for the Lean scratch `ju7dx3l8` (`sweep.sh --src-age-h
  6`): 50 entries, 548,104 files, 26.9 GB. `ju7dx3l8` itself was kept: a file in it was last written 113 min before, so it
  was under the 2 h rule. The 12:30Z sweep takes it if it is still idle.
  - Node 1, 17 source trees, 378,970 files, 19,645 MB. 6 h: `31f68948`, `42d7c299`, `7ec45f5e`, `96c6e103`, `eb33e23f`
    (30,698–30,760 files, 1,718–1,722 MB each), `fdb598b7` (27,803 files, 1,610 MB), `50bcd017` and `e43f30d1` (5,477–5,480
    files, 100 MB each). 7 h: `b59b4a88`, `d75d2f23`, `ee629453` (30,640–30,785 files, 1,718–1,723 MB each), `ec34d069`
    (27,804 files, 1,614 MB), `3044a24e` and `3b1d7b1b` (25,073–25,116 files, 1,079–1,080 MB each), and `0e6a848c`,
    `20235b3e`, `ce0e6081` (5,473–5,479 files, 100 MB each).
  - Node 1 check scratch, 2 h old: `/tmp/pytest-of-research/pytest-3015` (17,356 files, 2,920 MB), `pytest-3024` (3,187
    files, 1,617 MB) and `pytest-3025` (64 files, 1 MB).
  - Node 1 `jobs/src`: 4 content copies, 23,625 files, 526 MB: `15417a6884b2eb85` (6 h, 6,057 files, 155 MB),
    `4437db44ac250cd4` (7 h, 5,597 files, 102 MB), `a83836a28ff005d6` (6 h, 6,098 files, 158 MB) and `f578f1f6fcf1eb79` (7 h,
    5,873 files, 111 MB). And 24 per-pod copies, 113,949 files, 2,032 MB, 6–7 h old: `nd-circuits-c240fe2a0b-prover-d-0-z7mbg`
    (5,490 files, 100 MB) and 23 `nd-proofs-bf16-hi-*-prover-b-0-*` (4,700–4,718 files, 84 MB each).
  - Node 2, 2 source trees, 10,953 files, 200 MB: `20235b3e` (7 h) and `e43f30d1` (6 h), 100 MB each.
  - Kept: `62e3c42b` on node 1 and 28 trees on node 2. No `STUCK` lines.
  - After: node 1 at 8.15M inodes (40%), with four Lean scratch trees, one of them live.

- 09:55–09:59Z (2:55–2:59 AM PDT), the 6 h sweep run early from the 09:53Z tick's HARD line (`sweep.sh --src-age-h 6`):
  59 entries, 1,151,203 files, 70.4 GB.
  - Node 1, three idle Lean scratch trees with no process in them, 640,638 files, 37,985 MB:
    `lean-audit-scratch-_647d3r9` (last written 159 min before, 319,367 files, 18,558 MB), `ju7dx3l8` (202 min, 320,928
    files, 19,420 MB) and `ig8jestc` (135 min, 343 files, 7 MB). Verity #708, which stops a cancel orphaning them, is still
    a draft.
  - Node 1 check scratch, 42,279 files, 14,434 MB: `/tmp/pytest-of-research/pytest-3028` (3 h, 17,325 files, 3,118 MB),
    `-3029` (3 h, 7,041 files, 5,292 MB), `-3030` (3 h, 17,355 files, 2,920 MB), `-3108` (2 h, 305 files, 1,601 MB) and
    `-3149` (2 h, 253 files, 1,503 MB).
  - Node 1, 12 source trees, 268,472 files, 14,178 MB. 6 h: `10b608cb`, `1992d95c`, `986b3513`, `b8a769d1`, `fbd4a796`
    (30,699–30,873 files, 1,718–1,724 MB each), and `4468f3cb`, `63ce2ea1`, `9c447115` (5,480–5,541 files, 100–101 MB
    each). 7 h: `206b4520`, `70380622`, `b1bf0915` (30,851–30,865 files, 1,724 MB each) and `794de4ee` (5,534 files,
    100 MB).
  - Node 1 `jobs/src`, 38 per-pod copies, 194,334 files, 3,693 MB, 6–7 h old: 28 `nd-proofs-zk-cell-*` (5,084–5,106 files,
    92 MB each), 7 `nd-proofs-vllm-de-*`/`-vllm-mo-*` (4,673–5,871 files, 83–150 MB) and 3 `nd-proofs-bf16-hi-*` (4,700
    files, 84 MB each).
  - Node 2: source tree `63ce2ea1` (6 h, 5,480 files, 100 MB).
  - Kept: `62e3c42b` on node 1 and 29 trees on node 2. The new one is `f6173040` (no `.git`, and the bare repo lacks its
    commit). No `STUCK` lines.
  - After: node 1 at 8.21M inodes (40%), with three live Lean audits.

## 5. Waiting on an owner
- Node 2 has 13 finished runs older than 1 h without custody, which is over the threshold of 10:
  - three are node2-ops' hourly backups that stalled in multipart custody: `r20260930-081105-b32f` (17 GB),
    `-091913-2c58` (17 GB) and `-102051-0e13` (3.9 GB), superseded by chunked backups since 10:27Z;
  - ten are small smoke runs (104 KB to 1.2 MB: `true`, `sha256sum` and `bash`) between 14:34Z and 18:55Z, with no lane set.

  Nothing is deleted. The handoff asks node2-ops to publish them or confirm they can be marked superseded. (15 at
  3:40 PM PDT.)
- Node 1 `/workspace/jobs/src` (infra's job trees): 654 copies with 3.16M inodes, and nothing removes them. 533 are older
  than 6 h and named by no Running or Pending pod (about 2.5M inodes). Nothing is deleted.
  `note:20261001T1015Z-ask-from-resource-steward-jobs-src-copies-unreaped` asks infra to approve adding them to the sweep
  and to point `prover-bench` and `prover-dev` at `job_tree.sh`.
  - 01:46Z 2 Oct: 872 copies with 4.23M inodes (41% of node 1's used inodes), up 1.07M since 10:15Z, about 69k/h. By
    prefix: `nd-proofs-bf16-hi` 193, `nd-proofs-flock-f` 126, `nd-backend-sweep` 107, `nd-assumption-swe` 101. The note
    is still `open` with no reply. Node 1 sits near 10.1M between scratch bursts, and the bursts reach 2.3M (three
    770k audits), so at 69k/h node 1 crosses 80% around 4 Oct 12:00Z, before the nodes stop. If infra is still silent
    at the 2 Oct 15:00Z daily summary, the deletion goes to Daniel as a blocking `#ask-daniel` card.
  - 03:09Z 2 Oct: escalated early. Lean audits now hold 1.07M inodes each (770k before), up to four at once, which
    moves the projected 80% crossing to about 3 Oct 03:00Z. Blocking card `396420c8-85ef-4b7d-b79c-74eba3446bfe`
    (#approvals `1790910579.790289`, `sub_3254629b`): approve (add them to the sweep), wait (leave them for infra) or
    later (ask again past 70% inodes); recommended approve, default later, deadline 2 Oct 6:00 PM PDT (3 Oct 01:00Z).
    Nothing in `jobs/src` is touched until he answers.
  - 03:17Z 2 Oct: infra replied in the card thread: *Safe: yes*, recommends approve, with two rules. (1) Age a content
    copy by the newest `by-pod/*` file naming it. (2) If the re-check after the trash rename finds a live pod naming
    it, rename it back. At 03:24Z infra opened the source fix, verity #759: `prover-bench`, `prover-dev` and
    `port-capture` delete their per-pod copy when `research run` exits. Old copies and preempted pods' leftovers still
    fall to the sweep.
  - 03:50Z 2 Oct: `node-sweep.sh --jobs-src` implements both rules and is off unless the flag is given. It keeps
    content copies without `.copied` and anything a live pod, a by-pod file written since the rename, or a process
    names, and it stops if `kubectl` fails. Dry run on node 1 at 03:26Z: 811 entries (164 content copies and 647 per-pod
    copies), 3.94M files, 72.9 GB. No live pod's copy was among them, checked separately against the 45 live pods. The
    card is still pending; the flag is not run until Daniel answers.
  - **Resolved.** Daniel chose *Yes: add them to my sweep* at 8:59 PM PDT 1 Oct (03:59Z, by button, so the thread
    subscription never fired; I read it at 06:12Z). The rule is now in §1, and `sweep.sh` runs `--jobs-src` on node 1. First
    run 06:16Z: 836 entries, 75.5 GB (§4).
- Node 1 runs without custody (@infra, asked 05:48Z 2 Oct, #agent-coordination `1790920126.275509`, `sub_89635e42`).
  - 13 failed run dirs in `/workspace/research/runs`, about 2.8 GB. None has `.custody`, and each runner's last line is
    `custody: publishing the attempt…`.
  - Twelve are `check` runs on slots check-a/b/c, cancelled with SIGTERM (rc 143, UNKNOWN_SIGNAL): r20261001-180819-abf7,
    r20261001-183932-4cf9, r20261001-190541-260b, r20261001-212749-07d3, r20261002-011832-62a7, r20261002-012152-3d87,
    r20261002-020141-31a1, r20261002-024708-71e2, r20261002-032418-5560, r20261002-043450-b030, r20261002-043811-6aa7
    and r20261002-044148-7422. The thirteenth, r20260930-080414-bae0, is a 9.5 GiB Lean soundness build (UNKNOWN_EXIT).
    Its runner got SIGTERM during the upload.
  - For r20261002-044148-7422, the ssh session's scope ended 8 s after the SIGTERM (04:44:57Z) with no systemd kill.
    `requests/<id>/custody/cred.json` is still there, so `runner_publish`'s `finally` never ran: something SIGKILLs the
    runner after a cancel. Node 1's logind has KillUserProcesses=no, `mem_guard` is the laptop's, and `node_ops`' guard
    is node 2's.
  - The ask: find the killer, and publish the runs (`research data custody <id> --publish`) or label them. Nothing is
    touched. `--publish` also evicts the run dir's files of 1 MiB and more, so it is the owner's to run.
- Node 1 RAM (@circuits, asked 17:00Z): about 405 GB available. Circuits' three `boolean-replay` runs outside Kubernetes
  hold 800 GB of `/workspace/ramlock` reservations, while vllm-epoch-run replays are still queued in Kueue. The ask:
  start no new `boolean-replay` on node 1 until one finishes, and check that the queued replays fit. Thread
  `1790873900.706599` (`sub_0bac0d2b`).
## 6. Log
- 21:54–22:10Z (2:54–3:10 PM PDT) first turn: set up; took the baseline; committed the probe (`233f451f2`, `7bcf2fc5f`) and
  deployed it on both nodes; wrote this policy; sent handoffs to node2-ops and nebius-infra. Armed the timer
  `sub_2e3eb17f-7145-4485-98f4-f7b34e205e8c` (every 20 min), the daily summary `sub_4f6daaa1-65b4-4661-a34c-164a12906876`
  (15:00Z, 8 AM PDT) and the `#agent-alerts` subscription `sub_f6fd3baf-37fd-4fd9-9065-0f6312611b38` (top level, until 3 Oct
  22:09Z, renewed on every wake).
  Over thresholds now:
  - node 2: 13 runs without custody (handed to node2-ops);
  - node 1: GPUs 0, 2 and 4 hold 48–52 GiB at 0% for 15 min+ (`nd-vllm-epoch-run-*-gpu-0` in `deployments-gpu`),
    already flagged by `pool_n1`'s `gpu-idle-in-lease`, so the steward doesn't re-alert them.
  No Slack post.
- 22:20–22:33Z (3:20–3:33 PM PDT) tick: the agent VM had been reset, and `tools/bootstrap.sh` restored it. A false idle
  on node 1's GPU 0: DCGM's 15-min window spanned a pod handover (the new pod started 22:16Z). Fixed in the probe
  (`a38ac68a2` + `542169a73`): on node 1 a GPU is idle only when one pod held it for the whole window, and GPUs that
  `pool_n1` already flags idle-in-lease are recorded in `idle_gpus_pool_flagged` rather than re-alerted. Known: node 2's
  13 runs without custody (with node2-ops). No deletions, no Slack post.
- 22:40–22:45Z (3:40–3:45 PM PDT) tick:
  - **Node 1 `/workspace` at 77%, up from 71% at 3:05 PM PDT** (about 4–5 GB/min). `/workspace/jobs` went 517 → 736 GB:
    `jobs/runs` 149 → 304 GB, mostly backend-sweep-2's sampled-stage rows (`out/classes`: `r20260930-210718-2f89` 59 GB
    done, `-220453-9cce` 48 GB, `-220453-b99a` 40 GB done, `-220551-3af1` 35 GB, `-223358-1749` 17 GB); `cov` 76 → 144 GB;
    `probe-jit` 80 → 104 GB. The 80% alert is due about 4:20 PM PDT, the 85% hold about 5:15 PM PDT. Asked @proofs on
    Slack (above). Nothing in the policy's delete-without-asking list frees a useful amount: the caches are about 46 GB, and
    no source tree is 24 h old.
  - Node 1 gained 1.47M inodes/h: a one-off. The check-cache move (`r20260930-213917-d6b3`) ran at 22:10Z; `~/.cache/verity-check`
    is now a symlink to `/workspace/research/cache/verity-check`, and root is at 183 GB free.
  - Node 2 root gained 154k inodes/h (3% used). A timed window was running at 22:45Z, so nothing was looked at there.
  - RAM: answered nebius-infra's memory-requests alert with a request policy: Builds 160 → 48 GB, Commits below batch 8
    170 → 64 GB, limits unchanged (`note:20260930T2243Z-handoff-from-resource-steward-ram-requests`, in `lanes/nebius-infra/`
    and `lanes/vllm-epoch-run/`).
- 23:00–23:45Z (4:00–4:45 PM PDT) ticks:
  - Node 1 `/workspace` fell back to 72% by 4:00 PM PDT. @proofs and the old research coordinator answered at 3:44 and
    3:45 PM PDT ([thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790808184589359)): `out/classes` is
    regenerable. The feeder now prunes after each prove (`PRUNE=1`) and keeps at most 2 deployments on disk. They gave their
    yes to delete the surplus, but the lane had cleared it already: at 4:45 PM PDT one running row's 1 GB was left. Nothing
    deleted by the steward; closed in the thread.
  - Fixed `tools/tick.sh`: the breach key dropped the node's digit, so node 2's new inode-growth breach read as node 1's
    known one.
  - Node 2 `/workspace` is gaining about 117k inodes/h (12% used). The driver is `research/src` (about 320k new entries/h,
    one tree shipped per run), and the same holds on node 1. The policy's 24 h cleanup of unreferenced trees starts with the
    one-off timer `sub_27548cd0-02bb-4360-91f0-e8bcf31c9e86` at 1 Oct 05:30Z (10:30 PM PDT).
  - Node 2's runs without custody are up to 21:
    - node2-ops said yes to deleting the three superseded whole-node backups
      (`note:20260930T2215Z-reply-from-node2-ops-unpublished-runs`). They stay anyway, because the steward never deletes an
      unpreserved run output. Node 2 is at 37%, with no pressure.
    - Eight new small PoUW check runs launched without `--custody-r2`: asked @compute-accounting to fetch or publish them and
      to launch with custody ([thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790811792332849)).
    - The ten earlier smoke runs: node2-ops names bc-0f3f8a2f, bc-efe47341 and the nebius-infra steward as likely
      submitters; they stay (under 3 MB).
- 00:00Z (5:00 PM PDT) tick: node 1 `/workspace` is gaining about 336k inodes/h (40% used; space 70%).
  - The driver is `research/src`: about 5–10 trees shipped an hour, each with its own `.venv` (about 22k files) and often a
    Lean `.lake`, so about 24–30k inodes a tree.
  - With the policy's 24 h cleanup (first at 05:30Z), steady state is about 4–7M inodes for `src`, which should keep the
    filesystem under the 80% inode alert.
  - If it doesn't, the next step is to ask the research tool's owner to share one venv per lockfile across trees.
  - No action now.
- 00:20Z (5:20 PM PDT) tick: node 2's inode growth (about 112k/h, `research/src`, as at 23:40Z) came back after dipping
  under the threshold for one tick. `tools/tick.sh` now remembers a breach kind for 6 h, so a metric that flaps around its
  watermark doesn't wake the steward each time. No action.
- 00:40Z (5:40 PM PDT) tick: **node 1 `/workspace` inodes at 42% and rising 0.7–1M/h**, which is 80% in about 8 h (around
  1:40 AM PDT) and exhaustion around 6 AM PDT.
  - The driver is `research/src`: 196 trees hold 4.15M inodes, 3.57M of them in 167 trees older than 6 h (2.28M in 114 trees
    older than 12 h), and none is 24 h old. Each tree carries its own `.venv`. A missing tree is shipped again from the node's
    bare git repo (`remote.ship_source`).
  - A cleanup sooner than 24 h is deletion beyond the policy, so it went to Daniel as blocking card
    `01933aa8-6663-4d2e-989c-7b2d983bddfd` ([card](https://computeverification.slack.com/archives/C0C5UCA0S0Z/p1790815323264569)):
    6 h (recommended), 12 h, or keep 24 h, deadline 11 PM PDT, with a timing correction in its thread. A one-off timer at
    06:00Z checks it.
  - Probe `b27322950` (sha256 `ccf53b63…`, both nodes): inode growth is now HARD when the watermark is under 12 h away, so a
    known breach that escalates still wakes the steward; it had been hidden as `known:`.
  - Node 2 was in a timed window and was skipped.
- 02:20Z (7:20 PM PDT) tick: node2-ops alerted (`note:20261001T0218Z-alert-from-node2-ops-disk-48-pct-mvp-passes`). Node 2
  `/workspace` was at 48% at 7:15 PM PDT, up from 39% at 5:10 PM, so 55% (no new Verity guests) is about 8:45 PM PDT.
  - Drivers: `pouw/mvp-e2e/passes` is 800 GB (11 passes of about 73 GB each); `pouw/gpu3-fp8/out` is 737 GB (untouchable).
  - `/workspace/pouw/*` is compute-accounting's, so asked them about pruning or moving old passes, smaller passes, and holding
    new passes over 52% ([thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790821265698879)).
  - Node 2 was in a timed window, so nothing was inspected there.
  - Custody backlog on node 2 is down to 13 (compute-accounting's eight are preserved).
- 04:00Z (9:00 PM PDT) tick: node 1's root was gaining 326k inodes/h, though at 3% of its 33.4M inodes (80% about 79 h
  away). The writer was check scratch: `/tmp/pytest-of-research` held 249k files. Deleted the 15 directories untouched
  for over 2 h (§4: 226,587 files, 14.6 GB). Root is now at 582k inodes (2%) and 25% used. Pytest scratch accrues about
  300k files/h while checks run, so the src-cleanup step (05:30Z) also sweeps it each time.
- 05:29–05:45Z (10:29–10:45 PM PDT) source-tree cleanup timer: the first trees passed 24 h at about 05:22Z. Wrote
  `tools/sweep.sh` and `tools/node-sweep.sh` (§2) and ran them: §4 lists 6 trees on node 1 (489 MB) and one pytest dir on
  node 2. A first hand check had read its own `sudo` argv and `SUDO_COMMAND` as live references; the scripts read their
  patterns from files. The trees that matter are younger: node 1's 235 trees hold 4.84M of its 9.39M inodes, the biggest
  176k–303k files each (`.venv` and `.lake`), shipped 08:30–13:50Z on 30 Sep, so they pass 24 h between 1:30 and 6:50 AM
  PDT. The sweep now runs every 6 h at :30 (`resource-steward-sweep`), and the 6 h retention card still waits on Daniel.
- 06:03–06:35Z (11:03–11:35 PM PDT) card deadline timer: Daniel had chosen **6 h** on the retention card at 6:58 PM PDT
  (01:58Z). The steward saw the thread event then but didn't act on it, so the 6 h cleanup started four hours late (node 1's
  inodes stayed under 47% throughout). §1 now says 6 h.
  - A 6 h dry run listed 179 trees (221 GB) on node 1 and 285 (56 GB) on node 2. Some were 11–16 GB, so the steward checked
    whether trees hold run outputs. `node-sweep.sh` now keeps a tree with anything outside its commit besides build caches
    and registered fixtures (§5 lists the 13 it keeps). That leaves 176 trees, 3.72M files, 207 GB on node 1 and 280
    trees, 1.65M files, 56 GB on node 2.
  - The real sweep started at 06:25Z in tmux. It rescanned after each rename (about 60–90 s per tree), so `sweep.sh`'s 1 h
    limit stops node 1 at about 07:25Z after about 45 trees, and node 2 then runs the rewritten `node-sweep.sh`. The rewrite
    renames the batch, rescans once (26–38 s per node), deletes, clears what an interrupted sweep left in `src/.trash`, and
    takes a lock. A dry run of it on both nodes made the same decisions. The rest of node 1 goes at the next sweep, and
    §4 gets the totals then.
- 06:40Z (11:40 PM PDT) tick: node 1 GPU 6 held 64 GiB at 0% for 15 min (`pool_n1` hadn't flagged it). The holder was
  `nd-vllm-epoch-run-47a14bf90d-gpu-0-28gfh` (48–64 GiB from 06:00Z, last utilization 7%). It freed the GPU at 06:38Z and
  the pod is gone, so nothing was asked. Node 1's inode growth is under the threshold while the 6 h sweep runs.
- 07:20Z (12:20 AM PDT) tick: node 2 GPU 7 held 48 GiB at 0% for 15 min. The holder was a running vLLM Commit
  (`verity-commit-vllm-epoch-run-cov-cg09.sh`, run `r20261001-070053-839a`, gemma2-2b, owner bc-698052e1, from 07:01Z) at
  100% of one CPU, so it was in a CPU phase with its leased GPU still loaded. There were no lease waiters and 5 of 8 GPUs
  were free, so nobody was blocked and nothing was asked. Commit lease norms are node2-ops' and kueue-fold's.
- 07:40Z (12:40 AM PDT) tick: "queued replay 1080 GB (12 Commits) > half of available RAM 1551 GB" on node 2 was a probe
  bug. The fill runner keeps `.<job>.pgid` and `.<job>.unit` beside each running job, and `pathlib` globs match
  dotfiles, so each of the 4 running Commits counted three times. The real figure is 4 × 90 GB = 360 GB. Fixed in
  `infra/nebius` `f2d8decc9` (a test with the sidecars) and deployed; the breach is gone.
  - `tools/tick.sh`'s dedupe key also replaced the GPU index with `#` (`GPU_5` became `GPU_#`), so every GPU shared one
    breach kind. It keeps the index now (`GPU<5>`). GPUs 4–7 on node 2 are each held by one of the four running vLLM
    Commits (n048-2, n049-2, m001-2, cg09; 48 GiB each, 0% GPU, about 100% of one CPU). Like GPU 7 at 07:20Z, they were in
    a CPU phase with their leased GPU loaded. GPUs 0–3 were free and there were no waiters, so nothing was asked; the
    pattern goes in the 8 AM PDT summary.
- 07:49–08:10Z (12:49–1:10 AM PDT) finished the first 6 h sweep (§4: 481 trees, 281 GB). Run 1's ssh to node 1 had dropped
  during a load spike on node 1: load5 went from about 92 at 07:36Z to 473 at 07:51Z on 128 cores, with CPU pressure
  ("some") at 36–43% and I/O pressure low. It came from `lean` (user research) and `python` (user ubuntu) processes
  outside Kubernetes, not from the sweep, and was down to load1 163 by 07:59Z. `node-sweep.sh` now logs on the node and
  outlives a dropped ssh, and `sweep.sh` skips a node already sweeping (§2). Slack (over 50 GB): one announcement in
  #agent-coordination with the totals, addressed only to the owners of the kept trees (@circuits, @compute-accounting,
  @proofs), each asked whether its trees' extra files are preserved or not needed
  ([thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790841929326899), subscribed).
- 08:06Z (1:06 AM PDT) tick: node 2 GPU 0 held 48 GiB at 0% for 15 min. The holder was the vLLM Commit `cg09` again (run
  `r20261001-074552-988a`, from 07:45Z, owner bc-698052e1) at 98% of one CPU; GPUs 2, 4, 5 and 6 are held the same way
  by `cg17`, `n048-2`, `n049-2` and `m001-2`. The sampler showed lease waiters, but nothing was queued in
  `/run/gpu-lease`: the two ad-hoc `gate_job.sh commit` runs (ubuntu) asked at 08:05–08:06Z and were granted GPUs 7 and 1
  within a minute. The sampler seems to count a granted holder whose command line carries `--wait`. Every Commit lease is
  preemptible by the node's scheduler (`cluster agent`), so nobody was blocked and nothing was asked.
- 08:20–08:30Z (1:20–1:30 AM PDT) tick: node 2 GPU 2 held 48 GiB at 0%, the Commit `cg17` (same pattern as 08:06Z, nothing
  queued for a GPU, nothing asked). The kept trees' owners had all said yes in the
  [thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790841929326899) by 1:10 AM PDT (each author
  checked with `research slack verify-author`). The steward checked each claim before deleting:
  - the four vLLM trees' 24 workload files are byte for byte those of `fca071b24` (`origin/cursor/build-bench-6942`);
  - `b84e85ef`'s only change adds `BlackwellE4m3QmmaDot32_v1` `{"and": 9793}`, which main has;
  - `9b88cb01`'s two `lean-audit.json` equal main's (`3a0169610`), confirmed by @proofs and by the run's owner
    (@old-circuits-and-proofs);
  - `0555d893`'s `RUN_OUT/` matches `art:d49243022a1612615a58b4b70dac9a4bd6edaefea22ce153ed25cd8b236e324a` file for file
    by sha256, PRESERVED (read back);
  - the five hash-bench trees differ only in the tracked ELF `pouw_hash_bench`, rebuilt in place beside its `.cu`.

  The sweep then deleted them (§4). It now takes `--approved FILE`: approved trees still go through the reference scan,
  rename and rescan; the list goes through a file because a first dry run with the shas in argv read its own `sudo` as
  a live reference. Slack: one status line in the thread (51.4 GB).
- 09:34–09:45Z (2:34–2:45 AM PDT) tick (exit 0): node 2's `/workspace` went from 37.8% at 08:20Z to 45.7% at 09:35Z.
  - Drivers:
    - circuits' 20 grid-model checkpoints staged smallest first from node 1 (`/workspace/verity-guest/grid20-stage/run.sh`
      calling `n2_build.sh stage`): 265 GB in all, 85 GB still to come (Qwen3-14B and Qwen3-30B-A3B);
    - `pouw/mvp-e2e/passes`: 106 GB written in 80 min;
    - pouw-design's captures: 10 GB.
  - Compute-accounting's node 2 agent tracks it (`note:20261001T0927Z-reply-from-c066b30c-node2-disk-and-parked-verifies`):
    the staging ends near 47%, 52% is due around 7 AM PDT unless passes are pruned, and it asked for 146 GB of passes to be
    pruned. Its own rule holds new passes over 52%. The steward's stop is 55%, so nothing was asked.
  - Closed vllm-epoch-run's open B64 handoff as overtaken
    (`note:20261001T0945Z-reply-from-resource-steward-b64-commits`): those Commits run on node 2, their replays run on node 1
    under release.py's cap, and circuits held them at 1:32 AM PDT.
- 10:05–10:20Z (3:05–3:20 AM PDT) tick (exit 1): the probe's HARD line "n1: /workspace gaining 750,950 inodes/h: 80% of
  inodes in 11.3 h".
  - Node 1 inodes went from 36.1% at 09:43Z to 38.7% at 10:07Z.
  - The new inodes came from `research/cache/verity-check` (328k in 95 min), `research/build-speed/runs` (100k) and about
    25 newly shipped `research/src` trees.
  - By 10:13Z the burst had stopped: 39%, and no longer HARD. At the net rate since 08:06Z, 80% is about two days out.
  - The largest holder is infra's `/workspace/jobs/src` (§5). Nothing is deleted; it is asked in
    `note:20261001T1015Z-ask-from-resource-steward-jobs-src-copies-unreaped`. Slack refuses an `ask` from @infra to @infra,
    so the ask went as a note.
- 11:12–11:16Z (4:12–4:16 AM PDT) tick (exit 1): "n1: / gaining 113,637 inodes/h".
  - Root is at 3% of inodes. Its free space went from 197 GB at 10:50Z to 160 GB: ten live pytest sessions
    (`pytest-1460`–`1473`, about 3 GB each, written 11:10–11:13Z).
  - Deleted the four stale sessions under the 2 h scratch rule (§4, 4.65 GB). Root is now at 164 GB free, with the alert
    at 60 GB. No Slack, since that is under 50 GB.
- 11:55Z (4:55 AM PDT) tick (exit 1): "n1: GPU 4 holds 49 GiB at 0% for 15 min". By the time I looked it was already free
  (0 MiB, no process), and infra's GPU alerter covers idle holds. No action.
- 12:38–12:41Z (5:38–5:41 AM PDT) sweep (exit 1): 40.8 GB deleted (§4), no STUCK line. Node 2 was not in a timed window
  (`timed False` at 12:39Z). No Slack, since that is under 50 GB. Node 2 `/workspace` is at 48%, up from 45.7% at 09:35Z.
  Compute-accounting's hold is at 52% and my stop at 55%. Infra's `/workspace/jobs/src` note is still open.
- 13:30–13:55Z (6:30–6:55 AM PDT) tick (exit 1): the HARD line "n1: /workspace gaining 1,262,875 inodes/h: 80% of inodes
  in 6.1 h".
  - Node 1 inodes went from 38.5% at 13:09Z to 42.8% at 13:30Z, with load5 at 305. By 13:53Z they were back to 40% and
    the probe was no longer HARD (243k/h). A transient burst of about 660k files was created and removed.
  - The `find -cmin` scan at `ionice -c3` timed out under that load. A `du --inodes` at `ionice -c2 -n7` finished in
    7.7 min.
  - The lasting growth since 10:10Z is 604k inodes: infra's `jobs/src` +299k (713 copies, 3.46M), `verity-check`
    +174k and `pycache` +62k. I added these numbers to the open infra note. Nothing is deleted.
- 15:00–15:03Z (8:00–8:03 AM PDT) daily summary, posted in #agent-coordination to @infra only
  (`1790866938.158289`; thread subscribed, `sub_63a37581`). The two open items are both infra's, and an untagged
  announce would ask every handle for a status line. Its content:
  - Headroom:
    - node 1 at 40% space and 41% inodes, root 188 GB free, RAM about 90% available (lowest 48%), 270 GB of replays
      queued;
    - node 2 at 46% (about 400 GB before 55%), 11% inodes, root 184 GB free, RAM 98% available.
  - Deleted in 24 h: about 393 GB and 7.6M files (§4).
  - Waiting: `jobs/src` (infra) and node 2 custody (node2-ops).
  - Trends:
    - node 2 peaked at 53.0% at 03:42Z, fell to 36% after pruning, and has been back at 46–47% since 11Z;
    - node 1 fell from 76% to 29% after circuits deleted checkpoints;
    - node 1 inodes swing between 34% and 46%, with two short HARD bursts;
    - node 1 load spikes reached 473 and 305.
- 15:48Z (8:48 AM PDT) tick (exit 1): "n2: / gaining 406,923 inodes/h". Node 2 was not in a timed window.
  - Root is at 4% of inodes (1.09M) with 177 GB free. The growth is `/home/research/.cache` (824k inodes), a cache that
    can be rebuilt and is far under its watermark. No action.
- 16:54–17:00Z (9:54–10:00 AM PDT) tick (exit 1): "n1: queued replay 360 GB (4 Commits) > half of available RAM -283 GB
  (after ramlock reservations)". This is the replay-RAM hard stop.
  - Node 1: 1,310 GB used of 1,716 GB, 390–435 GB available over 15 min.
  - The consumers are circuits' bool-elementwise runs outside Kubernetes, each a `verity-vllm boolean-replay` with
    forked workers:
    - `r20261001-161823-8b22` (`l32-bool`, 9:18 AM PDT) and `r20261001-162600-177d` (`cov-l32-bool`, 9:26 AM), each
      with a 400 GB reservation;
    - `r20261001-163611-11a7` (`cov-g2b-bool`, 9:36 AM), with no reservation.
  - Summed process RSS reads 2.36 TB because forked workers share pages. Only the node totals mean anything.
  - The 128 GB reservation from `r20260930-235157-362d` has a dead pid. The probe and `research.mem` already leave it
    out, so I left it.
  - Kueue: vllm-epoch-run replays, two admitted (created 16:47 and 16:52Z) and one pending. Kueue can't see the host
    runs' memory.
  - Asked @circuits (`1790873900.706599`): start no new `boolean-replay` on node 1 until one finishes, and check that the
    queued replays fit. Nothing is stopped.
- 17:16–17:43Z ticks (exit 0): the replay line is known and easing, from 270 GB queued (3 Commits, -178 GB) at 17:23Z to
  90 GB (1 Commit, -37 GB) at 17:43Z. Circuits hasn't replied.
- 18:06–18:27Z (11:06–11:27 AM PDT) tick (exit 1): "n1: HARD /workspace gaining 714,153 inodes/h: 80% of inodes in 10.1 h"
  and "n1: GPU 7 holds 86 GiB at 0% for 15 min".
  - GPU 7 was free (1 MiB) by 18:07Z. No action.
  - Node 1 inodes went from 42.5% at 17:43Z to 47% (9.57M) at 18:15Z, in bursts of up to about 2M an hour. The drivers:
    - two `check` runs' Lean-audit scratch trees from 18:02Z, `lean-audit-scratch-otchoghv` (494k inodes, held by no
      process at 18:16Z) and `-yulqo3ye` (320k, the audit's cwd);
    - the leftover `-f7jkfxj1` (321k, untouched since about 14:11Z, held by nothing);
    - new source trees, and `jobs/src` up to 763 copies (from 713 at 13:53Z).
  - Ran `sweep.sh --src-age-h 6` early (§4): 92.3 GB and 1.85M files. Node 1's inodes fell to 43%. If `otchoghv` stays
    untouched, the 00:30Z sweep takes it under the 2 h rule.
  - Node 2, seen while checking: `/workspace` went from 49.5% at 18:06Z to 51.7% at 18:23:41Z, then stayed flat.
    - The writer was `served-wsd-b959acdf-8` (lane pouw-served, `bc-c62f9726`). Its e2e verify pass wrote retained
      passes at about 500 MB/s for 4 min into `/workspace/pouw/mvp-e2e/passes/fill-wsd-b959acdf-8`: 74.5 GB, the same
      as `fill-wsd-de74f334-7`'s, which its CPU verify is reading now.
    - There are 167 GB before 55%. Each served window keeps about 74.5 GB until its verify deletes it.
  - Slack: one announce to @infra and @compute-accounting (`1790879553.355979`), since the sweep was over 50 GB. No
    action asked.
- 18:38–18:42Z (11:38–11:42 AM PDT) sweep (exit 1): 8 entries, 7.1 GB (§4). No Slack. The infra `jobs/src` note is still
  open. node2-ops' `note:20261001T1808Z-handoff-from-node2-ops-fill-held-for-1150-cutover` holds fill on node 2 for an
  infra `/workspace` cutover at 18:50Z, so node 2 readings may look odd until the hand-back.
- 18:50–19:02Z (11:50 AM–12:02 PM PDT) tick (exit 1): "n1: HARD /workspace gaining 3,578,618 inodes/h: 80% of inodes in 1.9 h",
  then 5.07M/h and 1.2 h at 18:54Z. Also "grep: /workspace/pouw/fill/status.txt: No such file or directory".
  - Node 1 inodes: 8.74M (43%) after the 18:20Z sweep, then 9.81M at 18:50Z and 10.79M (52%) at 19:00Z. Space is at 44%.
  - The cause is check's Lean-audit scratch trees in `~/.cache/verity-check`:
    - three live checks hold 630k–770k inodes each: `a7mec2rc` (`r20261001-181223-5ae6`, `check-b`), `lkzyik2u`
      (`r20261001-180819-abf7`, `check-a`) and `ox_caqkn`;
    - `otchoghv` (494k) is orphaned. It belonged to `r20261001-180102-ee96`, which infra cancelled at 18:08:18Z
      ("superseded by 9890ad470"). The run exited 143 (SIGTERM), and the tree's newest file is from that same second.
  - The leak: `research cancel` and the dispatcher's killpg send SIGTERM, whose default skips `lean_audit.py`'s `finally`,
    so every cancel during the Lean audit orphans its tree. `f7jkfxj1`, swept at 18:18Z, was the same.
  - Fix: verity [#708](https://github.com/danielreuter/verity/pull/708) (`cursor/lean-audit-sigterm-0ead`, draft). SIGTERM
    exits 143 through the cleanup. It has a test that fails without the fix (`-15`); `verity-check` and `repository` pass.
    The first check after it lands re-audits every Lean package once.
  - Live checks can add at most about 0.9M more inodes (4 slots), against the 5.85M left before 80%, so the HARD projection
    overstates the risk. Nothing is deletable yet: `otchoghv` meets the 2 h rule after 20:08:18Z, and I run the sweep at
    the first tick after that.
  - The node 2 grep error: `status.txt` was missing at 18:50Z during the cutover (back at 18:54Z). `tick.sh` and `sweep.sh`
    skipped node 2 only when the file said `timed True`, so a missing file failed open. Both now run on node 2 only when it
    says `timed False`, and otherwise print why they skipped. `tick.sh` is reinstalled.
  - Slack: one announce to @infra (`1790881248.691289`) with the cause, the PR and the plan.
- 19:12–19:20Z (12:12–12:20 PM PDT) tick (exit 1): "n1: HARD /workspace gaining 3,345,655 inodes/h: 80% of inodes in 1.6 h"
  and "n2: HARD /workspace gaining 2,799,577 inodes/h: 80% of inodes in 5.2 h".
  - Node 2 is a false alarm. The 18:50Z sample, taken during the cutover, read another filesystem (24.6% space, 2.8% inodes)
    against 51.7% and 9.6% before and after. Inodes are flat at 9.6%, but that sample stays in the probe's 15–60 min base
    until about 19:50Z, so the 19:32Z tick will report it again.
  - Node 1: 10.99M inodes (53.4%) at 19:13Z, then 10.24M (50%) at 19:19Z, when a check ended and removed its scratch.
    Census at 19:13–19:18Z against 18:07–18:29Z:
    - `research/cache/verity-check`: 3.09M, from 1.42M. These are the Lean scratch trees; they don't outlast their checks
      except when a cancel orphans one (#708).
    - `/workspace/jobs/src`: 3.89M, from 3.72M, now 797 copies. It is the only consumer still growing without bound, about
      150k/h, which reaches 80% in about 40 h if nothing reaps it. The 10:15Z note to infra is still open.
    - `research/trees` 1.51M (flat); `research/src` 0.37M (0.81M before the 18:20Z sweep).
  - Nothing is deletable yet (`otchoghv` only after 20:08:18Z). No Slack: the 19:00Z post covers the scratch, and `jobs/src`
    is in §5 and the daily summary.
- 19:34Z (12:34 PM PDT) tick (exit 1): both HARD lines again, easing (node 1 at 1.18M/h and 5.5 h; node 2 at 1.43M/h and
  10.1 h, still the cutover sample). The actual numbers are falling or flat. Node 1 is at 9.99M inodes (48.5%), with two
  scratch trees left (`lkzyik2u`, and the orphan `otchoghv`) and `jobs/src` at 806 copies. Node 2 is at 1.99M (9.7%). No
  action.
- 19:56Z (12:56 PM PDT) tick (exit 1): node 1 HARD at 647k/h (80% in 9.6 h); node 2 over the 100k/h rate at 951k/h. Node
  2's is still the 18:50Z cutover sample, which stays the rate base until it is an hour old: its inodes are flat at 9.65%
  (1.99M) and `/workspace` is down to 47.65%. Node 1 is at 10.22M inodes (50%), with four scratch trees (`3g6nt1s0`,
  `frute7lo`, `lkzyik2u`, and the orphan `otchoghv`) and `jobs/src` at 811 copies. No action: `otchoghv` is sweepable
  after 20:08:18Z.
- 20:03Z (1:03 PM PDT) tick (exit 1): node 1 HARD at 814k/h (80% in 7.5 h), at 10.37M inodes (51%). The growth was
  check scratch: `3g6nt1s0` live (321k), `lkzyik2u` (770k, last written 19:07Z) and the orphan `otchoghv` (494k), with
  `jobs/src` at 812 copies. Ran the 6 h sweep once `otchoghv` passed 2 h (20:08:18Z): 25 entries, 43.5 GB, node 1 down to
  9.80M inodes (48%); §4. No Slack (under 50 GB). `lkzyik2u` is sweepable after 21:07Z if nothing holds it.
- 20:25–21:53Z ticks: exit 0.
- 22:15Z (3:15 PM PDT) tick (exit 1): node 1 HARD at 899k/h (80% in 7.1 h), at 10.03M inodes (49%): `anxt7zhi` live
  (770k), the orphan `lkzyik2u` (770k, last written 19:07Z), `jobs/src` at 816 copies. Ran the 6 h sweep at once: 14
  entries, 54.3 GB, node 1 down to 9.20M inodes (45%); §4. Slack (over 50 GB): one announce to @infra
  (`1790893411.516639`): the sweep, the three orphans since 18:00Z (1.59M inodes, 93.5 GB), PR #708 still a draft, and
  `jobs/src` still waiting.
- 22:30–23:05Z ticks: exit 0. #agent-alerts had two of infra's unmatched-writer alerts on node 1 (22:32Z and 22:58Z: lanes
  copying a Lean `.lake` and the warm `lean-deps` into their trees, 35–40 MB/s); infra's, no action.
- 23:26Z (4:26 PM PDT) tick (exit 1): node 1 HARD at 764k/h (80% in 8.9 h). Its scratch burst was already gone: no
  `lean-audit-scratch-*` left, 9.64M inodes (47%), `jobs/src` at 831 copies (+15 in an hour). The same tick showed a
  space burst: `/workspace` 46.8% at 23:05Z, 58.6% at 23:27Z and 2,951 GB (59%) at 23:29Z, then 2,819 GB at 23:33Z and
  2,608 GB (52%) at 23:37Z. About 600 GB written and released in under 40 min. Files over 200 MB created since 22:43Z
  came to only 26.5 GB, so the bulk was many smaller files or ones already deleted. At 23:29Z the writers were two `check`
  suites (115 and 36 MB/s) and `60-circuit.sh` (78 MB/s), and `nd-vllm-epoch-run-*` build/replay/gpu pods started
  23:32–23:35Z. It never reached the 80% alert. No action, no Slack. A burst of that rate from 52% would reach 85% in
  about an hour, so watch for a repeat.
- 23:49Z (4:49 PM PDT) tick (exit 1): node 1 HARD at 994k/h (80% in 6.4 h), measured from the 22:43Z reading just
  after the 22:16Z sweep. 10.09M inodes (50%): two live scratch trees (`83udayo7`, `puyaflbo`, about 320k each, written
  this minute), `jobs/src` at 836 copies. Space back to 51–52% (2,578 GB). Nothing deletable; no action, no Slack.
- 00:11Z (5:11 PM PDT) tick (exit 1): node 1 HARD at 729k/h (8.6 h). 10.16M inodes (50%): one live scratch tree
  (`27_slr0l`, 321k, written 00:09Z), `jobs/src` at 839 copies. Space 56% (2,770 GB). No action; the 00:30Z sweep is next.
- 00:32Z (5:32 PM PDT) tick: exit 0. Scheduled sweep 00:32–00:40Z: 17 entries, 19.1 GB (§4); no Slack (under 50 GB).
  Node 2 `/workspace` is down to 38%. `jobs/src` on node 1 reached 850 copies, about 11 more an hour.
- 00:53–01:15Z ticks: exit 0.
- 01:34Z (6:34 PM PDT) tick (exit 1): node 1 HARD at 1.19M/h (80% in 5.1 h), measured over the 20 min from 01:15Z, so
  mostly the live scratch tree `y16o44cs` (321k, written 01:34Z). 10.41M inodes (51%), 58 source trees, space 60%
  (2,992 GB). `jobs/src` reached 872 copies and 4.23M inodes (§5, with the projection and the escalation date). Nothing
  deletable; no action, no Slack.
- 01:47Z (6:47 PM PDT) tick (exit 1): node 1 at 192k inodes/h, over the 100k/h line but no longer HARD. It is the
  01:34Z growth (scratch, source trees between sweeps, `jobs/src`). Nothing deletable; no action.
- 02:00Z tick: exit 0 (192k/h known). 02:20Z (7:20 PM PDT) tick (exit 1): node 1 HARD at 751k/h (7.5 h). 10.84M inodes
  (53%): two live scratch trees (`44yxbhfn` 321k, `hk9lhiv8` 149k, both written 02:20Z), 63 source trees (12 over 6 h,
  left for the 06:30Z sweep), `jobs/src` flat at 872. Space 60%. Nothing deletable; no action.
- 02:40Z tick: exit 0. 03:00Z (8:00 PM PDT) tick (exit 1): node 1 HARD at 2.91M inodes/h (80% in 1.3 h). Node 1 went
  from 52.75% at 02:40Z to 12.79M (63%) at 03:00Z, then held flat. The cause was two live Lean audits, `pqalds2h` and
  `rijsvyll`, at 1.07M inodes each (each audit used to hold 770k), plus 72 source trees and `jobs/src` at 875. Ran the
  6 h sweep at once: 17 entries, 17.9 GB (§4). By 03:08Z both audits had finished and node 1 was at 10.52M (52%). The
  larger audits move the `jobs/src` projection forward a day, so I sent it to Daniel as a blocking card (§5, 03:09Z).
  No other Slack.
- 03:20Z tick: exit 0. Infra answered the card thread (§5, 03:17Z) and opened verity #759. I added `--jobs-src` to
  `node-sweep.sh` (off by default) and dry-ran it on node 1: 811 entries, 72.9 GB, no live pod's copy among them (§5,
  03:50Z). Nothing deleted; the card is still pending. Node 1 at 10.74M inodes (53%). No Slack.
- 03:40Z and 04:00Z ticks: exit 0. 04:20Z tick (exit 1): node 1 root gaining 134k inodes/h. That was `check`'s pytest
  scratch (`/tmp/pytest-of-research/pytest-2835` and `-2836`, about 25k files changed in the hour) plus k3s and
  `~/.cache/verity`. Pytest rotates these itself, keeping the newest three, and root fell from 683k to 594k inodes (2%) by
  04:24Z. Nothing to delete; no action, no Slack.
- 04:40Z to 05:22Z ticks: exit 0. 05:44Z tick (exit 1): node 1 had 12 finished runs over 1 h without custody (13 by
  05:48Z). All are failed runs whose runner died during custody, 12 of them cancelled `check` runs. Sent to @infra with
  the evidence (§5). Nothing deleted.
- 06:07Z (11:07 PM PDT) tick (exit 1): node 1 HARD at 862k inodes/h (80% in 5.0 h), at 12.17M (59%). The jump came from
  three live Lean audits' scratch, on top of `jobs/src`, which reached 1,003 entries (43 an hour). Ran the 6 h sweep at
  once: 26 trees, 32.1 GB (§4, 06:09Z). The card status then read *approve* (Daniel, 8:59 PM PDT), so I put `--jobs-src`
  into `sweep.sh` for node 1 and ran it: 841 entries, 79.1 GB (§4, 06:16Z). Node 1 is at 36% inodes (7.40M) and 57% space.
  Posted to @infra, since the total is over 50 GB.
- 06:30Z scheduled sweep (exit 1): 6 entries, 2.2 GB, on node 1 (§4). No Slack.
- 06:31Z to 07:25Z ticks: exit 0. 07:49Z (12:49 AM PDT) tick (exit 1), two lines:
  - Node 1 HARD at 1.81M inodes/h (80% in 4.1 h). The rate's base came just after the 06:23Z sweep (7.40M). Node 1 is
    at 9.02M (44%), with five Lean scratch trees. Four check slots hold locks (a, b, c, and a `check-d` added at 07:22Z),
    but only two trees have a process working in them. `ju7dx3l8` was last written about 06:18Z and passes the 2 h rule
    at about 08:18Z, so a one-off timer runs the sweep at 08:20Z. Headroom to 80% is 7.4M, more than five full audits.
  - Node 2 root gaining 761k inodes/h: one live audit's scratch in `~/.cache/verity-check` (14 processes in it) and
    pytest garbage that was already gone. Root is at 1.40M inodes (5%) and 158 GB free. No action.
  No Slack.
- 08:14Z tick: exit 0. 08:21Z one-off sweep (exit 1): 50 entries, 26.9 GB (§4). `ju7dx3l8` is still under 2 h untouched
  and is left to the 12:30Z sweep. Node 1 is at 8.15M inodes (40%), which closes the 07:49Z HARD line. No Slack.
- 08:36Z to 09:35Z ticks: exit 0. 09:53Z (2:53 AM PDT) tick (exit 1): node 1 HARD at 1.36M inodes/h (80% in 5.5 h), at
  9.02M (44%). There were six Lean scratch trees: three live audits, and three idle 135–202 min with no process in them.
  Ran the sweep at once: 59 entries, 70.4 GB (§4). Node 1 is down to 8.21M (40%). Posted to @infra, since the total is
  over 50 GB.
- 10:07Z to 10:53Z ticks: exit 0. 11:15Z (4:15 AM PDT) tick (exit 1): node 1 HARD at 2.36M inodes/h (80% in 3.4 h). That
  was four Lean audits starting together on slots check-a to check-d, all written within the last 3 min, from a base of
  7.68M (37%) at 10:53Z. Node 1 is at 8.56M (42%). Four full audits (about 1.07M each) would reach about 12.9M (63%).
  Nothing is idle or deletable, so no action and no Slack.
