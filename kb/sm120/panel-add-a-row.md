---
cursor:
  subagentId: "bc-2aa33ad8-7eb0-5ce2-8ffc-6420476ecd3d"
---

# Adding a row to the PoUW panel

For every GPU worker and theory lane on PoUW on sm_120. Owner: the panel coordinator, bc-2aa33ad8.

**The rule: nothing gets tried without a row.** Every optimization attempt you price or time goes into `internal/pouw/panel/attempts.jsonl`: a design estimate, a re-pricing, a kernel change, a protocol change, or a measurement. It is the single database behind Daniel's two slowdown plots (`media/pouw-slowdown-prefill.png`, `media/pouw-slowdown-decode.png`) and the [panel page](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/panel.md).

**Append it yourself** (Python 3 with matplotlib; `pip install matplotlib` if needed; it re-renders the plots and the page):

~~~sh
python3 /cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/panel/panel.py append \
  --line pearl-c-sm120 --version v1 --precision fp8 --phase prefill --shape m8192-n8192-k8192 \
  --kind estimated --slowdown 1.34 --lo 1.17 --hi 1.50 --gamma 0.00511 --change kernel \
  --description "epilogue hashing overlapped with the mainloop (K3)" --source "internal/pouw/hashing-sm120-options.md §5"
~~~

- **A measurement** adds `--kind measured --run <run id>` and the reference verifier's acceptance of that run's own
  transcript. `panel.py` refuses a measured row without all of these:
  - `--verifier-commit <sha>`: the reference verifier's git commit;
  - `--verifier-accept "<line>"`: its accept line on this run's transcript, verbatim;
  - `--transcript "<run id>:<path> sha256:<hex>"`: the transcript it checked, which must name this run;
  - `--negative-control "<line>"` (since 11:50Z): the verifier's reject line, verbatim and naming this run, on the run's
    negative-control arm. That arm writes nothing into the same output buffers, after they are poisoned. If it is
    accepted, the run fails.
  - `--sm-clock-arm MHz,MHz,...` and `--sm-clock-base MHz,MHz,...`: the SM clock of every rep, for the arm and for the
    baseline. The baseline is timed in the same run, on the same die, interleaved with the arm, in reps of similar
    duration. Under sustained load the card runs about 1% slower: "locked-2100" really means 2,070–2,092 MHz, and the power cap
    engages under sustained FP8 (ops), so unequal reps bias the ratio. Arm and baseline medians more than 0.5% apart are tagged
    "clock gap" on the page.

  The timed code emits that transcript itself: the commitments, digests and words the verifier recomputes, in the verifier's
  format. A stand-in commitment, hash or format doesn't count, even if it costs the same. A component measured alone (such
  as `:hashing-only`) has the verifier check that component's output, for example A's commitment recomputed from the same A.
  Measured rows logged before this rule carry no verifier record: they stay in the table tagged unverified, off the plots.
  To put one back, re-run it with the verifier and append the new measurement.

  **Stale outputs pass the verifier** (bc-b139c29c, 11:33Z, research-notes `lanes/pous/20260930T1133Z-note-from-hash-cut-change3-to-pouw-sm120-stale-outputs-pass-the-verifier.md`).
  The verifier checks that a transcript is right for its input, not that this arm's kernels wrote it. So when arms, or an
  untimed setup call and the timed call, share output buffers and inputs, a kernel that writes nothing passes on the
  output an earlier one left behind. Pearl-C4's `prime()` is one example: it writes `root_a` and `seed_a` before timing.
  The timed code must therefore:
  - fill every output buffer the transcript reads with a poison pattern (0xA5) immediately before the call it dumps,
    including buffers a setup step wrote;
  - run a negative-control arm that writes nothing into those poisoned buffers, which the verifier must reject;
  - ideally give each arm its own inputs, so no arm's correct output fits another's.

  The #491 harness does the first two for every arm with `dump` (arm interface v0.5; #583, bc-1a23b70c); an arm
  without `dump` poisons and dumps its own, and names `control` in its verifier declaration. A bench of your own does
  all three.
- **`--noisy`** marks a measured row that another job shared the GPU or the machine with during timing. The coordinator copies verified measured totals into the Verity root's attempt log (`ov.*` labels, `panel.py ov-sync`), and `--noisy` becomes `ov.noisy true` there.
- **Decode** also adds `--decode-method dependent-chain`; a measured decode row counts only when timed as a dependent chain.
- **The fields:**
  - `--line` and `--version` must be on the panel (`internal/pouw/panel/lines.json`); ask the coordinator for a new version.
  - `--phase` is `prefill` (`m8192-n8192-k8192`) or `decode` (`m32-n8192-k8192`). Other shapes are logged but not plotted.
  - `--slowdown` is the total, hashing included, over the fastest plain GEMM of the same precision; `--lo` and `--hi` give an estimate's range.
  - `--gamma` is a fraction (0.005111 = 0.5111%). **Compute it at two FP32 prices and give the larger** (the pous root,
    09:00Z; FP8 and FP4 alike): the cheapest bit-exact FADD (8.00 W1 per word) and the measured loop price, `1047/125` = 8.376, the one in-loop
    record for FP8 and FP4 (bc-824e54a2, 12:16Z; not "8.38"). Say in the description which price gave it, and cite the Lean
    pin when one exists (`internal/pouw/price-twins-lean/`). Omit it while it is being derived; an estimate is then plotted and marked "being derived". An attempt with γ above 1% is never plotted.
  - `--change` is `baseline`, `kernel` (same protocol, a new attempt on the line) or `protocol` (a protocol or cryptography change, which is a new version).
  - `--source` is a run id, a store document with its section, or an agent id.
  - `--attempt N` adds another phase or the measurement of attempt N; without it, the line's next number is used.
  - `--basis components|paper` says what an estimate rests on: measured components, or paper alone. An estimate that
    re-prices a paper estimate is paper.
- **Correcting a row:** append `--attempt N --revision "<what changed>"` (a γ, price or assumption restatement); it stays
  in the table, off the plots. Add `--voids` when attempt N's measurement doesn't count as its version at all (it timed
  something else, such as another commitment of A): its measured rows, every phase, stay in the table tagged voided and
  leave the plots.
- **A row under the wrong attempt number:** don't rewrite the log. Ask the coordinator, or run `panel.py renumber --line
  L --version V --phase P --run R --from N --to M --why "..."`, which appends a correction row applied when the log is
  read and listed under the page's Corrections. The same correction moves a protocol change logged under the wrong version
  (`--to-version V`) and marks an unadopted variant a candidate, kept in the table and off the plots (`--candidate
  "<why>"`). A protocol change is a new version: ask the coordinator for its line before logging it.
- **A component measured alone,** such as hashing around a stand-in GEMM, takes a shape suffix (`m32-n8192-k8192:hashing-only`).
  It's logged and tagged, never plotted: the plots show only protocol totals.
- **If you can't run it,** send the same fields to the coordinator (in your status file's `## Panel rows`, or your return), and it appends them.
- **The assessor's folder and ID are its own.** Only the assessor (bc-d7d4b0d1) writes in `internal/pouw/red-team/`, or
  queues fill or leases GPUs under its ID (`owner=bc-d7d4b0d1`, `GPU_LEASE_WHO=bc-d7d4b0d1`). Anyone else with code,
  a job or a proposal for it puts it in their own folder and tells the pous root, who passes it on. This keeps the
  assessment independent.
