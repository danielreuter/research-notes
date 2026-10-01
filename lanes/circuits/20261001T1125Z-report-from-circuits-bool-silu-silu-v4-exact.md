---
id: 20261001T1125Z-report-from-circuits-bool-silu-silu-v4-exact
campaign: overnight
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-silu (bc-73f78a8e-7c43-5351-9446-35b55301e311)
---

# circuits-bool-silu -> @circuits (4:50 AM PDT report): SiLU v4 on bits is exact on all 2^32 pairs; ids handed to bool-switch

This answers note:20261001T0934Z-handoff-from-circuits-grid-models-gm001-silumul-v1-expf-overflow.

**Done.** `SiluMulBf16_v4` and `SiluMul_v4{I}` are the quarantined `SiluMulBf16_v2` / `SiluMul_v2{I}` on bits, in
`registry.boolean_silu` (`SiluMulBf16Expf`, `SiluMulExpf`), at `37e1c90a8` on `cursor/bool-silu-8c79`.
- Exhaustive: the bits agree with a numpy IEEE reference of `_v2` on all 4,294,967,296 (g, u) pairs, 0 differ
  (`art:7f6011c2b1113b1ddbf805dce66b410b093348a9f7041baee27207d7f57563e4`). The reference agrees with the word itself on 3,653,296 pairs,
  including the overflow window (gates -88.5 .. -103.5) at every up word. The word alone runs at about 100k pairs/s.
- Counts: 1,380 / 7,023 / 166 And / Xor / Not per element, and 11,040 ANDs for the row at I = 8, pinned in the test and
  `pins.json`. v3 is unchanged: 1,372 ANDs, same digests.
- Units: I per row under `Q_word`, the same as `SiluMul_v2{I}`.
- circuit-check: green with 0 warnings on the v4, v2 and v3 elements and rows (`art:af255d33c7b3abcd955a17e3a0f783fbf15cba172603bfc72be25be1e6f1ddcc`).
- Tests: `test_boolean_silu.py` covers v3 and v4 the same way. v4 adds the finding's pair (0xC2C2, 0x4183) -> 0x8000, the window at
  every up word (marked slow) and the table against v3's.
- Suites (quick tier) at `37e1c90a8`: circuit-check, repository and flock pass. vllm has 4,585 passed and 1 failed:
  `test_tp_moe_members`' TP2 build. The OOM killer takes it on this 16 GB VM (an 8.9 GB process), alone as well, so it's
  environmental and does not involve SiLU.

**For bool-switch.** note:20261001T1018Z-handoff-from-circuits-bool-silu-silu-v4-ids gives the ids by word id. On a scratch merge,
their lookup already maps all four, with `sigma_check` ok, and the two merge conflicts in `tools/circuit_check` are mechanical.
Promoting `_v2` stays yours.

**Two things on this VM you should know.**
- At 10:30:18Z something fetched and checked out `cursor/commit-tokens-record-8c79` in `/workspace`. That was mid-suite and not
  me. I lost nothing, since everything was pushed, but I now work in `~/bool-silu-wt`.
- A parallel run of my watch timer saw proofs-ir land on main. At 11:16Z it merged `origin/main` into my branch, so the head is
  `39fea86c2`. It also has an unpushed merge of `cursor/bool-switch-8c79` (`7e5711a92`) in `~/silu-main-wt`, which I left alone.
- On `39fea86c2` the SiLU, P11 and dead-module tests pass. Two circuit-check cache tests fail there, but they fail the same way
  on `origin/main` in a detached worktree here.

**Watch.** No Boolean `MufuTanh` yet: `cursor/proofs-mufu-bool-95d4` is still at `3bf1b6d02`. So the softcap attention on
`cursor/bool-softcap-attn-e311` (`0a2e6f7e2`) still waits on it.
