---
id: 20261001T0203Z-handoff-from-f5bf55c8-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-f5bf55c8 (FP4 pricing, Pearl-C4), for its replacement in compute accounting's Project
---

# Migration handoff from bc-f5bf55c8 (Pearl-C4 FP4 pricing): two draft PRs, nothing in flight, one job waiting to be queued

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`.

**What this lane did:**
- priced Pearl-C4 (NVFP4) for γ and for honest coverage;
- priced the base-split fixes, ending in F1′ + F2;
- priced the verifier's cost;
- ran the census evidence behind the assessor's FP4 ratings.

**The deliverable** is the research store's `docs/pouw/pearl-c4-fix.md` (§§5–10, current to 17:32Z's rule). Older docs:
`docs/pouw/pearl-c4-v3.md`, `pearl-c4-v4.md` and `fp4-specialization.md`.

## 1. Branches and PRs

- **`cursor/fp4-emulation-cf5b`** (danielreuter/verity), head `ecf352c25d`, is **PR #530**, a draft against `main`.
  - It holds the benchmarks under `benchmarks/pouw/`: FP4 emulation, the v3 and v4 censuses, fix pricing,
    `fp4_f1_pricing.py` (the census), `fp4_f1_verifier.py` (the verifier's cost) and `ue4m3_scale` (the `lut256` scale
    step).
  - Nothing in core changes. `check` has not been run, and no merge is requested.
  - Left: run `check` and merge-request it, if the evidence should land on `main` (the backlog's done-but-unmerged row with
    #507 and #545). Otherwise keep it as the record.
- **`cursor/pearl-c4-v4-cf5b`**, head `d633771898`, is **PR #542**, a draft stacked on `cursor/pearl-c4-salt-keyed-b-2cf6`.
  - It is the v4 candidate reference (rank-2 FFMA noise), rejected on its debit and kept for replay.
  - Left: nothing. Close it unless someone wants the replay.

## 2. Runs and jobs in flight

- **None of mine is running,** on this VM or on node 2.
- **Waiting to be queued: the 70B FP4 coverage fill job, version 4,** in the research store at
  `internal/pouw/rtx-pro/fp4-coverage-70b/`. The exact command, the sha256, the inputs and the output dir are in `job.md`
  there.
  - It is NVFP4 only and CPU only once the capture exists. On node 2 that capture is done, in
    `/workspace/pouw/fill-out/fp4-coverage-70b/acts`.
  - The census goes into `/workspace/pouw/fill-out/fp4-coverage-70b/out4/` (`summary.txt`: the rule's uncredited share,
    the worst credited tile, and the rows `volunteer` gives up).
  - The backlog row says "Daniel decides: supports 70B only". bc-2aa33ad8 holds the queue decision.
  - **No custody.** It's a fill job, so its `out4/` must be preserved by hand: `research data put --tree … --preserve`
    from a machine with evidence-store access. Node 2 has none.
- **The V-EX coverage job** (`pearlc4-vex-coverage.sh`) is bc-a8466279's. It runs on my captures, and I have nothing in it.

## 3. Half-done state, and where everything is

- **Nothing of mine exists only on this VM.** I copied the VM-only material at 02:20Z: the census result JSONs (§§5–10),
  the scripts that merged them, and the 70B job's generator. It is in two places:
  - the evidence store, `art:1418cd489a01dd46fe6d6b477b4891261edb92441f889a5728d5d41db61c0e60` (preserved, remote
    verified);
  - the research store, `internal/pouw/rtx-pro/fp4-pricing-results/`, with an `INDEX.md` mapping each file to its section.
- **The census captures** (Qwen2.5-3B and -7B, README and `AGENTS.md` prompts) are in the evidence store:
  - `art:f525a034…` and `art:26935ac1…` (README); the README pair is also copied under
    `internal/pouw/rtx-pro/pearlc4-captures/`, with `sha256.txt`;
  - `art:bc659207…` and `art:12040974…` (`AGENTS.md`);
  - the full ids and the node-2 install steps are in `internal/pouw/rtx-pro/pearlc4-captures.md`.
- **Handed off, not mine to finish:**
  - term 3 per element for #556's reference: `internal/pouw/rtx-pro/handoffs/term3-per-element.md`, to bc-a8466279;
  - the `lut256` scale step: `handoffs/ue4m3-scale-lut.md`, which GPU 5 took.
- **My status file:** `internal/pouw/rtx-pro/workers/fp4-pricing.md`.

## 4. The next step for each kept item

- **70B FP4 coverage:**
  - queue version 4 if Daniel wants 70B;
  - preserve `out4/`;
  - report the rule's uncredited share and the rows `volunteer` gives up into `pearl-c4-fix.md` (a new §11) and this lane.
  - Expect a real loss on 70B `o_proj`. Under §5.3's older rule it was about 4% of credit, mostly R1 rows.
- **The rotated-weights re-read** (the backlog's row, bc-a8466279's): my census figures are on unrotated weights too.
  - Those are the B̃-at-10× honest cost and 0 voluntary rows on 3B and 7B (§9–§10).
  - With the keyed V/O rotation plus head interleave now ruled in (Daniel, 5:52 PM PDT), re-run `fp4_f1_pricing.py real` on
    rotated weights before anyone cites them for a registered model. It's CPU only, under an hour per model at 8 weight
    tiles, and it takes the same flags as §10.
- **PR #530:** run `check` and merge-request it, or leave it as the record. That is the research coordinator's call.
- **What I'd stop:**
  - MXFP4 (out of the domain since 15:34Z);
  - fixes (a) and (b), the count limit and the row-max floor (all superseded);
  - the v3 and v4 noise designs (rejected);
  - more F2 margin work on honest NVFP4: its tiles sit at 0.13–0.16 against triggers of 1.84 and up.

## 5. Traps

- **Credentials:**
  - list environment variables with `compgen -e` only; `env` printed part of a multi-line private key once;
  - pushes to research-notes fail with 403 as `cursor[bot]` unless git uses `RESEARCH_NOTES_TOKEN` alone, with global and
    system git config ignored (`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` plus a credential helper that reads
    the variable);
  - the Verity broker's `install` refuses an `origin` with an embedded token, so reset it to the plain URL first.
- **The research store:** reads and writes can fail with EAGAIN (Resource temporarily unavailable). Retry, and check the
  sha256 after every write.
- **The census rule has moved, so earlier figures aren't comparable.** `fp4_f1_pricing.py` now defaults to the 17:32Z rule:
  - the certified evaluation;
  - p_t zero on witness-dead codes only;
  - B̃ at 10×;
  - term 3 per element;
  - R1 and the tile reject.

  §5's tables are on an older rule (the 24-draw modal byte, p_t zero on whole screened blocks, B̃ at 1×). Compare only
  like with like, and read each run's `summary` for its law.
- **Captures are bit-exact only on the machine that made them** (this VM's CPU, torch 2.14 at one thread). A forward elsewhere
  gives different BF16 rounding, so copy them rather than regenerate.
- **The MKL first-call race** (the backlog's check):
  - the 70B job's census steps run with every math thread at 1, so they can't hit it;
  - but its capture step ran torch's CPU-spilled layers at 16 threads;
  - if the race predates node 2's warm-up fix, re-run the capture (it only takes minutes) before trusting the 70B numbers.
- **The 70B job's header says `owner=bc-f5bf55c8`,** and its yield logic skips the owner's own jobs. Re-own it in the header
  when you queue it.
- **Every-tile censuses on 7B are slow:** about an hour per four-layer half on one core. Split them by `--layers` across
  processes, and keep `OMP_NUM_THREADS=1`.
