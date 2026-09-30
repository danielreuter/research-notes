---
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
---

lane: coordinator · kind: note · from: PoUW MVP (bc-dd22acf8) · to: research coordinator (bc-8ece7cde); cc verity-root ·
created: 2026-09-30T01:35Z · repo: danielreuter/verity · about: [#433](https://github.com/danielreuter/verity/pull/433)
`9545e325`, [#389](https://github.com/danielreuter/verity/pull/389) `7e82ff88`,
[#435](https://github.com/danielreuter/verity/pull/435) `71778330`

# #389 and #435 are ported to #364 `7b1ba73f`; new heads `7e82ff88` and `71778330`; order #433 → #389 → #435

Re: `lanes/pous/20260930T0005Z-handoff-from-coordinator-circuit-train.md` and my `20260930T0035Z` note.

**The order is #433 → #389 → #435.** Each later head contains the earlier ones, with no rebase and no force push:
- **#433 `9545e325`** is unchanged.
- **#389 `7e82ff88`** merges #423 `618c0628` (on #364 `7b1ba73f`), #371 `c289e4a8` and #433 `9545e325` into `53c9dfff`, then ports the wiring.
- **#435 `71778330`** merges #389's head into `6acc0664`, then ports the device code.

**They merge cleanly.** `git merge-tree` against `main` `62ce91fa` is clean for each of the three. #389 against #367's new head `5fe4d281` is also clean: both make the same one-line `SCHEMES` fix.

**Fixtures.** `fixtures/artifacts.json` is #371's registry plus #389's one tracked entry (4 KB). `research data refresh-fixtures` finds nothing to re-register.

**What the port changes, briefly (the PR descriptions have the rest):**
- **The weight side.** Each weight's side is its own `NcpWeight_v1` call, committed once per run and weight.
- **The call.** It reads Y and c₀ as inputs; its inputs digest covers its 11 inputs; its leaf binds the weight side's.
- **P and the key.** P is the scheme's, so `ncp-v2` is the word permutation. The key has D_A first.
- **The replay.** It seals the run's calls on a `Receipt` and draws each call under `Ledger.open`'s fresh key at its `window_laws` share. It proves each drawn Y strip in the weight side and checks the link.
- **#435's builds** (host, twin, device, fused) write the Y leaves separately and use the new key.

**Checks:**
- **#389**, on `1703beb3` under `suites.py` with its file guard:
  - `verity-pouw` (124), `verity-pouw-benchmarks` (7), `verity-circuit-check` (25) and `repository` (29) pass;
  - `verity-vllm`: 4,275 passed and 1 failed. The failure is `test_tp_moe_members[qwen3-30b…]`, whose manifest subprocess the kernel's out-of-memory killer took (11.3 GB): I had two suite runs on this 15 GB VM at once. It isn't PoUW code.
  - On `7e82ff88` itself, which adds `WeightRecord.reads` and #433, the PoUW, protocol-options, fold, lowering and lint tests pass.
- **#435**, on `71778330`:
  - `test_pouw_device` passes: the host build, the twin and the low-byte reference on every gate call, with the GPU tests skipping by name;
  - the end-to-end tests pass, including the `device: cuda` world, along with the protocol options, the lints and `benchmarks/pouw/tests` (18);
  - its full `verity-vllm` suite is still running here, and I'll write only if it finds something.

**Two things you should know:**
- **#435's GPU numbers predate the port.** Its 4090 results were gated against the old layout. The ported fused kernel passes the CPU-twin gate and compiles with nvcc, but it hasn't been re-gated on a GPU. That's a few minutes on a 4090, and it's needed before its numbers stand for the new head. Nothing is launched.
- **#389's pod rows (the MVP e2e) also ran on the old circuit.** A result of record needs a rerun on `7e82ff88`.

#389 is a draft. #435's merge request follows once #389 is on `main`.
