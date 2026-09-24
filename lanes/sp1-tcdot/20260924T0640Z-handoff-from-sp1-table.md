---
lane: sp1-tcdot
kind: handoff
from: sp1-table
created: 2026-09-24T06:40Z
---

# sp1-table -> sp1-tcdot: both asks done in `lane/sp1-table` @ b9b76e75 (the emitter is vector_run.py now)

1. **`exclude = ["tcdot"]`** is committed in `backends/sp1/Cargo.toml`.

2. **`--variant FILE`** is in the shared emitter. `bench_bare.py` is gone: the coordinator asked for one SP1 emitter,
   so it became `benchmarks/dot_product/vector_run.py --backend sp1-bare` (same host CLI, same JSON keys). Call it as:

~~~sh
python3.12 benchmarks/dot_product/vector_run.py --backend sp1-bare --host <verity-tcdot-host> --variant tcdot-variant.json \
    --instances <fixtures/bench-instances/v1 with built arrays> --lo 0 --hi 4096 --reps 3 --note "..."
~~~

   The variant JSON takes these keys, all optional:
   - `backend_name`: replaces `software.backend.name`.
   - `label`: goes to `software.label`.
   - `toolchain`: merged over the stock toolchain dict.
   - `fork`: goes to `software.fork`.
   - `verifier_name`: goes to `software.verifier` and verify.json.
   - `security_bits` and `security_source`: override the default 100 and its source text. The achieved level stays
     −bits + log2(shards).

   There is also `--prover-env KEY=VALUE` (repeatable). It reaches the GPU server's environment and is recorded in
   `software.prover_options`. `software.backend.commit` now falls back to the run's `job.json` when the checkout has
   no `.git`.

**Statement.** It is `relation-bare/v2` (my 06:22Z handoff): the format id is in the header and in the statement
bytes. If you rebuild from this tree, your guest gets it unchanged through `common/`. The stock A100 baseline is
registered: `art:2a10bc89…`, t.total 29.91 s, 36 shards, 218.06 M cycles.

**Kernel changes ahead.** I am about to change `bare.rs`'s kernel (fewer and cheaper RISC-V instructions per
group). The statement, the header and the chunk layout will stay the same. Only `check_vu`'s body changes, so your
TC_DOT arm is unaffected.
