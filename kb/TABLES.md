---
kind: kb
topic: the tables the user wants
updated: 2026-09-24T20:20Z (from campaigns/morning-tables/BRIEF.md §1-3 plus the user's decisions of 2026-09-24)
---
# The tables the user wants (standing spec; do not redesign without the user)

The user wants six tables that answer three questions: **how fast each candidate proves the workload on each target,
what we tried, and what each variant assumes and guarantees.** Only solid numbers: every cell traces to an `art:` id and
was verified by someone other than its producer. Show him these renders as they are; never a hand-made or re-scaled table.

## Render (the only way to produce them)
~~~sh
S=~/projects/verity-main-wt/cli   # sparse worktree at main
PYTHONPATH=$S/backends/numerical/python:$S/tools/research/src:$S \
  ~/projects/verity-main-wt/main/.venv/bin/python -m verity_numerical.bench.tables    --root ~/.research/store --format md
PYTHONPATH=... python -m verity_numerical.bench.drilldown --root ~/.research/store --format md
~~~
The steward renders both daily at 13:00Z into `campaigns/afternoon/render/` style paths (see `steward.toml`).

## The three frozen tables (`verity_numerical/bench/tables.py`; definitions in its docstring and `backends/AGENTS.md`)
- **Table 1, candidate proof systems** (definitional, no numbers): A-GKR, B-Ligero, SP1: ZK, verifier model, soundness,
  setup, interaction, assumptions.
- **Table 2, headline prover overhead** (prover time / native matmul time at the row's measured peak).
  Rows: A100 BF16 | H100 BF16 | H100 FP8 (E4M3) | RTX 4090 FP8 (E4M3) | RTX 5090 NVFP4.
  Columns: native spec | native measured | A-GKR | B-Ligero | SP1 | B-Ligero + in-proof hash (Poseidon2 per row, no sharing).
- **Table 3, prover phase decomposition** of every populated Table 2 cell (witness, encoding + commitment, arithmetic,
  lookup, ZK additional, serialization, other).

## The three drill-downs (`verity_numerical/bench/drilldown.py`, same store and validity predicate; layout fixed)
- **D1, variants and security properties**: every variant we built or tried, with its ZK property, operands hidden from
  the verifier, what binding rests on, soundness, and whether it is in Table 2 (which column, or why not).
- **D2, fastest measured `t.total` per variant and target** (the five rows): `seconds · overhead×`; ✓ = Table-2-valid, else
  the first reason as a letter (U not independently verified, I other instance set, P phase-sum, S shared hashing,
  Z class/ZK not the column's, K prover not on the row's SKU, B batch != 4096, X other). Shows the fastest independently
  verified result and footnotes a faster unverified one.
- **D3, communication and verifier cost per Table 2 cell**: proof bytes per batch, prover-to-verifier Gbit/s to keep pace,
  verifier-to-prover bytes (coins), rounds, verifier CPU s per batch, verifier cores to keep pace, same-datacenter live tax.

## Rules the user set (all in force)
- Same security for every variant: 2^-128 target AND achieved (union-bounded). No 100-bit cell in Tables 2/3, SP1
  included; a variant that cannot honestly reach 2^-128 is reported as such in D1/D2, never relabelled.
- A Table 2 cell needs: K = 1536, B = 4096, the row's frozen instance set, prover on the row's SKU, the column's proof class,
  validation passed, phase buckets summing to `t.total`, proof bytes dumped and preserved, `verified=accepted` by a
  non-producer, no red-team downgrade. The renderer's "Rejected" list names the reason for every result left out.
- Phase-sum: a result whose buckets exceed `t.total` beyond tolerance stays out; fix the accounting, never the rule.
- Re-packed instances count as the frozen set only with an `instance-equiv/v1` artifact, verified by a non-producer,
  showing decoded x, W, y byte-identical (footnoted).
- SP1 column = best valid SP1 variant. The two SP1 approaches are named **SP1 stock** (unmodified SP1) and **SP1 precompile**
  (the TC_DOT chip fork) everywhere: D1/D2 row labels, kb notes, briefs (user, 2026-09-24). Table 2's frozen footnote still
  reads "modified SP1 (TC_DOT chip)" (tables.py is frozen); read it as SP1 precompile. SP1 precompile beyond A100 is on HOLD.
- SP1 security (user, 2026-09-24): SP1 reaches only ~100 bits, field-bound (KoalaBear^4), and cannot reach 2^-128 without
  protocol changes; recorded in D1 (Table 1 frozen). State it for a whole proof (all shards, like B-Ligero over
  sub-batches), per-shard figure secondary.
- A-GKR column = best valid A-GKR implementation in its class; the user wants it hill-climbed and on every row. A more
  promising GKR variant may get its own lane (standing permission).
- Table 1's A-GKR hash is SHA-512 Merkle (corrected 2026-09-24).
- Any change to a definition, column or rule above needs the user's explicit approval first.

## What "complete" looks like, and the gaps (render 2026-09-24 18:00Z + verifier-cost)
| Table 2 column | populated | missing |
|---|---|---|
| B-Ligero | 5/5 | keep improving (lane arith) |
| B-Ligero + in-proof hash | 5/5 | 3.5-4x the bare column; improve |
| A-GKR | 2/5 (A100 BF16, H100 BF16) | H100 FP8, 4090 FP8, 5090 NVFP4 |
| SP1 | 0/5 | every row: all SP1 results so far are 100-bit; needs a 2^-128 configuration or an honest "cannot" in D1 |
D3: all 12 current cells measured (verifier-cost, merged ab9573fd). D2: SP1 stock has all five targets at ~100-bit; SP1 precompile (TC_DOT) +
TC_DOT only A100 (fastest verified 5.81 s art:174d7b4d).

## Provisional cells (coordinator, user decision 2026-09-24 5:48 PM PT)
- RTX 5090 NVFP4 · A-GKR art:49757870: was provisional; red-team-lk PASSED all rewrites 2026-09-25 02:00Z (no downgrade).
  tables.py is frozen and has no marker; the flag is carried in the scoreboard's changed list and the digest. Pulled if red-team-lk FAILs.
- H100 FP8 · A-GKR art:ad76c106 (merged LK): provisional pending red-team-lk's statement-level check (2026-09-25 03:55Z).
- Rule kept for future statement rewrites: they enter Table 2 only after verify-po AND a red-team pass (verify-po holds the label).
