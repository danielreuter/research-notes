---
id: 20260930T0717Z-draft-host-unit-eval
campaign: overnight-sep30
lane: flock-v2-design
kind: draft
status: open
repo: danielreuter/verity
origin: cursor/host-unit-eval-c9e2
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

# flock-m0-v2 lever: the deep unit's host witness in one pass

For M0 (bc-ff572e70, lane `flock-netlist`), as a backlog item. Branch `cursor/host-unit-eval-c9e2`, merged with your
`1c1e90e5`. The lever is commits `482c83d3` and `f5d6b77c`, which touch only `ir_block.rs`, `circuit.rs`, `gpu_circuit.rs`
and `lookup.rs`. `e227b321` is its measurement script, `72-host-unit-eval.sh`.

**What changes.** A deep unit (at least 2048 levels, `deep_unit`) is evaluated on the host in `slot_zab`: 64 units form a
lane group, and each thread walks one group through `IrUnitNet::eval64`.

- `eval64` walks every row's A and B columns three times, once each for z, a and b, through `Vec<Vec<usize>>`.
- For each lane group that is 3 × 32.7 M column reads at K = 2048 and 3 × 131 M at K = 8192. The column indices alone are
  0.26 and 1.05 GB per pass, and every group re-reads them.
- `eval64_flat` reads flat u32 forms of the rows instead. They are built once per circuit: 131 and 524 MB, about 0.1–0.4 s,
  paid in the warm session. It walks the rows once. Every column a row reads is an earlier one or the constant's, so a row's
  z, a and b are final when the walk reaches it. An assertion row reads its own column; that read is carried as a parity bit.
- The group's input rows are formed by 64 × 64 bit transposes.

**What stays the same.** It is bit-for-bit `eval64`, so the witness, and with it the proofs, are byte-identical.

- A net with a row that reads a later column keeps the two-pass path.
- `FC_UNIT_CHECK=1` runs `eval64` beside it on every group and asserts equality.
- Unit tests cover random nets (input, empty, constant, repeated-column and assertion rows, plus a later-column net) and
  every lookup net.
- No statement, pin, circuit, relation or protocol changes, so there is nothing for circuit-check.
- `FC_UNIT_PROFILE=1` prints `UNITPROF` lines to stderr: the flat build, the eval, the transposes, `host_slots` and `pack`.

**Where it pays: the model.** Under your pipeline the metric is max(wait + prove, prebuilt / depth). Per coordinate, that
is s = max(device, host CPU / T) for T host threads.

The inputs come from r20260930-054739-26cc (FC_PIPELINE=0) and the 4×4 tile run r20260930-063458-7a27:

| per coordinate | device | host CPU (old eval) |
|---|---|---|
| K=2048, untiled | 0.59 ms | ≤ 4.2 ms |
| K=2048, 4×4 tile | 0.184 ms | ≤ 4.2 ms |
| K=8192 | 1.24 ms | ≤ 18.6 ms |

The host CPU bounds are witness_s × groups / n.

**Predicted overhead** (× native; prefill M=256, decode M=1..8). Baseline 26cc: prefill 3.48e7, decode 7.91e5.

| configuration | T | old eval | one pass (host ≥ 1.7× cheaper) |
|---|---|---|---|
| v1: untiled, pipelined | 18 (prover-bench) | 2.06e7 / 4.85e5 | 2.06e7 / 4.85e5 |
| v1: untiled, pipelined | 8 | 2.36e7 / 5.39e5 | 2.06e7 / 4.85e5 (at 2.5×) |
| v2: K=2048 4×4 tiles, pipelined | 18 | 1.03e7 / 2.30e5 | 8.8e6 / 1.94e5 |
| v2: K=2048 4×4 tiles, pipelined | 8 | 2.18e7 / 4.95e5 | 9.6e6 – 1.27e7 / 2.1e5 – 2.9e5 |

- In v1 at T = 18, M0's pipelining alone already reaches the device-bound ("prove only") number. The lever keeps it there
  on fewer cores, for example next to vLLM.
- Tiles make K = 2048 host-bound at 18 threads, and there the lever gives about −15% prefill and −16% decode.
- The decode rows ignore partial tiles. At M = 1 a 4×4 tile is only 1/4 full, so for decode a 1×C tile at 2^23 bits is the
  fair one.

**Measured.** Kueue job 36 (`fv2-a1`, prover-bench) runs three things:

1. the attempt with FC_PIPELINE_DEPTH=4 and UNITPROF;
2. the sweep with FC_PIPELINE=0;
3. the equality check, with eval64's time beside the one pass.

Results go to this folder's report as `art:` ids.

**Next, if it holds.**

1. Write a and b into the mapped host slots straight from the bit-sliced rows. Today `lanes()` makes 3 × 256 KB `Vec<F128>`
   per unit, 768 MB per K = 2048 build, then `pack` copies them again.
2. Parallelise within a group by levels for K = 8192, which has 8 groups for 18 threads.
