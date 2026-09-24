---
id: vllm-refactor/coordinator-checks-4
lane: vllm-refactor
kind: note
created: 2026-09-24T16:45Z
---
# Coordinator spot-checks of survey-observe-acquire-tp.md (at f0810a11)

## Confirmed
- **The plan's residual tables depend on whether torch is importable.** `acquire/plan.py:371-377`: `_lifetime_tables()` swallows the ImportError from `native_collect` (which imports torch at module level) and uses empty `GATHER_FLUSH_LEAVES` and `PRE_FLUSH_LEAVES`. So a CPU gate without torch and the GPU stage evaluate different tables.
- **An environment variable changes the committed leaf layout.** `acquire/native_collect.py:721`: `VERITY_LAYOUT` selects chunk-leaf-v1 or chunk-leaf-v2 inside library code. The first survey also found that padding leaves read a different variable, `VERITY_LEAF_LAYOUT` (`commit/padding_steps.py:405`).

## Corrected
- **The prefix-equality finding (#12) is not about checkpoint shards.** `_eq` at `input_provenance/weights_of_record.py:676-677` treats two digests as equal when one is a prefix of at least 16 characters of the other. It is defined in and used for **program-digest** matching against the of-record set. Shard pins are compared through `pinned` flags (`:664-673`). This is a real weakness (a truncated digest is accepted), but medium severity, not a checkpoint-authentication hole.

## Already confirmed in the first spot-check
- TP value checks read committer buffers too (`tp/worker.py:1192` calls `OC.committed_reader(com)`), the same gap as single-rank Commit.
