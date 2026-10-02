---
id: 20261002T0745Z-reply-from-red-team-proofs-554-pr792-gk
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: PR #792 (Theorem GK and T6's extraction), GRANT

Re: [PR #792](https://github.com/danielreuter/verity/pull/792) at `8f6d6953842efa68a955159e2236e80011c735bd`
(`cursor/zk-lean-gk-95d4`), beside `note:proofs/20261002T0735Z-finding-pr792-gk-statement-review`. Check
`r20261002-062825-e44d` passed at this exact head, all ten steps including `lean-audit` and `lean-agreement`. Evidence:
`art:da9e6079ab155dbc1643a00e18a9c0eb10e22a8559ddbb44cf82514180338bde` (`findings.md`, with file:line for every point).
Labels: `grant red-team` and a `finding` on `pr:792@8f6d6953842efa68a955159e2236e80011c735bd`.

## Verdict: GRANT, with one non-blocking condition

**Q1. The bound is what the PR claims, with no hidden weakening.**
- `gk_simulate` (`GK/Theorem.lean:479`) bounds `|E_sim[Out.val φ] − E_real[φ]|` by
  `3δC + 8tδB + 3^{-t} + t/M + q²/2^513` for every `φ : V → [0,1]`.
- `Out.val` scores `bind` and `fail` as 0 (`GK/Sim.lean:41-44`). So this is a statistical-distance bound between the real
  view and the simulator's output, with bind and fail as ⊥ (for an event that contains ⊥, take complements).
- `bind_real` is the only semantic field of `Model`. It is GK's identical-until-bad: for V*'s fixed tape and the prover's
  fixed coin-tree nonce, a real-witness rewind with no coin conflict is the real run. Rust's `rewind` keeps the extraction
  run's `Hello` and refuses any other coin.
- `PrefinalClose` and `RewindClose` are Lemmas C and B as `Link.lean` derives them:
  - `δC = 2|L|δ₁`, at every coin;
  - `δB = 2·nH·δ₁`, at completed first runs only.
- The collision-resistance budget q is stated, not checked, as everywhere in the repository. Its honest value is about
  `(1+5M)·t′` hash evaluations.
- Two instantiation notes for the end-to-end statement:
  - a `Model` is per (V*'s tape, the prover's nonce ν), with ν outside `Ωd`, and `gk_simulate_avg` averages over ν. Rust
    does the same: it draws ν in the extraction run and reuses it.
  - the rewind views in `hS` and `hR` are truncated at V*'s first coin that differs from the first run's.

**Q2. The simulator is honest.**
- `Model.sim` is `gk` applied to `dummy`, `rwS`, `comp` and `bad` only (`GK/Theorem.lean:92`, `GK/Sim.lean:90-98`).
- It matches Rust's `gk_simulate` on four points:
  - a first run that does not complete is the output;
  - `4·runs` rewinds;
  - a coin conflict is ⊥ (Lean `bind`; Rust fails with an empty view);
  - an invalid opening aborts the rewind and the loop continues.
- It does not match on the cap. Lean's estimation stops at M runs and outputs `fail` there. Rust's `gk_estimate`
  (`zk_veil.rs:79-86`) has no cap, and PROTOCOL.md §9 says "with no cap".
- **Condition C1 (no new head):**
  - the PR body says the Lean simulator is `gk_simulate` with its estimation capped at M;
  - a follow-up either adds the cap to `gk_estimate` (it is the seed-injection harness, so this is cheap, for example
    `M = t·2^40`, with §9 updated) or corrects `GK/Sim.lean:7,12`, which describe Rust's simulator as capped.

**Q3. V* can choose degenerate coins, but the prover refuses them on the CPU `--zk` path before the proofs, so a run at
such coins never completes.**

`gk_simulate_hm96` assumes `hrank`, `hpad`, `hW`, `hpads` and `hβ` only at completed first runs (`GK/Link.lean:211-217`),
and the rewinds must answer exactly those coins: any other valid opening is `bind`. Each check is a function of the
committed coins and public data alone (PROTOCOL.md:389-390), so the real prover and the dummy prover refuse the same coins.
The code paths:
- **β = 0:** `prove_inner`, `live/src/zk_veil.rs:968-971`, returns `PROVER-STOPPED` after drawing β and before absorbing
  `Y` (974). A V* strategy exercises it: selftest `zk_verifier_commits_beta_zero`, `bin/flock-circuit.rs:3027-3044`.
- **Mask rank:**
  - `zk_masking`'s `at_open` (`bin/flock-circuit.rs:943-961`) runs at the opening's label, before any opening message
    (`zk_veil.rs:310-311`, 334-343), and panics with `PROVER-STOPPED`.
  - `mask_rank_ok` (`zk_veil.rs:1045-1069`) tests full GF(2)-rank 128·k, which is Lean's `Rank`.
  - The claim points are per table and shared by the two reps (`bin/flock-circuit.rs:2434-2435`), so the last check
    covers all four masked claims.
- **Dependent ρ:** flock-zk-b684b12.patch:500 asserts `rho_independent` (`PROVER-STOPPED`) after drawing ρ and before
  absorbing T′ and ȳ (505-506). `rho_independent` (patch:297-300) is the 2×2 determinant over F128, which is `Wr`
  bijective. On the device path the refusal is CUDA's return code 240 (`gpu_circuit.rs:994`); I did not read the CUDA side.
- **PadOnto and PadsOnto:** these hold at every coin by parameters, so no refusal is needed:
  - `t_pad = 2·q0`, with `zk_queries0`'s refusal of oversized `t_pad` (`zk_veil.rs:63-65`, `bin/flock-circuit.rs:118-134`),
    and the named assumption `PadNonvanishing`;
  - `K_PAD = 192 ≥ Q = 168` (`zk_veil.rs:50-53`).

A refusal is a panic caught at `bin/flock-circuit.rs:2622`. After it, `session_finish` sends only `Finish` (2720-2726),
and the honest prover sends no proof before the last coin (`early_proofs` is `false` by default; it is a test-only prover
without the barrier). What V* sees before a refusal is the pre-final view, which Lemma C covers at every coin.

**Obligation O1 (for the end-to-end `--zk` theorem, not this PR).** No Lean statement yet derives `hrank`, `hβ` and `hW` from
`comp`. The instantiation must define `Model.comp` so that completion implies the prover's three checks passed at the
view's coins. The code as it is satisfies this.

**Nit (no condition):** only β has a V* strategy that exercises its refusal. A `dependent-rho` strategy (ρ₁ = ρ₀) and a
`low-rank` strategy would cover the other two refusals.
