---
id: 20260930T2259Z-handoff-from-proofs-formula-and-record-schema
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# The overhead formula is settled, and each run emits `hillclimb.json` for the console (the schema is fixed)

1. **Formula** (the research owner, 3:56 PM PDT; follow `backends/numerical/python/verity_numerical/bench/contract.py`):
   - 1 VU = one `GemmCoordinate_v2{K, DOT}` = K MACs = 2K FLOP.
   - overhead = peak ÷ R_proved, where R_proved = 2·K·VUs ÷ t_prove.
   - t_prove = every prover bucket (the contract's `t.<bucket>`: witness, commit, arithmetic, lookup, serialization), steady
     state (warm session, back to back), per accepted VU.
   - Setup (staging, circuit build) is reported beside it, not in it. **The verifier is excluded,** but record
     `verify_s_per_statement`.
   - Also record **GPU-held s/VU**: only that series shows the verifier fix.
   - peak: add `rtx-pro-6000-bse/{bf16,e4m3,e2m1}` to `census/hardware.json`. Use the FP32-accumulate figure (GeForce parts
     halve it), dense rather than the 2:4-sparse AI TOPS, at the stated clock, from NVIDIA's datasheet or the RTX Blackwell
     whitepaper.
   - M0's 4.80e6× isn't convertible yet (its measured-native FLOP/s is unknown). Keep it off plot (1).
2. **Each run's `result.json`** follows the campaign contract: fingerprint fields plus measurements. Use `fingerprint()` and
   `measurement()` from the contract, and run `validate()` until it returns empty.
3. **Each run also emits a declared output `hillclimb.json`,** with the schema in
   `note:20260930T2259Z-handoff-from-proofs-hillclimb-plots-spec` (`lanes/console/`). It carries the run labels
   `campaign=proofs-hillclimb`, `subcircuit=bf16/GemmCoordinate_v2/K=<K>` and `question=<text>`. Step 0 is the baseline at
   each K; keep the tile, batch and statement parameters fixed within a step.
4. **K:** Daniel's set is 2,048, 4,096, 8,192 and 16,384. The research owner also suggested K = 1,536 (ledger-comparable) as
   an optional extra, once the four are baselined.
5. **Node 1's Kueue is admitting again** (3:57 PM PDT; disk at 73%). The steward pauses at 82%, so still keep outputs small.
