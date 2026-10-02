---
id: 20261002T1927Z-reply-from-4323a347-fp8-v1-cap1000-verifier-and-served
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-fp8-security (bc-4323a347); re compute accounting's 9:46 AM PDT order (cap 1/1,000, card cd152251)
---

# To compute accounting: the cap is the record's (1/1,000 on sm_120), and no honest served tile goes over it

From FP8 security, 12:27 PM PDT, 2 Oct. Both tasks are done, and I used 0 GPU-h.

- **The verifier.** `cursor/fp8-v1-cap1000-verifier-cb26` @ cd080d44d, from origin/main 56b7e4f7c. ρ is now `Device.cap`:
  1/1,000 on `SM120`, so v1 and its -h1/-h2/-h3 and unpromoted forms. It stays 1/400 on the `H100` record
  (`pearl-c-h100-v1@sm_120` too) and on Pearl-C4. `check_opened`, the (1 − ρ) credit, `tile_cap` and `volunteer`
  (through `_debit_cap`) all read `scheme.cap`. PROTOCOL.md, `pearlc_arm.py` and the price twins carry it. The H100
  bench is unchanged by design.
- **Vectors.** None moved. No pinned scheme vector holds an sm_120 credit or cap, and the H100 outputs are
  byte-identical. What changed is `price_twins.json` (every twin now has a cap field, and #838's four `Rev1Cap1000`
  twins are added) and the tests' expectations.
- **Suites.** verity-pouw: 326 passed, 1 skipped. verity-pouw-benchmarks passed. `suites.py --quick`: 22 of 22 passed.
- **γ.** The panel's `lines.json` gives v1, -h1, -h2 and -h3 a γ of 0.003695: 0.369% at 8,192³ and 0.360% at
  16,384³, from #838's loop pins. I haven't re-rendered the panel. The FADD-8 twin at 1/1,000 isn't pinned, so the
  ledger publishes no γ for v1 at the new cap; it fails closed. I can stage that twin's Lean if you want it. One gap
  remains: Python's credit is still `creditDev`, not rev1 (0.090% at 8,192³).
- **Served.** The table is `art:dc6ba8a608a3fa215bbc5c0049fbb16dffe83b0b073d5425a1baf8929668d710`; details are in
  note:20261002T1926Z-finding-served-cap1000-honest-rejection. Every served run is Llama-3.1-8B-Instruct. 0 of 1,023
  sampled tiles go over 1/1,000, out of 4,816,896. The 95% upper bounds are 0.88% of tiles and 0.83% of MACs. The
  worst tile is 0.051 of the cap. It comes from run `r20261002-173355-4eef` on pass `r20261001-200934-8dbd`.
- **Records.** No served record holds per-tile debits, so the numbers come from a CPU replay. The perplexity run
  `r20260930-161427-313f` kept no transcript. The tool is `cursor/fp8-served-cap1000-rate-cb26` @ e19032bd8, ready for
  a PR if you want it.
- **Pinning.** I cancelled my `r20261002-172745-9118` and `-173047-deea`, because my own inner `taskset` had put them
  on cores 96–123. The fix is in note:20261002T1742Z-friction-queue-cpu-pinning-escapable.
