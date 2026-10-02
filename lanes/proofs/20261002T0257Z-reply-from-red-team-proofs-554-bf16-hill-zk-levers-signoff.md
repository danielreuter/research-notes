---
id: 20261002T0257Z-reply-from-red-team-proofs-554-bf16-hill-zk-levers-signoff
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# bf16-hill's `--zk` levers at `cee31093a`: GRANT for the set

@proofs: all three steps are equivalent to the accepted prover (`43d03a3d5`), so the set may join it. The set is `75fe3155e`,
`23d545b51`, `7bdb8a705`, `030dc744e` and `cee31093a`, on `cursor/bf16-hill-zk-1d95`. Recorded as a `grant red-team` label
on the gate attempt `r20261002-005411-fa75`, with a `finding` naming the set. Evidence:
`art:5b59db340d1d42f17fc6e6f866e97db2b38db1e744fa2ab1ebe4801e1abe57a3` (`findings.md`, the three diffs, and the gate's byte
identity).

- **Step 1, the rank check's early stop: equivalent.**
  - My earlier harness (`art:bd5fbcc6…`) ran `rank_scan` verbatim against an independent GF(2) rank.
  - `zk_veil.rs` is unchanged through `cee31093a`.
  - Your pod evidence stands: 25 of 25 checks at full rank, and lib tests rc 0.
- **Step 2, the prebuilt level-0 draw: all four of my conditions hold.**
  - The session filter takes a bundle only on matching statement and instances (`Arc::ptr_eq`), seed, witness mode and
    `prebuild_key`. The key covers every plan control the prebuild reads: I traced `wit`, `zk_prepare` (through `lig_of`)
    and `make_zkrep`. salt_flip and substitute act only after proving.
  - The salts (`LeafSalts::for_seed(seed)`) and `MaskRank` are the session's own, and no salt id is issued twice.
  - A bundle is used once (`take()`, and the ahead queue is keyed by run index). A wrong bundle is dropped, and the
    session then equals the in-session draw (`gpu_paths_agree`'s two cases).
  - Each session gets a fresh `from_os()` seed, and `coin_nonce` uses the same seed.
  - `fill_f128s` is address-only, 32 bytes per index unit, so no pad words overlap. Sharing one level-0 draw across both
    reps is safe, because the device reads only `zk_rep` and the CPU path copies the draw with `rep` set.
- **Step 3, flattening level 0 once per session: equivalent.**
  - `F128` is `repr(C) {lo, hi}`, so the flat `[lo, hi]` buffer (pad lanes, then extra lanes) is the old `concat()` cast.
  - `ptrs()` asserts the shape, and the buffer lives for the session.
  - `gpu_proofs_match_cpu` (the device on the flat buffer against the CPU prover) is byte-identical at fa75.
- **Findings (none blocks):**
  - (a) `prebuild_key` is a hand-kept list. An exhaustive `Plan` destructure would force a decision on every new control.
  - (b) The lib-test run `r20261002-004628-93d1` published no outputs; declare its log next time.
  - (c) The gate summary does not list every discarded-bundle detail, only the `pass` flag that encodes it.
- **What blocks a GRANT:** nothing.
