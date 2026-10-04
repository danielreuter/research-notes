---
id: 20261004T2202Z-report-relay-docs-lean-trusted-layer-review
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/lean-trusted-layer-review.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/lean-trusted-layer-review.md`, sha256 `985ee68b57d2fbce3530b2f880d6c465480594cf4a1459e6fea9317dda3c11a7`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Lean trusted layer for POUS — statement red-team review

Verdict (second pass, 27 Sep 2026): **GRANTED WITH CONDITIONS.** First pass: **NOT GRANTED** (below, kept for the record).
The second-pass section is at the end; it supersedes the first-pass verdict.

## First pass (superseded)

Two problems would survive an hour of proof-focused review. (1) The grader accepts a `sorry`-backed
proof of *any* pinned target, because `grade.sh` verifies `TRUSTED.sha256` and reads `AXIOMS` around a
submission compile that runs arbitrary IO — the kernel replay never sees the attack. (2) The pinned
requirement `Meets` is satisfied by a scheme whose decoder ignores the codeword: all of `W` is parked in
the audit-free `pp`, `C` is incompressible noise, and the audit still passes. Both are machine-checked
below with the toolchain in `lean-toolchain` (Lean `v4.34.0`, Mathlib `5ed2965`, `lake exe cache get`);
the trusted layer itself builds and `check.sh` prints `ALL CHECKS PASSED` unchanged. All exploit files are
in a scratch copy; the store copy is untouched (`TRUSTED.sha256` still verifies).

## Findings

| # | Sev | Lean location | Witness / exploit | Suggested fix |
|---|-----|---------------|-------------------|---------------|
| F1 | **Critical** | `grade.sh` (hash check L21 *before* `lake build PousSubmission` L37; `AXIOMS`/grader read L38) + `Grader/Main.lean` (reads `AXIOMS` and `Pous` oleans from disk at run time) | Submission with a compile-time `#eval` that appends `sorryAx` to `AXIOMS` (then restores it): `theorem solution : Pous.Pinned.Theorem1ii := sorry` → **PASS**. A variant that replaces `.lake/build/bin/pous-grader` with a script emitting a hardcoded PASS accepts an arbitrary statement. Both verified; files self-restore so the later `TRUSTED.sha256` recheck passes. | Grade in a sandbox on a **read-only** checkout; give submission elaboration no filesystem-write access. Re-verify `TRUSTED.sha256` **and** hash `AXIOMS` + the grader binary + the `Pous` oleans *after* the submission compiles and immediately before the audit. Read `AXIOMS` into the grader before building the submission. |
| F2 | **High** | `Pous/Accounting/Params.lean` `Meets` (L39–42); `Pous/Model/Audit.lean` `AuditSecure` (L76–82); `Pous/Model/Scheme.lean` `Correct`/`SpaceBound` (L46–52) | `RedTeam.junk_meets` (3 axioms): scheme with `n=t=2660, B=1, ℓ=133`, `enc W _ r := (W, fun _ => r)`, `dec pp _ _ := pp` proves `Meets junk .simultaneous D Q k 0` for all `D,Q` and `k ≥ 1`. `dec` never reads `C`. | The model must tie retention to `W`. Bound `|pp| ≪ |W|` (the intended pp is a short public key/seed, not a copy of `W`), or charge `pp` into the ρ‖C‖ state, or make the audit guarantee reconstruction of `W` rather than of `C`-blocks. Confirm the intent with the problem statement (see below). |
| F3 | Medium | `Pous/Accounting/Params.lean` `Meets` ε (L39); `AuditSecure` δ+ε bound | `RedTeam.meets_eps_one` (3 axioms): every correct, space-bounded scheme proves `Meets sch rv D Q k 1`. Since `pr ≤ 1` always, any `ε ≥ 1−δ` makes the audit clause vacuous. | Require `ε < 1−δ` inside `Meets` (ideally `ε ≤ 2^{-λ}` or another named crypto bound), and have the grader reject targets whose `ε` is not a specified small constant. `m1_meets` uses `ε=0`, so drafts are not yet exploited — the definition still permits it. |
| F4 | Low (documented) | `Pous/Pinned.lean` `Theorem1ii` (L19–24); `PousTargets.fibre_count` | No exploit. For a correct scheme, untimed `INC(β,π)` forces `β ≲ 0.05·n`, far below `ρ‖C‖`, so `Theorem1ii`'s hypothesis is unsatisfiable at the operating point: the reduction is sound but can never be *instantiated*. | Keep, but annotate `Theorem1ii` as non-instantiable and grade the timed form for real use. The reviewer guide already states this (choice #7); make it visible at the pin. |
| F5 | Low (open) | `Pous/Model/Audit.lean` `SimResponder.bounded` (one `(D,Q)` for all `k`) vs `SeqResponder` (per round) | No exploit. Simultaneous reveal gives the adversary a single `(D,Q)` budget for all `k` answers, under-charging it relative to sequential's `k·(D,Q)`; a construction may pick `.simultaneous` to look more secure. | A policy call, not a bug: fix the deadline semantics (per-answer vs shared) in the problem statement, then constrain which `Reveal` a graded `Meets` may use. |

Not weaknesses (checked and sound): quantifier order in `AuditSecure`/`INC`/`Theorem1ii(Timed)` puts `W`
before the primitive and the coins, matching the problem statement; deterministic adversaries suffice by
the mixture argument; exactly-`S`-bit state is WLOG as strong as at-most-`S`; `⌊ρ‖C‖⌋` is the correct
conservative floor; per-block `TimedINC` is deliberate and necessary (a whole-expander form would make
`Theorem1iiTimed` false); the parallel-oracle `Prog` counts rounds/queries per primitive with free local
compute as intended; the pinned targets are genuine (not trivially provable) and the ideal-tag (`no vk`)
and sequential-reveal timing match the documented simplifications.

## Witnesses (scratch: `~/scratch/pous/Exploits.lean`, `~/scratch/exploits/`)

F1, registry tamper (`grade.sh SUB Pous.Pinned.Theorem1ii` → PASS with `sorryAx` in the reported axioms):

~~~lean
import Pous
#eval show IO Unit from do          -- runs during `lake build PousSubmission`, after grade.sh's hash check
  let orig ← IO.FS.readFile "AXIOMS"
  IO.FS.writeFile "AXIOMS" (orig ++ "sorryAx\n")
  let _ ← IO.Process.spawn { cmd := "sh", args := #["-c", "(sleep 20; printf '%s' ... > AXIOMS) &"] }
theorem solution : Pous.Pinned.Theorem1ii := sorry
~~~

The grep hygiene filter (`native_decide|implemented_by|extern|unsafe|skipKernelTC|debug.`) does not block
`#eval` / `run_cmd` / `IO`. A second file swaps `.lake/build/bin/pous-grader` for a script that prints a
clean PASS and restores it — accepting an arbitrary statement.

F2, decoder ignores the codeword (abridged; full proof compiles with `[propext, Classical.choice, Quot.sound]`):

~~~lean
def junk : Scheme IdealModel.plain where
  n := 2660; t := 2660; B := 1; ℓ := 133; B_pos := Nat.one_pos
  Coins := Bits 133
  enc W _ r := (W, fun _ => r)     -- pp := W (free at audit);  C := 133 fresh bits
  dec pp _ _ := pp                 -- decoding never looks at C
theorem junk_meets (D Q k : ℕ) (hk : 0 < k) : Meets junk .simultaneous D Q k 0
~~~

`Correct` holds via `pp` alone; `|C|+|pp| = 133 + 2660 = 2793 = 1.05·2660` is within the space bound;
state `⌊ρ‖C‖⌋ = 126` bits cannot reproduce the 133-bit noise block, so the audit passes with prob
`≤ 1/128 ≤ δ`. The 1/19 "retention" of `C` guarantees nothing about `W`.

## What Daniel should look at himself

- **Truth of the pinned targets.** I verified the reductions `Theorem1ii`/`Theorem1iiTimed` are *meaningful*
  and (on paper) sound, but did not machine-check a proof. These are what provers will target — read the
  statements, and in particular the per-block vs whole-expander choice in `TimedINC`, which is load-bearing
  for `Theorem1iiTimed` being true.
- **The problem statement's `pp` accounting** (root cause of F2): is `pp` meant to be short/public-recomputable
  (`|pp| ≪ |W|`), or charged into the ρ‖C‖ state? The current `|C|+|pp| ≤ 1.05|W|` with `pp` free admits the
  degenerate scheme; decide the intended bound before re-pinning `Meets`.
- **Deadline / reveal semantics** (F5): per-answer vs one shared `(D,Q)`, and which `Reveal` a graded `Meets`
  may use. This is a spec decision, not something the Lean can settle.
- **The certified numbers** (`Pous/Accounting/Numbers.lean`, `p₀ ≈ 0.978630`, `k = 214`): I confirmed they
  build; I did not independently re-derive the arithmetic against the report.

---

# Second pass (27 Sep 2026) — verdict: GRANTED WITH CONDITIONS

Re-reviewed on a fresh copy (`~/scratch2/pous`, same toolchain; `lake build` and `check.sh` both pass: 13
audited theorems on the three standard axioms, `leanchecker --fresh`, 1 positive + 9 negative grader
controls). The author's fixes hold up under the attacks I could mount. The remaining conditions are the
provisional modelling choices the author has flagged for Daniel, plus two grader-hardening items.

**F1 (grader escape) — fixed.** `grade.sh` now records hashes of the grader binary, `lean`, the trusted
sources and the package `.olean`s, compiles the submission with `lean` inside `unshare --user --pid --mount
--net` where every mount but the scratch dir is remounted read-only (with an explicit writability probe that
aborts if that failed), then re-checks all hashes and `TRUSTED.sha256` before grading; the allowlist and
pinned-target list are compiled into the grader (`Grader/Registry.lean`), not read from disk. I re-ran both
first-pass exploits and confirmed they now fail (they are also negative controls `rt_registry_tamper` →
`unregistered axioms: [sorryAx]`, `rt_grader_swap` → `does not have the pinned type`). I then attacked the
new boundary directly:

- **Load-time code execution.** A submission with `initialize do IO.FS.writeFile …` and one with
  `@[init pwnFn]` both compiled to `.olean` and were graded — the marker file was **never** written and the
  verdict was unaffected. `importModules` loads the submission as data; it does not run its initializers, and
  `lean -o …olean` emits no native code for them. So the "`.olean` at load time" vector (`initialize`,
  `@[init]`, env-extension registration) does not execute in the grader.
- **Environment-extension / attribute smuggling.** Even if it did, trust routes only through
  `base.toKernelEnv.replay newConsts` + `collectAxioms` on the kernel env; extension entries add no constants
  and no axioms, so they cannot forge `solution` or hide a `sorry`.
- **Compile-time IO.** Writes to `/tmp`, `$root` and `$root/..` from a submission `#eval` were all blocked by
  the sandbox; the submission still compiled and graded normally.
- **"Runs compiled code" filter + axiom audit.** `native_decide` is rejected twice over — the new
  `reduceBool/reduceNat/ofReduce*` used-constant filter and the `native_decide.ax` axiom in `collectAxioms`.

**F2 (`Meets` vacuity) — fixed, provisionally.** `Meets` now also requires `CodeHoldsW` (`|W| ≤ |C|`) and
`ε ≤ εMax = 2^-128`. My first-pass `junk` is dead: `CodeHoldsW junk` is `2660 ≤ 133`, false (author's
`junk_not_meets`). I checked for a **new** vacuity that `CodeHoldsW` (a size-only condition) might admit —
the task's "`C = W` plus noise, `dec` reads only a small part." It does not, and the reason is instructive:
the responder `A₂` receives `W` for free, so any scheme whose codeword is a simple function of `W` (plus
`≤ (X−1)|W|` slack) is caught by `AuditSecure`, not by `CodeHoldsW`. Machine-checked witness
(`~/scratch2/pous/Exploit2.lean`, 3 axioms): the identity scheme `C = W` (`n=B=100, ℓ=1, t=0`) satisfies
`Correct`, `CodeHoldsW` and `SpaceBound`, but `RT2.idsch_not_meets` proves `¬ Meets` because an adversary
that stores nothing and echoes `W` passes with probability 1 (`RT2.idsch_attack_pr_one`). So no new
vacuity; `CodeHoldsW` closes the `pp`-parking hole and `AuditSecure` (quantified over the `W`-reading
responder) does the rest.

**F3 (`ε` unconstrained) — fixed, provisionally.** `ε ≤ 2^-128` is required; `not_meets_eps_one` and
`not_meets_of_lt_eps` are correct (`ε = 1`, and any `ε > εMax`, are excluded).

**Negative sanity theorems (item 4) — they prove what they claim.** `junk_not_meets` discharges via the
`CodeHoldsW` clause (`h.2.2.1`), `not_meets_of_lt_eps`/`not_meets_eps_one` via the `ε ≤ εMax` clause
(`h.1`), each hitting the intended part of `Meets`; `junk_correct`/`junk_spaceBound` confirm `junk` fails
*only* on `CodeHoldsW`, so that clause is load-bearing. All 13 audited theorems build on the three axioms.

## New findings (second pass)

| # | Sev | Lean location | Note / suggested fix |
|---|-----|---------------|----------------------|
| G1 | Low | `grade.sh` `state()` (hashes `$root/.lake/build/lib/lean/*.olean` + grader + `lean` + trusted sources) | The re-hash does **not** cover dependency (`Mathlib`) `.olean`s under `.lake/packages/*/.lake/build/lib`, which `base ← importModules` trusts. Not exploitable today (the sandbox remounts them read-only and the `$root` probe covers them; grading fails closed if user namespaces are missing), but a poisoned Mathlib olean would inject a false constant into `base` if the sandbox were ever weakened. Hash every olean on `LEAN_PATH`, or build `base` only from hashed oleans. |
| G2 | Low | `grade.sh` step 3 (`unshare` … `\|\| fail "does not compile"`) | If unprivileged user namespaces are unavailable, `unshare` fails and the submission is reported as a submission-level FAIL rather than a `fatal` environment error. Fails closed (no false PASS), but misattributes. Assert user-namespace availability up front and `exit 2` if absent. |

## Conditions for GRANTED

1. Daniel confirms the provisional modelling choices the fixes encode: `CodeHoldsW` / `pp`-accounting (F2),
   `εMax = 2^-128` (F3), and the reveal/deadline semantics (F5). These are policy, now flagged in the guide's
   "Waiting on Daniel" section, not defects.
2. `CodeHoldsW` is a size-only condition; keep it paired with `AuditSecure` (which carries the real
   incompressibility-given-`W` guarantee) — do not weaken `AuditSecure` on the assumption `CodeHoldsW` covers
   retention.
3. Address the two grader-hardening items G1–G2.
4. Unchanged from the first pass: the pinned targets' *truth* still needs machine-checked proofs (F4 keeps
   `Theorem1ii` non-instantiable; the timed form is the one to prove), and the certified numbers were not
   re-derived.

---

# Proof verification and draft vetting (27 Sep 2026)

Done on a fresh copy (`~/scratch3/pous`, same toolchain), `TRUSTED.sha256` verified before and after every run.

## 1. Independent grading of the first proofs (Theorem 1(ii))

The `sha256` of each graded file matches `submissions/thm1ii/GRADE.txt` exactly
(`2765b2…9835b` `Theorem1ii.lean`, `daeec9…eb60` `Theorem1iiTimed.lean`). Re-graded with the store's `grade.sh`:

| File | Target | My verdict | Axioms |
|---|---|---|---|
| `Theorem1ii.lean` | `Pous.Pinned.Theorem1ii` | **PASS** (exit 0) | `propext, Classical.choice, Quot.sound` |
| `Theorem1iiTimed.lean` | `Pous.Pinned.Theorem1iiTimed` | **PASS** (exit 0) | `propext, Classical.choice, Quot.sound` |
| `Theorem1ii.lean` | `…Theorem1iiTimed` (control) | FAIL "does not have the pinned type" | — |
| `Theorem1iiTimed.lean` | `…Theorem1ii` (control) | FAIL "does not have the pinned type" | — |

Both proofs are **independently confirmed**: they prove the pinned statements on the three standard axioms, and each
is rejected against the other target. The proof is the report's §3(ii) compression argument (averaging + `exists_code`
over `fits`); the timed version uses the per-block expander `Option.elim (patch i) (A₂.prog …) Prog.ret`, so the
per-block `TimedINC` form (guide choice 6) is genuinely load-bearing.

## 2. Draft targets — pin verdicts

For A2/A3/A7/`m1_meets` I use the restatements from the [sms5 ideal-model review](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/sms5-review-ideal.md).

| Draft | Verdict | Reason / fix |
|---|---|---|
| `theorem1_i_timed` | **pin as is** | Sound timed 1(i): a `TimedINC`-breaker gives a sequential responder (store `w`, run `exp` per round), so `AuditSecure .sequential ⇒ TimedINC` at `β = S`, `π = δ+ε`. `{rebuild all} ⊆ {accept}` and is `I`-independent, so it holds for every `k`. Self-contained. |
| `theorem1_ii_seq` | **pin as is** | Faithful stateful-sequential 1(ii). The adversary class is pinned by `SeqResponder` (per-challenge `S`-bit state, `(D,Q)` per round = sms5 class (b)); coefficient `∑_{j<k} B^j = (B^k−1)/(B−1)` is the history union of tradeoff Thm 1. Unproven but well-formed and non-vacuous. |
| `theorem1_iii_timed` | **pin as is** (resolved §4) | Matches report 1(iii) except the `p_η` numerator drops the report's `− λ` (seed cost). That drop is now **proved sound** (`Theorem1iiiTimed.lean`, type-identical to the draft, three axioms): see §4. |
| `fibre_count` | **pin as is** | Report Prop 9(a) counting bound `(1−π)·2^{n+β} ≤ 2^{t+B·ℓ}`, self-contained; this is what makes F4 precise (untimed `INC` unmeetable at the operating point). |
| A1 (`a1_compression_card`, `a1_compression_pr`) | **pin as is** | An injection of `E` into `≤L`-bit strings gives `|E| < 2^{L+1}`; the ≤2^{L+1}−1 codewords argument is exact. Independent. |
| A2 (`a2_lemmaA_m1`) | **pin as is** | sms5 grants Lemma A for M1; the Lean bound `2^S·C(B,g)·∑_{h≤g}C((g+1)Q,h)/2^{ℓg}` matches it with `T := Q` per run and `M = 2^ℓ`. (The M2 follow-on, not present, would need the `Dist` hypothesis.) |
| A3 (`a3_seq_m1`) | **pin after fix** — superseded by A3′ (§4) | The class-mixing objection stands, but it is now moot: the generic class-(b) restatement **A3′ (`a3_prime`) is delivered and proved** (§4). Pin `a3_prime`; derive or drop the M1-specific `a3_seq_m1` (it follows from `a3_prime` + A2 with `G = True`, per the prover). |
| A5 (`a5_rabin_gcd`) | **pin as is** | `x²=y²`, `x≠±y ⇒ 1 < gcd(x−y,N) < N`: if `gcd=1` then `x=−y`; if `gcd=N` then `x=y`. Vacuous (hence fine) for `N` prime/0/1; meaningful for composite `N`. |
| A6 (`a6_rederive_untimed`, `a6_rederive_timed`) | **pin as is** | If `C` is re-derivable from `κ`-bit advice then `cmp = z, exp = R` rebuild `C` w.p. 1, so `INC(κ,π) ⇒ 1 ≤ π` (untimed) and a `κ`-bit adversary passes every sequential audit w.p. 1 (timed). Self-contained. |
| A7 (`a7_m1_params`) | **pin after fix** | sms5 F8: exact-rational evaluation is infeasible (`M^g` has ~5.3·10¹¹ bits) and `B=2^28 ≠` the script's `275,590,552`. Restate per sms5 **A7′**: certified **log** form, `λ' = 128`, `log₂φ(N)` not `w`, giving `k ∈ {117, 142, 175, 238}`. |
| `m1_meets` | **pin after fix** (conditional) | sms5: rests on **Conjecture B1′**, so it is a modeling claim, not a theorem about the real scheme. Pin only with B1′ as an explicit named-`Prop` hypothesis, on the fixed A3′/A7′, labelled as the ideal permutation model M1 — and record sms5 **F1**: at `w=2048, λ=128` the real RW–SMS scheme fails the target game (factor `N` in `2^{112} < 2^{128}` preprocessing), so it does **not** transfer. Structural clauses (`CodeHoldsW`, `SpaceBound`) hold with `t=0, n=B·ℓ`. |
| B1 (`b1_indep_set`) | **pin as is** | Proved (see §3), discharges the draft verbatim on the three axioms. |
| B3 (`b3_chain`) | **pin as is** | Proved (see §3) with the corrected `(D·q+1)/m` and tweaked chain. If moved to `Pinned.lean`, carry the `chain` definition; `Check.lean` supplies the one-line bridge. |

## 3. Pebbling submission (B1, B3 proved; B2 drafted)

**`Check.lean` reproduced.** Placing `B1IndepSet`/`B3Chain` under `Pebbling/` and running `Check.lean` against my
build gives exactly `AXIOMS.txt`: `b1_indep_set`, `b3_chain`, `b1_free_fraction`, `b3_chain_bounded`,
`pebbling_b1_as_drafted`, `pebbling_b3_as_drafted` each depend only on `propext, Classical.choice, Quot.sound`. The
`type_of% @PousTargets.b1_indep_set`/`b3_chain` checks confirm the proofs discharge the **drafted** statements
themselves (B3 through the identical-`chain` equality). With the B2 proof now landed (`B2Stacking.lean`), `Check.lean`
imports it too and adds `PebblingB2.b2_stacking`, `exists_path_avoiding`, `card_reach_ge` and `pebbling_b2_as_drafted`;
all ten declarations reproduce `AXIOMS.txt` exactly on `propext, Classical.choice, Quot.sound`, and `b2_stacking`
carries no `sorry` (only the separate `B2Draft` does). `pebbling_b2_as_drafted : type_of% @PebblingB2Draft.b2_stacking`
confirms the proof discharges the **reviewed** draft statement verbatim (the draft file, namespace-renamed). With the
Claims 13–14 proofs now landed (`FischClaims1314.lean`), `Check.lean` imports them and `FischDraft` too; I rebuilt all
seven `Pebbling` modules and reran it — all **15** declarations reproduce `AXIOMS.txt` exactly on the three standard
axioms, `claim13`/`claim14`/`green_before` carry no `sorry`, and `pebbling_claim13_as_drafted`/`pebbling_claim14_as_drafted`
(`type_of% @PebblingFischDraft.claim1{3,4}`) confirm the proofs discharge the reviewed draft statements verbatim.

**The two extra variants mean what `NOTES.md` claims.**
- `b1_free_fraction`: yes — for a loop-free digraph with combined in/out degree `≤ Δ` at each vertex, it yields an
  edge-free `S` with `n ≤ (Δ+1)|S|`; edge-freeness puts every parent of a vertex of `S` outside `S`, so labels
  outside `S` re-derive `S` in one round. Caveat (the author flags it too): `Δ` is the **total** degree, whereas a
  DRG bounds only in-degree `d`; the in-degree/Turán reading `n/(2d+1)` is the tighter "free fraction". Undrafted, so
  this is a proposed reading, not a pin.
- `b3_chain_bounded`: yes — it is the audit game's `(D,Q)` form, `Prog.Bounded D Q ⇒ Pr ≤ (Q+1)/m`, the same
  `b3_pr` core as `b3_chain` with total work `Q` in place of `D·q`.

**B2 (`b2_stacking`, Fisch 2018/702 Claim 12) — review.**
- *Faithful*, with the modelling choices the header lists: `DepthRobust` = §2.6 ("every ≥`αn`-node subgraph has a
  `≥βn`-node path"); the superconcentrator enters only as `DisjointPaths` (any equal-size source/sink sets joined by
  vertex-disjoint green paths staying in `V_i∪G_i` until the sink), which is exactly the property Claim 12's proof
  uses; DAG via a rank function; path length in vertices (hypothesis and conclusion use the same measure).
- *Non-vacuous*: the hypotheses are jointly satisfiable (a real DRG + superconcentrator connectors, `black=red=∅`,
  `α+δ<1` forced by `1 ≤ (1−α−δ)ℓ`), so the conclusion asserts a genuine unpebbled path; no hypothesis is
  unsatisfiable and the `DisjointPaths`/`DepthRobust` premises are met by the actual construction (not an
  F4-style uninstantiable hypothesis).
- *Quantifier order*: correct — graph, depth-robustness and connectors are fixed first, then the pebble placement is
  universally quantified within its budget, then `∃ P`; the conclusion picks the last layer (`t+1 = ℓ`). This is
  Claim 12's "for any placement … there exists a path."
- *Verdict*: **pin as is** (updated — the proof has landed). My earlier "pin after fix" asked to confirm that the
  conclusion, which is **strengthened** beyond Claim 12's literal wording (it demands `P` itself unpebbled *and* an
  **unpebbled** green path from each node to `V_ℓ`, where the claim's text asks only for a green path to an unpebbled
  node), is actually provable. `B2Stacking.lean` now proves exactly that strengthened statement (kernel-checked, three
  axioms), so the fix is discharged and no statement change is required. The strengthening is structural, not a
  fragile add-on: `G i` is defined throughout the downward induction as the layer-`i` nodes with an *unpebbled* green
  path to `V_t` (`IsPathTo green (Unpebbled black red) …`), and the core lemmas `card_reach_ge`/`exists_path_avoiding`
  are generic in the vertex predicate `Q`.
- *Would the existing proof survive a change?* Yes, for the one that matters. If the team instead prefers Claim 12's
  **literal** (weaker) conclusion, the current proof already implies it (stronger ⇒ weaker): only the final `refine`
  assembly of `b2_stacking` would change — the predicate-generic lemmas (`IsPathTo` composition, `exists_path_avoiding`,
  `card_reach_ge`, the `hbound` induction) are untouched. That matches the prover's claim that "only the final assembly
  should need rework." The same holds for a conclusion-only repackaging; a change to a *hypothesis* (e.g. an
  edge-count length measure in `DepthRobust`, or a different connector abstraction than `DisjointPaths`) would also
  touch the definitions and `card_reach_ge`, but I did not request either — the vertex-length, `DisjointPaths`, DAG and
  `0<n` choices are acceptable as documented.

**Fisch Claims 13–14 (`claim13`, `claim14`) — review.** Both are proved (see the axiom check) and discharge their draft
statements verbatim; they reuse B2's graph model.
- *Claim 13* (`δ < ε/4`): **pin as is.** Faithful — "at least `εn/2` unpebbled paths ending in `εn/2` distinct
  `V_ℓ` nodes" is modelled as a set `E ⊆ Fin n`, `εn/2 ≤ |E|`, each `b ∈ E` ending a B2-style (unpebbled, simple,
  `≥βn`, unpebbled-green-to-`V_t`) path; `node t` injective makes the endpoints distinct. The proof is the paper's:
  if `|E| < εn/2`, pebble the endpoints black too (`≤ (1−ε/2)n`) and apply Claim 12 at `ε/2`, which needs exactly
  `δ < (ε/2)/2 = ε/4` — so the `δ < ε/4` hypothesis is the right one. Non-vacuous; quantifier order as in B2
  (graph/DR/SC, then the placement, then `∃ E`).
- *Claim 14* (the white/green game): **pin as is.** The two review points hold. (i) **The reverse move needs a green
  child:** `Available`'s reverse disjunct is `(∃ u, green v u) ∧ ∀ u, green v u → u ∈ C ∧ (all white parents of u ∈ C)`;
  the `∃`-conjunct is necessary — without it a node with no green child would be pebbled for free (the `∀` is vacuous),
  which the draft header and Fisch's proof ("assuming it has at least one green edge target") both require. (ii)
  **Top-layer nodes have no green out-edge:** the hypothesis `htop : ∀ b u, ¬ green (node t b) u`, used so the green
  path's last vertex (`node t b`) has no green child, which drives `green_before`. The forward disjunct
  (`∀ u, StackedEdge u v → u ∈ C`) is "all parents (white and green) pebbled"; the reverse's "white parents of `u`"
  is `drg`-parents — both faithful to App. B's wording. Non-vacuous, and it carries only the hypotheses its proof uses
  (no DAG/DR/SC/pebble-count needed — a genuine minimality, and it stays true without them since it is proved).
  "Requires `t` rounds" is rendered as the per-node order bound `P[k] ∈ C r → k < r`, which is the usable content.

**B5 (`b5_ex_post_facto`, `b5_ex_post_facto_bounded`, Pietrzak 2018/194 Thm 10 + §8) — review.** A drafted target
(`sorry`, not in the axiom check; its two sanity `example`s do elaborate). *Verdict:* **pin as is, scoped** — the
statement is faithful and ready as a proof target for the **one-way-label** bound, provided the scope caveat below is
recorded with it.
- *Faithful & sound modelling.* `label G d H i = H(i, ℓ_par(i)) ⊕ d_i` (§8 PoR labels; sanity-checked); `d` is a
  parameter **fixed before the oracle**, which is not merely a simplification but the correct POUS model (the trusted
  layer fixes `W` before the primitive), and it legitimately drops §8's adaptive commitment step and its `q₁²/2^w`
  term (`d = 0` recovers the plain Theorem 10). `PebblingHard` via greedy `reach` is the right hardness notion
  (greedy is optimal, Remark 6). The explicit bound `N·2^m·(Q_tot²/2^w)^{s+1}`, `Q_tot = |VC|(Q+1)+N`, is Theorem 10
  rearranged with conservative slack (`+log N` for `|F|`, `s+1` for ">`s` fresh labels", `log Q_tot` for `log q₂`),
  so it is a looser — hence safer — form, not a strengthening. Both the `Bounded D Q` and `RoundBounded D q` variants
  are given. Non-vacuous (hardness is satisfiable; the bound is meaningful when `m + log N + α ≤ (s+1)(w − 2 log Q_tot)`);
  quantifier order correct (params/data, hardness, then `∀ A₁, A₂`).
- *P3 scope — I agree with the prover.* B5's model is the **standard, forward-only** pebbling game (`TopoDAG`,
  `reach`) with **one-way** labels. P3's labels `Enc(H(…), e^{(ℓ−1)}_i)` are **invertible**: local decoding is a
  **reverse (green) move** of Fisch's white/green game (the very move Claim 14 analyses on the pebbling side).
  Pietrzak's ex-post-facto compression counts one saved table entry per fresh one-way label; with invertible labels a
  fresh `e^{(ℓ)}_i` only helps if `e^{(ℓ−1)}_i` is already known, so the accounting does not carry over, and Fisch
  §4.2 explicitly leaves the labelling↔pebbling equivalence for that game **open**. So B5 gives P3-type graphs a bound
  only for one-way labels (no local decode); a **P3 bound with local decoding needs a new reduction for invertible
  labels, which is not stated in any current target.** Even the one-way bound does not yet connect to Claims 12–14: a
  bridge from B2's graph model to `TopoDAG` (with `δ = 0` hardness from Claim 13) is still needed.

## 4. Theorem-1 family and Track A proofs (independent build)

Built both folders on the fresh copy (each file standalone: `import Pous` + a few `Mathlib`). Every theorem compiles
with no `sorry` and `#print axioms = [propext, Classical.choice, Quot.sound]`. For each of the eight theorems that has
a `PousTargets` draft I also ran an independent **type-identity** check: renaming the submission namespace to
`SubCheck` and elaborating `theorem chk : type_of% @PousTargets.X := @SubCheck.X` (the `Check.lean` method); all eight
compiled, so each proven type is defeq to its draft, on the three standard axioms.

| Theorem | Axioms | Type = draft? | Verdict |
|---|---|---|---|
| `theorem1_i_timed` | 3 std | yes | **pin as is** — proved as drafted (confirms §2). |
| `theorem1_ii_seq` | 3 std | yes | **pin as is** — the drafted `(∑_{j<k}B^j)·π` naive-union bound is proved; a tighter `k·π` is possible but neither drafted nor needed. |
| `theorem1_iii_timed` | 3 std | yes | **pin as is** — resolves the earlier "pin after fix"; the `−λ` drop is proved sound (below). |
| `fibre_count` | 3 std | yes | **pin as is** — proved (report Prop 9(a)); underpins F4. |
| `a1_compression_card`, `a1_compression_pr` | 3 std | yes | **pin as is** — proved. |
| `a6_rederive_untimed`, `a6_rederive_timed` | 3 std | yes | **pin as is** — proved. |
| `a3_prime`, `a3_prime_lam` (new, `PousTrackA`) | 3 std | new draft | **pin as is** — see below. |

**A3′ (`a3_prime`/`a3_prime_lam`) — pin as is.** This is the sms5 A3′ restatement I asked for, and it is faithful and
proved. (i) *Class (b) only*: it quantifies over `SeqResponder`/`TimedProdResponder` (state `S` bits at each challenge,
`(D,Q)` per answer), so the review's `T` is `Q`; class (a) is correctly omitted (the layer has no unbounded-carried-state
responder type). (ii) *Lemma A as a named `Prop`*: `LemmaA sch S D Q g Γ G` is a hypothesis, per the layer's
no-`axiom` convention, and it ranges over exactly the `(state-function, per-block predictor)` shape of `a2_lemmaA_m1`.
(iii) *`Pr[¬G]` charged once*: the bound is `((g−1)/B)^k + (∑_{j<k}B^j)·Γ + pr(¬ G W)` with the good-event (the M2/M3
`Dist`, and `True` for M1 so the term vanishes) added **once**, not folded into `Γ` and multiplied by `|Hist|`. The
`(g−1)/B` and the `∑_{j<k}B^j = (B^k−1)/(B−1)` history count match the review; `a3_prime_lam` gives the folded
`|Hist|·Γ ≤ 2^{−λ'} ⇒ … + 2^{−λ'}` form. Non-vacuous (edge cases `g=0`/`Γ≥1`/`k=0` degrade gracefully), correct
quantifier order (the Lemma-A hypothesis before the `∀ (W, A₁, A₂)`). It supersedes the class-mixing `a3_seq_m1`.

**The `−λ` drop in Theorem 1(iii) is sound — I agree, and the proof settles it.** The report stores a `λ`-bit random
seed in the compressed string, so `λ` enters the length and hence `p_η`. The draft instead uses, for each seed value
`s`, a *deterministic* `(cmp_s, exp_s)` pair with `s` hard-coded; `TimedINC` quantifies over every deterministic pair,
so `Pr_setup[pair s rebuilds C] ≤ π` holds for each `s` with the seed costing **zero** message bits — hence no `−λ`
in `p_η`. The seed is averaged only in the analysis (`E_s Pr[fits_s] ≤ π` since each term `≤ π`, plus a miss term
`≤ 2^{−λ'}`), not stored. This is exactly legitimate because the ideal-model `TimedINC` places **no size/uniformity
bound on the compressor**, so a seed-specialised `cmp` is free; the prover's own caveat is right that a later
compressor-bounded `INC` would turn the hard-coded seed into non-uniform advice and bring the `λ` charge back. The
proof confirms it: `Theorem1iiiTimed.lean` proves the drafted bound verbatim — `p_η` numerator `(β−S−B)` with **no**
`−λ`, while keeping the `k·(2⁻¹)^lam` miss term (its `lam` is the report's `λ'`, not the seed length) — on the three
standard axioms. So restoring `−λ` would only weaken a true statement; **pin as is**.

## 5. Pinned layer check (24 statements)

Focused pass on a fresh copy: `TRUSTED.sha256` verifies, `lake build` succeeds, and **`check.sh` prints ALL CHECKS
PASSED** — 13 trusted theorems on the three standard axioms, `leanchecker --fresh` (kernel replay from empty), the
reference `KFloor` PASS, and every negative control rejected, now including a **"no user namespaces → exit 2"** control
(the earlier G2 hardening note is addressed; the sandbox fails closed as an environment error, not a submission FAIL).
The 24 pinned names in `Registry.lean` match `Pinned.lean`; 17 have PASS submissions (the rest — `A2LemmaAM1`,
`A5RabinGcd`, `A7Params`, `M1Meets`, `B5ExPostFacto{,Bounded}` — are pinned but open, and the lone `A2LemmaAM1` "FAIL"
in `track-a/GRADE.txt` is a wrong-target control, not a failed proof).

- **Statements and moved definitions are token-identical to the reviewed drafts.** I read `Pinned.lean` against the
  drafts and the moved definition files: `Model/M1.lean` (`codeEquiv`, `perms`, `m1`), `Model/HashChain.lean`
  (`chain`), `Model/Pebbling.lean` (`DepthRobust`, `StackedEdge`, `DisjointPaths`, `Unpebbled`, `Available`,
  `IsPebbling`), `Model/Labelling.lean` (`TopoDAG`, `LabelQry`, `bxor`, `label`, `reach`, `PebblingHard`) and
  `Assumptions.LemmaA` are verbatim copies (only the namespace changed, e.g. `PebblingB2.StackedEdge → Pous.DRG.StackedEdge`).
  Each pinned `Prop` is the draft's binders and conclusion. I confirmed this by kernel definitional equality:
  re-grading a sample across every category — `Theorem1iiiTimed`, `A3Prime`, `FibreCount`, `B2Stacking`, `B1IndepSet` —
  all returned **PASS** on `[propext, Classical.choice, Quot.sound]`, i.e. each pinned type is defeq to the
  submission's proven draft (the wrappers are `solution : Pous.Pinned.X := @<draft>`; a defeq mismatch would FAIL, as
  the wrong-target controls do). The cross-namespace `StackedEdge`/`DepthRobust` unfold to identical bodies, so
  `@PebblingB2.b2_stacking` grades against `Pinned.B2Stacking` cleanly.

- **A7′ (`A7Params` via `A7Row`) — the change is sound.** `A7Row logHG B S T k := ∃ g, 1 ≤ g ∧ g ≤ B ∧
  ((g−1)/B)^k ≤ 1/100 ∧ ∀ M ≥ 2^2048 − 2^2029, logHG … M ≤ −128`. The **"some g works"** existential is the right
  shape for a parameter certificate (the prover exhibits `g`); it is not trivially satisfiable — `g = 1` kills the
  soundness factor but leaves `logHG ≈ S ≈ 5.2·10¹¹ ≫ −128`, so `g` must thread `g ≲ 0.96·B` (soundness) against
  `g·log₂M ≳ S` (compression), a genuine tight conjunction (the sms5 witnesses `258,033,293 …` sit in that window).
  The **domain `M ≥ 2^2048 − 2^2029`** (`log₂M ≥ 2048 − 2.8·10⁻⁶`, which `φ(N)` meets for a 2048-bit `N`) is used
  monotonically: `logHG` is decreasing in `M` (the `−g·log₂M` term), so `∀ M ≥ M₀` reduces to the worst case `M₀`,
  a real inequality — non-vacuous, and the four rows (M1 `k=117,142`, M2 `k=175,238`) are the review's.

- **`M1Meets` carrying B1′ as a hypothesis — sound and non-vacuous.** `M1Meets := ∀ D, B1Prime (m1 2^28 2048)
  (2^2048) (stateBound ρ) D 2^20 117 → Meets (m1 …) .sequential D 2^20 117 εMax`. This is **not vacuous**: for M1 the
  hypothesis `B1Prime` is *true* — it follows from the proved `A2LemmaAM1` and `A3PrimeLam` with `G = True`
  (`Pr[¬G] = 0`) and `gammaM1`'s `M^g = 2^{ℓg}` at `Mdom = 2^ℓ = 2^2048` — so `M1Meets ⟺` the genuine `Meets`, whose
  proof needs A7′ row 1's `g` (hence `M1Meets` stays *open*, correctly). Keeping B1′ as a hypothesis is the deliberate
  guard that the claim not be misread as an unconditional RW–SMS result (sms5 F1: it does not transfer at `λ=128`).
  Structural clauses hold (`n = B·ℓ`, `t = 0`). One observation, conservative not a bug: A7′ certifies at record size
  `S = ⌊(18/19)·2056·B⌋` (RW–SMS `w+8`) while `M1Meets`'s `stateBound` uses `ℓ = 2048`; since `gammaM1` grows with
  `S` and `2056 > 2048`, the A7′ margin at the larger `S` implies M1's at the smaller `S`.

- **No new vacuity from the moved definitions.** Every pinned hypothesis remains satisfiable under the trusted defs
  (DRG `DepthRobust`/`DisjointPaths` by a real DRG + superconcentrator; B5 `PebblingHard` by the draft's own sanity
  instance; `LemmaA`/`B1Prime` for M1 from A2/A3′), and no definition was altered to trivialize an event. The
  `label` recursion, greedy `reach`, and `Available` reverse rule (`∃` green child) are unchanged from review.

**Verdict (pinned layer check): PASS.** The pinned layer faithfully realizes the reviewed statements — moved
definitions verbatim, pinned `Prop`s token-identical (defeq re-grades), both deliberate changes sound and non-vacuous,
`check.sh` green, and a re-graded sample of the 17 PASSes reproduced on the standard axioms. No new blocking finding;
the overall verdict stands at **GRANTED WITH CONDITIONS** (the provisional modelling choices `CodeHoldsW`/`εMax`/reveal
and the still-open targets — `A2`, `A5`, `A7′`, `M1Meets` — remain; `B5ExPostFacto{,Bounded}` are now proved, §6).

## 6. B5 folder: grading, the B2→B5 bridge, and the one-way stacked bound

Independently, on the fresh copy (`TRUSTED.sha256` verifies).

- **Both B5 solutions grade PASS.** `Solution-B5ExPostFactoBounded.lean → Pous.Pinned.B5ExPostFactoBounded` and
  `Solution-B5ExPostFacto.lean → Pous.Pinned.B5ExPostFacto` each return **PASS** on `[propext, Classical.choice,
  Quot.sound]`, sha256 matching `AXIOMS.txt` (`e9d997…`, `00842b…`); the two cross-controls (each against the other
  target) FAIL with "does not have the pinned type". So the two pinned B5 statements are proved.

- **Bridge `B2ToB5` — faithful, and the proof assumes nothing silently.** `b2ToB5_of_claim13 : FischClaim13 → B2ToB5`
  builds (three axioms). Faithfulness: it is B5's greedy *black* pebbling over all `StackedEdge`s with `δ = 0` and
  `red = ∅` (one-way labels, no green/reverse move — Claim 14 is not needed), and Claim 13 supplies the unpebbled
  `βn`-path that delays black pebbling. The one thing to check — that the proof does not lean on an unstated
  premise — holds: Claim 13's `hdag` is **derived** from the given numbering (`hG`: `e u ∈ G.par (e v) ↔ StackedEdge
  u v`, so rank `= e` and `par_lt` give acyclicity), not assumed; every other Claim-13 hypothesis (`hnode`, `hlevel`,
  `hdr`, `hsc`, `hn`, `hε`, `hℓ` at `δ=0`) is a bridge hypothesis. Non-vacuous (a real DRG + superconcentrator with a
  topological `e` satisfies it) and the quantifier order is correct (graph, DR, connectors, numbering fixed, then
  `s,D,k` within their budgets, then `PebblingHard`). `StackedOneWay.lean` discharges it unconditionally
  (`fischClaim13 := @PebblingFisch.claim13`, Claim 13 copied verbatim from the graded pebbling file, sha256
  `aa36f33a…`; it typechecks at `Pous.Pinned.FischClaim13`, so the copy really proves the pinned Claim 13) —
  `b2ToB5` and `b5_stacked` both build on the three standard axioms.

- **`b5_stacked` — the two added hypotheses are sound domain conditions, and the event is the right one.**
  - `hε1 : ε ≤ 1` is used exactly to make `s = ⌊(1−ε)n⌋` satisfy `s ≤ (1−ε)n` (`Nat.floor_le` needs `(1−ε)n ≥ 0`);
    `ε ∈ (0,1]` is the only meaningful range anyway ((1−ε)n black pebbles), so this is not a restriction.
  - `hβ : 1 ≤ β·n` is used so `⌊β·n⌋ ≥ 1`, i.e. `D = ⌊β·n⌋ − 1` does not underflow and `D + 1 = ⌊β·n⌋ ≤ β·n`; a
    depth-robust path of `< 1` node would give no delay, so this too is the minimal non-degenerate condition. Neither
    hypothesis trivializes the statement — the challenge threshold `k = n − ⌈εn/2⌉ + 1 ∈ [1, n]` stays meaningful.
  - **"At least `k` of the `n` last-layer challenges answered" is the right event to convert into an audit bound.**
    Given `H`, the correctly-answered set `S_H = {c ∈ V_t : A₂(A₁H,c) = label c}` is deterministic and the challenge
    set is the fixed `n` last-layer nodes, so a uniform `k'`-challenge audit passes iff all `k'` land in `S_H`, with
    probability `E_H[(|S_H|/n)^{k'}] ≤ Pr_H[|S_H| ≥ k] + ((k−1)/n)^{k'}`. `b5_stacked` bounds the first term
    (tiny, `N·2^m·((n(Q+1)+N)²/2^w)^{⌊(1−ε)n⌋+1}`) and `k = n − ⌈εn/2⌉ + 1` makes the second `≈ (1 − ε/2)^{k'}` —
    exactly the incompressibility/retention shape (as in Theorem 1(ii) / A3′). So it is the correct convertible
    prerequisite; the averaging step itself is not part of this statement (and is not claimed to be). Non-vacuous,
    three standard axioms.

**Verdict (B5 folder): PASS.** Both pinned B5 forms are independently graded PASS; the `B2ToB5` bridge is faithful,
non-vacuous, correctly quantified, and derives `hdag` rather than assuming it; `b5_stacked`'s two added hypotheses are
sound domain conditions and its "≥ k of n answered" event is the right one to feed an audit reduction. Scope is
unchanged and honest: this is the **one-way**-label bound; P3's invertible labels still need the white/green
reduction. No new blocking finding; overall verdict remains **GRANTED WITH CONDITIONS**.

## 7. N10: the invertible-label reduction (`InvertibleExPostFactoDraft.lean`)

Built independently (`import Pous`); sha256 `f8b425f6…`. This is the P3 spec's central open node.

- **The two core lemmas build on the three standard axioms and mean what they claim.** `transpose_mixing` and
  `reverse_needs_all_children` both report `[propext, Classical.choice, Quot.sound]`, no `sorry`; the sanity examples
  (`P⁻¹` inverts `P`; the decode equation `c¹_u v = component u of (P⁻¹(c²_v) ⊕ k²_v)`) elaborate. `transpose_mixing`
  says: for the `K_{n,n}`/transpose connector, if the top labels are known only on a proper subset `S ⊊ univ` then a
  lower label `c¹_u` is undetermined — it exhibits two top configurations agreeing on `S` whose decoded `u`-th lower
  labels differ (in one bit, handling the `k²` XOR by cases). That is exactly "recovering one lower label needs all
  `n` top labels," refuting the store-`n−1`-and-rebuild shortcut. `reverse_needs_all_children` unfolds the *trusted*
  `DRG.Available` reverse rule and shows a decode (reverse) move on a layer-0 node forces a pebble on every layer-1
  node (all its green children under the complete-bipartite `green2`). Both are faithful renderings.

- **The N10 statement is faithful, non-vacuous, correctly quantified, and correctly modeled** — as an *open target*.
  - *Faithful.* `inv_ex_post_facto_two_layer` is B5 (`Pous.Pinned.B5ExPostFactoBounded`) with three substitutions:
    `p3Model` (the ideal model `H` + one permutation `P` with `P⁻¹` queryable), the two-layer invertible labels
    `c¹ = P(W ⊕ H(0,·))`, `c² = P(transpose(c¹) ⊕ H(1,·))` (matching `docs/p3-scheme.md §1` verbatim, salt folded
    into `H`), and `WhiteGreenHard` in place of `PebblingHard`; the bound is B5's at `w = m = n·wc`, `n` challenges,
    `Q_tot = n(Q+1) + 2n`, exponent kept at `s + 1` (an additive per-label loss, per the spec's warning that any
    constant *factor* on `s` breaks 5.26%). This is precisely PIEs (ePrint 2018/684) **Conjecture 1** restricted to
    the `L = 2` operating point — the smallest genuinely open case (layer 1's data is `W`, covered by B5; the open
    content is the one invertible top layer).
  - *Model correct.* `p3Model.answer` routes `.inr (.inr z) ↦ ω.2.symm z`, so the online `A₂ : Prog (p3Model)` really
    can invert `P` (the sanity check confirms `answer (.inr (.inr (P y))) = y`); `P : Equiv.Perm (Lab)` is one ideal
    permutation of whole `m`-bit labels (`Lab = Fin n → Bits wc ≃ Bits m`); `WhiteGreenHard` quantifies over *all*
    legal white/green pebblings `C` (the trusted `DRG.IsPebbling`, reverse rule included) with `black` only (no red
    pebbles — trusted encoder), and its challenge set is the top layer, matching the labeling challenge on `topLabel`.
  - *Non-vacuous.* `WhiteGreenHard` is satisfiable for a real depth-robust `G` (it is Claims 12–14 at `δ = 0`), so the
    implication is not vacuous; the conclusion is a genuine probability bound; edge cases (`n = 0`, `k = 0`) degrade
    to `0 ≤ bound`, not to falsity.
  - *Quantifier order.* Parameters, graph `G` and data `W` are fixed; then the hardness hypothesis; then `∀ (A₁, A₂)`
    with `A₂` `(D,Q)`-bounded — the B5 order, with `W` before `ω` (guide choice 1). Correct.

- **Break attempt: none found, matching the prover's search.** I pushed the two natural inverse-query strategies:
  (i) *store `n−1` top labels and forward-recompute the rest* — this is forward pebbling of layer 1, whose depth is
  `> D` for a depth-robust `G`, so it is exactly what `WhiteGreenHard`/`DepthRobust` forbid (for shallow `G` the
  hypothesis simply fails and N10 is vacuous, not broken); (ii) *invert the stored top labels to reconstruct lower
  labels* — by `transpose_mixing`, reconstructing even one lower label `c¹_u` needs `P⁻¹` on *all* `n` top labels, so
  storing `s < n` and inverting yields only `s` of the `n` components of each lower label, never a full lower label,
  hence no missing top label. Both fail to beat the bound, consistent with the prover's `n ≤ 7` search (0 matched-budget
  witnesses). I did not find an inverse-query adversary that beats the stated bound.

**Verdict (N10).** *Core lemmas:* **pin as is** (proved, three axioms, faithful). *N10 statement:* **pinnable as an
explicitly-conjectural open target** — faithful to PIEs Conjecture 1 (`L = 2`) and to the P3 spec, non-vacuous,
correctly quantified, with `p3Model` (`H`, `P`, `P⁻¹`) and `WhiteGreenHard` modeled correctly; I found no attack.
It must be labelled as the central open conjecture, not a near-term-provable target: pinning is *sound* (a `sorry` or
false proof cannot pass the grader), but no proof is known and, per the analysis and Fisch §4.2/PIEs, none is
expected without a new result. This does not change the overall verdict, which remains **GRANTED WITH CONDITIONS**.

## 8. Dense `Meets` (first unconditional `Meets`) and the sampled-audit lemmas

Both built independently on the fresh copy (`import Pous` + Mathlib; `TRUSTED.sha256` verifies). **`DenseMeets.lean`:**
`dense_meets` on `[propext, Classical.choice, Quot.sound]`, and `leanchecker` (kernel replay) exits 0; its scheme
definitions and theorem signature are **byte-identical** to `DenseMeetsDraft.lean` (independent `diff`). **`SampledAudit.lean`:**
all five theorems on the three standard axioms, `leanchecker` exits 0.

**`DenseMeets` — I tried hard to show it is hollow; it is not.** `Meets (denseScheme (2^16) 8192) .sequential 64
(2^20) 107 (2⁻¹^128)`, the first end-to-end `Meets` with **no named assumption** (contrast `M1Meets`, which carries B1′).
- *Real scheme, no definitional gap.* `denseScheme` has `t = 0` (no free `pp` to park `W` in — the F2 junk gap is
  impossible), `C_i = H(i, C_{<i}) ⊕ W_i` over the complete DAG, and `dec` genuinely reads the whole codeword
  (`W_i = C_i ⊕ H(i, C_{<i})`, one label-shaped query per block). `Correct` holds for all `W`; `CodeHoldsW` and
  `SpaceBound` hold with `|C| = |W|` (rate 1). Security is the real content: the complete DAG is `PebblingHard`
  at `(B−D−1, D, B)` (from `s` pebbles greedy reach is `s+D < B` in `D` rounds), which the *proved* B5 turns into
  `TimedINC` and the *proved* `Theorem1iiSeq` turns into `AuditSecure`. Not the junk/identity/`pp`-parking shape.
- *Label-shaped random oracle.* The oracle answers only label-shaped queries `(i, partial label assignment)`, but the
  responder `Prog` has full access to *all* such points; a real hash's other inputs are label-independent, so
  restricting to label-shaped queries does not inflate security — it is w.l.o.g. within the ideal model (the same B5
  idealization, and the problem statement's "attacks through the primitive" scope). It is a genuine idealization
  (a standing framework caveat, choice #3), not a `DenseMeets`-specific gap.
- *`W` fixed before `H`.* Matches the trusted layer's choice 1; `AuditSecure` quantifies `∀ W` (worst case), and the
  proof uses B5's data-fixed-before-oracle variant soundly (dropping the commitment term). The deployment caveat (a
  real scheme needs a salt drawn after `W`) is flagged in the NOTES — a standing limitation, not an exploit.
- *Sequential-reveal semantics.* `.sequential`: per-answer `(D,Q) = (64, 2^20)`, `S`-bit state carried across the
  `k = 107` rounds — the demanding mode (F5), routed through `Theorem1iiSeq`. Correct; it does not fall back to the
  weaker simultaneous budget.
- *Certificate arithmetic — verified exactly.* `|C| = 2^29`, `S = ⌊(18/19)·2^29⌋ = 508,614,548`, `β = 531,499,840`,
  `β − S − B = 22,819,756`, `p₀ = 1 − 22,819,756/2^29 = 0.9574949`; `p₀^107 = 0.009585 ≤ 1%` while
  `p₀^106 = 0.010011 > 1%` (so `k = 107` is tight). Union term: `(B(Q+2))^2 ≤ 2^74` so `(B(Q+2))^2/2^ℓ ≤ 2^-8118`,
  and `|Hist|·π ≤ 2^{1712 + 16 + 531,499,840 − 8118·65,472} = 2^{-128}` exactly (`1712+16+531499840 = 531,501,568`,
  `8118·65472 = 531,501,696`, difference `−128`). So `Pr[pass] ≤ p₀^107 + |Hist|·π ≤ 1% + 2^-128 = δ + ε`.

  *Verdict (`DenseMeets`):* **pin as is** — a sound, non-hollow, genuine first `Meets` with no named assumption
  (proved, kernel-replayed, statement byte-identical to the reviewed draft, arithmetic exact). The honest scope, which
  should travel with it: it certifies the timed audit game's **security + correctness + rate only, not decode cost**
  (decode hashes every earlier block, `Θ(B)` per byte — deliberately not the 2× cost target), and it carries the
  framework's standing ideal-model caveats (label-shaped RO; `W` before `H`). None of these make it hollow.

**Sampled-audit lemmas (`SampledAudit.lean`).** These supply exactly the "threshold ⇒ audit bound" averaging step
that `b5_stacked` (§6) left for a later reduction, and they are proved.
- `sampled_audit_prod` / `sampled_audit_seq` / `sampled_audit_sim` — **pin as is.** General and correct: from "except
  with probability `p` over setup, fewer than `k` blocks are answerable" they conclude `Pr[pass] ≤ ((k−1)/B)^t + (p or
  |Hist|·p)` (product / sequential-per-history / general-simultaneous with the `η` slack), via `pr_prod_le` +
  `card_pi_mem` / the history union / `pr_joint_le`. Non-vacuous, correct quantifier order; reusable across schemes.
- `stacked_audit_seq` — **pin as is.** Chains `b5_stacked` through the sequential reduction to bound the stacked
  one-way graph's `t`-round audit; correct, conditional on the DRG/superconcentrator hypotheses (inherent).
- `stacked_audit_one_percent` — **pin as is, but conditional.** Proved: at `n = 2^16`, `w = 8192`, `N = 2^17`,
  `Q = 2^20`, `S = ⌊(18/19)·n·w⌋ = 508,614,548`, `ε = 1/23`, a `t = 210`-round sequential audit of the stacked
  one-way graph passes with probability `≤ 1% + 2^-128`. Arithmetic checks (`⌈εn/2⌉ = 1425`, `⌊(1−ε)n⌋ = 62,686`,
  `(64111/65536)^210 ≤ 1/100`, union exponent `8118·62,687 − (16·210 + 17 + 508,614,548) = 275,141 ≥ 128`). The
  caveat: it is *conditional* on the existence of a suitable depth-robust stacked graph (`hdr`, `hsc` — item N4, still
  unproven), and it is only the audit-security clause of the stacked (S2) scheme, not a full `Meets`. So it is an
  honest conditional building block, not an unconditional result; the `ε = 1/23` is the stacked-graph pebbling deficit
  (state below one layer), distinct from `ρ`'s `1/19`, and `S` is `ρ` of the last layer — both consistent.

**Verdict (§8): PASS.** `DenseMeets` is the genuine first unconditional `Meets` — sound, non-hollow, arithmetic exact,
byte-identical to its draft — with the honest "security-not-cost" scope. The five sampled-audit statements are proved
and correct; `stacked_audit_one_percent` is sound but conditional on a concrete DRG. No new blocking finding; the
overall verdict remains **GRANTED WITH CONDITIONS**, now with the first assumption-free `Meets` in hand.

## 9. N10 is FALSE — the pinned `InvExPostFactoTwoLayer` and the assumption `InvertibleLabels` must be withdrawn

A cryptanalyst (`docs/p3-cryptanalysis.md`) and a second prover both found that N10 is false, and the prover
machine-checked it (`lean/submissions/p3-forward/Refutation.lean`). **I independently confirmed the refutation, and
it is decisive.** My earlier "no attack found" (§7) missed this: `transpose_mixing` blocks recovering a *lower* label
from a subset of top labels, but the attack runs the *other* direction — a *top* label `c²_v` reads only **column
`v`** of the lower layer (one `wc`-bit component of each lower label), which whole-label `WhiteGreenHard` cannot charge.

- **Independent build + replay.** On the fresh store copy (`TRUSTED.sha256` verifies), `Refutation.lean` compiles;
  `not_invExPostFactoTwoLayer` and `not_invertibleLabels` depend only on `[propext, Classical.choice, Quot.sound]`;
  `leanchecker` passes and **`leanchecker --fresh`** (replay from an empty environment, rechecking Mathlib + Pous +
  Refutation, 3m39s) exits 0.
- **It negates exactly the pinned constants, not a copy.** A separate checker importing the trusted `Pous` afresh
  accepts `example : ¬ Pous.Pinned.InvExPostFactoTwoLayer := PousP3Forward.not_invExPostFactoTwoLayer` and the same
  for `InvertibleLabels`, and `Pous.Assumptions.InvertibleLabels = Pous.Pinned.InvExPostFactoTwoLayer` holds by `rfl`.
  The witness uses the trusted `WhiteGreenHard`, `p3Model`, `topLabel` (via `open Pous.Invertible`); the file defines
  nothing in a `Pous.*` namespace.
- **The witness (kernel-checked).** An 8-node chain `chain8`, `n=8, wc=64, m=512, s=1, D=3, Q=4, k=2`, `W=0`:
  `hard : WhiteGreenHard chain8 1 3 2` is *proved* (so the hypotheses are genuinely met — not vacuous), a forward-only
  adversary making **no `P⁻¹` query** answers both challenges with probability `≥ 2^-448` (`pr_attack`, by guessing 7
  components = 448 bits), while the statement's own bound is `8·2^512·(56²/2^512)^2 = 78,675,968·2^-512 ≈ 2^-485.8`
  (`bound_lt`). I re-checked the arithmetic: `2^-448 > 2^-485.8`, so `pr(pass) ≤ bound` is false. Hence the pinned
  statement, applied to a witness satisfying all its hypotheses, yields a false conclusion.
- **Root cause.** The bound charges `(s+1)` **whole** labels (`(s+1)·(n·wc)` bits) of incompressibility, but a top
  label needs only column `v` — `wc` bits per lower label. Whole-label pebbling `s` does not lower-bound the bit-cost
  of a column/guessing adversary. This is exactly the PIEs Conjecture-1 gap, now with a concrete counterexample.
- **Corroborating (lower priority): the 40%-source counterexample.** I reproduced the cryptanalyst's scripts:
  `toy_labels.py` gives a *deterministic* attack answering **every** block from `0.840` of `C` in 3 rounds with no
  `P⁻¹` (`CX … ok=True`), and `graph_savings.py` gives a `17.87%` saving on the 88-source + complete-core graph,
  which **breaks 18/19 outright**. On paper `WhiteGreenHard G 219 3 220` holds for it (re-pebbling a top node needs
  ≥261 whole-label pebbles > 219). This is the stronger (probability-1) attack; the machine-checked `chain8` guessing
  refutation is the rigorous proof and needs no DR certificate.

**Verdict (N10): the pinned target `Pous.Pinned.InvExPostFactoTwoLayer` and the named assumption
`Pous.Assumptions.InvertibleLabels` are FALSE and must be WITHDRAWN.** Remove them from `Pinned.lean`, `Registry.lean`
and `PousTargets.lean`; any conditional result taking `InvertibleLabels` as a hypothesis is vacuous and must not be
read as a P3 security claim. Kernel/grader soundness is unaffected (a false pinned target simply cannot be proven, and
the grader rejects any `sorry`/false proof) — this is a *mathematical* refutation of the conjecture, not a grader
break. My §7 verdict ("pinnable as an open target") is **retracted**: it is not merely open, it is refuted.

**Column-aware restatement (`p3-forward/NOTES.md`) — requirements are sound; I agree.** A valid N10 replacement must
be a *column-granular* game: holdings of whole lower labels (cost 1), single components `(w, u)` (cost `1/n`), and
whole top labels (cost 1); a forward top-move needing, per lower `w`, either `w` whole or `(w,u)` held; an inverse
move yielding a whole column; guessing a component at `2^-wc`. Two points are load-bearing and correct: (i) **position
encoding must name each revealing query once (`≈ log₂ Q_tot` bits) plus an `n`-bit mask, not `Q_tot²` per component** —
at the operating point `Q_tot² ≈ 2^41.6 > 2^wc ≈ 2^37`, so a per-component `Q_tot²` charge is vacuous; (ii) the theorem
must **subtract a certified *upper* bound on the column saving `X(G,D)`** over *mixed* strategies — a genuinely new,
hard per-graph certificate (the cryptanalyst's greedy numbers are only lower bounds), whose feasibility is unassessed.
A graph condition layered on whole-label `WhiteGreenHard` does not rescue the proof.

**Cryptanalysis result 1 and the `KQ` side finding — both confirmed.**
- *P3.1 (digest variant) is broken.* `toy_labels.py`: storing only the two layers' `λ_d`-bit digests keeps `0.250`
  of `C` and answers every block in 3 rounds (`ok=True`), i.e. a **75% saving** at `λ_d = 1024`. Fix per the memo:
  `λ_d ≥ m/L` (≥ 4096 at `L=2`) or key on full labels — after which the concrete-`P` cost (§6) still misses 2×.
- *The trusted `KQ` lacks a salt/segment index.* `Pous.Invertible.KQ = Fin 2 × Fin n × (Fin n → Option (Lab))` —
  layer, node, parents only. With one `ω` reused across segments, equal-`W` segments get identical `C`
  (`identical=True`). Add `(salt, segment)` to `KQ` before any multi-segment (`N`-segment average) claim; the
  single-segment refutation above does not depend on this.

**Effect on the overall verdict.** The trusted *framework* (kernel, grader, the proved lemmas, and the assumption-free
`DenseMeets` of §8) stands. But a **pinned target and a named assumption are mathematically false**; until they are
withdrawn and (optionally) replaced by the column-aware game, the overall verdict is **GRANTED WITH CONDITIONS, plus a
required correction: withdraw `InvExPostFactoTwoLayer` and `InvertibleLabels`.**

## 10. N10′ — the column-aware restatement (`ColumnAwareDraft.lean`): I tried to refute it; it survives

Built independently (`import Pous` + `Pebbling.Encoding`): the helper lemmas `perLine_ratio_lt_one`,
`perComponent_ratio_ge_one`, `invWork'_le_of_bounded` are proved on the three standard axioms; `n10prime`,
`basePath_columnHard`, `cex_not_columnHard` are the `sorry` targets. I attacked `n10prime` the way `chain8` refuted
N10, and **could not refute it** — the redesign closes the gap that killed N10.

**Why the chain8 attack no longer works.** N10 died because whole-label `WhiteGreenHard` with `s=1` gave the bound
exponent `s+1=2`, charging only 2 labels while a guess of 7 components (448 bits) beat `2^-485.8`. N10′ recurrencies
the currency: `ColumnHard G D k X` bounds *column* holdings (`ColState`: whole lower = `n` units, a component = `1`,
whole top = `n`), so any holding reaching `k` tops in `D` forward rounds has `size ≥ (k−X)·n` **column** units, and the
bound's exponent is `(k−X)` **lines**, matching the `(k−X)·n` components actually needed. A guessing adversary is then
priced: on its success event, `state ∪ guesses` is a column holding reaching `k` tops, so `ColumnHard` forces
`m/wc + g ≥ (k−X)·n`, hence `success ≤ 2^{m−(k−X)·n·wc}`, whereas the bound is `N·2^m·Q_tot^{k−X}·2^{−(k−X)·n·wc}` — a
factor `N·Q_tot^{k−X} > 1` looser. So `success/bound = 1/(N·Q_tot^{k−X}) < 1`: no guessing refutation (I checked the
`chain8` numbers: exponent `k−X=7`, `56` columns/`3584` bits needed, guessing bounded). Either `ColumnHard chain8 3 8 1`
holds and guessing is priced, or it fails and `n10prime` simply does not apply — either way `chain8` cannot refute it.

**The specific checks.**
- *Prices every strategy the game can see.* `ColState` carries mixed whole-label and per-component holdings, so
  partial columns and whole/column mixes are counted; a top move needs, per lower `w`, either `w` whole or `(w,u)`
  held, and its top parents whole — exactly "read column `u`". Guessing is priced via the effective-holding argument
  above; inverse queries are charged `q_inv` whole lines (`Q_tot^{q_inv}`, one line per `P⁻¹`), and one `P⁻¹(c²_u)`
  reveals only column `u` (useful for top `u` alone), so `q_inv` inverses answer `q_inv` tops — the bound goes
  correctly *vacuous* (`>1`) once `q_inv` approaches `k−X` (`hXk : X+q_inv ≤ k`). H's structure is out of scope: in
  the ideal salted RO there is none (a real-hash attack is the documented standard-model concern, §6 of the
  cryptanalysis).
- *No adversary benefits from knowing `W`.* The game's lower move needs only lower parents (W is free, as in the real
  encoder), and `W` is a parameter fixed before `ω`; the worst case is already granted, and the salt (below) stops `W`
  from shaping `H`.
- *Per-line charge is sound.* Every `P`/`P⁻¹` query reveals a whole `n·wc`-bit line, named once by its `Q_tot`
  position — so the charge is `Q_tot/2^{n·wc}` per fresh line, provably `<1` (`perLine_ratio_lt_one`), not the vacuous
  per-component `Q_tot²/2^{wc} ≥ 1` (`perComponent_ratio_ge_one`, since `Q_tot² ≈ 2^{41.6} > 2^{wc} ≈ 2^{37}`). The
  `Encoding.lean` interface (`pr_le_of_decode_charge`, `charge_cancels`) is proved and correct.
- *Hypotheses are not vacuous.* `ColumnHard` is a real condition (false for shallow graphs — a small holding reaches
  everything; satisfiable for the complete DAG and, conjecturally, base paths). The meaningful regime is `X < k`
  (`X ≥ k` makes the bound `>1`, trivial). Quantifier order is the B5 order (params, `tag`, `G`, `W`, then
  `ColumnHard`, then `∀ (A₁, A₂)`), correct. `hXk : X + q_inv ≤ k` keeps the exponent `k−X−q_inv ≥ 0`.
- *Salted `KQ'`/`p3Model'`.* `KQ' = Bits 256 × Fin 2 × Fin n × parents` adds the `(salt, segment)` tag, and
  `topLabel'`/`c1'`/`c2'` thread it, so equal-`W` segments no longer dedupe (attack 3 fixed). Correct and non-vacuous.

**Verdict (N10′): NOT refuted — it survives the `chain8`-style attack, and is a sound redesign** that prices the
column and guessing attacks the pinned N10 missed. Two load-bearing caveats keep it an *open* target, not a
near-provable one, and I'd pin it (if at all) only as an explicitly-conjectural column-aware statement:
1. **The core proof is the open conjecture.** `n10prime`'s truth rests on an incompressibility reduction — that any
   `m`-bit `A₁` state answering `k` tops reduces to a `ColState` of size `≈ m/wc` (the `ColState` abstraction being
   w.l.o.g.). That is PIEs Conjecture 1 in column form, still unproven; the draft supplies the charge interface but
   not this core.
2. **Usefulness hinges on `basePath_columnHard`, an unassessed and hard certificate.** `ColumnHard` with small `X` for
   the operating-point graph needs a certified **upper** bound on the column saving `X(G,D)` over **all mixed
   strategies**. The cryptanalysis figures (`X ≈ 2.2` at `D=20`) are greedy **lower** bounds; an upper bound is a new,
   harder certificate whose feasibility is unknown. If base paths in fact save more via a mixed strategy the greedy
   search missed, `ColumnHard(small X)` is unsatisfiable and `n10prime`, though true, is uninstantiable (an
   F4-style dead end). `cex_not_columnHard` (excluding the 40%-source graph) is likewise still a `sorry` target.

So N10′ is the right shape and defeats the known attacks, but it converts one open conjecture (labelling↔pebbling for
invertible labels) into two (the column-incompressibility core, plus a mixed-strategy `X(G,D)` upper-bound
certificate). It should replace the withdrawn N10 as the open target; it is **not** yet a proved or clearly-provable
result. Overall verdict unchanged: **GRANTED WITH CONDITIONS** (withdraw N10/`InvertibleLabels`; N10′ is the corrected
open target).

## 11. Fixed N10′, the `p3-column` certificate, and the recording-vs-circularity reduction (27 Sep 2026)

Rebuilt independently (`~/n10pbuild`, same toolchain; `Pous`/`Encoding` from the store copy, `TRUSTED.sha256` verifies
before and after). Three verdicts.

### (A) Fixed N10′ draft (`ColumnAwareDraft.lean`, sha `0cec2bb6`) — faithful; both counterexamples still handled.

It builds; the only `sorry` is `n10prime` (line 189). `cex_not_columnHard` is **now fully proved** (no `sorry`, three
axioms), as are `posSaving_ratio_lt_one`, `perComponent_ratio_ge_one`, `invWork'_le_of_bounded`. The four fixes are
faithful and each closes a gap §10 flagged:

1. **Game rounds `(D+1)/2`.** `n10prime` takes `ColumnHard G ((D+1)/2) k X`; two oracle rounds per label level plus the
   final top query give `d = (D+1)/2` (`D=20 ⇒ d=10`). Correct — the earlier round-count conflation is gone.
2. **Total online inverse budget.** `hInv : ∀ σ ω, (∑ c, invWork' … (A₂ σ c)) ≤ q_inv` charges the sum over the `k`
   challenge programs, not one program. A total budget is the right thing to price; faithful.
3. **Lower-label promotion.** `colRoundF` now promotes `w` to whole once *all its columns are held*
   (`… ∨ ∀ u, (w, u) ∈ c.lowerCol`), closing the meet-in-the-middle hole. This makes `colReach` reach more, so
   `ColumnHard` becomes a claim about **more** holdings — a genuine strengthening, the right direction. (It is also
   what breaks the `p3-column` certificate — see (B).)
4. **Named-position charge.** `N10primeBound = N·2^m·(Q_tot·2^n)^{pos} / 2^{((k−X)−q_inv)·(n·wc)}`, `pos ≤ 3n`, an
   `n`-bit freshness mask per position; `posSaving_ratio_lt_one` proves the ratio `< 1` when the position cost is below
   the net saving. This corrects the old per-line undercount. The false `hDR : True` `basePath_columnHard` is removed.

**Both counterexamples remain handled.** The column-hole graph is excluded *by machine-checked proof*:
`cex_not_columnHard` exhibits a `q_inv=0` holding of size `n²−src²` columns recovering all `n` tops in 3 rounds, so it
saves `src²/n > X` and its `ColumnHard` hypothesis is false — N10′ does not apply to it. The guessing chain is priced
by the column currency exactly as in §10 (`ColumnHard` forces `size ≥ (k−X)·n`, the bound is a factor `N·Q_tot^{k−X}`
looser). Vacuity and quantifier order are as §10; the salted `KQ'`/`p3Model'` still fixes attack 3. **Verdict: the
fixed draft is faithful and closes the flagged gaps; I found no refutation of `n10prime`.** It remains an open target
(`n10prime` is the sole `sorry`; its truth is the column-form PIEs Conjecture 1).

### (B) `p3-column` certificate — FINDING: it does not build against the fixed draft; the promotion voids it. *(Resolved in §12 — the prover has since adapted it; kept here for the record.)*

`ColumnSaving.lean` (`columnHard_of_bounds`, `basePath_columnHard'`, `lowerReach_basePath_empty`) was built against
`ColumnAwareDraft.lean` sha `e04d37f7` (its own `AXIOMS.txt`), **not** the pinned-for-review `0cec2bb6`. `NOTES.md`
claims "`ColState`, `colRoundF`, `colReach` and `ColumnHard` are unchanged since the restatement" — this is **false**:
fix (3) above changed `colRoundF`. Rebuilding the certificate against the current draft:

- The **types match**: `ColumnSavingDraft.lean` (the three signatures) elaborates against `0cec2bb6` with only `sorry`
  warnings, producing `ColumnHard G d n X` — the `k := n` case of `n10prime`'s `ColumnHard G ((D+1)/2) k X`.
- The **proofs fail**: `PebblingCol/ColumnSaving.lean:42:14: error: unsolved goals` at `colReach_lowerWhole`, and
  `:227:20: error: Function expected at hv` in `lowerReach_basePath_empty_sub`. So none of the three targets compiles
  against the fixed game.

Root cause is not a build-path artefact but the promotion. `colReach_lowerWhole` ("the lower layer evolves on its
own") assumes `lowerWhole` depends only on the previous `lowerWhole`; the promotion couples it to `lowerCol`, so the
lemma is now **mathematically false**. Kernel-checked disproof (`~/n10pbuild/Disprove.lean`, `by decide`, three
axioms): on the 2-node spine with `c0 = ⟨∅, {(1,0),(1,1)}, ∅⟩`, one round has `1 ∈ (colReach G c0 1).lowerWhole`
(promoted from its held columns) but `1 ∉ (colReach G ⟨∅,∅,∅⟩ 1).lowerWhole`. Since `columnHard_of_bounds` and
`basePath_columnHard'` both rest on `colReach_lowerWhole`, they are **void for the fixed game** and are not
tactic-repairable: the promoted game reaches strictly more, so `ColumnHard` on it is a genuinely stronger claim than
the certificate's counting establishes. (`lowerReach_basePath_empty` is still a *true* statement — its `lowerReach`
starts from empty columns, which the promotion cannot touch — but its delivered proof also fails and would need
rewriting.) **The two fixes are in direct tension:** the promotion that closes the refutation's MITM gap is exactly
what invalidates the column-saving certificate meant to make the game usable. This must go back to the author/provers;
the certificate has to be redone against the promoted `colRoundF`.

**The rebuild hypothesis `hreb` — a reasonable per-graph condition, not a smuggled conclusion, but the load-bearing
unproven core, and moot under promotion.** `hreb : ∀ L0, |lowerReach (basePath …) L0 (d−1)| ≤ 2·|L0| + (d−1)` bounds
the *forward reach* of the lower-whole layer from whole-label seeds (a `par`-based reachability growth bound). It is
**not** the conclusion in disguise: `ColumnHard` bounds the size of *any* holding — columns and tops included — that
reaches `k` tops, and `columnHard_of_bounds` does the real bridging work (the `firstTop` argument turning each dropped
top's needed columns into `|C0| ≥ (n−|L|)·|U|`, the depth-robustness bound on `|U|`, the `nlinarith` count). So `hreb`
is an honest hypothesis. But it is the hard, unverified part: only the `L0=∅` case is proved
(`lowerReach_basePath_empty`); the general-`L0` `2|L0|+(d−1)` growth is proved for *no* family in Lean — only
brute-forced for band graphs `B(n,k)` at `n ≤ 16` and sketched combinatorially (`NOTES.md §4`, needing `k ≥ d−1`), and
random/sampled DR graphs already **fail** the companion `hDR` at the operating point (`d=10` low-depth sets `> n/2`).
And under the promotion `hreb` (stated via `lowerReach` from *empty* columns) no longer controls the promoted game's
reach at all, so even a true `hreb` would not bound `colReach` from a column-bearing `c0`. **Verdict: `hreb` is a
sound, non-circular per-graph condition, but it is the unproven crux *and* it is the wrong quantity for the fixed
game.** Net: the `p3-column` deliverable is stale — its targets do not build against `0cec2bb6`, and the reduction it
encodes must be re-derived for the promoted game before any `X(G,D)` certificate can feed `n10prime`.

### (C) Recording vs circularity (`NOTES.md`) — the reduction HOLDS; but the timed route does not yet follow from it.

Claim: recording every online `P⁻¹` answer breaks the circular extraction order, so bounded-`q_inv` `n10prime` reduces
to forward-only `n10prime_forward` when `q_inv < k − X`. I pushed all five break vectors; **none breaks the reduction.**

- **(a) inverse inputs depending on earlier inverse answers.** Reproducible. Every online inverse answer is recorded,
  the adversary is deterministic on the fixed `ω`, and each inverse query's input is a deterministic function of the
  `m`-bit state plus prior answers — recorded (inverse) or re-derived from the fresh-line stream (forward). No input is
  ever both un-recorded and un-derivable, so nothing is unreproducible.
- **(b) `P⁻¹` on a value that is never a real top label.** The answer is junk (a random pre-image), but it is recorded
  and charged like any line and kept consistent in the decoder's partial-permutation graph; it cannot help the
  adversary (challenges need real tops) and cannot invalidate the encoding (recording only lengthens it).
- **(c) adaptive order divergence.** Fixed `ω` + deterministic adversary + correct supplied answers ⇒ the replay is the
  *same* execution in the *same* order. The one real requirement is that the decoder merge recorded inverse pairs into
  its forward memo (a later `P(x)` on a recorded pre-image `x` must return the recorded `y`, with no second "fresh"
  charge); standard bookkeeping, not a divergence.
- **(d) offline preprocessor queries.** They stay free — **true**. The encoder replays only the online `A₂` and the
  honest labeler, never the unbounded `A₁`, whose entire effect is its `m`-bit output (charged once in `2^m`). This is
  sound precisely because `W` is fixed before `ω` (no §8 replay-`A₁` extraction step); the notes correctly flag that an
  adaptive-data variant would reintroduce the charge.
- **(e) the `n·wc`-bit recording cost.** Covered arithmetically: the exponent `((k−X)−q_inv)·(n·wc)` subtracts exactly
  `q_inv` lines of `n·wc` bits — the `charge_cancels` identity at `b = n·wc`, `e = q_inv`, `f = k−X`.

The candidate cycle genuinely cannot form: inverting `c²_j` yields **only** column `j`, while forward-computing `c²_i`
needs column `i`, so no inverse answer is ever needed to *form* an earlier inverse query's input. **So the reduction is
sound: bounded-`q_inv` `n10prime` does reduce to `n10prime_forward` given `q_inv < k − X`.** (This is a paper argument,
not machine-checked — `n10prime_forward` is a `sorry` target in the sibling `p3-forward`.)

**Two caveats keep the timed route open despite the sound reduction.** (i) `n10prime_forward` is itself unproven — the
residual ideal-cipher/PIEs-Conjecture-1 forward incompressibility; the reduction *shifts* the difficulty there, it does
not remove it (the prover says as much). (ii) **The enabling hypothesis `q_inv < k − X` is not discharged at the
operating point.** In `n10prime`, `q_inv` bounds the **total** online inverse queries (`invWork'` sums every
`.inr (.inr _)` across the `k` programs), and `N10primeBound` charges one full `n·wc`-bit line per such query. The
timing link gives only total `≤ k·Q ≈ 2^20`, whereas `k − X ≈ n ≈ 220`: a *single* `(D,Q)`-bounded answer that spends
its `Q ≈ 2^13` budget on inverse queries already exceeds `k − X`. So for a general `(D,Q)`-bounded adversary
`N10primeBound` is **vacuous** at the operating point — "timing gives `q_inv ≤ k·Q`" (`NOTES.md`) does *not* imply
`q_inv < k − X` in the column model. (The notes' separate feasibility line — "`≤ log₂Q ≈ 13` bits/label, negligible" —
uses a cheaper per-query charge that `N10primeBound` does **not** implement, and even that is negligible only if the
charged inverse queries number `≈ n` distinct lines, not `k·Q`.) Closing the timed route therefore needs the charge on
**distinct** revealed lines (`≤ n`), plus a `ColumnHard`-style argument that distinct recorded lines stay below
`k − X` — or a proven cheaper per-query charge. Neither is in the current statement or bound.

**Verdict (recording vs circularity): the reduction holds — no break vector succeeds, offline queries are free, and the
recording cost is exactly the `q_inv` term. But it is a *conditional* reduction: the timed route it is meant to enable
is not yet established, because `n10prime_forward` is open and, more sharply, the premise `q_inv < k − X` is not met by
the `(D,Q)` timing bound in the column model. `invWork'`/`hInv` should charge distinct revealed lines (bounded by `n`),
not every inverse query, before "the timed route rests on this" can hold.**

**Overall verdict unchanged: GRANTED WITH CONDITIONS** (withdraw N10/`InvertibleLabels`; N10′ is the corrected open
target). New for this pass: the fixed N10′ draft is faithful and both counterexamples are handled (`cex_not_columnHard`
now proved), **but** the `p3-column` certificate is stale — it does not build against the promoted game and must be
redone — and the recording-vs-circularity reduction, though sound, does not yet close the timed route (`q_inv < k − X`
undischarged; `n10prime_forward` open).

## 12. `p3-column` rebuilt against the promoted game, plus the band-graph certificate (27 Sep 2026) *(superseded by §14 — that promotion-only certificate was removed when the game became two-directional)*

The prover adapted `ColumnSaving.lean` to the promotion and added `BandCertificate.lean` + `CheckBandCertificate.lean`.
I rebuilt the whole folder independently against the current `ColumnAwareDraft.lean` (sha `0cec2bb6`), `Encoding.lean`
and the trusted `Pous` (`~/colbuild3`, same toolchain; store `TRUSTED.sha256` verifies before and after). **This
resolves the §11(B) finding: the certificate now builds against the fixed (promoted) game, and the adaptation is a
sound strengthening, not a workaround.**

**1. Builds, standard axioms, `--fresh` replay — all confirmed.** `Encoding`, `ColumnAwareDraft`, `ColumnSaving` and
`BandCertificate` compile with 0 errors and 0 warnings (only the draft's own `n10prime` `sorry` remains). All 15
targets — `columnHard_of_bounds`, `basePath_columnHard'`, `lowerReach_basePath_empty`, `colReach_lowerWhole_subset`,
`band_long_path`, `band_depthRobust`, `band_rebuild`, `band_columnHard`, `columnHard_of_rounds`,
`band_columnHard_refined`, and the five numeric instances — report `[propext, Classical.choice, Quot.sound]` only (no
`sorryAx`, no `native_decide`; the `by decide`/`norm_num` side-conditions compile to kernel proofs). `leanchecker`
exits 0, and `leanchecker --fresh PebblingCol.BandCertificate` (replay of Mathlib + Pous + the module from an empty
environment) exits 0 in 3m28s. `AXIOMS.txt`'s hashes match the store files, and it now records `0cec2bb6` as the draft
built against (the earlier `e04d37f7`).

**2. `CheckBandCertificate.lean` genuinely restates with the draft's own definitions.** Every check is written with
`PousColumnAware.ColumnHard`, `basePath`, `colReach` and the trusted `Pous.DRG.DepthRobust`, with the band graph spelled
out inline (`bandG n k := basePath n (fun v => univ.filter fun u => u.val+1 < v.val ∧ v.val ≤ u.val+k) …`), and closed
by the corresponding `BandCertificate` theorem — e.g. `check_refined_220_12 : ColumnHard (bandG 220 12) 10 220 3 :=
band_columnHard_refined_220_12`. These typecheck only because `bandG` is definitionally the draft's `basePath` instance
(`bandGraph`) and `ColumnHard`/`colReach`/`DepthRobust` are the draft's/trusted symbols; all seven checks build on the
three axioms and replay `--fresh`. So the certificate is stated in the draft's vocabulary, not an isolated copy.
`CheckColumnSaving.lean` still discharges the three *accepted* statements (`ColumnSavingDraft.lean`, unchanged sha
`60d8507b`) verbatim by `type_of%` — so **no accepted statement changed**.

**3. The promotion adaptation is sound — a strengthening, not a weakening.** The proof, not any statement, was changed.
The old (now false) equality `colReach_lowerWhole` is replaced by the true **subset** `colReach_lowerWhole_subset`: the
game's lower-whole set after `r` rounds is contained in the *column-free* forward rebuild from
`c0.lowerWhole ∪ promoted c0`, where `promoted c0` is the labels all of whose columns are held. This is exactly the
direction the counting needs (`w ∉ L ⇒ w not whole in the game ⇒ the dropped top must hold column `(w, u)`), so nothing
is lost. In `columnHard_of_bounds`/`columnHard_of_rounds` the promoted labels are (i) added to the rebuild base and
(ii) charged `n` columns each, from a family of columns provably disjoint (`hdisjC`) from the dropped-tops' columns — so
a promoted label costs `n` (its full `lowerCol` row), the same `n` it would cost held whole. The counting closes with
the same `X`; I checked the algebra (`n·n ≤ n·|L0|+|C|+n·|T0|+X·n` via the promoted term) and it balances. Decisively,
the promotion makes `colReach` reach **more**, so more `c0` satisfy `ColumnHard`'s antecedent, so `ColumnHard` on the
promoted game is a **strictly stronger** claim than on the old game — and it is the *same* `Prop` the draft feeds
`n10prime`. Proving the stronger claim with the same `X` is a real strengthening; there is no vacuity and no weakened
signature. The prover's summary ("a promoted label costs `n` columns, the same as holding it whole; no statement
changed") is accurate.

**The band certificate itself is a genuine, concrete `ColumnHard` witness.** `bandGraph n k` (each node's `k`
predecessors as parents) is proved `(1/2, k/(n+2k))`-depth-robust (`band_depthRobust`, via a starts/windows long-path
count) and to satisfy the rebuild bound for `d − 1 ≤ k` (`band_rebuild`), and these feed `basePath_columnHard'` to give
`ColumnHard (bandGraph n k) d n (d/2)`. A refined per-round reduction (`columnHard_of_rounds` + `band_rank_sum`)
tightens the saving to `X = 3` at `B(220,12), d=10` and `d=11` and at `B(220,16), d=12` — a **better** bound than the
basic `X = 5/6`, `k` kept a parameter so a different point only re-runs `norm_num`/`decide` side-conditions. Two honest
caveats, both design-side not soundness: the band graph's robustness is thin (`βn ≈ k`), so any P3 hypothesis wanting
more than `d < k·n/(n+2k)` depth robustness (e.g. `DepthRobust(½,0.1)` needs `k ≥ 28`) forces a larger in-degree; and
this certifies `X(G,d)` for the *band* family only — the sampled DRG at the operating point still fails `hDR` (§11),
so the graph P3 actually deploys must itself be a certified band-type family.

**Verdict (§12): the `p3-column` folder builds against the fixed draft, uses only the standard axioms, and replays
`--fresh`; `CheckBandCertificate` restates it in the draft's own definitions; and the promotion adaptation is sound — a
strengthening with unchanged statements, not a workaround.** §11(B) is resolved: the certificate is no longer stale.
The two open items from §11 that this does *not* touch remain: `n10prime` itself (the column-incompressibility core) is
still a `sorry`, and the recording-vs-circularity route still needs `q_inv < k − X` discharged (§11(C)). With a
certified `X`, `basePath_columnHard'`/`band_columnHard` now supply the graph hypothesis `n10prime` consumes at
`X ∈ {3,5,6}` — the remaining gap is the core reduction, not the certificate. Overall verdict unchanged: **GRANTED WITH
CONDITIONS** (withdraw N10/`InvertibleLabels`; N10′ is the corrected open target, now with a machine-checked `X(G,d)`
certificate for the band family).

## 13. N10′ redesigned to in-game inverse (option (b), key-gated); the core is now `n10prime_core` (27 Sep 2026)

The N10′ draft changed again (`ColumnAwareDraft.lean` sha `c386ed62`, `ForwardCoreDraft.lean` `57a80cb1`,
`internal/n10-invertible-label-analysis.md` §"Inverse-move decision"). Inverse queries are no longer a bound-level
`q_inv` charge; they are a **key-gated reverse move inside the column game**, so `N10primeBound` and `n10prime` drop
`q_inv` and the core target is `n10prime_core`. This directly answers §11(C): the vacuous `q_inv < k − X` premise is
gone. I rebuilt both files independently against the trusted `Pous` (`~/colbuild4`, same toolchain; store
`TRUSTED.sha256` verifies before and after). They compile with only the two intended `sorry`s (`n10prime` L203,
`n10prime_core` L42); the proved lemmas (`cex_not_columnHard` re-proved, `src_card`, `core_card`,
`posSaving_ratio_lt_one`, `perComponent_ratio_ge_one`, `invWork'_le_work`, `invWork'_le_of_bounded`) are all on the
three standard axioms.

**(1) The key gate is faithful to `c2`/`decodeLower`; no real inverse query yields more than the reverse move.** The
new `colRound` adds `lowerCol := c.lowerCol ∪ (univ ×ˢ c.topWhole.filter (fun u => G.par u ⊆ c.topWhole))`: a held whole
top `u` whose top-parents are whole yields column `u` of *every* lower label. This matches the trusted
`Pous.Invertible`: `c²_u = P(x²_u ⊕ k²_u)` with `x²_u = transpose(c¹)_u` (column `u` of the lower layer) and
`k²_u = H(1, u, {c²_w : w ∈ par u})`, so `x²_u = P⁻¹(c²_u) ⊕ k²_u` is recoverable exactly when `c²_u` is held *and* the
key is computable, i.e. all of `u`'s parents' top labels are whole — precisely the gate `G.par u ⊆ topWhole`, and it
yields exactly the full column `{(w,u) : w ∈ univ}` (`decodeLower` is the `transpose` of the decoded top inputs). The
three probe cases all fail to beat it:
- *Inverse on a non-top value* `P⁻¹(y)`, `y ≠ c²_u`: returns a random pre-image, unrelated to any real column; the
  game grants nothing for it (reverse fires only on held whole tops). Yields *less*, not more.
- *Partial key*: `k²_u` is a single random-oracle value at the *full* parent set `{c²_w : w ∈ par u}`; with only some
  parents' tops the adversary can only query `H` at a different input, getting an unrelated hash, so it cannot form
  `k²_u` and cannot strip the mask off `P⁻¹(c²_u)`. The gate's "all parents" is exactly right (not "some").
- *Inverse of a lower label* `P⁻¹(c¹_w)`: returns `W_w ⊕ k¹_w` — that label's own input, no column of any *other*
  label; it needs `c¹_w` whole to be issued at all, so it grants nothing new. The game correctly offers no lower-reverse.

The move is faithful *and tight*: it grants exactly what a real inverse grants — so `ColumnHard` over this game is
neither too strong (which would make the certificate impossible) nor too weak (which would make `n10prime` false).

**(2) With `q_inv` gone, the inverse-query / circular-extraction difficulty has moved into `n10prime_core`, but into a
tractable, acyclic form.** `n10prime_core` (`sorry`) must prove, for a `(D,Q)`-bounded adversary with **unrestricted**
inverse queries against a `ColumnHard G ((D+1)/2) k X` graph, that `pr(answer ≥ k tops) ≤ N10primeBound N m n wc Q_tot
pos k X + Q_tot²/2^(n·wc)`. The previous design tried to *reduce* bounded-`q_inv` to a forward-only lemma
(`n10prime_forward`) via recording, keeping inverse handling outside the core but needing the undischarged `q_inv < k−X`
(§11C); option (b) instead prices inverse *inside* `ColumnHard`, so the reduction and its premise are gone and the
inverse handling now lives in the core. It is not literally forward-only, but the recording argument plus in-game
pricing make the replay **acyclic**: the reverse move fires only on tops that are *held* (in `σ`, known at the start)
or *forward-derived* (whose column was already available, so their reverse adds nothing new), and held-top reverses are
gated in `G`'s DAG order — so the run is "reverse-expand `σ`'s held tops (bounded, acyclic), then forward," and fresh
columns are still refilled forward from `σ`. The candidate cycle from §11(C) still cannot form (inverting `c²_j` gives
only column `j`; forward-computing `c²_i` needs column `i`). So the core is a *two-directional* column-granular Pietrzak
extraction whose reverse part is structurally bounded, not a separate reduction — the difficulty is now honestly
contained rather than deferred to a premise that could not be met.

**(3) Quantifier order is correct; the "all `n` tops" claim holds and is faithful; but a new vacuity risk: the
certificate no longer builds against this game.** Quantifier order is the B5 order — params/`tag`/`G`/`W`, then
`ColumnHard`, then `∀ A₁, A₂` with `A₂` `(D,Q)`-bounded, `W` before `ω` — correct; `hXk : X ≤ k` keeps `k − X ≥ 0`. The
claim "holding only tops recovers every lower column only if all `n` tops are held" is **true in the game and faithful
to reality**: each column `u` comes only from reversing top `u` (needing `u` held and `par u` whole), and promoting a
lower label to whole needs *all* `n` of its columns, so a proper subset of held tops recovers only its own gated
columns and cannot bootstrap the rest — matching that `x²_u` is obtainable only by inverting `c²_u`. Holding all `n`
tops is storing the entire top layer (`ρ = 1`, no saving), so a space-saving adversary is forced back onto the
forward, depth-robust lower layer — which is what makes the two-directional certificate meaningful.

The vacuity risk is real and is the headline caveat. `ColumnHard` is now quantified over the **two-directional** game,
a strictly stronger property than the promotion-only game of §12 (reverse moves make `colReach` reach more, so more
`c0` satisfy the antecedent). **The §12 band certificate does not establish it:** the `p3-column` files are unchanged
(`ColumnSaving.lean` `58d31f9e`, built against `0cec2bb6`) and do not build against `c386ed62`. I confirmed this — the
rebuild fails because `colRoundF` is renamed to `colRound` and, structurally, `colReach_lowerCol` ("columns never
change") is now **false**: I kernel-disproved it (`~/colbuild4/DisproveRev.lean`, `by decide`) — on a 2-node spine,
holding only the source top `0` adds column `(0,0)` after one round, so `lowerCol` grows. This is the exact analogue of
the §11 promotion break (`colReach_lowerWhole`), now for the reverse move breaking the "columns constant" invariant. So
under the current game **`ColumnHard` is uncertified for any operating-point graph**, and `n10prime`'s hypothesis is not
yet known to be satisfiable with small `X`. The draft/analysis acknowledge this ("it *will* re-derive the band
certificate against this game"; `inverse_rule_sim.py` estimates the key gate costs only ≈1 extra label, `X≈4` — but
that is a Python estimate, not a Lean certificate). `cex_not_columnHard` is re-proved against the new game (the
column-hole graph is still excluded), so the counterexample side is sound.

**Verdict (§13): the option-(b) redesign is faithful and is a genuine improvement — it removes the vacuous `q_inv < k−X`
blocker (§11C) by pricing key-gated inverse moves structurally in `ColumnHard`, the gate is exactly `Pous.Invertible`'s
`c2`/`decodeLower` key requirement, no inverse query yields more than the reverse move, the "all `n` tops" property is
faithful, and quantifier order is correct.** Two things are now open, and one is newly urgent:
1. **`n10prime_core` (the core, `sorry`).** What is left to prove is the two-directional column-granular Pietrzak
   extraction: build the encoding (replay deterministic `A₂` + honest labeler; a column `(w,u)` is *fresh* if read
   inside a top-query input `x²_u` before `c¹_w`'s forward query; delete fresh columns' `wc` bits from `P`'s table,
   refill on replay from `σ`); show every online `P⁻¹` is a reverse move on a held top (`c²_u ∈ σ`, priced by the
   holding) or a derived top (adds nothing), so the replay is acyclic and the refill forward; prove injectivity; and
   the counting step — the decoded holding is a `ColState` reaching `k` tops, so `ColumnHard` forces
   `size ≥ (k−X)·n` columns, giving `N10primeBound` via `pr_le_of_decode_charge`, plus the explicit forward-`P`
   collision term `Q_tot²/2^(n·wc)` (permutation-entropy correction absorbed). This is PIEs Conjecture 1 in
   two-directional column form — the same hardness class as before, but now *containing* the inverse accounting instead
   of deferring it.
2. **The `X(G,d)` certificate must be re-derived against the two-directional game** (`ColumnHard` over `colRound` with
   the reverse move). The §12 band certificate is stale here (`colReach_lowerCol` is false; `colRoundF` renamed); until
   it is redone, `n10prime`'s hypothesis is uninstantiated and the result, though the right shape, is not yet known to
   be non-vacuous at the operating point. Expect `X` to rise by ≈1 label if the key gate behaves as the Python
   simulation predicts.

Overall verdict unchanged: **GRANTED WITH CONDITIONS** (withdraw N10/`InvertibleLabels`; N10′ is the corrected open
target). Option (b) is the right modelling fix and closes the §11(C) gap in principle; the residual is now two clean
`sorry`s — the two-directional core extraction, and a re-derived column-saving certificate for the new game.

## 14. The column-saving certificate re-derived for the two-directional game (`p3-column`, 27 Sep 2026)

This closes the second `sorry` flagged in §13: the `X(G,d)` certificate now exists for the key-gated two-directional
game. The `p3-column` folder was rewritten — the `colRoundF`-era files are gone (`ColumnSaving.lean`,
`BandCertificate.lean`, the old checks, `PromotionCheck.lean`), replaced by `TwoWay.lean` (`columnHard_of_schedule`),
`BandComb.lean`, `BandWeights.lean`, `BandTwoWay.lean` (X = 3 instances) and `CheckTwoWay.lean`. I rebuilt the whole set
independently against the current draft (`ColumnAwareDraft.lean` sha `a0beea74`, `~/colbuild5`, same toolchain; store
`TRUSTED.sha256` verifies before and after).

**1. Builds, standard axioms, `--fresh` replay — all confirmed.** `Encoding`, `ColumnAwareDraft`, and the four
`PebblingCol` modules compile with 0 errors / 0 warnings (only the draft's own `n10prime` sorry). Every target —
`columnHard_of_schedule`, `band_scheduleBound`, `band_columnHard_twoWay`, the three instances
(`band_twoWay_220_12`, `…_12_d11`, `…_16`, each `ColumnHard (bandGraph n k) d 220 3`) and `band_depthRobust` — reports
`[propext, Classical.choice, Quot.sound]` only; the numeric instances discharge their side-conditions with `decide`/
`norm_num` (kernel `decide`, no `native_decide`). `leanchecker --fresh PebblingCol.BandTwoWay` (Mathlib + Pous + the
modules from an empty environment) exits 0 in 3m26s. The draft's *game* (`colRound`, `ColumnHard`, `colReach`) is
byte-identical to the `c386ed62` I reviewed in §13 (the only draft change is `n10prime` gaining `hN : 1 ≤ N`), so the
§13 faithfulness verdict on the key-gated reverse still stands.

**2. `CheckTwoWay.lean` restates everything with the draft's own definitions.** Each result is written in
`PousColumnAware.ColumnHard` and `basePath` (via `bandG` spelled out) and closed by the `PousP3Column` theorem —
`check_twoWay_220_12 : ColumnHard (bandG 220 12) 10 220 3 := band_twoWay_220_12`, etc. `ScheduleBound`, `ndHeld` and
`tri` are spelled out inline (`check_columnHard_of_schedule` writes the full schedule hypothesis; `check_ndHeld` proves
the `ndHeld` unfold; `tri m` is written as `∑ i ∈ range (m+1), i`), and `band_depthRobust` uses the trusted
`Pous.DRG.DepthRobust`. These typecheck only because `bandG`/`ScheduleBound`/`ndHeld`/`tri` are definitionally the
draft's and the certificate's own terms; all seven checks are on the three axioms and replay `--fresh`. So the
certificate is stated in the draft's vocabulary, not a private copy.

**3. The promoted-label pricing is sound and tight — a promoted label cannot be cheaper than charged.**
`columnHard_of_schedule` reduces `ColumnHard` to a `ScheduleBound` by charging, per lower label `w`, a base cost the
stored columns must cover (`hrow : base w ≤ fib w + φw w`, `fib w` = `w`'s stored columns). A *promoted* label (`w ∈ P`,
all its columns available at `t w − 1` but not from its own parents) is charged `base = |U| + |ndHeld G U r (t w)|` —
the dropped tops `U`, plus the held tops whose key-gated reverse is *not yet open* at `t w`. The charge is a genuine
lower bound, discharged by `col_origin`: **every** column in the reached `lowerCol` is either in `c0.lowerCol` (stored)
or revealed by a whole top `v` *whose parents are whole* — i.e. only by storage or the key-gated reverse, which is
exactly faithful to `Pous.Invertible.c2`/`decodeLower` (`x²_v = P⁻¹(c²_v) ⊕ k²_v`, `k²_v = H(1,v,{c²_w : w∈par v})`).
The sub-proof then rules out reveal for these specific columns: for `v ∈ U` the dropped top is not whole early enough,
and for `v ∈ ndHeld` the definition supplies a dropped parent placed late, so `par v` is not whole and the key-gate is
**closed** — the column must be stored. So a promoted label could be cheaper only if a column could be obtained without
storage and without a key-gated reverse, which `col_origin` (faithful to the trusted labels) forbids. The `ndHeld`
charge *is* the key gate doing its work: `inverse_rule_sim.py` shows the ungated rule would let promotion save ≈14
labels (killing the certificate), the gated rule ≈1 — and the machine-checked bounds (savings 2.33, 2.74, 2.70 vs the
cryptanalyst's best-found 2.33, 2.73, 2.67) confirm the pricing is neither unsound nor loose: `X = 3 = ⌈saving⌉` at all
three points. Because the reduction takes the schedule as given and prices *every* category (held `n−|U|`, rebuilt
saves only dropped tops placed later, promoted `|ndHeld|`, never-whole `|U|`), the adversary cannot escape by
re-categorizing; `band_scheduleBound` covers all schedules. Net: **no, a promoted label is not cheaper than the proof
charges**, and a held top used for reverse costs its full `n` columns — exactly the columns its reverse reveals, so the
reverse move earns no label (the certified `X` equals the forward-game value).

**4. `columnHard_of_bounds` and `basePath_columnHard'` are withdrawn; nothing in code depended on them.** They were the
§12 route to `ColumnHard` over the promotion-only game and referenced the renamed `colRoundF`; they are not
re-established, and the files that proved them are deleted (they no longer build — see §13's `colReach_lowerCol` break).
Nothing depends on them: `n10prime`/`n10prime_core` consume `ColumnHard` as a *hypothesis* (a `Prop`), now supplied by
`band_columnHard_twoWay` via `columnHard_of_schedule`, and no Lean code names the old lemmas. The only residue is stale
prose — the draft's comment block (`ColumnAwareDraft.lean` L228/230), `pebbling/AXIOMS.txt` L50, and `pebbling/NOTES.md`
L330 still say the certificate is "adopted from … `columnHard_of_bounds`/`basePath_columnHard'`"; these should be
updated to name `columnHard_of_schedule`/`band_columnHard_twoWay`, but they are comments, not dependencies. The
game-independent combinatorics (`BandComb`: F1, starts/ends, `band_rank_sum`) were carried over unchanged.

**Verdict (§14): the two-directional certificate builds against the settled draft, uses only the standard axioms, and
replays `--fresh`; `CheckTwoWay` restates it in the draft's own `ColumnHard`/`basePath`; the promoted-label pricing is a
sound, tight lower bound (a promoted label is not cheaper than charged — the key gate forces the `ndHeld` columns to be
stored, faithful to `c2`/`decodeLower`); and the withdrawal of `columnHard_of_bounds`/`basePath_columnHard'` breaks
nothing but stale comments.** This resolves §13's second open item: `ColumnHard` is now certified with `X = 3` at the
operating points *for the two-directional game*, so `n10prime`'s hypothesis is instantiated and non-vacuous. The single
remaining `sorry` on the N10′ path is `n10prime_core` — the two-directional column-granular extraction (§13(2)). Overall
verdict unchanged: **GRANTED WITH CONDITIONS** (withdraw N10/`InvertibleLabels`; N10′ is the corrected open target, now
with a machine-checked two-directional `X(G,d)=3` certificate and a single core extraction left to prove).

## 15. P3 end-to-end `Meets`, conditional on N10′ (`p3-meets`) — the `n10prime` interface is broken as stated (27 Sep 2026)

The `p3-meets` folder assembles P3's `Meets` from `n10prime`'s statement (as a `type_of%` hypothesis, its `sorry`
unused) and the pinned `Theorem1iiSeq`. I rebuilt it independently against the current draft
(`ColumnAwareDraft.lean` sha `364ade17` — a **comment-only** change from the §14 `a0beea74`, updating the stale
lemma-name references I flagged in §14; the game/`n10prime`/`N10primeBound` code is byte-identical) plus the `p3-column`
chain (`~/colbuild6`; store `TRUSTED.sha256` verifies before and after). The prover's own `NOTES.md` pre-flags the
interface problems; I confirmed each independently.

**1. Builds, standard axioms, `--fresh`.** `Encoding`, `ColumnAwareDraft`, the four `PebblingCol` modules and
`PebblingMeets/P3Meets` compile with 0 errors / 0 warnings (only the draft's `n10prime` sorry). All ten P3Meets targets
(`p3Scheme_correct`, `…_codeHoldsW`, `…_space`, `segBound_of_n10prime`, `segBound_of_n10prime_pos3n`,
`masked_charge_vacuous`, `sampling_119`, `sampling_185`, `p3_meets`, `p3_meets_of_segBound_nomask`) and the three
`CheckP3Meets` restatements report `[propext, Classical.choice, Quot.sound]` only. `leanchecker --fresh
PebblingMeets.P3Meets` exits 0 in 3m30s.

**2. `n10prime` collapses to `pos = 0` — stronger than intended and unprovable. CONFIRMED.** `n10prime` takes `pos` as
a universally-quantified argument with `hpos : pos ≤ 3n`, and `N10primeBound = N·2^m·(Q_tot·2^n)^{pos}/2^{(k−X)·n·wc}`
is monotone increasing in `pos`. So `∀ pos ≤ 3n, pr ≤ bound(pos)` is equivalent to its smallest member, `pos = 0`,
whose bound `N·2^m/2^{(k−X)·n·wc}` carries **no** position charge. I verified this with an independent check
(`~/colbuild6/CollapseCheck.lean`, three axioms): from the `n10prime` hypothesis, instantiating `pos := 0` yields the
charge-free bound directly. `segBound_of_n10prime` uses exactly that instance (`h10 … 0 …` then `pow_zero, mul_one`),
so `p3_meets` (`k = 119`) rests on the position-charge-free bound. But the intended reading is that `pos` is the number
of positions the extraction actually names (an *output*, ≤ 3n) and the bound is charged there; the `∀`-form instead
demands the `pos = 0` bound, which the real core (`n10prime_core`, §13) cannot deliver — it genuinely names positions.
So `n10prime` as written is stronger than intended and almost certainly false, and `p3_meets` at `k = 119` is hollow
(a true implication from an unprovable premise). **Fix:** fix `pos := 3n` (or existentially quantify it), not `∀`.

**3. `masked_charge_vacuous` — the honest `pos = 3n` charge with the `n`-bit mask yields no audit bound. CONFIRMED.**
With `p₀ β S B ℓ = 1 − (β − S − B)/(B·ℓ)` (trusted `Inc.lean`) and `S = ⌊(18/19)·|W|⌋ = 1 696 547`,
`B·ℓ = |C| = 1 790 800`: at `pos = 3n` each position costs `log₂(Q_tot·2^n) ≈ 248` bits (dominated by the `n = 220`-bit
mask), so `3n = 660` positions cost `163 680` bits = **9.1 % of C**, while the whole pre-state slack is
`(n − X)·ℓ − S − B = 69 613` bits = **3.9 % of C**. Since `9.1 % > 3.9 %`, the masked loss `L = 1 602 700 < S + B`, so
`β − S − B < 0` and `p₀ ≥ 1` for every `β ≤ L`. `segBound_of_n10prime_pos3n` derives that `L` from `n10prime` at
`pos = 660`, and `masked_charge_vacuous` proves `1 ≤ p₀ β …` for `β ≤ L`; then `Theorem1iiSeq`'s sampling term
`p₀^k ≥ 1`, so no `Meets` follows for any `k`. So the intended (honest, masked) charge is vacuous — the `pos`-collapse
in finding 2 is the *only* reason `p3_meets` goes through.

**4. The no-mask variant (`k = 185`) is sound, and freshness needs no stored mask. CONFIRMED.**
`p3_meets_of_segBound_nomask` proves `Meets … 185 …` from a `SegBound` at `L = 1 766 380 − 660·36 = 1 742 620` (36 =
`⌈log₂(n·Q_tot)⌉` bits per position: which node, which query — the location needed to refill, with **no** mask). The
arithmetic checks (`β = 1 741 012`, `p₀ ≈ 0.9753`, `p₀^185 ≈ 0.98 % ≤ 1 %`, `sampling_185`). The load-bearing claim —
that a decoder can infer freshness without the mask — is **sound**: the decode is a deterministic replay of `A₂` + the
labeler on the fixed `ω` (acyclic, §13), so at each revealing query the decoder knows which lower labels are already
forward-computed, hence which components are fresh (a component `(w,u)` is fresh iff `c¹_w` is not yet computed). The
`n`-bit mask is therefore redundant over-charge; charging only the 36-bit position identity is enough. **But** this
variant takes the improved `SegBound` as a *hypothesis* — the current `n10prime` supplies only the collapsed `pos = 0`
bound or the vacuous masked `pos = 3n` bound, not this one. So `k = 185` is real only once `n10prime` is **restated**
with the recommended no-mask bound `N·2^m·(n·Q_tot)^{3n}/2^{(k−X)·n·wc}` (fixed `pos = 3n`, no free `pos`, no mask); the
prover gives the ten-line bridge shape (`segBound_of_n10prime_pos3n`).

**5. `p3Scheme` is a faithful (single-segment) P3. CONFIRMED, with two honest scope caveats.** It is a real scheme over
the salted `p3Model' 220 37` (H, P, P⁻¹): graph `B(220,12)` in both layers, `C` = the 220 genuine two-layer invertible
top labels `c²_v` (built from `c1'`/`c2'`), `pp` = the 128-bit salt = the coins, tag `(salt, segment 0)`; `dec` is
public and bit-exact (key, `P⁻¹`, transpose, key, `P⁻¹`) and reads all of `C` — not the F2 junk/identity shape.
`p3Scheme_correct` (`dec∘enc = id`), `CodeHoldsW` (`|C| = |W| = 1 790 800`, rate 1) and `SpaceBound 21/20`
(`|C|+|pp| = |W|+128`) are all proved, and `stateBound = ⌊(18/19)|W|⌋ = 1 696 547`. The reduction chain
`SegBound → TimedINC` (`p3_timedINC`: compressor = state, block programs = per-label programs, salt averaged via
`pr_prod_le_snd`, `Lab`↔`Bits` via `progMap`) `→ Meets` (via the pinned `Theorem1iiSeq`, union + sampling terms) is
sound. The two caveats, both flagged by the prover, are scope not faithfulness: (i) it is **one segment** (`B = 220 = n`,
`|C| ≈ 224 KB`) — a full-size P3 needs `n10prime` stated for all `N` segments *jointly* (the shared `P` means
per-segment bounds don't multiply); (ii) label width is `220·37 = 8140`, not the spec's `8192` (the `Lab n wc` type
needs `n | m`).

**Verdict (§15): `p3-meets` builds, is on the standard axioms, and replays `--fresh`; `p3Scheme` is a faithful
single-segment P3 and the `SegBound → TimedINC → Meets` chain is sound — but the end-to-end result is only as good as its
`n10prime` premise, and that premise is broken as stated.** Because `pos` is universally quantified over an increasing
bound, `n10prime` collapses to its position-charge-free `pos = 0` case (independently reproduced), which is stronger
than intended and unprovable; the honest `pos = 3n` masked charge is vacuous (9.1 % > 3.9 % slack,
`masked_charge_vacuous`). So the headline `p3_meets` at `k = 119` is hollow. The genuine result is the no-mask
`k = 185` variant — sound, with freshness correctly inferred from the deterministic replay rather than a stored mask —
but it is conditional on a **restated** `n10prime` (fixed `pos = 3n`, charge `(n·Q_tot)^{3n}`, no mask). **Required
correction:** restate `n10prime`'s bound with no free `pos` and no `n`-bit mask before `p3-meets` can claim P3 `Meets`
(then at `k = 185`, one segment). This does not change the overall verdict — **GRANTED WITH CONDITIONS** — but it adds a
concrete statement-level fix to `n10prime` on top of the still-open `n10prime_core`, and confirms the trusted chain
(`p3Scheme`, `TimedINC`, `Theorem1iiSeq`) is otherwise sound and faithful.

## 16. `PermIncompressibility` — the named incompressibility kernel: I tried to refute it; it holds (27 Sep 2026)

The core `n10prime_core`/`n10prime` are now proved **modulo a named hypothesis** `PermIncompressibility`
(`pebbling/PermKernelDraft.lean`), the De–Trevisan–Tulsiani / Gennaro–Trevisan permutation-incompressibility kernel, to
be discharged later by a Lehmer-code library. Given the N10 burn (a false named assumption), I reviewed it hard on a
fresh build (`~/colbuild7`, current drafts: `ColumnAwareDraft` `d7bf88d3`, `ForwardCoreDraft` `03ad6394`,
`PermKernelDraft` `e5688239`; store `TRUSTED.sha256` verifies before and after). **Also note the drafts moved since §15:
`n10prime` has adopted every §15 fix** — `pos` is now **fixed at `3n`** (not `∀`-quantified, so the §15 collapse is
gone), the `n`-bit mask is dropped (charge `n·Q_tot` per position), and it carries the `+ Q_tot²/2^{n·wc}` collision
term — so `n10prime` and `n10prime_core` are now identical in shape and both follow from the kernel.

**Build / axioms / `--fresh`.** All four modules compile (only the draft's own `n10prime` sorry). The kernel's whole
support layer is machine-checked on the standard axioms: `reduced_saving` and `henc_card_of_pool` on `[propext]` (pure
`Nat`), and `core_to_bound`, `n10prime_core_of_encoding`, `pr_partition`, `pr_pair_le`, `funcCollision_le`,
`model_collision_le`, `card_lab`, `n10prime_core_of_kernel`, `n10prime_of_kernel`, `permIncompress_of_construction` on
`[propext, Classical.choice, Quot.sound]`. `leanchecker --fresh Pebbling.PermKernelDraft` exits 0 (3m32s).

**Is it true as stated, for every `ColumnHard`, `(D,Q)`-bounded setup? — Plausibly yes; I found no refutation.** The
kernel asserts, for every such setup, a collision predicate `Coll` with (i) a covering decode of the *non-colliding*
winners from `σ` plus a hint whose cardinality satisfies `card Xh · 2^{(k−X)·n·wc} ≤ (n·Q_tot)^{3n}·|Ω|`, and (ii) a
birthday bound `Q_tot²/2^{n·wc}` on the colliding winners. Two things make this categorically unlike N10 (which had a
concrete counterexample and a currency error):
- *The arithmetic is machine-verified, including the subtle part I attacked first.* The DTT/GT permutation encoding
  saves the **falling factorial** `M!/(M−d)! = M^{\underline d}` (delete `d` predicted `P`-outputs → `(M−d)!` reduced
  descriptions), **not** the power `M^d = 2^{d·n·wc}` the bound names. I worried this made the card bound false by the
  factor `M^d/M^{\underline d} ≈ 1 + d²/M`. The prover has already isolated exactly this: `reduced_saving` proves
  `(M−d)!·(M+1−d)^d ≤ M!` (via `descFactorial`), and `henc_card_of_pool` carries the **pool correction**
  `hpool : M^d ≤ e·(M+1−d)^d` as an explicit hypothesis, absorbed by the position budget `e = (n·Q_tot)^{3n}` (at the
  operating point `M = 2^{8140}`, `d ≈ 217`, `e ≈ 2^{23760}`, so `(M/(M+1−d))^d ≈ 1 + 2^{-8124} ≪ e`). So the
  falling-factorial gap is honestly accounted, not ignored — the bound is achievable.
- *The reduction is genuine, not vacuous.* `permIncompress_of_construction` (proved) commits `Coll := pColl`, the
  concrete event "the segment's `P`-query trace repeats an input" (`¬(pInputs (segTrace …)).Nodup`), and reduces the
  kernel to exactly two concrete obligations: `hconstr` (the covering decode of `¬pColl` winners with the reduced
  cardinality) and `hbirthday` (`pr(win ∧ pColl) ≤ Q_tot²/2^{n·wc}`). Both are standard, sound techniques — the DTT/GT
  rank code and a birthday bound — and the birthday machinery is already proved (`model_collision_le`). Neither is
  formalized yet; that is the honestly-deferred Lehmer library.

So the kernel is *plausibly true* and *unproven*, and — crucially, unlike N10 — shows no currency error, no
counterexample, and no vacuity. The two places to keep the Lehmer prover honest (the only spots I see residual risk):
(a) `hconstr` must bridge "`ColumnHard` ⇒ stored `≥ (k−X)·n` columns" to "`(k−X)` **whole** deletable `P`-entries" —
the column-units-to-whole-labels step, since `P` is deleted per whole label, not per column; (b) `hbirthday` must bridge
the proved static `model_collision_le` (collision of `H`-*values*) to `pColl` (collision of `P`-*inputs* `x²_u ⊕ k²_u`,
adaptive over the run). Both are believable, but they are the load-bearing unproven content.

**Strong enough to derive `n10prime_core` without being stronger than the real lemma? — Yes.** `n10prime_core_of_kernel`
and `n10prime_of_kernel` both prove their exact targets from it (three axioms, no `sorry`). It is not stronger-than-true:
the card bound it demands is *achievable* (the falling-factorial gap is absorbed, not over-claimed), so it is the
constructive form of the same probability bound — the standard technique's natural strength, neither weaker (it derives
both targets) nor an over-claim (it asks only for the achievable `M^{\underline d}`-with-slack saving).

**Could its quantifiers smuggle in the conclusion? — No.** The `∃ Coll` cannot be abused: the birthday clause
`pr(win ∧ Coll) ≤ Q_tot²/2^{n·wc}` forbids dumping the winners into `Coll` unless they are genuinely that rare, and
`permIncompress_of_construction` pins `Coll` to the concrete `pColl` (which does *not* always hold — `Nodup` `P`-inputs
is the typical case, so the `¬pColl` winners are the bulk and `hconstr` is non-vacuous). The `∃ Xh, dec` cannot be
abused either: the card bound forces `card Xh ≤ (n·Q_tot)^{3n}·|Ω|/2^{(k−X)·n·wc} ≈ |Ω|/2^{1.75·10⁶}`, so the decode
must genuinely compress the winners by ~`2^{1.75·10⁶}` — it cannot cover them with a trivially large hint. The kernel is
a real compression statement, not a disguised assumption of the conclusion.

**The `+ Q_tot²/2^{n·wc}` collision term — necessary, honest, and now in both `n10prime` and `n10prime_core`.**
Confirmed present in the current `n10prime` (`d7bf88d3`). It is *necessary*: the collision-free form `pr Win ≤
N10primeBound` is false, because colliding winners (the `k−X` predicted `P`-inputs not distinct) have probability up to
`≈ Q_tot²/2^{n·wc} ≈ 2^{-8100}`, which dwarfs `N10primeBound ≈ 2^{-1.75·10⁶}` — so without the term the bound is
violated on the collision event. It is *honest*: the birthday bound behind it (`model_collision_le`/`funcCollision_le`/
`pr_pair_le`, `card_lab`) is proved. Downstream impact, which the `p3-meets` owner must absorb (and which supersedes
§15's numbers): the term is `m`-independent and now *dominates* `N10primeBound`, so the effective per-round `π ≈ 2^{-8100}`
is flat in the state size `β`; the audit still closes because `|Hist|·π = 2^{8k}·2^{-8100} ≤ 2^{-128}` binds only
`k ≲ 996` (not `β`), while `β` can be taken above `S+B` to drive `p₀^k` down — so `p3-meets` survives at `k = 185`, but
its `SegBound`/`union_term` arithmetic must be re-derived against the collision-dominated bound (the §15 `pos = 0`,
collision-free `p3_meets` at `k = 119` no longer even typechecks against the new `n10prime`).

**Verdict (§16): adopt `PermIncompressibility` only as the explicitly-temporary scaffold it is labelled to be — it is a
faithful, non-smuggling, right-strength statement of a sound (DTT/GT) incompressibility technique, its arithmetic
(including the falling-factorial subtlety) is machine-verified, and I found no refutation.** This is *not* another N10:
there is no counterexample and no currency error, only unformalized (believable) content — the covering decode and the
adaptive birthday, cleanly isolated by `permIncompress_of_construction` into `hconstr` and `hbirthday`. It is safe to
build `n10prime`/`n10prime_core` on it *as a tracked scaffold*, provided (1) it is discharged by the Lehmer library
before the layer is treated as unconditional, and (2) the two load-bearing steps above (columns→whole-labels in
`hconstr`; `H`-value→`P`-input adaptivity in `hbirthday`) are proved, not assumed, when it is. The collision term is a
required, honest correction; `p3-meets` must re-derive its parameters against it. Overall verdict unchanged:
**GRANTED WITH CONDITIONS** (withdraw N10/`InvertibleLabels`; N10′ is the corrected open target, now resting on a
reviewed, plausibly-true, still-to-be-discharged incompressibility kernel rather than a false whole-label conjecture).

## 17. PR #162 head `f856ae00` (`protocols/pous`): trusted `ColumnGame`, the 46 pins, and narrow-state H (27 Sep 2026)

Re-reviewed the draft PR that lands the POUS package under `protocols/pous/lean/` (head `f856ae00`, branch
`cursor/pous-lean-2464`), read via `git show` at that commit (workspace stayed on `main`, nothing checked out or
modified; the store copy is untouched).

**1. `Pous/Model/ColumnGame.lean` — the six trusted defs are exactly what I reviewed in §14.** The trusted layer now
carries the column game in namespace `Pous.ColumnGame`: `ColState`, `ColState.size`, `colRound`, `colReach`,
`ColumnHard`, `basePath`. I diffed each definition **body** against the `a0beea74` draft I reviewed in §14 (my
`colbuild5` copy) — they are **identical** (confirmed both by a normalized body-diff and by direct comparison of the
load-bearing lines: the key-gated reverse `lowerCol := c.lowerCol ∪ (univ ×ˢ c.topWhole.filter (G.par u ⊆ topWhole))`,
the forward-top rule, `ColumnHard`'s `(k−X)·n ≤ c0.size`, and `size`). Only three things changed, all non-semantic and
correct: the namespace (`PousColumnAware → Pous.ColumnGame`), shortened docstrings, and the deliberate **exclusion** of
the draft's model/bound/statement — `p3Model'`, `c1'`/`c2'`/`topLabel'`, `N10primeBound`, `n10prime` are **not** in the
trusted layer (the file's header says so), and the unused `ColWin` was dropped. So only the graph-combinatorial game the
band certificate needs is trusted; the unproven crypto (`n10prime`) stays out. My §14 faithfulness verdict on these
defs (the reverse move matches `Pous.Invertible.c2`/`decodeLower`; the promoted-label pricing) carries over unchanged.
`ColumnGame` imports only `Pous.Model.Labelling` (for `TopoDAG`), not `Invertible` — a clean trusted boundary.

**2. The 46 pins in `lean-audit.json` are consistent with `PROTOCOL.md`.** Every statement `PROTOCOL.md`'s table marks
**proved** is pinned (`KFloor`; the `Theorem1i/ii/iii` family; `FibreCount`/`A1`/`A6`; `A3Prime`/`A3PrimeLam`;
`B1IndepSet`/`B2Stacking`/`B3Chain`; `FischClaim13/14`; `B5ExPostFacto{,Bounded}`; `TransposeMixing`/
`ReverseNeedsAllChildren`; `N10Refuted`; `SampledAudit{Prod,Seq,Sim}`; `StackedAudit{Seq,OnePercent}`; `DenseMeets`),
and the two "also proved, no `Pinned` statement" entries (`PousBridge.b5_stacked`, `PousP3Column.band_twoWay_{220_12,
_d11,220_16}` at `X = 3`, matching §14) are pinned too. Crucially the **open** targets (`A2LemmaAM1`, `A5RabinGcd`,
`A7Params`, `M1Meets`) are **not** in the pins, and the **withdrawn** `InvExPostFactoTwoLayer`/`InvertibleLabels` are
**not** pinned while `N10Refuted` (`¬ InvExPostFactoTwoLayer`) **is** — exactly the §9 correction, now baked into the
package (`Assumptions.lean` records `InvertibleLabels` as retracted). No real `sorry` backs any pin: the only two
`sorry` tokens in `Pous/`+`PousProofs/` are inside docstrings ("Only the `sorry` is replaced"), and the pinned proofs
(`PousProofs.B2Stacking := @PousB2.b2_stacking`, etc.) are genuine. The 46 pins are a **superset** of the prose table:
11 further pins are proved sanity/negative-control/accounting lemmas (`honest_/raw_seq,sim_accepted`, the F2/F3 controls
`junk_{correct,not_meets,spaceBound}`/`not_meets_{eps_one,of_lt_eps}`, `plain_short_coins_insecure`, `k_ge_86`,
`Accounting.p₀_at_report`, `report_k214`) that `PROTOCOL.md` references (the floor, the `|C|≥|W|`/`ε≤2^-128` guards,
the certified numbers) but does not tabulate. That is a non-exhaustive prose table, not a discrepancy — nothing is
pinned that `PROTOCOL` calls open/false, and nothing `PROTOCOL` calls proved is missing. (I did not re-run `audit.py` on
the PR — CI shows only GitGuardian on this draft — but I independently built and axiom-checked the substantive pins in
§3–§14 against the store copy the PR mirrors, and confirmed the proofs are sorry-free here.)

**3. The narrow-state H caveat is accurate, well-scoped, and honest — and it is the dominant real-world caveat.**
`PROTOCOL.md` §"Choices that could be wrong" states that **every** result modelling H as a monolithic `m`-bit random
oracle (B3, B5, the stacked audits, `DenseMeets`, P3's labels) holds **only in that model**, while the band certificate,
being pure combinatorics, is unaffected. This is correct and matches my reviews (the ideal-RO is load-bearing for the
crypto results; `Pous.ColumnGame`/`band_twoWay` contain no H). The stated attack is real and correctly attributed: a
real hash whose `m`-bit output is squeezed from a narrower internal state lets the adversary store each label's
pre-squeeze state and regenerate the label — with SHAKE's 1600-bit state, Dense from ≈20 % of `C` in one round, P3 from
≈39 % in three — which the ideal-RO model cannot see. The citation (Ristenpart–Shacham–Shrimpton: indifferentiability
does not compose into multi-stage/storage games) is the right one, and the consequence is stated without hedging: no
ideal-hash result transfers to a concrete hash by citation, so `DenseMeets`'s "no named assumption" means *within the
ideal-hash model only*. The planned fix (H as a wide sponge, state ≥ `m`, over an ideal permutation, re-proved in the
ideal-permutation model; Lean statements unchanged) is credible. My one framing note: this caveat is more than a
"choice that could be wrong" — it means **no current POUS security result yet gives concrete-hash security**, so it is
the single most important open item for real-world soundness and deserves top billing, not a sub-bullet. But it is
stated accurately and completely, and it does not touch the *in-model* correctness of any pinned statement.

**Verdict (§17): the PR head faithfully lands what I reviewed.** The six trusted `ColumnGame` defs are byte-identical
(bodies) to the §14-reviewed draft, with the unproven model/bound/`n10prime` correctly kept out; the 46 audit pins are
consistent with `PROTOCOL.md` (all "proved" pinned, all "open" and the withdrawn N10/`InvertibleLabels` excluded,
`N10Refuted` included, no real `sorry`), the only gap being a non-exhaustive prose table; and the narrow-state H caveat
is accurate, correctly cited, and honestly scoped (the dominant real-world limitation, which I'd elevate in prominence).
No blocking finding. Overall verdict unchanged: **GRANTED WITH CONDITIONS** — the trusted layer and pinned proofs are
sound and faithfully packaged; the standing conditions remain the provisional modelling choices (`CodeHoldsW`/`εMax`/
reveal), the still-open targets (`A2`/`A5`/`A7′`/`M1Meets`, and the N10′ path resting on the §16 kernel), and — now
made explicit at the package level — the narrow-state H model gap that every crypto result depends on.

## 18. Tweakable-P restatement (`TweakedDraft.lean`, sha `07ae5999`): per-node permutations — reviewed like N10′ (27 Sep 2026)

The scheme now uses a **tweakable** permutation, one `P_t` per `(segment tag, layer, node)`. I reviewed the restated
statements (`p3ModelT`, `c1T`/`c2T`/`topLabelT`, `N10primeBoundT`, `n10primeMulti`, `n10prime`) and the rationale
(`internal/n10prime-tweaked-p-evaluation.md`) the way I did N10′. It builds against the current `ColumnAwareDraft`
(`~/colbuild7`): everything elaborates, only the two intended `sorry`s remain (`n10primeMulti` L80, `n10prime` L96); the
column game (`ColState`/`colRound`/`ColumnHard`) is reused unchanged and is model-agnostic.

**Faithful — as a deliberate scheme change, with a higher instantiation cost.** `p3ModelT` gives each honest label its
own permutation: `c¹_{s,v} = P_{(s,0,v)}(W_v ⊕ H(…))`, `c²_{s,v} = P_{(s,1,v)}(transpose(c¹)_v ⊕ H(…))`, tweaked by the
`(tag, layer, node)` that `H` already takes. This is a genuine change to P3, not just the model, and it is faithful to
P3's *intent* (fast invertible decode + DRG-hard reconstruction): decode still inverts the (now per-node) permutation,
and the reconstruction hardness is still the graph's. The consequence worth stating plainly: since `A₁` is unbounded and
can query every `P_t` offline, **the permutation adds no cryptographic hardness** — the adversary effectively *knows*
every `P_t` — so **all** of P3's security now rests on `ColumnHard` (the column/DRG hardness); the invertible layer
provides invertibility (for decode), not secrecy. That is an honest clarification, not a weakening. The real cost is
instantiation: the model now demands a **tweakable wide-block (`n·wc = 8140`-bit) invertible primitive**, one keyed
permutation per `(tag, layer, node)`, which is *harder* to realise concretely than a single hash and inherits — and
amplifies — the §17 narrow-state-H caveat (a real construction would build `P_t` from `H`, and a narrow internal state
still enables the pre-squeeze storage attack). So the tweak makes security *easier to prove* and *harder to instantiate*;
faithfulness is contingent on the deployed scheme committing to genuinely per-node-independent tweakable permutations
(if it ships a single/shared `P`, this proof does not transfer).

**Does the per-node tweak change what the adversary can precompute? — No shortcut; it only removes shared-`P` structure
(a safe direction).** `A₁` can precompute every `P_t` in full under both the shared and tweaked models; in neither does
that shortcut the labels, because producing `c²_{s,v}` still requires its input column `x²_{s,v}` (DRG-hard, the content
of `ColumnHard`). What the tweak *removes* is cross-node structure of a single shared `P` (relations `P(a)⊕P(b)…` an
adversary might exploit): with independent `P_t` there is none. That only helps security, so it is safe — but it is
exactly why faithfulness is contingent on the scheme actually being per-node (an over-idealisation otherwise). The
compression still correctly charges the adversary for the `(k−X)` fresh uniform outputs per segment it must produce.

**The single-entry deletion is exact — this removes both §16 subtleties.** Because each honest label is the *single*
honest input of its *own* fresh permutation, predicting it is one deletion from that `P_t`: `Equiv.Perm.decomposeOption`
gives `Perm(Lab) ≃ Lab × Perm(Lab∖{x})`, so fixing the honest output leaves `(M−1)!` and saves exactly `M = 2^{n·wc}`
per predicted tweak, hence `M^{k−X}` per segment and `M^{N(k−X)}` jointly — **exactly** `2^{sav·n·wc}`, with **no
falling-factorial (`M^{\underline d}`) gap** (the §16 `hpool` correction vanishes) and **no Lehmer library** (Mathlib's
`decomposeOption` replaces the whole interface (A)–(D)). That is a real improvement in both honesty and formalisation
burden over the shared-`P` rank code.

**The collision term `(N·n)²/2^{n·wc}` — a valid, direct independent-uniform birthday.** With distinct tweaks the
`N·n` honest tops are outputs of *distinct* permutations, hence independent uniform, so "two honest tops coincide" is a
plain birthday bounded by `(N·n)²/2^{n·wc}` — provable straight from the already-proved `funcCollision_le`/`pr_pair_le`
at `B := Lab`. This turns §16's genuinely hard obligation (the *adaptive input-collision* bridge `x²⊕k² = x²'⊕k²'`
under one shared injective `P`) into the easy already-proved birthday: input collisions across distinct tweaks live in
different tables and cannot matter, so only output coincidence remains. Its magnitude (`≈ 2^{-8090}` at the operating
point) is comparable to the untweaked term, so it does not newly dominate. One thing to check when `hbirthday` is
actually proved: the term counts the `N·n` *tops*, but the encoding deletes entries across *both* layers (`≤ 2Nn`
honest labels); if the decode needs all deleted outputs distinct, the honest bound is `(2Nn)²` — a ≤4× (2-bit) gap,
negligible but the proof should match the term to the exact set of deleted entries. Not a refutation.

**Multi-segment now multiplies correctly — this resolves §15's finding 3.** *(Erratum: the `n10primeMulti` form
reviewed here is **false** — it omits per-segment data and injective tags, so segments can coincide; superseded by
`N10primeMultiFixed`, see §20. The multi-segment *structure* below is right; the missing hypotheses are the bug.)* Under a shared `P`, per-segment bounds did
not compose (the `N` factor only multiplied one segment's bound, so P3 was single-segment). Under per-node tweaks the
segments' deletions are from disjoint tweak families, independent, so `n10primeMulti`'s joint event "≥ k tops in *every*
one of the `N` segments" compresses by `N·(k−X)` independent single-entry deletions — a genuine joint bound, saving
`2^{N(k−X)·n·wc}`. `n10prime` is exactly its `N = 1` case (verified: `sav = k−X`, `pos ≤ 3n`, collision `n²/2^{n·wc}`).
Whether "≥ k in every segment" is the right event to feed the audit is `p3-meets`'s conversion to settle; the statement
itself is well-formed. Set-encoded positions (`Nat.choose (N·Q_tot) pos`, `pos = 3nN`) are a legitimate tightening over
sequence encoding — the decode infers order from its replay (§15), so only the *set* of fresh positions needs naming —
and they are what improves `k` (the rationale's 159/144 vs 332).

**Not vacuous, not smuggling; correct quantifier order.** `ColumnHard` is satisfiable (the §14 band certificate, `X=3`),
and the bound is non-trivial at the operating point (the set-position cost stays under the `sav·n·wc` saving, `k=159`
claimed), so the statements are not vacuous. They do not smuggle the conclusion: the bound is a genuine compression
(each of the `N(k−X)` fresh outputs is a real single-entry deletion *forced* by `ColumnHard`), the collision `∃`/event
is the concrete independent-uniform birthday, and the hypotheses (params, `tags`, `G`, `W`, then `ColumnHard`, then
`∀ A₁,A₂` with `A₂` `(D,Q)`-bounded, `W`/`tags` before `ω`) are in the right order.

**Verdict (§18): the tweakable-P restatements are true (plausibly — via obligations that are now strictly *easier*),
faithful (as a deliberate scheme change, contingent on deploying genuinely per-node-independent tweakable permutations),
non-vacuous and non-smuggling.** The tweak is a real improvement over the shared-`P` N10′: the single-entry deletion is
*exact* (`M^{N(k−X)}`, no falling-factorial gap), it removes the Lehmer-library dependency (`decomposeOption`), it turns
the hard adaptive-collision obligation into the already-proved independent-uniform birthday, and it makes the
multi-segment bound compose (resolving §15's single-segment limitation). The remaining genuine content is now just
`columnHard_fresh` (`ColumnHard ⇒ ≥ (k−X)` fresh answered tops) plus the mechanical `decomposeOption`/birthday wiring —
both markedly smaller than the §16 kernel. The one caveat to record, and the price of the win: the security got *easier
to prove* by making the primitive *stronger and harder to instantiate* — a tweakable wide-block invertible permutation
per node, under which the permutation carries no hardness (all security is `ColumnHard`) and the §17 narrow-state-H gap
still governs any concrete instantiation. No refutation found. Overall verdict unchanged: **GRANTED WITH CONDITIONS**
(withdraw N10/`InvertibleLabels`; N10′ — now in tweakable-P form — is the corrected open target, with a cleaner, exactly
-accounted incompressibility argument and a heavier instantiation requirement).

## 19. P3 concrete instantiation (`docs/p3-instantiation.md`): SHAKE-Feistel P and wide-sponge H — red-teamed (27 Sep 2026)

The §18 caveat asked for a concrete tweakable wide-block primitive; `docs/p3-instantiation.md` specifies it: `P_T` a
keyed 10-round Feistel with SHAKE256 round functions and the tweak `T = (tag, layer, node)` inside every round, and `H`
a sponge (rate `m`, capacity 512) over a second untweaked Feistel `Π`. I red-teamed the three claims; I verified the
cited ePrint results against the papers (web).

**1. It realizes `p3ModelT`'s `Tweak → Perm Lab` — the citations say what's claimed, for the keyed/tweaked form.**
`p3ModelT`'s permutation family (a uniform `Tweak → Perm(Lab)`) is exactly an **ideal cipher** with key = tweak. The
construction — 10-round Feistel with round functions `F_i(T,x) = SHAKE256(0x50‖i‖T‖x)` — feeds the tweak into every
round function, which is precisely the *keyed* Feistel that **ePrint 2015/876 (Dachman-Soled–Katz–Thiruvengadam,
EUROCRYPT 2016)** proves indifferentiable from an **ideal cipher** at 10 rounds, `O(q¹²/2ⁿ)` (verified: the paper keys
the round functions to obtain the ideal cipher; the doc cites it correctly). Per fixed tweak the unkeyed random-
permutation results corroborate — **2015/874 (Dai–Steinberger)**, 10 rounds → random permutation, `ε = 6.0·10⁶·q⁸/2ⁿ`,
and **2015/1069 (Dai–Steinberger)**, 8 rounds → random permutation — both verified, and the doc's `7.4·10⁶` constant for
the 8-round bound is in the right range. The doc's round-count map ("5 distinguishable, 6–7 open, 8 one proof, 10 two
independent proofs, 14 = Holenstein–Künzler–Tessaro") matches the papers verbatim. Because the tweak enters as an
**RO input** (`0x50‖i‖T‖…`), distinct tweaks give *independent* round functions, hence independent Feistels — so the
family is independent-per-tweak even for adversarially-related tweaks, exactly `p3ModelT`. At the half-width
`n = 262,240` bits, every bound (`q¹²/2ⁿ` at `q=2¹²⁸` ≈ `2^{-260704}`) is astronomically below `2^{-128}`. **Sound.**
Caveats, all inherent and flagged by the doc: (i) these are *single-stage* indifferentiability results — carrying them
into the storage game is claim 2; (ii) they rest on SHAKE256/Keccak-f = RO/ideal-permutation (a standard heuristic the
doc lists); (iii) low-round Feistel indifferentiability has a history of subtle errors (the 5/6-round claims were wrong,
Seurin's 10-round simulator was flawed and repaired by the FIFO→LIFO switch), so standing on 10 rounds with HKT-14 as a
fallback is the prudent choice — which the doc makes.

**2. "No data path narrows below the label width" closes the *known* narrow-state attack, but not the general RSS gap —
which the doc states honestly.** *(Correction, §23: the residual RSS assumption is now **falsified** — the recommended
wide sponge is not RO-like in the storage game (`dense_two_labels_from_one_state`: public IV + `Π⁻¹` regenerate two
labels from one wide state). The "no narrow path" argument does not suffice; a feed-forward fix is needed.)* The specific §17/§18 attack (store a label's narrow pre-squeeze state, re-expand it)
is genuinely defeated here: `H` is a *wide* sponge (state `m+512 > m`, key = the `m`-bit rate), so `H`'s output has no
narrow seed; and inside the Feistels the only narrow states are the transient 1600-bit Keccak states of the round
functions, each computed by absorbing a *half* `R_i` — and `R_i` is carried forward as the next round's `L_{i+1}` (the
Feistel property), so the computation must hold the wide half anyway and caching the 1600-bit state instead saves
nothing. So the doc's structural argument is correct and well-targeted: the concrete construction adds **no** compressible
narrow seed that the ideal-cipher abstraction lacked. **But** this is an argument about the *honest* data path; it does
not prove multi-stage composition. RSS (ePrint 2011/339) shows indifferentiability need not transfer to storage
(multi-stage) games, and Mittelbach (2013/286) rescues only "unsplittable"/reset-indifferentiable games — which P3 is
not shown to be. So an *adversarially-constructed* (non-honest-path) compression is not formally ruled out; the argument
reduces the risk to "no narrow honest seed + no known multi-stage attack," which the doc labels precisely as a **named
assumption** ("checked, not proved"). Verdict: it closes the *known* narrow-state gap and is the right thing to check,
but it does **not** close the RSS gap in the sense of a proof — the strongest honest claim is the one the doc makes.

**3. No concrete attack on the recommended SHAKE-Feistel design; related-tweak and slide are structurally defeated.**
- *Related-tweak:* the tweak is an RO *input* (`0x50‖i‖T‖x`), not an algebraic key schedule, so `P_T` and `P_{T'}` for
  `T≠T'` are built from *independent* round functions — no algebraic relation survives, so related-tweak/related-key
  attacks have nothing to exploit. (This is also why the ideal-cipher abstraction is faithful for arbitrary tweaks.)
- *Slide:* each round function carries the round index (`0x50‖u8(i)‖…`), so the rounds are distinct — there is no
  self-similarity for a slide/reflection attack.
- *Feistel structure:* 10 rounds is indifferentiable (2015/874/876); 5 is distinguishable but unused. A storage
  adversary knows every round function offline, yet the Feistel is a *bijection* with no exploitable structure, so it
  cannot compress a label below its `m`-bit input — the reconstruction hardness stays the DRG/`ColumnHard` bound, and
  the concrete `P_T⁻¹` is just the Feistel inverse, matching `p3ModelT`'s reverse move (no new leverage).
- *A correctly-caught pitfall:* the doc notes a per-instance IV must go in the sponge **capacity**, not the rate (a rate
  IV gives the XOR-linearity collision `(h,c) ≈ (h', c⊕h⊕h')`); the spec places the header as a first rate *block* with
  a zero capacity IV and keeps any `IV(salt,…)` in the capacity, which avoids it. Good defensive design.
- *The ARX / 5-round Even–Mansour variant* (tweak = round key, trivial schedule) genuinely *would* invite related-key
  and slide concerns, and the doc correctly quarantines it as **heuristic** and non-recommended ("light mixers are
  distinguishable"). So the residual attack surface lives only in the option the doc already rejects.
No concrete storage attack found on the recommended design.

**Verdict (§19): the instantiation is sound and honestly scoped; it discharges the §18 "primitive exists" caveat for
the recommended SHAKE-Feistel design and correctly realizes `p3ModelT`'s ideal-cipher family, with all three cited
results verified to say what is claimed (including the keyed ideal-cipher form the tweak needs).** Related-tweak and
slide attacks are structurally defeated (RO-input tweak + per-round domain separation), and no storage adversary can
beat the DRG/`ColumnHard` bound through the Feistel. The one load-bearing residual is exactly the one the doc flags: the
**RSS multi-stage composition** step — carrying the single-stage ideal-cipher indifferentiability into P3's storage game
— is a *named assumption*, narrowed to "no narrow honest data path (established here) + no known multi-stage attack," not
a proof; and it rests on the standard SHAKE256/Keccak-f = ideal-primitive heuristic. (The enormous cost — ≈85× prefill,
≈2000× decode — is a viability, not a security, matter, explicitly workstream 2's.) So the §17/§18 narrow-state caveat
moves from "no concrete primitive specified" to "a concrete primitive that defeats the known attack and realizes the
ideal model, resting on an honestly-labelled multi-stage-composition assumption." No refutation found. Overall verdict
unchanged: **GRANTED WITH CONDITIONS** — with the concrete-hash security of every crypto result now pinned to the
Keccak-ideal-permutation heuristic plus the RSS multi-stage-composition named assumption, which the instantiation makes
explicit and argues for but does not prove.

## 20. Erratum to §18 (`n10primeMulti` is false) and review of `N10primeMultiFixed` (27 Sep 2026)

**Erratum to §18.** In §18 I judged `n10primeMulti` "true, faithful, non-vacuous, non-smuggling." **That was wrong for
the multi-segment statement — it is false as landed**, and the `p3-meets` owner is right. `n10primeMulti` (in
`TweakedDraft.lean`) keys *every* segment with **one shared** `W : Fin n → Lab n wc` and takes `tags : Fin N → Bits 256`
with **no injectivity**. So with `tags` constant and `N = 2`, both segments have identical top labels
(`topLabelT (tags s) G W ω v` is independent of `s`), and an adversary that stores one segment's 220 tops (or an `A₂`
that ignores `s`) answers *every* segment with probability 1 — against a bound of `≈ 2^{-1.7·10⁶}`. So the
universally-quantified statement has a concrete counterexample: it is false, exactly like N10. My miss is specific and
worth naming: I applied the distinctness/domain-separation lens to the *single-segment* `KQ'` salt (attack 3, §9 — "equal-`W`
segments must not dedupe") but failed to carry it *across* segments in the joint statement, even while writing that "the
statement itself is well-formed." (My §18 minor flag — that the collision set spans both layers, `2Nn` not `Nn` — was in
the right direction; the fix uses `(2Nn)²`.) The **single-segment** `n10prime` of §18 is **unaffected** (one tag, one
`W`, no cross-segment coincidence); this erratum is scoped to the multi-segment `n10primeMulti`.

**`N10primeMultiFixed` (in `p3-meets/P3MeetsT.lean`) closes the bug.** It makes exactly the two changes the
counterexample forces, both load-bearing:
- **Per-segment data** `W : Fin N → Fin n → Lab n wc` (the scheme stores different weights per segment; `topLabelT` now
  uses `W s`).
- **`Function.Injective tags`.** Distinct segments get distinct tags, hence — since the tag is the first component of the
  permutation tweak `(tag, layer, node)` — **distinct tweaks**, hence *independent* permutations per segment (the ideal
  cipher of §18/§19). So even for coincidentally-equal data the segments produce independent labels, and the "store one
  segment, win all" collapse is impossible.
With these, the joint event `JointEventT` ("≥ k tops of segment `s`, keyed by `tags s` on data `W s`, in every segment")
is a genuine `N`-fold *independent* challenge: the joint compression is `N·(k−X)` independent single-entry deletions
across the distinct-tweak segments (`sav = N·(k−X)`), and the collision term is the two-layer `(2·N·n)²/2^{n·wc}`. This
is the correct joint accounting; the fix is faithful, non-vacuous (`ColumnHard` satisfiable via the §14 band cert; bound
non-trivial), and non-smuggling (the injectivity/per-segment-data hypotheses are the real content, not a disguised
conclusion). It is now plausibly true on the same footing as the single-segment `n10prime` (§18), scaled by tweak
independence — I found no refutation of the *fixed* form. And it is **correctly instantiated**: the multi-segment scheme
`p3SchemeNT` keys segment `s` by `tagN N salt s = (salt, s)`, which is injective for `N ≤ 2^128` (`tagN_injective`,
proved, no `sorry`), and stores per-segment data via `Wseg`; `p3_meets_multiT` threads `tagN_injective` into
`N10primeMultiFixed`, so the `N = 62542` (14 GB, `k = 144`) result rests on the fixed hypothesis with genuine
distinctness, not the broken one.

**Does any other statement have the same missing-distinctness pattern? — No.** The pattern is *deterministic instances
that collapse because a distinctness/domain-separation hypothesis is missing*. I checked the three the owner named:
- **Multi-segment audits.** The only statement with `N` deterministic per-segment instances was `n10primeMulti` (now
  fixed); the multi-segment scheme `p3SchemeNT`/`p3_meets_multiT` is the sole consumer and it is correctly fixed
  (`tagN` injective + per-segment `Wseg`). Every other audit result — `SampledAudit{Prod,Seq,Sim}`, `StackedAudit{Seq,
  OnePercent}`, `b5_stacked`, `DenseMeets`, `M1Meets` — is a *single* scheme; its multiplicity is the `k` **random**
  challenges, not deterministic instances, so there is nothing to collapse.
- **The salts.** The salt is one value per audit, drawn *after* `W` (correct order, so `W` cannot be chosen to match a
  salt), and within a scheme the segments are separated by the segment index carried *inside* `tagN` (injective), not by
  the salt alone. The single-segment `KQ'` salt was already handled (attack 3). No salt can coincide across instances
  that must be distinct.
- **`Theorem1iiSeq`.** No such pattern. Its `k` challenge indices `I : Fin k → Fin B` are drawn **uniform and with
  replacement** as part of the random `Outcome` (`Model/Audit.lean`), so they are independent *by construction*; the
  bound `(∑_{j<k} B^j)·π + p₀^k` is an expectation over that randomness and correctly absorbs the (rare) coincidence of
  two challenges. Unlike `n10primeMulti`, the "instances" here are random draws, not adversary-collapsible deterministic
  segments, so no distinctness hypothesis is needed (independence, which randomness already supplies, is what the bound
  uses). With-replacement is the conservative choice and the reduction handles it. Sound.

**Verdict (§20): §18's `n10primeMulti` judgment is retracted — it is false (missing per-segment data and injective
tags), and I record the erratum. `N10primeMultiFixed` adds exactly those two hypotheses and closes the collapse; it is
faithful, non-vacuous, non-smuggling, and correctly instantiated by `p3SchemeNT` (via the proved `tagN_injective` and
per-segment `Wseg`). No other statement shares the pattern: the audits (including `Theorem1iiSeq`) draw their `k`
challenges at random, so independence is built in, and the salts are per-segment-indexed and drawn after `W`.** The
recurring lesson — now seen twice (attack-3 `KQ` salt in §9, and this cross-segment collapse) — is that any statement
quantifying over multiple instances over a *shared* primitive must carry an explicit distinctness/domain-separation
hypothesis; the pebbling prover restating `n10primeMulti` to `N10primeMultiFixed`'s shape is the right move. Overall
verdict unchanged: **GRANTED WITH CONDITIONS**, with the multi-segment N10′ statement now corrected to require distinct
tags and per-segment data.

## 22. The game-depth ↔ oracle-round conversion `(D+1)/2` undercounts the adversary (27 Sep 2026)

The reference-implementation workstream (PR #166, `cursor/pous-reference-9796`) reports that N10′'s conversion from the
adversary's oracle-round budget `D` to the column game's depth is anti-conservative. **Q1 verdict: the finding is real —
`ColumnHard G ((D+1)/2) k X` is the wrong hypothesis, and `n10prime` as stated is false for some graphs.** (Reply-fast
verdict; Q2/Q3 below.)

**Why (Q1).** `n10prime`/`n10prime_core`/`FreshnessInvariant` all assume `ColumnHard` at game depth `d = ⌊(D+1)/2⌋`,
justified by "one game round = one forward label level = 2 oracle rounds." But `colRound` bundles **four** move types in
one round — forward-lower, **promotion**, **key-gated reverse**, forward-top — and their oracle costs differ:
a forward level is 2 oracle rounds (query `H`, then `P`), but a **reverse** (`P⁻¹` on a held top whose key is ready) is
**1** oracle round and a **promotion** (all columns held ⇒ whole) is **0**. So a reverse/promotion-heavy
meet-in-the-middle strategy realizes *more* game rounds per oracle-round budget than the all-forward case the conversion
assumes. The reference's pinned witness makes it concrete: a MITM holding recovers every top in `D = 20` oracle rounds,
which is **12** `colReach` game rounds — but `n10prime` grants only `⌊21/2⌋ = 10`. So the reduction step "a winning
`(D,Q)` holding reaches `k` tops within `(D+1)/2` game rounds" is **false**: a holding that reaches `k` tops only at
depth 12 makes `ColumnHard`-at-10's antecedent vacuous, so `ColumnHard`-at-10 does not lower-bound its size, and the
`n10prime` bound does not follow. The direction of the error is the giveaway: `(D+1)/2` is the *fewest* game rounds
(all-forward); a security statement must charge the *most* the adversary can realize, which is larger. So for any graph
whose saving at the true depth exceeds `X` while its depth-`(D+1)/2` saving is `≤ X`, `n10prime` is false. `B(220,12)`
itself survives — its MITM saving is `2.29 < X = 3` even at the deeper depth, so it is not a concrete break — but the
conversion is unsound in general, and it is not certified at the depth the adversary actually reaches.

**Blast radius.** The bug is in the **untrusted** conversion, not the trusted game. It lives in `n10prime`'s
`ColumnHard G ((D+1)/2) …` (`ColumnAwareDraft.lean` L212, `TweakedDraft.lean` `gameDepth` L76), in `n10prime_core`
(`ForwardCoreDraft`), in `FreshnessInvariant` (`FreshnessStmt.lean`, same `((D+1)/2)` — so the §21 handoff inherits it),
and in the `p3-meets` chains that consume `n10prime`/`n10primeMulti` via `type_of%` (their `Meets` results are
conditional on a false hypothesis until the depth is fixed). **The trusted `ColumnGame.lean` of PR #162 is *not*
affected**: it defines only `ColState`/`colRound`/`colReach`/`ColumnHard`/`basePath`; it does not fix the depth, so no
trusted statement is wrong — the conversion is chosen where `ColumnHard` is *invoked*, all of which is untrusted/`sorry`.
So no pin changes; the fix is confined to the open N10′ target and its consumers.

**Q2 — the correct conversion.** Charge `ColumnHard` at the *largest* game depth a `(D,Q)` adversary can realize, over
the worst move-mix, not the all-forward best case.
- *With the random-oracle `H` (abstract model):* reverse = 1, promotion = 0, forward = 2 oracle rounds. Because
  promotions are free and reverse is cheap, the conservative bound is `d = D` (each oracle round advances at most one
  game round; free promotions do not stack unboundedly, since progress past already-held columns needs forward `H`/`P`
  queries). So the sound hypothesis is `ColumnHard G D k X` (or a properly-derived *timed-game* depth `≤ D`), **not**
  `(D+1)/2`. The MITM's `d = 12` at `D = 20` is a lower bound on how bad it gets; `d = D = 20` is the safe upper bound.
- *With the wide sponge `H` (§19 instantiation):* a reverse costs **≥ 14** oracle rounds (inverting through the
  sponge/Feistel is as dear as a forward wide call), and a forward ~14, so each game round costs ≥ 14 oracle rounds and
  `d ≤ D/14`; the §19 timing bound already caps the adversary at ≈ 1 wide call (≈ 1 level) at `Δ = 300 µs`. So under the
  *concrete* primitive the conversion is *favourable* — `d ≪ (D+1)/2` — and a depth-10 certificate is over-provisioned.
  The right long-term shape is to parametrise the game depth by the per-move oracle costs `(r_fwd, r_rev)` so one
  statement covers both models: RO (`r_rev = 1`) gives `d ≈ D`; the sponge (`r_rev ≥ 14`) gives `d ≈ D/14`. As written,
  N10′ silently assumes the *worst-for-it* (RO) costs while charging the *best-for-it* (all-forward) depth — the two
  errors do not cancel.

**Q3 — yes, the band certificate needs more depths.** It currently proves `ColumnHard` for `B(220,12)` at `d = 10, 11`
and `B(220,16)` at `d = 12`. For a model-agnostic (RO-safe) `n10prime` the deployed graph must be certified at the
corrected depth — conservatively `d = D = 20` — and `X` re-checked there (a deeper game reaches more, so the saving can
only grow; the MITM's `2.29` is at `d ≈ 12` for `B(220,12)` and is unproven at `d = 20`). If instead the statement is
tied to the wide-sponge costs (`d` small), the existing `d = 10–12` certificates already suffice and no new depth is
needed. So the certificate-depth requirement is contingent on which conversion N10′ adopts; if it takes the safe RO
`d = D`, re-certification at `d = 20` (with `X` possibly `> 3`) is required.

**Verdict (§22).** Real finding, adjudicated: the `(D+1)/2` game-depth conversion is anti-conservative (reverse = 1,
promotion = 0 oracle rounds, vs the assumed 2), so `n10prime` with `ColumnHard G ((D+1)/2) k X` is unsound and false for
graphs whose true-depth saving exceeds `X`; `B(220,12)` happens to survive but is uncertified at the depth it needs. Fix:
replace `(D+1)/2` with the conservative `d = D` (or a per-move timed-game depth), in `n10prime`, `n10prime_core`,
`FreshnessInvariant` and the `p3-meets` chains, and re-certify the band graph at the corrected depth. The trusted
`ColumnGame.lean` (PR #162) and all 46 pins are unaffected — the conversion is entirely in the open N10′ target.
Overall verdict unchanged: **GRANTED WITH CONDITIONS**; N10′ carries one more required correction (the depth conversion)
on top of the freshness/kernel obligations.

## 23. Correction to §19: the wide sponge is not RO-like in the storage game (`sponge-dense`, 27 Sep 2026)

§19 accepted "no data path narrows below `m`" as the argument that the recommended wide sponge closes the narrow-state
gap, while flagging the general RSS multi-stage composition as an unproven named assumption. **The pilot has now
falsified that assumption with a machine-checked lemma; I record the correction.** I verified `sponge-dense`
(`SpongeModel.lean`/`SpongeDense.lean`, on the store `lean/pous`, `TRUSTED.sha256` intact): everything is on
`[propext, Classical.choice, Quot.sound]`, no `sorry`/`axiom`/`native_decide`, and `--fresh` replays (212s).

**`dense_two_labels_from_one_state` — verified, and it is the right refutation.** For **every** permutation `π`, storing
one intermediate sponge state of `ℓ + 512` bits (row `i` after `q` calls) and dropping labels `C_i` and `C_{i−g}`, the
program `twoFromOne` recovers **both** labels in `max(g−1, q−g+1, i−q+1)` rounds — exactly `D` at `i = 3D−2, q = 2D−1,
g = D`. The mechanism (`gap_close`) is the one §19 missed: the sponge IV is **public**, so a row runs *forward* from the
IV and *backward* from the stored state via `Π⁻¹`, and the block where they meet falls out. So one wide state
regenerates two labels (`2ℓ` bits), saving `ℓ − 512` per row — a genuine storage-game compression the random-oracle
model does not see. The lemma is non-vacuous (universal in `π`, a real meet-in-the-middle, depth within budget) and
kernel-checked. **So the §19 conclusion is wrong: "no data path narrows below `m`" does *not* make the wide sponge
RO-like in the storage game.** The narrow-state attack is indeed gone (no state is narrower than a label), but
invertibility + a public IV give a *wide*-state, two-labels-from-one compression instead — precisely the adversarially
constructed, non-narrow compression my §19 verdict said the "no narrow path" argument could not rule out. §19's residual
RSS named assumption is therefore **falsified for the recommended sponge**; a feed-forward replacement (breaking the
backward-runnability) is being designed.

**The pilot model is faithful and well-built.** `SpongeModel.lean`: `idealPerm` (`Π`, `Π⁻¹`); the sponge with the
domain in the **capacity** (`iv dom = 0^r ‖ dom`), which correctly avoids the rate-IV XOR collision §19 flagged; the
dense scheme (rate 1, forward-only decoder); the **state game** (`Know`/`round`/`reach`, whose moves are forward,
backward `Π⁻¹`, and mid-gap extraction — the concrete analogue of the column game's reverse); `SpongeHard` (the pebbling
conjecture, `(B−D−1, D, B)`, exhaustively checked for small `B,D` with only tiny gains), `SpongeExPostFacto` (the B5
replacement, the real new work), and the two-permutation P3 model. `spongeDense_correct`/`spongeDenseMeets_iff` are
proved; the restated target `SpongeDenseMeets` counts `D,Q` in `Π`-calls. Certificate: `k = 119` (conjecture, 3-pointer
ex-post-facto) or `k = 200` (the crude provable bound). Round accounting (`le_levels`, `p3_level_ge_three`) shows a
sponge reverse/level costs ≥ 3 `Π`-calls, so `levels D 3 = ⌊(D−1)/3⌋+1` — which ties into §22: over the *sponge* the
depth conversion is favourable (expensive reverse), the opposite of the RO model's undercount. No indifferentiability
shortcut is used (RSS): every step is in the two-permutation model directly. **Verdict (§23): lemma verified; §19
corrected — the recommended sponge is not RO-like in the storage game (public IV + `Π⁻¹` ⇒ two-labels-from-one-state,
proven), so the concrete-security story needs the feed-forward fix plus the two new obligations (`SpongeHard`,
`SpongeExPostFacto`); the pilot model is a sound basis for that.** The same key-state compression reappears for P3
(NOTES §5: a held key-state yields the key and one whole parent), tying to the §21 key caveat below.

## 21. Freshness: `FreshnessInvariant` is refuted, and `g(D) = D` (27 Sep 2026)

Per the coordinator's redirect, I treat §21 as **confirming** the Lean refutation of `FreshnessInvariant` (the §21
handoff statement I began reviewing), and I adjudicate the `g(D)` follow-up to §22.

**The refutation is correct, machine-checked, and robust to the §22 depth fix.** `freshness/Refutation.lean` proves
`¬ FreshnessInvariant` — and, stronger, `not_freshnessInvariantAt gd` for **every** depth conversion `gd : ℕ → ℕ`
(`freshnessInvariant_eq : FreshnessInvariant = FreshnessInvariantAt gameDepth` by `rfl`), all on the three standard
axioms, Verity audit PASS (`--fresh` 219s). So the flaw is deeper than §22's depth bug: it survives any `g(D)`. The
counterexample is a path graph on `n = d+1` nodes, `wc = 2`, one segment, `k = n`, `X = d` (so `k−X = 1`), `D = Q = 1`;
`columnHard_path` proves `ColumnHard (path) d n d`. Two adversaries refute "untouched" on *every* winning non-colliding
`ω` — and both of the suspicions I was asked to check in §21 are exactly the witnesses: `advFwd` stores the top **inputs**
(lower columns + keys) and queries `P_t` **forward** at each honest input (touches every forward entry); `advInv` stores
every `c²_u` whole and queries `P_t⁻¹(c²_u)` (touches every inverse entry) — so "count stored lower columns" alone does
not rescue it, and the lucky-guess variant is subsumed (the statement quantifies over all such `ω`). So
`FreshnessInvariant` is **false**: "the honest entry is untouched, forward or inverse" is neither necessary nor
achievable — a correct adversary must query the entry to answer it. My in-progress §21 review is superseded by this
refutation, which I confirm.

**The restatement direction is right; one red-team point to hold for it.** The proposed fix (freshness `NOTES.md`)
replaces "untouched" with: build an ex-post-facto `ColState` counting **every** held unit (lower wholes, columns, tops),
a unit being "in `c0`" when its value appears in the trace **before** its honest `P`-entry is queried forward at its
honest input; make it relative to a `Guess` event bounded by a union `≲ N·Q_tot / 2^{n·wc}`; and require, decoder-side,
that **a deleted entry is never queried forward at its input before its output has appeared** (an inverse query at a
deleted top's output is allowed — it is the key-gated reverse). This is sound in shape and matches the §16/§18 kernel.
The load-bearing thing to verify when it lands (the prover flags it too): **a reverse move must never need data that is
itself deleted** — i.e. the columns a reverse reveals are derived, not held, so they are not among the deleted units.

**`g(D) = D` — the freshness prover is right; my §22 conservative `d = D` is tight, not `2D`.** The `2:1` worry
(alternating reverse → promotion) provably fails, for exactly the reason the prover gives and I derived independently:
**promotion produces whole lowers, never new reversible tops**, so a reverse after a promotion has no new top to reverse
— "reverse → promotion → reverse" is not a chain. Every new whole top needs a forward-top (≥ 1 oracle round), and the
DAG dependency forces one oracle round per top level on the critical path, so tops reachable in `D` oracle rounds are in
`colReach c0 D`. Promotion is the only sub-unit-cost move (0 oracle rounds, 1 game round), and its output never advances
a top for free (a forward-top uses the promoted label's *columns*, which were already in `lowerCol` since promotion
needs all of them; its only new consumer is a child's forward-lower at 2 oracle rounds). This is now **half-proved in
Lean**: `PousTimedGame.timedReach` charges each move its true oracle cost and `topWhole_timedReach_sub`
(`(timedReach G c0 D).topWhole ⊆ (colReach G c0 D).topWhole`) *is* `g(D) = D`, with `columnHard_timed` pricing it and
`timedReach_not_half` formalizing my §22 point (on `0→1`, top `1` is timed at round 4 but absent from `colReach` at
`(4+1)/2 = 2`). So the answer to the follow-up: **the maximal realizable depth is `g(D) = D`** (one game round per
oracle round; tight, witnessed by the 4-round "reverse, promotion, child-forward-lower, forward-top, reverse" cycle),
**not `≈ 2D`.** So §22's fix stands with `d = D` (re-certify the band graph at `d = D`, not `2D`).

**One open caveat I must surface (it crosses §21/§22/§23): `ColState` has no keys.** The timed→column simulation's model
half is still open, and it has a real gap: if the stored state `σ` holds a **key** `k²_u = H(1,u,par)`, the adversary
computes `c²_u` without the parents' tops and reverses at `u` **without the key gate** — which the column game does not
model (its reverse is gated by `par u ⊆ topWhole`). The simulation therefore needs either keys as held units of cost `n`
(they are predicted `H`-outputs, deletable from `H`), or a domination lemma (a held key ≤ the top `u` or its columns at
the same cost). This is the same held-key-state compression that §23's sponge finding exhibits concretely (a key-state
yields the key **and** a whole parent). Until it is priced or dominated, the g(D)=D simulation and the freshness
restatement are not complete. **Verdict (§21): the refutation of `FreshnessInvariant` is confirmed (false at every
depth); `g(D) = D` is correct and half-proved; the restatement's shape is sound; the load-bearing open items are the
run-to-knowledge simulation, the "reverse never needs deleted data" property, and pricing held keys in the column
game.** Overall verdict unchanged: **GRANTED WITH CONDITIONS** — the trusted layer stands; the open N10′ path now
carries the depth-conversion fix (§22, `d=D`), the freshness restatement (`FreshnessInvariant` withdrawn), the
key-pricing gap, and — for concrete security — the sponge feed-forward fix (§23).

## 24. The overwrite-chain H (feed-forward fix): I tried to break it in the storage game; it holds (27 Sep 2026)

The §23 break (sponge is not RO-like: public IV + `Π⁻¹` regenerate two labels from one wide state) is answered by a new
`H` in `docs/p3-instantiation.md`: an **overwrite chain** `(r_j, h_j) = Π₂(B_j ‖ h_{j−1})` on a double-width
(`2m+512`-bit) Feistel-SHAKE256 `Π₂`, keeping `h_j` (`m+512` bits) and **dropping** `r_j` (`m` bits); the key is the
dropped rate of the pad call. I red-teamed it along the four vectors asked, and checked the freshness enumeration. **I
found no break: the design is sound, for the reason the designer gives.**

**1. Stored `h_j` — one label only.** `h_j` (`m+512`) drives the chain *forward* (with the remaining older parents) to
this row's key = one label. It reveals no absorbed parent: recovering `B_j` or `h_{j−1}` from `h_j` needs either a
forward query on the unknown `B_j`, or `Π₂⁻¹` on `(r_j ‖ h_j)` with the **dropped** `r_j` — and `h_j` does not determine
`r_j` (for a permutation, the `m+512`-bit suffix leaves `2^m` possible outputs, each with a distinct preimage). So the
backward walk that broke the sponge is blocked; `h_j` yields exactly its own row's key, `≤ Q·2^{-m}` otherwise. Not a
break.

**2. Stored Feistel half-states — a masked parent needing the prefix, dominated.** The input `B_j ‖ h_{j−1}` splits into
halves of `m+256`; the first half `L_0 = B_j ‖ (256 bits of h_{j−1})` carries the parent `B_j` linearly. But to advance
or invert a Feistel you need *both* halves, and the other half is part of `h_{j−1}` (the prefix, from the newer
parents). So a stored half (`m+256`) reveals `B_j` (`m` bits) only if you already recomputed the prefix — no shortcut,
and it is dominated (store `B_j` directly for `m < m+256` bits). It does not also hand you the row's key for free (that
needs both halves, the rest of the Feistel, and the older parents). Worth ≤ 1 label. Not a break.

**3. `Π₂⁻¹` queries — need the dropped `r_j`.** To invert a real chain entry you must query `Π₂⁻¹(r_j ‖ h_j)`, which
needs the dropped `r_j`: either **stored** (`m` bits — but then `r_j ‖ h_j` is the whole `2m+512`-bit call state,
yielding `B_j` + this row's key = two labels for a `>2`-label cost, **dominated**), or **guessed** (`2^{-m}` per query,
`≤ Q·2^{-m}` total, negligible). Either way no compression. This is the momentarily-tempting path (m-bit `r_j` → parent
+ row) and it resolves cleanly: `h_j + r_j` *is* the whole call state. Not a break.

**4. Anything linear in a parent — the parent is a separate `m`-bit input, so parent-revealing checkpoints are `≥ 2`
labels.** This is the precise fix over Miyaguchi–Preneel. In MP the checkpoint (`x_j = s_{j−1} ⊕ (B_j‖0)`, `m+512` bits)
is an equation in `B_j` *and* finishes the row — worth two labels at one-label cost. The overwrite chain feeds the
parent as a **separate** `m`-bit input on a **wider** permutation, so every parent-revealing checkpoint (a whole call
input/output/Feistel state) is `2m+512` bits — worth exactly two labels, hence dominated. The only intermediates linear
in a parent are the half-states (handled in 2). Design goals (i) "no checkpoint below two labels reveals an absorbed
parent" and (ii) "no value linear in a parent is a checkpoint" are met.

**Freshness claim (a)/(b)/(c) is exhaustive.** A label `c_v` is a `P_T` output and the key is a `Π₂` output (a dropped
rate, fed to no later call); a permutation output is learned only by (a) the forward final/`P_T` call, (b) a `Π₂⁻¹`
answer whose query carries the dropped `r_j` (charged `m` bits stored, i.e. the dominated whole-state case, or `2^{-m}`
guessed), or (c) prediction/storage. I could construct no fourth path. So the ex-post-facto charge is back to ~one label
per recovered label (the B5-like freshness the sponge lost). The designer's state game corroborates: I checked
`internal/p3-instantiation/overwrite-state-game.log` — for the overwrite mode the *only* item worth two labels is the
`full` call state (2.06 labels, "dominated"), while the sponge and MP have 1.06-label items worth two; and at larger `D`
no mode has any (the geometry runs out).

**Verdict (§24): the overwrite chain resists all four vectors and the freshness enumeration is exhaustive — I found no
storage-game break.** It correctly fixes §23: dropping `r_j` blocks the backward walk/gap-close, and separating the
parent as an `m`-bit input on a double-width `Π₂` forces every parent-revealing checkpoint to `2m+512` bits (≥ two
labels, dominated). Caveats, all honest and flagged: this is a design + state-game + analysis review, **not
machine-checked** — the Lean obligation is the ex-post-facto (B5-analogue, the `SpongeExPostFacto`-style lemma) re-proved
for the overwrite mode with the (a)/(b)/(c) freshness, plus the standing `Π₂ = ideal-permutation` (Feistel-SHAKE)
heuristic (§19); and the cost roughly doubles the sponge's (double-width `Π₂`: ≈150× prefill, ≈3800× decode — a
viability, not security, matter). Overall verdict unchanged: **GRANTED WITH CONDITIONS** — the concrete-`H` storage-game
gap of §23 is closed in design by the overwrite chain (no break found), pending the machine-checked ex-post-facto proof.

## 25. `ChainHard` (proved) and `ChainExPostFacto` (stated): the dense scheme's concrete-H obligation structurally sidesteps both the §26 over-crediting and §27 rewind-and-solve traps (27 Sep 2026)

Review of `sponge-dense/SpongeModel.lean` (sha `7e7b2cb7`) / `SpongeDense.lean` (sha `a5032ce0`): the overwrite-chain
`ChainKnow` game, `ChainHard`, and the stated `ChainExPostFacto`. This matters more now because
`docs/scheme-choice-e2e.md` recommends the **dense scheme over the overwrite chain** as the workstream-1 secure-first
scheme (64 KB labels, `B = 512`, `D = 5`, `k = 106`), and `ChainExPostFacto` is its concrete-`H` proof obligation — the
one the memo calls "in progress, no open research step," in contrast to P3's core which "ends at an open conjecture
(DGO19)." So I read it specifically through the §26–§27 lens. **Verdict: `ChainHard` is true, faithful, correctly priced
and non-vacuous — it is proved (`chainDense_hard`), and I re-verified it on the standard axioms on my own VM.
`ChainExPostFacto` is a faithful, correctly-shaped, non-vacuous *stated* target (not proved), and — the point that makes
the dense scheme tractable — it structurally avoids both traps that block P3: the overwrite chain's concatenation gives
syntactic B5 freshness (no §26 over-crediting), and one-way labels make the decode a B5 replay, not a §27
rewind-and-solve (no DGO19). Nothing is false. The remaining work is the ex-post-facto proof itself (a real but
B5-patterned effort) and the standing `Π₂ = ideal-permutation` heuristic.**

**Independent build + axiom check (my VM).** My `scratch5/pous` was stale (it predates `Pous/Model/Dense.lean`, which
`SpongeDense.lean` uses via `Dense.blocks`/`Dense.completeDAG`), so I rebuilt a fresh `pous` from the store
(`~/scratch6-pous`, TRUSTED verifies, Mathlib cache reused), compiled `SpongeDense.lean` against it, and ran
`#print axioms`:

- `chainDense_hard`, `chain_invariant`, `chainHard_of_pebblingHard`, `complete_hard'`,
  `dense_two_labels_from_one_state` — all `[propext, Classical.choice, Quot.sound]`.
- `ChainExPostFacto`, `ChainDenseMeets`, `SpongeDenseMeets`, `SpongeHard`, `SpongeExPostFacto` — all *stated* `Prop`s,
  **no** theorem discharges any of them (grep confirms; `ChainExPostFacto : Prop` type-checks, no proof term).

No `sorry`, no `native_decide`, no `axiom` in either file. Store copy untouched (`SpongeDense.lean` still `a5032ce0`).

**`ChainHard` — faithful, and the pricing is right.** `ChainKnow.round` (`SpongeModel.lean` §10) grows the holding by
exactly three moves: **forward** (a call whose block and previous chaining value are known yields its `(r, h)`),
**inverse** (a call whose *whole* output `(r, h)` is known is inverted, yielding its block and the *previous* chaining
value), and **read** (a pad-call `r` is the key, so its label is `key ⊕ W`, `W` free). This matches the designer's
"three ways to learn a label" precisely. The decisive detail versus the sponge: `rs` (dropped-`r`s) is grown **only by
`canCall` (forward)** — never by inversion — so to invert a call you must have *stored* its `r` (priced 1), or have made
it forward (which needs the block = the label already). That is exactly the overwrite chain's fix: dropping `r` blocks
the free backward walk that broke the sponge (`dense_two_labels_from_one_state`, which I confirmed is a real Lean witness
for the sponge). Pricing (`ChainKnow.size`): a label or a dropped `r` costs 1 (both `ℓ` bits), a chaining value `h`
costs `1 + c/ℓ` (it is `ℓ + c` bits), and the public IV `h_{v,0}` is free (`p.2 ≠ 0` filter). That is bit-faithful. The
reduction `chainHard_of_pebblingHard` maps a holding to its `seeds` (labels; rows of held chaining values; blocks of held
`r`s) with `card_seeds_le_size : |seeds| ≤ size` (conservative — a chaining value gives one seed but is priced `1 + c/ℓ ≥
1`), and `chain_invariant` (a genuine four-part mutual induction, machine-checked) proves the chain game's reachable
labels ⊆ B5's pebbling reach of the seeds. So `ChainHard G VC c ℓ s D k` follows from `PebblingHard`, and
`chainDense_hard` instantiates it to `(B − D − 1, D, B)`-hard on the complete DAG via the proved `complete_hard'` — the
exact hardness the random-oracle certificate used. **Non-vacuous, faithful, correctly priced, proved.** The §26–§27
worry — a game move that is free in-game but unrealizable for the decoder — does **not** apply here: the only reverse
move is priced (stored `r`), so `ChainHard`'s power is honestly costed. (As with any hardness *hypothesis*, that the game
*over*-approximates the real `Π₂`-adversary — so game-hard ⇒ real-hard — is the burden of the ex-post-facto proof below,
corroborated but not replaced by the `state_game_chain.py` search, which finds no sub-two-label item worth two on dense
or band rows.)

**`ChainExPostFacto` — faithful, right shape, non-vacuous, and it dodges both traps.** The win condition is the storage
game: an `m`-bit preprocessor `A₁` and `(D, Q)`-bounded online `A₂` answer `k` of the `B` labels `labelOv π dom Wb`
correctly. The bound is `2^m · 2 · (nPos² · B · 2)^{s+1} / 2^{ℓ·s} + nPos²/2^{2ℓ+c}` — the B5 shape: `2^m` for
preprocessing, `2^{ℓ·s}` saving from `s` stored labels, `(nPos² · B · 2)^{s+1}` for naming each of `≤ s+1` fresh items
by two positions and a row, and a `Π₂`-collision term at the full `2ℓ+c` width. **[Erratum, corrected in §35: this
collision-width validation is WRONG. The pad-call's block is the fixed constant `padBlk`, so two rows' real points
coincide when their `(ℓ+c)`-bit chaining values do — width `ℓ+c`, not `2ℓ+c`. The stated `nPos²/2^{2ℓ+c}` is too small by
`2^ℓ` and the statement is false as stated; the amended term is `nPos²/2^{ℓ+c}`. See §35.]** It is **not vacuous**: `ChainHard` is
satisfiable (`chainDense_hard`), and at the pinned regime the exponent gap `ℓ·s − m` is large (`≈ (1/19)ℓB − ℓ(D+1) > 0`
for `B > 19(D+1)`, easily met) and dwarfs the `(s+1)·log(nPos²·B·2) ≈ (s+1)·89`-bit naming cost, so the bound is
meaningfully below `2^{-128}` for the certified `k` (`certificate.py`: 111 with a row name, 106 without). Now the two
lessons:
- **§26 (over-crediting): structurally avoided.** In the sponge, a label absorbed mid-row appears only XOR-masked by a
  chaining state that depends on newer labels, so resampling at a predicted call can *move the mask* — the exact
  over-crediting hazard `cred`/`cred2` had to guard against. The overwrite chain's queries are **concatenations**
  (`B_j ‖ h_{j−1}`), so a query shows its parent label and chaining value in **clear slots**, and an inverse shows `r`
  in the clear. Freshness is therefore B5's syntactic notion ("a `Π₂`-answer part equal to an earlier clear value"),
  well-defined per position with no circular dependency. There is no `cred`-style credit-vs-derive ambiguity to get
  wrong.
- **§27 (rewind-and-solve / DGO19): not needed.** The dense labels are **one-way** — there is no `P⁻¹` on a label; the
  only inverse is `Π₂⁻¹`, which needs a stored `r`. So the decoder replays forward from the IV plus its stored items in
  dependency order and answers each `Π₂⁻¹` query from data it already holds — a B5 replay, not the §27 bounded-fibre
  `ConsistentBound`. The DGO19 circularity that forced P3 into rewind-and-solve (`Probe.lean`, §27) simply does not
  arise. This is precisely why the memo can claim the dense proof "has no open research step" while P3's ends at the
  DGO19 conjecture.

**Caveats (all honest, none fatal).** (1) `ChainExPostFacto` is **stated, not proved** — the actual B5-for-a-permutation
argument (two-part `(r, h)` answers, inverse queries compared against an earlier answer's `h`, resampling a permutation
at a fresh point `≤ 2^c/(2^{ℓ+c} − nPos)`, and the collision term) is the real remaining work and *is* the concrete-`H`
obligation the memo bets on. It is mechanical relative to the open P3 conjecture, but it is not yet machine-checked, so
it should not be treated as done. (2) The faithfulness of `ChainKnow` as an over-approximation of the real
`Π₂`-adversary is discharged only when that proof lands; today it rests on the design argument plus the Python search,
which is evidence, not proof. (3) Tightness knobs, not soundness: `s+1` named items against an `ℓ·s` saving (a
one-label conservative slack) and the "two positions + a row" naming (the 111-vs-106 gap). (4) The standing heuristic
`Π₂ = ideal permutation` (Feistel-SHAKE, §19/§24) and the timing/isolation assumptions of `scheme-choice-e2e.md` remain
outside Lean.

**Verdict (§25): `ChainHard` is true, faithful, correctly priced and non-vacuous (proved, re-verified on standard
axioms); `ChainExPostFacto` is a faithful, correctly-shaped, non-vacuous stated target whose design — concatenation
freshness and one-way labels — structurally sidesteps both the §26 over-crediting and §27 rewind-and-solve/DGO19 traps.
Nothing is false.** The dense-over-overwrite-chain scheme is therefore in a materially stronger proof position than P3's
core: its one open Lean obligation (`ChainExPostFacto`) is a B5-pattern ex-post-facto with no circular decode, versus
P3's `DecodeHyp3` whose fibre bound is the open DGO19 conjecture (§28). The conditions to close it: prove
`ChainExPostFacto` (the permutation B5 with two-part answers and the collision term), and keep the `Π₂`-ideality
heuristic honest. Overall verdict unchanged: **GRANTED WITH CONDITIONS** — the trusted layer stands, and if the
end-to-end build switches to the dense scheme, its concrete-`H` security reduces to this one clean, trap-free, still-open
lemma rather than to P3's open conjecture.

## 26. `KnowledgeSim` (adversary→game simulation): sound game-side, but the qI2/DGO19 decode is the real open piece (27 Sep 2026)

Priority review of `freshness/KnowledgeSim.lean` (sha `67e6c3a2`, statements only — the prover is starting the proof).
It is the adversary→game simulation the P3 core needs. **Verdict: nothing in the statement is outright false, and the
game-side credit rules are sound — but the claim that this is "the last big piece" is premature: the load-bearing
`qI2`/DGO19 decode recoverability is a genuine, unresolved circularity that `KnowledgeSim` does not close.** (Fast reply
per the priority; a prover is on it.)

**Good, and confirmed sound (game-side).** The keyed timed game now prices **keys** (`Keyed.lean`: `KState = ColState +
lowerKey + topKey`, `KState.size` charging `n` per held key), which closes the §21 caveat that `ColState` had no keys;
`columnHard_timedK` is proved. `KnowledgeSim` says `know t ⊆ timedReachK (cred D) t` and every correct answer is in
`timedReachK (cred D) D`, so with `columnHard_timedK` a `≥k`-answer win forces `(cred D).size ≥ (k−X)·n`. The credit
rules read the trace correctly: each fresh use credits the right unit (an `H`-parent, a `P⁻¹` label, `k¹` at `qP1`, the
missing columns/key at `qP2`, or a final answer). **The "no guess event" design is right.** My earlier proposal to send
the "neither `x²_u` nor `k²_u` known" case to a bounded guess event is correctly rejected: `XorNeitherUnbounded` shows
`pr(XorNeither) = 1` for the `advFwd` adversary (which stores the honest top *inputs*), so a guess bound would be
vacuous; crediting **top `u`** instead is sound in the game (a held top input `x²_u ⊕ k²_u` forward-yields the top at the
same one-label cost, so it is dominated by the held top). So the statement needs no guess event — a genuine improvement.

**The crux — a top credited through `qI2 u` (inverse), and DGO19 — is not resolved, and is genuinely circular under the
query order.** `cred`'s `topWhole` credits `u` when `qI2 u` (`P_{(τ,1,u)}⁻¹(c²_u)`) is first asked before the forward
`qP2 u`. For the compression this credited entry `(x²_u ⊕ k²_u ↦ c²_u)` must be *deleted* and *recovered on replay*: when
the adversary issues `qI2 u`, the decoder must return the input `x²_u ⊕ k²_u = transpose(c¹)_u ⊕ H(1,u,·)`. But the
adversary inverts **precisely because it lacks column `u` (`x²_u`)** — obtaining it is the point of the inverse — and
forward-computing `x²_u` is DRG-deep (the hardness the scheme rests on). So at the `qI2 u` moment the decoder cannot
recompute the answer without the very column the inverse supplies: the classic ideal-permutation-inversion circularity
(DGO19 / Garg–Lu–Waters, Moran–Wichs). `KnowledgeSim` **abstracts this away** — in `timedReachK` the key-gated reverse of
a held top to its column is a free game move — so proving `KnowledgeSim` does *not* establish that the `qI2` credit is
recoverable as a deletion. The prover flags exactly this ("Load-bearing (DGO19)… needs `x²_u ⊕ k²_u` computable when
that query is made", explicitly "not part of this statement"), so it is known-open; my role is to confirm it is real and
load-bearing, which it is. A resolution likely needs a **topological / sequence-then-switch decode** (not the adversary's
query order), exploiting the §18 acyclicity ("inverting `c²_j` yields only column `j`; forward-computing `c²_i` needs
column `i`", so the dependency graph is acyclic) — but that reordering argument is the hard, unproven core, and it is the
piece `KnowledgeSim` leaves out.

**Verdict (§26): `KnowledgeSim` is a sound game-side statement (credit rules sound, keys now priced, no-guess-event
design correct, plausibly provable), but it is not the last big piece of the P3 core — the `qI2`/DGO19 decode
recoverability is a separate, load-bearing, unresolved circularity, and the credits are not yet shown recoverable as
deletions.** So proving `KnowledgeSim` should not be treated as closing the core; the DGO19 decode (a topological
sequence-then-switch that supplies each inverse answer from data available in dependency order, without the column the
inverse shortcuts) is the remaining obstacle — the same circularity that killed the shared-`P` N10 (§11C) and that the
tweakable-`P` single-entry deletion (§18) was meant to sidestep, now localized to exactly the `qI2`-credited tops.
Nothing false to withdraw; the caution is against declaring the core finished. Overall verdict unchanged: **GRANTED WITH
CONDITIONS.**

## 27. `KnowledgeSim2` / `cred′`: the §26 over-credit is Lean-confirmed and fixed; nothing false, the decode is cleanly deferred (27 Sep 2026)

Priority review of `freshness/KnowledgeSim2.lean` (sha `5f7a0503`, statements only) with its proof file
`KnowledgeSim2Proof.lean` (sha `7a29f814`) and the Lean-checked over-credit instance `Probe.lean` (sha `4a6d76f5`). This
is the game-relative replacement for §26's `cred`. **Verdict: nothing is false. `cred′` (`cred2`) correctly removes the
over-crediting §26 flagged — the concrete flaw is now machine-confirmed for the old `cred` and machine-fixed for the new
one — `KnowledgeSim2` is proved and faithful, and `ConsistentBound`/`ConsistentCompression` have the right shape and are
not vacuous. This is real progress: the DGO19 decode is no longer hidden inside a "recover the credits" hand-wave but
localized to one stated, still-open hypothesis (`ConsistentBound`). It is not yet the finished core.** (Fast reply per
the priority; a prover is on it.)

**Independent build (my VM, not the prover's artifact).** I assembled the `Freshness` package against my own built
`pous` (scratch `~/freshverify`, Lean v4.34.0, Mathlib 5ed2965), compiled the five exempt `Pebbling` drafts and all nine
freshness modules, and ran `#print axioms` myself. The drafts **do** carry `sorry` (`ColumnAwareDraft`,
`ForwardCoreDraft`, `TweakedDraft` — the pebbling prover's WIP, audited in their own submissions), so the load-bearing
check is whether the freshness theorems inherit them. They do not:

- `PousKnowledge.knowledgeSim2` — `[propext, Classical.choice, Quot.sound]`
- `PousKnowledge.probeCredOne` — `[propext, Classical.choice, Quot.sound]`
- `PousKnowledge.consistentCompression` — `[propext, Classical.choice, Quot.sound]`
- (and `overcredit`, `knowledgeSim`, `xorNeitherUnbounded`, `askedAll` — same three)

No `sorryAx`, no `native_decide`, no extra axioms. So the three §27 theorems are genuinely established and do not lean on
the drafts' holes. (The prover's own audit corroborates: `AUDIT … PASS`, 19 pinned theorems, `--fresh` replay 207.6 s.)
The store copy is untouched (`KnowledgeSim2.lean` still `5f7a0503`); I only read it and copied it into scratch.

**1. `cred′` no longer over-credits — checked on every family asked, and machine-confirmed on the Probe witness.** The
fix is structural: `roundCred C r` credits round by round, and every credit is guarded by *non-availability in the keyed
timed game of the earlier credits* `Γ = timedReachK G C (r−1)` — `¬ avail Γ` for a lower column, `∉ Γ.topWhole` for a
top, `∉ Γ.lowerWhole` for a lower label, `¬ keyTop`/`¬ keyLow` for a key. A unit the game already derives from what was
credited before is never re-credited. Case by case:
- **Redundant forward queries.** A credit fires only on `FirstAt` (the round a query is *first* asked), so a repeat is
  inert; and even the first `qP1 w`/`qP2 u` is gated by `w ∉ Γ.lowerWhole` / `u ∉ Γ.topWhole`. No credit.
- **Key queries after inverses** (the Probe / §26 cycle: invert `c²_u`, extract `k²_u` from the columns, then re-query
  `qP2 u` to "use" the key). Once `qI2 u` has credited top `u`, `u ∈ Γ.topWhole`, so the later `qP2 u` matches none of
  the three `qP2` branches (`topKey` needs `u ∉ Γ.topWhole ∧ ∀w avail`; `topWhole` needs `u ∉ Γ.topWhole`; the
  missing-columns `lowerCol` branch needs `keyTop ∧ ¬avail`). The key is not double-credited.
- **XOR uses.** A `qP2 u` credits **exactly one** unit-type, selected by `(keyTop?, all-columns-available?)`:
  missing-columns if the key is there but columns are not; the key `k²_u` if columns are there but the key is not; top
  `u` if neither. The three guards are mutually exclusive, so no `qP2` is charged twice.
- **`qH1`/`qH2` parent uses.** A hash query credits the used parent's not-yet-in-game columns / top, guarded by
  `¬ avail` / `∉ Γ.topWhole`; a credited column is thereafter in the game (held `lowerCol` is reachable), so it is not
  re-credited in a later round.

The decisive evidence is `probeCredOne` (proved): on the exact instance where §26/`Probe.lean` showed the **old** `cred`
credits **two** labels from a one-label `σ` (`overcredit`, also machine-checked here), `cred2 … 2` has size **1**. The
proof `probe_R2` is the fix in action — at round 2 the lower column of `c¹_0` is already in `timedReachK` from the held
top `0` (`rev_mem`/`lower_in_game_top`), so it is not credited. So the credit set is not merely smaller; it is *tight*
against `|σ|` on the witness. That tightness is also the anti-vacuity guarantee for point 2 (below): `cred2` is not
inflated to make the inclusion cheap.

**2. `KnowledgeSim2` is true (proved) and faithful.** The statement quantifies universally over every adversary program
family `ps` and every `ω` (no existential smuggling): for `t ≤ D`, `know t ⊆ timedReachK G (cred2 D) t`, and every
correctly answered top (`(ps u).run answer = c2 u`) is in `(timedReachK G (cred2 D) D).topWhole`. The proof
`knowledgeSim2_know` is a clean case split at each unit's first round using game-monotonicity in the holding
(`timedReachK_mono_hold`) and credit-monotonicity in the round (`credUpTo_mono`); `knowledgeSim2_answered` credits any
correct answer not already in the game as a held top (the `cred2` extra term), so in-head-derived answers are covered
too. With `columnHard_timedK` this still yields `(cred2 D).size ≥ (k−X)·n` on a `≥k`-answer win — the size bound is
preserved, now against the tighter `cred2`. Faithfulness caveat (unchanged from §26, and the honest one): `KnowledgeSim2`
proves an *inclusion into the game*, and the game `timedReachK` grants the key-gated reverse and promotion "for free."
That is sound **as a knowledge statement**; its force as a *storage* bound still depends on those free game moves being
realizable by a decoder. `KnowledgeSim2` does not close that — but, unlike §26 where it was implicit, the gap is now
named and pushed into a single hypothesis (point 3), which is the improvement.

**3. `ConsistentBound` / `ConsistentCompression`: right shape, not vacuous, and they correctly relocate all the remaining
difficulty into one place.** `ConsistentCompression` is *proved* (`consistentCompression`, standard axioms): it is the
pure fibering count — partition the winners by `(A₁ ω, R ω, pat ω)`, bound each fibre by `2^b` (the `ConsistentBound`
hypothesis), and multiply by the `≤ 2^m · |Red| · |Pat|` cells. I read the proof; it is exactly
`card_eq_sum_card_fiberwise` → `sum_le_sum` → `sum_const`, and the `2^m` comes honestly from `card (Bits m)`. Correct and
not vacuous **as a lemma** — but note it carries **no** cryptographic content by itself: it holds for *any*
`A₁, R, pat, Win, b`. All the security now lives in eventually *proving* `ConsistentBound` for the concrete instance
(`A₁ = σ`, `Red =` undeleted tables, `pat = cred2`, `b =` hint index). Its shape is right: with the decode worker's
`|Red| ≈ |Ω| / 2^{(credited units)·wc}`, `ConsistentCompression` gives `2^{cred·wc} ≲ 2^m · |Pat| · 2^b`, i.e.
`cred·wc ≲ m + log|Pat| + b`, which — against `cred.size ≥ (k−X)·n` — is the storage lower bound. `ConsistentBound`
itself is a genuinely strong (not vacuous) hypothesis: at most `2^b` winning `ω` share a given `(σ, R ω, pat ω)`. It is
the formal content of the **rewind-and-solve** decode (`freshness/NOTES.md`, "Probe" §): the paper witness (path `0→1`,
`σ = {c²_1, s}`) shows that after `cred′` **no dependency-order replay** recovers both credited tops — the round-1 answer
needs `k²_1 = H(τ,1,1,c²_0)` and `c²_0`'s only use is built from that answer — but a decoder that runs `A₂` on a dummy,
reads the slot, and *solves* `x ⊕ H(τ,1,1,x) = s ⊕ transpose(c¹)_1` against the `H` table recovers the true `c²_0`, with
a `log #solutions`-bit hint. `ConsistentBound` is exactly "that fibre is `≤ 2^b`." This is the right move: it converts
the DGO19 replay circularity (§26, §11C — "you can't replay an inverse answer you needed the inverse to learn") into a
*counting* obligation (bounded solution multiplicity), which is not obviously circular. Whether it discharges — whether
`b` is genuinely small for a concrete `R` — is the open work, and the prover correctly defers it to `internal/p3-decode/`
(a concrete `R`, and `ConsistentBound` for it with `pat = cred2`).

**Verdict (§27): nothing false. `cred′` fixes the §26 over-credit — machine-confirmed (`overcredit` for the old `cred`,
`probeCredOne` for the new), and checked sound on redundant forwards, key-after-inverse, XOR and parent uses;
`KnowledgeSim2` is proved on the standard axioms and faithful (non-vacuous, `cred2` shown tight on the Probe witness);
`ConsistentCompression` is a correct, non-vacuous, proved counting step, and `ConsistentBound` is the right-shaped,
load-bearing, still-open hypothesis that now carries the whole decode.** So the §26 concern is resolved at the level it
can be: the over-credit is gone, and the DGO19 obstacle is no longer hidden — it is a single named hypothesis whose
discharge (a small-fibre rewind-and-solve decode) is the remaining real work. `KnowledgeSim2` is *not* the finished core;
`ConsistentBound` for a concrete `R` is. But this is a genuine, checkable step forward, not a blocking finding. Overall
verdict unchanged: **GRANTED WITH CONDITIONS** — the trusted layer stands; the open N10′ path now carries the
depth-conversion fix (§22, `d=D`), the freshness restatement (`FreshnessInvariant` withdrawn, §21), the concrete-`H`
overwrite-chain ex-post-facto proof (§23/§24), and — as the successor to §26's DGO19 item — the decode's `ConsistentBound`
fibre bound (§27).

## 28. `DecodeHyp3`/`DecodeHypMulti3`: the whole N10′ core now rests on one named hypothesis; it is plausible and not vacuous, but `pos = 3n` is tight and the fibre `b` is the real open work (27 Sep 2026)

Top-priority review of `freshness/AssemblyHyp.lean` (sha `e84c45a8`) and `freshness/Assembly.lean` (sha `247db254`), with
the collision bound `pebbling/LabelBirthday.lean` (sha `bdb8403b`). N10′ (`PousTweaked.n10prime`, `…Multi`) is a `sorry`
target in the draft; `Assembly.n10prime_of_decode : DecodeHyp3 → type_of% @PousTweaked.n10prime` proves the *exact*
statement from a single named hypothesis. **Verdict: the assembly is sound and machine-checked — the reduction from
`DecodeHyp3` to `n10prime` has no `sorry` and uses only the three standard axioms — and `DecodeHyp3` is plausibly true,
not vacuous, and not trivially satisfiable. Two honest caveats: `pos = 3n` is *tight* (I found a same-round `qI2 + qP2`
pattern that credits a top as both a whole label and a key, threatening `4n`; the decode can likely still hit `3n` by
choosing which units to delete, but that per-entry accounting is unproven and owned by the decode worker), and the
load-bearing content is the `ConsistentBound` fibre `b`, which the `HintT` bridge does *not* establish. Nothing is false;
the danger to guard against is exactly the N10 one — declaring `DecodeHyp3` discharged before the fibre and the `3n`
accounting are proved.**

**Independent build + axiom check (my VM).** I extended my `~/freshverify` build with the four remaining modules
(`HintCard.PartialOutput`, `Pebbling.HconstrTweaked`, `Pebbling.HintCardStmt`, `Pebbling.LabelBirthday`) and the two
freshness files, compiled everything against my own `pous`, and ran `#print axioms` myself:

- `PousAssembly.n10prime_of_decode` — `[propext, Classical.choice, Quot.sound]`
- `PousAssembly.n10primeMulti_of_decode` — `[propext, Classical.choice, Quot.sound]`
- `PousAssembly.n10prime_of_consistent`, `…Multi_of_consistent`, `decodeTarget_of_hintCard`, `winner_cred2_size` — same
- `PousLabelBirthday.labelBirthdayT`, `PousAssembly.labelBirthdayAll` — same

No `sorryAx`, no `native_decide`, despite `ColumnAwareDraft`/`ForwardCoreDraft`/`TweakedDraft` carrying `sorry` (including
`n10prime` itself). So the chain genuinely does **not** route through the drafts' holes, and `n10prime_of_decode` proves
`type_of% @PousTweaked.n10prime` without invoking the sorry'd `n10prime`. The **only** free assumption is `DecodeHyp3`
(the audit lists it as `n10prime_of_decode`'s single `assumption`; `LabelBirthdayAll` is discharged by `labelBirthdayT`).
Store copy untouched (`AssemblyHyp.lean` still `e84c45a8`); I only read and copied it.

**1. `ConsistentBound + DecodeTarget` is the right, sound decomposition.** The counting is `pr_le_of_consistent`:
`consistentCompression` (§27, proved) gives `|{E}| ≤ 2^m · |Red| · 2^b` (the pattern is folded into `Red` via
`pat = fun _ => ()`, so `|Pat| = 1`), and `DecodeTarget` — `|Red| · 2^b · 2^{(k−X)·n·wc} ≤ C(Q_tot, 3n) · |Ω|` — divides
through to `pr E ≤ 2^m · C(Q_tot,3n) / 2^{(k−X)·n·wc}`, which is *definitionally* `N10primeBoundT 1 m n wc Q_tot 3n
(k−X)`. `n10prime_of_consistent` then splits `pr(Win) = pr(Win ∧ ¬Coll) + pr(Win ∧ Coll)`, bounds the first by that
target and the second by `labelBirthdayT` (`(2n)²/2^{n·wc}`), matching `n10prime`'s stated bound exactly. I checked the
collision bound end to end: `LabelBirthdayT` is now a *theorem* (not an interface), by dependency-congruence
(`c1T_congr`/`c2T_congr`: a pair's lex-later tweak is fresh for both labels) → a per-pair `1/|Lab|` via single-entry
deletion (`permSplitAt`) → a union over `≤ (2n)²` pairs. That is faithful and complete. So the decomposition is correct:
`DecodeHyp3` really is the *only* gap between the machine and `n10prime`, and `Q_tot = n(Q+1)+2n`, `sav = k−X`,
`pos = 3n` all line up with the pinned statement. **Sound.**

**2. Can `pos = 3n` be enough under `cred2` (up to `6n` crediting queries/segment)? — Plausible, but tight; I found the
stress case.** `pos` is the number of *hit positions* recorded (a subset of the `N·Q_tot` pool, costing
`log C(Q_tot, pos)`); a *smaller* `pos` is a *stronger* bound, so understating it makes `DecodeHyp3` too strong (false),
not too weak. The saving is `(k−X)·n·wc` bits; the decoder deletes credited units from honest **entries**, one recorded
position per distinct entry. The `6n` "crediting queries" (the six types `qH1,qH2,qI1,qI2,qP1,qP2` per node) do **not**
each need a position, because forward/inverse of a node hit the *same* entry and lower columns share their lower entry:
- **all `lowerCol (w,·)` credits live in the `≤ n` lower entries `P_{(0,w)}`** (the entry is the first coordinate `w`),
  so *any* number of lower columns needs `≤ n` positions — this is what defuses the naive "`(k−X)·n` columns ⇒ `(k−X)·n`
  positions" worry;
- `topWhole` → `≤ n` entries `P_{(1,u)}`; `lowerKey` → `≤ n` entries `H_{(0,w)}`; `topKey` → `≤ n` entries `H_{(1,u)}`.

The clean budget is **3 entries per node** — one top entry, one lower-columns entry, one lower-key entry — i.e. `3n` —
**provided a node's top is never credited as both a whole label and a key.** `cred2`'s guards enforce that exclusion
*across* rounds (a `qI2`-credited `topWhole u` puts `u` in the game, blocking a later `qP2` `topKey u`, and vice versa —
this is the §27 fix). But **within one round it does not**: a program that asks *both* `qI2 u` and `qP2 u` in the same
round, with all of `u`'s columns already in the game at `r−1` and `u`'s key not (`¬keyTop`), first-credits `topWhole u`
(from `qI2`) **and** `topKey u` (from `qP2`) — two top entries for one node, so the true worst case is `4n`, not `3n`.
Both credited units are genuinely deletable (one label each: `c²_u` from `P`, `k²_u` from `H`), so this is not an
over-credit in the §27 sense; it is a *position-count* excess. The decode can plausibly still hit `3n` because it only
needs `(k−X)·n·wc` of the `≥(k−X)·n·wc` available bits, so it can **drop the redundant top-key** at each double-credited
node and keep `≤ 3` entries/node — but when `size = (k−X)·n` exactly *and* many nodes double-credit, dropping `n` bits per
such node may undershoot the saving, and *that* is not obviously recoverable. **So `pos = 3n` is defensible (matching the
`3` = {top, lower-columns, lower-key} per node) but genuinely tight; the same-round `qI2+qP2` pattern is the concrete
thing the decode worker must rule out or absorb.** This is not a soundness risk to the *assembly* (it is parametric in
`pos`); the pinned comment "Moving to `6n` is one edit here" is the safety valve — `6n` (= the `6` crediting queries/node,
unconditionally safe) restores it at the cost of a weaker `k` (159 → lower). I would not let `DecodeHyp3` at `3n` be
marked proved until the `≤ 3` entries/node accounting (with the same-round exception handled) is written down.

**3. Could an adversary make the true consistent-ω count exceed any admissible `2^b`? — Yes in principle; this is the
DGO19 risk, now the binding constraint, and `DecodeHyp3`'s truth is exactly its absence.** `ConsistentBound` requires a
*single* `b` with `|{winning ω sharing (σ, R ω)}| ≤ 2^b`. The affordable `b` is the security margin:
`|Red|·2^b·2^{(k−X)·n·wc} ≤ C(Q_tot,3n)·|Ω|`, i.e. `b ≲ (k−X)·n·wc − m − log C(Q_tot,3n)` (positive by design). An
adversary that arranges a `(σ, R)` fibre larger than that — e.g. by making the rewind-and-solve equation
`x ⊕ H(τ,1,1,x) = s` (§27 witness) have many winning solutions — refutes `DecodeHyp3`. This is precisely the
ideal-permutation-inversion circularity of §11C/§26/§27, now sharpened into "the fibre is small." Two points confirm it
is the *real* open piece: (a) the `HintT` bridge (`decodeTarget_of_hintCard`) only meets **`DecodeTarget`** (the
counting), and only at `b = 0` — it says nothing about `ConsistentBound`; and (b) `b = 0` means a *unique* decode, which
`Probe.lean`/§27 proved fails, so a real decode needs `b > 0`, and `HintT` at `b > 0` needs slack
`b ≤ wc·(size − (k−X)·n)` — so if `columnHard` only gives `size = (k−X)·n` with no slack, the margin for `b` must come
from the `C(Q_tot,3n)` headroom, not from `HintT`. **So `DecodeHyp3` is neither vacuous nor trivially satisfiable:** you
cannot satisfy it with huge `Red` or huge `b` (the target forbids it — `b = log|Ω|` forces `|Red| < 1`), the `ColumnHard`
premise is satisfiable (the band certificate, §14), and `Win` is the genuine event. It is a sharp, falsifiable `∀∃`
claim whose truth *is* the small-fibre rewind-and-solve decode.

**Verdict (§28): the assembly is sound and machine-verified — `n10prime`/`n10primeMulti` follow from `DecodeHyp3`/
`DecodeHypMulti3` alone, on the three standard axioms, with `LabelBirthdayAll` discharged and no `sorry` leaking from the
drafts. `DecodeHyp3` is plausibly true, non-vacuous, and not trivially satisfiable; the `ConsistentBound + DecodeTarget`
decomposition is faithful and the collision bound is fully proved.** The two things that must be discharged before
`DecodeHyp3` may be treated as established (and the two things a red team should keep hammering): the **fibre `b`** (the
DGO19 small-fibre claim for a concrete `R`, `internal/p3-decode/`) and the **`pos = 3n` per-entry accounting** (the `≤ 3`
deleted entries per node, with the same-round `qI2+qP2` double-credit either excluded or absorbed; else fall back to the
pinned `6n`). Both are exactly where a false-assumption disaster would hide, so neither should be waved through. Overall
verdict unchanged: **GRANTED WITH CONDITIONS** — the trusted layer stands, and the entire open N10′ core is now a single,
clean, machine-audited hypothesis (`DecodeHyp3`), with its load-bearing sub-obligations (fibre `b`, `3n` accounting)
named and localized.

## 29. Erratum to §28: `DecodeHyp3` is FALSE (machine-refuted), not "non-vacuous" — the corrected `ZeroAdvice → AdviceBound → N10primeAtGe` chain, and an attack on the load-bearing route-completeness step (27 Sep 2026)

**This corrects §28.** §28 judged `DecodeHyp3` "not vacuous and not trivially satisfiable." **That was wrong.** The
decode prover has machine-refuted `DecodeHyp3` (and `DecodeHypMulti3`, `FixedAdvice*`) for **every** `pos`
(`freshness/DecodeHypFalse.lean`), and `N10primeAt` at `7n`/`9n+1` on degenerate instances
(`freshness/PosTooLarge.lean`). I verified both on my own VM (fresh `pous`, three standard axioms). So the §28 chain
`n10prime_of_decode : DecodeHyp3 → n10prime` proves `n10prime` **from a false hypothesis** — it is vacuous and
establishes nothing. I retract §28's non-vacuity verdict.

**The refutation, and exactly where my §28 reasoning failed.** `DecodeHyp3` is `∀ (n wc m D Q k X) …, ColumnHard … →
… → ∃ Red b, ConsistentBound ∧ DecodeTarget`. Take `k > n` (witness `n = wc = 1`, `m = D = Q = X = 0`, `k = C·|Ω| + 2`).
Then `ColumnHard G d k X` holds **vacuously** — no holding reaches more than `n < k` tops (`columnHard_vacuous`,
verified) — but `DecodeTarget` still demands `|Red|·2^b·2^{(k−X)·n·wc} ≤ C(Q_tot,pos)·|Ω|` with `|Red| ≥ 1`. The saving
exponent `(k−X)·n·wc = k` grows without bound in `k`, while `C(Q_tot,pos)·|Ω|` is fixed (independent of `k`), so
`2^k > C·|Ω|` breaks it (`not_decodeHyp`, `not_decodeHyp3`, verified). **My error was precise and instructive:** in §28 I
checked that the `ColumnHard` premise is *satisfiable* (via the band certificate, §14) — a *non-degenerate* instance —
and concluded non-vacuity. But `DecodeHyp3` is a `∀∃`, so it is refuted by the *degenerate* corner `k > n`, where the
premise holds for the wrong reason (vacuously) and the target is unsatisfiable. Checking that a hypothesis *can* hold is
not checking that it *always* holds; for a universally-quantified hypothesis only the latter is non-vacuity. This is an
N10-class miss (a false named assumption slipped through), and it is exactly what the coordinator was guarding against.
§28's `pos = 3n` "tight, same-round `qI2+qP2`" sub-analysis is now moot: the decode's real position count is `9n + 1`
(below), and `3n` "is not supported" — `ZeroAdvice3` may itself be false.

**The `pos` refutations (`PosTooLarge.lean`, verified).** `N10primeAt pos` (unrestricted) is false whenever `pos 1 > 3`
(at `Q = 0`, `Q_tot = 3n`, so `C(3, pos 1) = 0`, leaving only the birthday term, which a `k = 0` program beats with
`pr = 1`) or `pos 0 > 0` (at `n = 0`). So `N10primeAt` at `posP3 = 7n` (`not_n10primeAt_posP3`), at `9n + 1`
(`not_n10primeAt_nine`), and `ZeroAdvice` at `9n + 1` unrestricted (`not_zeroAdvice_nine`) are all refuted. `pos = 3n`
escapes both witnesses (it equals `Q_tot`'s floor at `Q = 0`), which is why `n10prime_of_zeroAdvice3` is stated
unrestricted — but that does not make `ZeroAdvice3` true.

**The corrected chain (`Decode2.lean`, verified on three standard axioms).** The fix removes the two defects:
- **`AdviceBound pos`** is the per-advice count with **no `max`**: `#{ω | A₁ω = σ ∧ win ∧ ¬coll} · 2^{(k−X)·n·wc} ≤
  C(Q_tot, pos n)·|Ω|`. When nothing wins the LHS is `0`, so it holds — no existential target to force a contradiction
  at `k > n`. `n10primeAt_of_adviceBound` sums it over the `2^m` advice strings (giving the `2^m` factor with **no `R`,
  no `b`**), and `adviceBound_of_zeroAdvice` reduces it to **`ZeroAdvice`** (fixing `σ`, the run is the fixed advice-free
  family `A₂ σ`, so `{A₁ω = σ ∧ win} ⊆ {A₂σ wins}`). So `n10prime` now rests on a statement about **advice-free**
  programs, with no reduction `R` and no fibre `b` — the entire §27/§28 `ConsistentBound`/rewind-and-solve apparatus is
  gone, replaced by a direct lucky-guess count.
- **`N10primeAtGe Q₀ pos`** and **`ZeroAdviceGe Q₀ pos`** add `0 < n → Q₀ ≤ Q →`. `n10prime_of_zeroAdvice9 :
  ZeroAdvice9 → N10primeAtGe 27 posZA` (with `posZA n = 9n + 1`) is verified.

**Task 2 — is `N10primeAtGe` (`0 < n`, `Q ≥ 27`, `pos = 9n + 1`) a faithful, non-vacuous restriction? Yes, with the new
rule applied.** *Faithful:* it is literally `N10primeAt` with two hypotheses added, same bound and event; the excluded
instances (`n = 0`, `Q < 27`) are degenerate and outside the real regime (`n = 220`, `Q = 2^20` satisfy both), and the
`pos = 9n + 1` (vs §28's optimistic `3n`) is the honest position count from the decode, so the bound is legitimately
weaker (larger `C`, smaller `k`) rather than sneakily changed. *Non-vacuous, and now checked against the coordinator's
new rule:* the restriction is not only faithful but **necessary** — without `Q ≥ 27` the binomial `C(Q_tot, 9n+1)`
vanishes and the statement is refutable, so the guards are load-bearing, not cosmetic. I verified `N10primeAtGe 27 posZA`
dodges **both** `PosTooLarge` witnesses (`n = 0` and `Q = 0` are excluded), and — honoring "require a Lean witness that a
hypothesis is satisfiable before calling it non-vacuous" — I **authored and machine-checked** a witness
(`zeroAdvice_ineq_holds_kBig`, three standard axioms) that `ZeroAdvice`'s inequality **holds** at the exact `k > n`
instance that killed `DecodeHyp3`: since a win needs `k ≤ n` (`winZ_needs_k_le_n`), the winner count is `0` and the bound
is `0 ≤ RHS`. So the corrected hypothesis degrades gracefully precisely where the old one broke. **What I do NOT certify:**
`ZeroAdvice9` itself is the *open* lucky-guess lemma — there is **no Lean witness of its full truth**, so per the new
rule I do not call it established, only structurally sound (it survives every degenerate attack that felled its
predecessors) and correctly connected (`ZeroAdvice9 → N10primeAtGe`, proved).

**Task 3 — attack on `internal/p3-decode/inverse-decode.md` §7.3 (route-completeness), the load-bearing paper step.** The
claim: conditioned on the view before a slot, an honest value is fixed **only** through (1) an honest query answer
(`= know`, inside the game by `knowledgeSim2`), (2) a preimage hit (L2), or (3) compositions of these (game moves); all
else leaves the value's table entries uniform up to pool exclusions. I tried to break it and **found no counterexample**,
but it is genuinely unproven and is where I would keep pushing. The four pressure points:
1. **It is an *extension* of `knowledgeSim2`, which is proved only for `know`.** `knowledgeSim2` (§27) covers plain
   oracle answers; §7.3 needs completeness for the full **lucky-hit-augmented, adaptive** view (routes 2 and 3). That
   extension — that every fixing of an honest value is a game move from credits *and hits* — is asserted, not
   machine-checked, and is the real gap between what is verified and what the bound needs.
2. **The (L2) preimage-hit enumeration at `2n`.** §5c shows preimage probes are real and subtle (a *forward* query at
   `z₀ = P_t⁻¹(x_t)` leaks the honest input, recreating the inverse obstacle with no `P⁻¹`). The claim that exactly `2n`
   such hits (one per tweak) exhaust this route — no higher-order preimage-of-preimage leak — is plausible for a single
   permutation but is asserted, and is the most enumeration-fragile line.
3. **The `k²_u` one-time-pad claim.** "A `P_t⁻¹` answer at honest output `c²_u` reveals nothing about the columns while
   `k²_u` is unknown, and `k²_u` is learned only through `qH2 u` (parents then in the game)." Sound in the ideal model —
   `H` is a random function, so `k²_u` is learned only by querying `H` at the honest input `(1,u,{honest parents' c²})`,
   which requires knowing those parents — but this is exactly the DGO19-adjacent step, and it rests entirely on `H` being
   an ideal random function and `P` an independent permutation family (no chaining correlations, which holds for
   `p3ModelT` but is a modelling assumption).
4. **Adaptivity and pool exclusions.** The min-entropy argument conditions on the view and relies on lazy-sampling
   leaving unfixed values uniform; the interaction of adaptive inverse queries with the permutation pool factor
   `(M/(M−Q_tot))` is precisely the territory where ideal-permutation-inversion arguments are historically subtle.
   §7.5 concedes the Lean proof "needs conditional probability over adaptive runs" and "is sizeable."

**Verdict (§29): §28 is corrected — `DecodeHyp3` is false (machine-refuted, verified), so its non-vacuity claim is
retracted and that chain establishes nothing. The replacement chain `ZeroAdvice(Ge) → AdviceBound(Ge) → N10primeAt(Ge)`
is proved on the standard axioms and is structurally sound: `AdviceBound`'s no-`max` count dodges the `k > n` vacuity,
and `N10primeAtGe 27 posZA` is a faithful, non-vacuous, refutation-dodging restriction (with a Lean satisfiability
witness for the graceful-degradation corner). The load-bearing open step is now `ZeroAdvice9` via the §7.3
route-completeness claim — unproven, not refuted by me, and the thing to keep attacking; I found no counterexample but
will not certify it.** Two process points I am adopting per the coordinator: (a) **no named hypothesis is called
non-vacuous without a Lean satisfiability witness** — retroactively this would have caught the §28 error, since
`DecodeHyp3` has no such witness (indeed it is refutable); (b) the fault in §28 was accepting "the premise is
satisfiable" as non-vacuity for a `∀∃` hypothesis, which is unsound. Impact on the build: since Daniel has chosen the
**dense** scheme for secure-first, P3's `n10prime` is the performance candidate, not the secure path, so this erratum
does not move the secure-first workstream (which rests on §25's `ChainExPostFacto`). Overall verdict for the trusted
layer unchanged: **GRANTED WITH CONDITIONS** — the trusted layer itself is untouched by this; the correction is confined
to the open P3 N10′ path, which is now honestly on `ZeroAdvice9` + route-completeness rather than on the false
`DecodeHyp3`.

## 30. Dense re-certificate at 64 KB (`dense_meets_64`) and 14 GB multi-segment (`seg_meets_14`): closed theorems, §20 handled structurally, witnesses and necessity proofs exemplary (27 Sep 2026)

Review of `dense/DenseReCert.lean` (sha `b7d6ebf3`) — the secure-first scheme's numeric certificate at the operating
point `scheme-choice-e2e.md` chose: `dense_meets_64` (64 KB labels, `B = 512`, `D = 5`, `Q = 2^20`, `k = 106`) and
`seg_meets_14` (448 segments, 14 GB, `k = 106`), plus the multi-segment machinery (`segDAG`, `card_reach_seg`,
`seg_hard`, `seg_timedINC`) and an explicit witness/necessity suite. **Verdict: both certificates are faithful,
non-vacuous, tightly certified, and machine-verified on the three standard axioms; the §20 distinctness pattern is
handled structurally (segment coincidence is impossible by construction); and the edge-case/vacuity discipline is
exemplary — the file supplies both satisfiability witnesses and necessity proofs for every hypothesis, exactly the §29
lesson applied proactively. Nothing is false. Crucially, `dense_meets_64`/`seg_meets_14` are *closed theorems with no open
named hypothesis* (in the random-oracle model) — a fundamentally stronger status than P3's `DecodeHyp3`/`ZeroAdvice9`.**

**Independent build + axiom check (my VM).** Built `DenseMeets` + `DenseReCert` against my fresh `pous`
(`~/densererevify`) and ran `#print axioms` on all 16 theorems — `dense_meets_64`, `dense_union_term_64`,
`dense_sampling_term_64`, `stateBound_dense_64`, `seg_meets_14`, `seg_hard`, `card_reach_seg`, `seg_timedINC`,
`segScheme_correct`, `seg_union_term_14`, `seg_sampling_term_14`, `stateBound_seg_14`, `audit_k_lt_B`, `seg_hard_14`,
`seg_hard_needs_hN`, `seg_hard_needs_hD` — all `[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide`.
Store copy untouched (`DenseReCert.lean` still `b7d6ebf3`).

**Faithfulness — `Meets` is the genuine predicate, `β` is not a cheat knob.** `Meets` (trusted, `Params.lean`) requires
`ε ≤ εMax`, `Correct`, `CodeHoldsW`, `SpaceBound expansion`, and `AuditSecure sch reveal (sch.stateBound ρ) D Q k …` — so
the adversary storage is exactly `sch.stateBound ρ = ⌊ρ·|C|⌋` (the real 18/19 bound), which `stateBound_dense_64` /
`stateBound_seg_14` confirm equal `⌊(18/19)·2^28⌋ = 254307274` and `⌊(18/19)·448·2^28⌋ = 113929658799`. The parameters
match the memo exactly: `ℓ = 524288` bits = 64 KB, `B = 2^9 = 512`, `D = 5`, `Q = 2^20`, `k = 106`, `ε = 2^-128`,
sequential; the 14 GB point is `448·2^28` bits. The soundness routes through the trusted `theorem1_ii_seq`
(`Theorem1iiSeq`: `pr ≤ (∑_{j<k} B^j)·π + p₀(β,S,B,ℓ)^k`) with `dense_timedINC`/`seg_timedINC`. I checked `β` is the
genuine Theorem-1(ii) incompressibility parameter, not a free lever: it appears as `2^β` in the union term (larger `β`
*worsens* it) and inside `p₀ = 1 − (β−S−B)/(B·ℓ)` (needs `β > S+B` for `p₀ < 1`, else the sampling term is `≥ 1` and
useless). At 64 KB, `β−S−B = 11475226 > 0`, giving `p₀ ≈ 0.95725`, and the certificate is *tight both ways*:
`p₀^106 ≈ 0.00975 < 1%` while `p₀^105 ≈ 0.0102 > 1%` (so `k = 106` is minimal, matching the memo), and the union
exponent `(524288−59)·507 − (9·106+9+β) = 128` lands the union term at *exactly* `2^-128` (I recomputed both by hand and
they check; the proofs discharge it by `norm_num`). The 14 GB certificate re-balances (`β = 119067414778`,
`N·B = 229376 ≤ 2^18`) to the same `k = 106` and again exactly `2^-128`.

**§20 distinctness — handled structurally; the bug cannot recur.** §20's failure was a multi-segment statement where
shared data + non-injective tags let segments coincide, so one segment's stored tops won all. `segScheme` avoids this by
construction: it is *one* scheme on `Fin (N*B)` **global** block indices, with `segDAG N B` giving each node the earlier
blocks of *its own* segment (`par k = {j : j/B = k/B ∧ j < k}`) — I checked there are **no cross-segment edges**, so it is
the disjoint union of `N` complete DAGs. The single random oracle is keyed by the global `(node, parents)`, so every
block has a *distinct* key; the flat `W` split by global index gives per-block data. So the "distinct tag" is the global
index (trivially injective) and the "per-segment data" is automatic — a cleaner realization of §20's fix. Segment
coincidence is impossible: even if an adversary picks `W` with equal data across blocks, the labels differ (distinct
`H`-keys), and `seg_hard` is *data-independent* (quantified over all `W`, about the DAG and reach only). `seg_hard` itself
is a correct generalization of `complete_hard`: `card_reach_seg` proves each round adds at most `N` nodes (one per
segment, via `Set.InjOn (·/B)` on the newly-reached set), so `reach ≤ |P₀| + N·D`, giving `(N*B − N*D − 1, D, N*B)`-hard.

**Edge-case vacuity — the `DecodeHyp3` lesson applied, proactively and correctly.** This is the part I scrutinized
hardest given §29, and it is done right:
- **No binomial position term, so no `n = 0`/small-`Q` degeneracy.** The dense bound is `(∑_{j<k} B^j)·π + p₀^k` with
  **no** `C(Q_tot, pos)` factor — the exact structural feature whose absence removes the `PosTooLarge` failure mode. The
  collision `((B(Q+1)+B)²/2^ℓ)^{s+1}` is monotone in `Q`, so a smaller `Q` only shrinks the union term; `dense_timedINC`
  and `seg_timedINC` are proved for *every* `Q`, needing no lower bound (unlike P3's `Q ≥ 27`).
- **`k` vs `B` non-vacuity.** `PebblingHard G univ s D k` is non-vacuous only for `k ≤ |univ|` (else `filter.card ≤
  |univ| < k` automatically — P3's `k > n` vacuity). `seg_hard` uses `k = N*B` *exactly* (tight), and `audit_k_lt_B`
  confirms the audit `k = 106 < B = 512 ≤ N*B`, so neither route is vacuous.
- **Satisfiability witnesses:** `seg_hard_14` instantiates `seg_hard` at the real 14 GB point (`hN`, `hD` met, `k = N*B`
  tight); `segNeZero_witness` supplies the `NeZero (448·2^9)` instance.
- **Necessity proofs (the key discipline):** `seg_hard_needs_hN` proves `¬ PebblingHard (segDAG 0 …) …` (at `N = 0`,
  `k = 0`, so `filter.card < 0` is impossible — the statement is *false*, not vacuously true), and `seg_hard_needs_hD`
  proves `¬ PebblingHard (segDAG 1 1) univ 0 1 1` (with `D ≥ B` one round pebbles everything). Both show that dropping
  the hypothesis makes the theorem *false*, i.e. the guards are load-bearing. This is exactly the "witness + necessity"
  standard §29 called for, supplied for every hypothesis in the chain.

**The status that matters.** Unlike P3, `dense_meets_64` and `seg_meets_14` take **no** named hypothesis — they are
closed theorems in the random-oracle model, resting only on `complete_hard`/`seg_hard` (proved), B5 (proved), and
`theorem1_ii_seq` (trusted). So there is no `DecodeHyp3`-style assumption that could be secretly false; the only standing
assumption is the RO model itself. The remaining gap for *concrete* security is the RO → overwrite-chain-`H` swap via
`ChainExPostFacto` (§25), and the file is explicitly structured so that swap is segment-by-segment without touching
`segDAG`/`seg_hard`.

**Verdict (§30): the dense re-certificate is faithful, non-vacuous, tight, and machine-verified — `dense_meets_64` and
`seg_meets_14` are closed `Meets` theorems at the memo's operating points (64 KB / 14 GB, `k = 106`, `ε = 2^-128`), with
the §20 distinctness pattern made structurally impossible and an exemplary witness+necessity suite that embodies the §29
discipline. Nothing false.** The secure-first workstream's *random-oracle* certificate is therefore complete; the one
remaining condition is the concrete-`H` obligation `ChainExPostFacto` (§25). Overall verdict unchanged: **GRANTED WITH
CONDITIONS** — and, notably, the dense path's only open item is now a single B5-pattern ex-post-facto lemma, with the
numeric certificate, the multi-segment composition, and all their edge cases already closed in Lean.

## 31. PR #183 dense additions (tag alignment, trusted-`denseScheme` switch, `PROTOCOL.md`): merge the draft, with two follow-ups before the tagged deployment is cited as certified (27 Sep 2026)

Review of the additions in [PR #183](https://github.com/danielreuter/verity/pull/183) (head `f8181a51`, stacked on
#162): `DenseReCert.lean` moved from sha `b7d6ebf3` (§30) to `99709a42`, which adds the per-segment tag alignment; the PR
also switches `DenseMeets` to the trusted `Pous.Dense.denseScheme` and updates `PROTOCOL.md`. I re-verified everything on
my own VM. **Verdict: merge the draft. Nothing is false or vacuous; the trusted-`denseScheme` switch is a strict
improvement; the tag-alignment additions are correct; and `PROTOCOL.md`'s claims are accurate and honestly caveated. Two
follow-ups are required before the *tagged, deployed* 14 GB scheme (as opposed to the global-index proxy) may be cited as
machine-certified — neither blocks the draft, but call 2 is the higher priority and sits exactly in the §20 keying-danger
zone.**

**Independent re-verification (my VM, fresh `pous`).** Rebuilt `DenseReCert` (`99709a42`) and ran `#print axioms`:
`domainSep_equiv`, `tag_injective`, `tag_injective_14`, `u64_inj`, and the unchanged `dense_meets_64`/`seg_meets_14` all
reduce to `[propext, Classical.choice, Quot.sound]`; no `sorry`/`native_decide`. I also diffed the trusted
`Pous.Dense.denseScheme` (`Pous/Model/Dense.lean`) against the `PousDense.denseScheme` copy §30 reviewed — the bodies are
**byte-identical**, so stating `dense_meets`/`dense_meets_64` over the trusted definition (change 1) is semantics-preserving
and removes the "is the verbatim copy faithful?" question. Good change. Store copy untouched (`99709a42`).

**The tag-alignment additions are correct pure-math facts.** `segIndexEquiv N B := finProdFinEquiv` is the standard
`Fin N × Fin B ≃ Fin (N*B)` (the (segment, block) ↔ global-index bijection). `u64 s` is the low 64 bits; `tag salt s =
salt ‖ u64 s` is 256 bits, matching `chainDense`'s salt slot. `u64_inj` (equal low-64 bits ⇒ equal, for values `< 2^64`)
and `tag_injective` (distinct segments ⇒ distinct tags, for `N ≤ 2^64`, from `u64 s` via `Fin.append_right`) are sound.
`domainSep_equiv` proves the core alignment: `∃` an injective `t` with `(tag_s, i) = t (segIndexEquiv (s,i))` — i.e. the
tagged keying is the global-index keying composed with an injective relabeling. `tag_injective_14` discharges `N = 448 ≤
2^64`. The "salt-entropy independence" note is accurate: the `2^-128` in `dense_meets_64`/`seg_meets_14` comes entirely
from the union term (the salt appears nowhere in those bounds), and inter-segment separation comes from `u64 s`, not salt
entropy — the salt is the opaque first `Fin.append` argument and is never read.

**`PROTOCOL.md` is accurate and honestly caveated — no overclaiming.** It states the dense results are within the
ideal-hash model only; names `ChainExPostFacto` (B5 for `Π₂`) as the stated-not-proved concrete-`H` obligation and "the
main caveat"; and, crucially, says of the tagged keying: "`domainSep_equiv` proves that this keying is the global-index
keying followed by an injective relabeling when `N ≤ 2^64` … The step from there to `seg_meets_14` under the tagged
keying (an injectively relabeled random oracle is again one) is **argued in the file, not proved as a separate `Meets`**."
So the doc scopes the claim correctly; a reader is not misled into thinking the deployed keying is machine-certified.

**Judgment call 1 — where the segmented definitions live.** Split the answer:
- *The tag-alignment defs* (`tag`, `u64`, `segIndexEquiv`, and the lemmas `u64_inj`/`tag_injective`/`domainSep_equiv`) are
  pure mathematical facts, not the subject of any `Meets`. They should **stay beside the proofs** (like #162's
  `bandGraph` helpers); moving them into the trusted layer would only bloat it.
- *`segDAG` and `segScheme`* are different: `seg_meets_14` — a headline secure-first *deployment* claim (14 GB) — is
  stated over `segScheme`, so that definition determines what "14 GB is secure" *means*. Its single-segment sibling
  `denseScheme` already moved into the trusted `Pous/Model/Dense.lean` (change 1), which leaves an asymmetry:
  `dense_meets_64` is over a trusted def but `seg_meets_14` is over a proof-file def that the `lean-audit.json` pins only
  *read*. **I recommend moving `segDAG` + `segScheme` into `Pous/Model/Dense.lean`** alongside `denseScheme`, so the 14 GB
  deployment scheme is audited, pinned and `TRUSTED.sha256`-covered, and cannot be silently changed to weaken/vacuate the
  theorem. This is a *should*, not a hard blocker: the pins'-`reads` mechanism plus my §30/§31 faithfulness review make
  the current beside-proofs placement acceptable for the draft (and it matches the `bandGraph` precedent), but the clean
  home for a deployment-load-bearing scheme is the trusted layer.

**Judgment call 2 — does the tagged-keying transfer need to be a theorem before merge?** `domainSep_equiv` proves the
mathematical *core* (index bijection + tag injectivity ⇒ an injective relabeling), but it does **not** prove
`Meets (taggedScheme …) …`: there is no tagged scheme defined, and no `Meets`-transfer lemma. And the gap is a bit larger
than the comment's "an injectively relabeled random oracle is again one": `segScheme`'s oracle is keyed by the full
`LabelQry` (node *and its parents' labels*), whereas the tagged implementation keys by `(tag_s, block, parents)`, so the
transfer is a *scheme-level* equivalence (the relabeling must commute with the parent structure and the enc/dec/label
maps), not just a relabel of a bare key. Because the deployment uses the tagged keying while `seg_meets_14` is proved over
global indices, **the deployed scheme is currently certified only via a proxy plus an argued step** — and this is exactly
the keying-distinctness territory that produced the §20 false statement. So: **I recommend the transfer be turned into a
theorem** (define the tagged scheme, prove its `Meets` from `domainSep_equiv` + an RO-relabel/scheme-iso lemma) **before
the 14 GB tagged deployment is represented as machine-certified.** For *this draft PR* it is not a hard blocker — the
proved content is sound, `domainSep_equiv` carries the core, and `PROTOCOL.md` is explicit that the step is argued — but
it is the higher-priority of the two follow-ups and should land in this or the immediately-following PR, per the standing
discipline (§29) of not treating an "obvious" keying step as done until it is machine-checked.

**Merge recommendation: MERGE the draft PR #183.** Rationale: (a) every proved statement — `dense_meets_64`,
`seg_meets_14`, `domainSep_equiv`, `tag_injective_14` and the witness/necessity suite — verifies on the three standard
axioms with no `sorry` (I re-checked); (b) the switch to the trusted `Pous.Dense.denseScheme` is byte-identical and a
strict improvement; (c) `PROTOCOL.md` accurately scopes every claim, including the two gaps; (d) the trusted layer is
unchanged (`TRUSTED.sha256` verifies), so the grader is unaffected. **Required follow-ups (tracked, not draft-blocking):**
(1) move `segDAG` + `segScheme` into `Pous/Model/Dense.lean` (keep the tag defs beside the proofs) — or record explicit
coordinator sign-off that beside-proofs is the intended home; (2) prove the tagged-keying `Meets` transfer as a theorem
before the tagged deployment is cited as certified. **Verdict (§31): merge; nothing false; two follow-ups before the
tagged 14 GB deployment is machine-certified, call 2 first.** Overall verdict unchanged: **GRANTED WITH CONDITIONS** — the
dense secure-first path's open items remain `ChainExPostFacto` (concrete `H`, §25) and now the tagged-keying transfer
(§31, call 2), with the random-oracle global-index certificate (§30) and its tag-alignment core (§31) machine-checked.

## 32. `ZeroAdviceLucky` / `AdaptiveMinEntropy` (P3 lucky-guess, corrected): my §29 pressure points were real gaps; they are now one precisely-scoped, plausible open hypothesis (27 Sep 2026)

Review of the P3 prover's response to §29's §7.3–7.4 attack: `freshness/ZeroAdvicePlan.md` (the three gaps + plan), the
new `LuckyHyp.lean` (`ZeroAdviceLucky`, `AdaptiveMinEntropy`), the witnesses `LuckyWitness.lean`, and the proved
machinery (`Lucky.lean`, `LuckySim.lean`, `LuckySlots.lean`, `LuckyCount.lean`, `LuckyGlue.lean`, `LuckyRoutes.lean`).
**Verdict: the three gaps the prover found are real and are exactly the pressure points §29 flagged; the response is sound
and honest — it *weakens* the target (`ZeroAdvice9` → `ZeroAdviceLucky`) and isolates the remaining difficulty into one
precisely-stated hypothesis, `AdaptiveMinEntropy`, which is plausibly true and (I checked) not `DecodeHyp`-refutable.
Every proved step verifies on the three standard axioms (I rebuilt the whole chain independently). Nothing is false.
`AdaptiveMinEntropy` is still open, and I do not certify it — its load-bearing case-completeness (M8d) is the sharpened
form of my §29 route-completeness concern.**

**The three gaps are real, correctly diagnosed, and credited to §29.**
- **F1 — the pool factor cannot be dropped.** A program guesses a column `(w,u)` at `qP2 u` among values its earlier
  `P_{(τ,0,w)}` answers have not shown, then guesses `k¹_w` at `qP1 w`; the joint probability is `2^{−wc}/(M−q)`, not
  `2^{−wc}·2^{−n·wc}`, so an exact `2^{−bits}`-per-pattern bound is *false*. This is my §29 pressure point 4 (pool
  exclusions / adaptivity). Fix: a pool factor `M/(M−2Q_tot)` per event, needing `Q_tot ≪ M/n`, formalized as the
  hypothesis `64·n·Q_tot ≤ 2^{n·wc}`. Correct.
- **F2 — two lucky targets per forward query.** A forward `P_t(z)` is lucky at both `z = x_t` (a credit) and
  `z = z₀_t = P_t⁻¹(x_t)` (a hit, L2), so a slot subset's weighted count reaches `2^{|S|}`, which §7.4's
  `C(Q_tot, 9n+1)` did not pay for. This is my §29 point 2 (the §5c forward-probe subtlety). Fix: the factor `2` per
  slot (the `2M` in `AdaptiveMinEntropy`) and `pos = 9n+1 → 10n` at `Q ≥ 2^15`. Correct.
- **F3 — per-slot conditioning is false on rare views.** With `c¹_w` guessed one column at a time, the last column can be
  *determined* by the view (all but one completion already used outputs of `P_{(τ,0,w)}`), so a per-slot `2^{−wc}` bound
  fails; only the *joint* bound over all of `c¹_w`'s columns survives. This is my §29 point 1 (route-completeness is an
  extension of `knowledgeSim2`; joint conditioning). Fix: `AdaptiveMinEntropy` is stated jointly per slot set `S` (not
  per slot), with a cylinder-decomposition proof plan (M8). Correct.

**`ZeroAdviceLucky` is a faithful, non-vacuous, appropriately-weaker restriction.** It is `ZeroAdvice` at `pos = 10n`
restricted to `okLucky n wc Q := 0 < n ∧ 2^15 ≤ Q ∧ 64·n·Q_tot ≤ 2^{n·wc}`, same count and event. Every change relative
to §29's `ZeroAdvice9` (`9n+1`, `Q ≥ 27`, no pool) makes it *weaker* — the honest consequence of F1/F2, and each
restriction is *necessary*, not cosmetic (F1 needs the pool bound; F2 needs `10n` at large `Q`). The witnesses
(`LuckyWitness.lean`, all standard axioms, which I re-verified): `okLucky_one` shows the restriction is inhabited
(`n=1, wc=32, Q=2^15`); `zeroAdviceLucky_ineq_of_lt` shows the inequality holds at `n < k` (the exact `DecodeHyp` corner —
no family wins, count `0`); `zeroAdviceLucky_ineq_of_le` at `k ≤ X` (trivial saving, `C(Q_tot,10n) ≥ 1`). So the target
dodges the corners that felled `DecodeHyp`, and the restriction is genuinely satisfiable. The proved chain
`AdaptiveMinEntropy → ZeroAdviceLucky → AdviceBoundIf → N10primeAtIf okLucky posLucky` (and `knowledgeSimHits`,
`luckyBits_ge` coverage, `card_luckySet_le ≤ 9n`, `union_bound`, `choose_ten_ge`, `pow_le_two_mul_pow_sub`) all verify on
the three standard axioms on my VM. `KnowledgeSimHits` (point 1) is fully *proved* — a real closure of one of my four §29
points — and `LuckyRoutes` proves model-level forms of points 2 (`answer_honest_iff`, `swapOut_*`) and 3 (`oneTimePad`).

**Is `AdaptiveMinEntropy` plausibly true and non-vacuous? Plausibly yes; not certified.** The statement: for every
bounded family and every slot set `S`, `(Σ_{ω: luckySet=S} 2^{luckyBits ω})·(M−2Q_tot)^{|S|} ≤ (2M)^{|S|}·|Ω|`
(`M = 2^{n·wc}`), with the `2` = F2 and `M/(M−2Q_tot)` = F1, proved jointly = F3. It is a *faithful* formalization of the
corrected argument.
- **Non-refutable in the `DecodeHyp` sense.** The decisive structural check (the §28/§29 lesson): there is **no free
  unbounded parameter on the LHS**. `DecodeHyp` died because `2^{(k−X)·n·wc}` grew without bound in `k` while the RHS was
  fixed; here the LHS weight `2^{luckyBits}` is *summed over a fixed class* `{luckySet = S}` and the RHS `(2M)^{|S|}`
  scales with the *same* `|S|`, so no saving-blowup exists. Honoring the §29 rule, I authored and machine-checked a
  satisfiability witness (`ame_ineq_poolcollapse`, three standard axioms): where the pool collapses (`2Q_tot ≥ M`,
  `|S| ≥ 1`) the LHS factor is `0` and the inequality holds with room — confirming it is not identically false and
  degrades gracefully. (The prover supplied witnesses for `ZeroAdviceLucky` but *not* for `AdaptiveMinEntropy` directly;
  I recommend adding one, e.g. the `S = ∅` count, to fully discharge the rule for this hypothesis.)
- **What is not settled.** The witness covers only the pool-collapse slice; `AdaptiveMinEntropy` in the *pool-positive
  winning regime* is the open M8 (cylinder decomposition: `cylinder`, `cylinderCount`, `freshAnswer`, `creditResolved`).
  The load-bearing part is **M8d `creditResolved`** — that *every* credited unit's lucky equation follows from pins of
  *disjoint* randomness, in topological order or from a later fresh answer. This is the sharpened form of my §29 §7.3
  route-completeness concern: the plan's own "cases M8d must cover" list (partial-column-then-key, `qI2` with partial
  key, `qH1`+`qP1` same round, hit-after-output on one tweak = two pool factors, the `qP2` "neither" credit) is exactly
  where a hidden non-disjoint dependency would break the product bound. Until M8d is proved, the case-completeness is
  asserted, not established — so I do not certify `AdaptiveMinEntropy`, only that it is plausible and refutation-free so
  far. One minor observation: `AdaptiveMinEntropy` is stated `∀ Q` (no `okLucky`), which is fine — it is the pure
  counting bound (the `Q ≥ 2^15` binomial step lives in the glue, not here) — and being more general it is not a hidden
  over-claim, but restricting it to `okLucky` would make a full satisfiability witness easier.

**Verdict (§32): the P3 prover confirmed my §29 pressure points are real gaps in the paper argument, and responded
correctly — `ZeroAdviceLucky` is a faithful, necessary weakening (`pos = 10n`, `Q ≥ 2^15`, pool `64·n·Q_tot ≤ 2^{n·wc}`),
its chain to `n10prime` and `KnowledgeSimHits`/route lemmas are proved on the standard axioms, and the one remaining
hypothesis `AdaptiveMinEntropy` is plausible, non-vacuous, and (checked) free of the `DecodeHyp` refutation. Nothing is
false.** This is real, honest progress: four §29 concerns are now one precisely-scoped open lemma with a concrete proof
plan. But P3's `n10prime` is *not* closed — `AdaptiveMinEntropy`'s winning-regime truth (M8d case-completeness) is open —
and P3 remains the performance candidate, with the **dense** scheme (secure-first) resting instead on `ChainExPostFacto`
(§25). Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 33. `CreditResolved` (M8d, the load-bearing lemma for `AdaptiveMinEntropy`): chain machine-checked, `S=∅` witness proved, stage-4 rank/pivot claim is the open combinatorial core (27 Sep 2026)

Review of the P3 prover's `CreditResolved` step: the paper proof `internal/p3-decode/credit-resolved.md`, the Lean
statements and chain in `LuckyHyp.lean` / `LuckyResolve.lean` / `LuckyGlue.lean`, the scaffolding `LuckyChain.lean` /
`LuckyFibre.lean`, and the `S=∅` witness in `LuckyWitness.lean`. **Verdict: the chain `CreditResolved →
AdaptiveMinEntropyPool → ZeroAdviceLucky → N10primeAtIf okLucky posLucky` is machine-checked on the three standard
axioms (I rebuilt it), with `CreditResolved` the single open hypothesis; `AdaptiveMinEntropyPool` is a faithful,
necessary restriction; and `adaptiveMinEntropy_empty` (the `S=∅` witness I requested in §32) is proved. Stage 4 (the
rank claim + the pin-substitution rule) is the genuine load-bearing combinatorial core: I attacked it and found no
counterexample, but it is not proved, and the prover's own cases 2–3 (the naive rule double-books) show it is subtle
enough that it must become a theorem before `CreditResolved` is discharged. Nothing is false.**

**Independent verification (my VM).** Rebuilt the full chain against my fresh `pous` and ran `#print axioms`:
`adaptiveMinEntropyPool_of_creditResolved`, `n10prime_of_creditResolved`, `n10prime_of_adaptiveMinEntropyPool`,
`adaptiveMinEntropyPool_of_adaptiveMinEntropy`, `adaptiveMinEntropy_empty`, and the scaffolding `chain_sum_le` /
`class_sum_w_le` all reduce to `[propext, Classical.choice, Quot.sound]`; no `sorry`/`native_decide`. `CreditResolved`
and `AdaptiveMinEntropyPool` are `Prop`s (open). The scaffolding `LuckyChain` is a sound, model-free counting lemma: a
chain of pins with `PrefixDet` (pools/pin-sets prefix-determined) and `Fibre` (each value of `X_ℓ` has `≤ 1/P` share in
its prefix class) satisfies `Σ_ω Π_{ℓ<m} w ≤ |Ω|` — a clean supermartingale-style bound. So `CreditResolved`'s job is
exactly to *construct* such a chain for the P3 credits, and `LuckyResolve` correctly turns it into `AdaptiveMinEntropyPool`
by summing over each class.

**Task 1 — `AdaptiveMinEntropyPool`: faithful and necessary.** It is `AdaptiveMinEntropy` with `0 < n` and the pool
`64·n·Q_tot ≤ 2^{n·wc}` added (no `Q ≥ 2^15` — that lives in the glue's binomial step, not the counting bound).
*Faithful:* it is exactly what `ZeroAdviceLucky` consumes (its `okLucky` instances have `0 < n` and the pool), and it is
the form the proof reaches (the comment's "pool losses accrue per pinned variable, not per slot" is right — the pool
factor is applied `≤ 6n` times per class in stage 4, giving loss `(M/(M−Q_tot))^{6n} ≤ e^{6/64} ≈ 1.098 < 2`, which the
`64` in the pool condition is calibrated for). `adaptiveMinEntropyPool_of_adaptiveMinEntropy` confirms it is genuinely
*weaker* than §32's `AdaptiveMinEntropy`. *Necessary:* the pool hypothesis is the F1 condition — §32 established (via the
two-guess witness) that without `Q_tot ≪ M/n` an exact per-pattern `2^{−bits}` bound is false and the union bound
diverges, so it is load-bearing, not cosmetic; `0 < n` is needed for the chain construction (and is harmless — the bound
holds trivially at `n = 0`). *Not vacuous* (the `S=∅` witness is a real count) and *not refutable* (same no-free-parameter
argument as §32: the LHS weight is summed over a fixed class, the RHS scales with the same `|S|`). Caveat, per my §29
rule: the pool's necessity is argued (F1), not machine-checked as a `¬(bound without pool)` theorem; a necessity witness
would strengthen it, though F1's argument is sound.

**Task 2 — attack on stage 4 (the rank claim) and the pin-substitution rule.** Stage 4 claims: on `{luckySet = S}` the
credited equations, restricted to fresh source components, have rank `≥` the number of credited units (columns count `1`,
tops/keys/hits count `n`). Given the claim, each variable's pin `A_ℓ` is the affine solution set, prefix-determined, and
the chain lemma finishes. The whole claim reduces to the **pivot injection `ι`** being *total* and *injective*:
- *Total* (every credit gets a fresh pivot): rests on `cred3` being game-relative (a unit is credited only if it is not
  already in the game) plus stage 2 (`Φ`-forced ⟹ in the game, the semantic companion of `knowledgeSimHits`). So a
  credited unit is not forced by the prefix ⟹ its equation has a fresh unknown. This is the crux link between the §27
  game-relative credits and the rank, and it is *why* `cred3` is game-relative — coherent, but stage 2 is itself
  unproved.
- *Injective* (distinct pivots): the "≤ 3 credit groups per node, one per source (`κ`, the pair, the hit `b`)" budget,
  from the credit rules' game-based mutual exclusions. The **naive rule "pin the later source" double-books** — the
  prover's cases 2 (`qI1 w`+`qP1 w` same round) and 3 (column via `qH1` then earlier "neither" `qP2 u`) both collide, and
  are only fixed by *substituting forced values*. That the naive rule is wrong is a real warning: the correct rule
  (substitute every already-forced quantity, then pivot on the last remaining fresh unknown in chain order) must be shown
  to *always* yield an injection, across the interplay of time-order processing and chain-order pivots.

I pushed on the places a 7th bad case might hide and found none: cross-node sharing (a column `(w,u)` credit pins the
lower source `y_w(u)` while top `u`'s "neither"/key equation uses the columns as forced — different sources, and case 3
handles the time-order inversion); within-round double top credits (`qI2`+`qP2`, §28 — pins the pair vs `κ²`, distinct);
the factor-2 forward ambiguity (`A` = union of honest- and hit-target solutions, paid once); and the substitution
creating no cycles (time order is well-founded). So the mechanism is coherent. **But the global injectivity of `ι` —
that every adversary strategy yields distinct pivots for all credited units — is asserted from a per-node argument plus a
six-case check, not proved. That is the load-bearing open claim, and given cases 2–3 it is genuinely delicate. It should
become a theorem (`ι` explicitly constructed and proven injective) before `CreditResolved` is treated as within reach.**
The pin-substitution rule is *necessary* (cases 2–3 prove the naive rule fails) and plausibly sufficient, but its
sufficiency is exactly what is unproven.

**Task 3 — the `S=∅` witness `adaptiveMinEntropy_empty`.** Proved, and correct: `luckySet ω = ∅` implies no honest query
is asked, no hit, no credited output (`luckySet_eq_empty_iff`), hence `credUpTo3 = empty` (`credUpTo3_eq_empty`) and
`luckyBits ω = 0` (`luckyBits_eq_zero`), so the `S=∅` inequality is `#{ω : luckySet ω = ∅} ≤ |Ω|`. I re-verified it on
the standard axioms. This directly discharges my §32 request for a direct `AdaptiveMinEntropy` satisfiability witness (the
prior witnesses were for `ZeroAdviceLucky`), and together with my §32 pool-collapse witness it covers both the empty and
the pool-collapse corners — confirming the hypothesis is not identically false and degrades gracefully.

**Verdict (§33): the `CreditResolved → AdaptiveMinEntropyPool → ZeroAdviceLucky → n10prime` chain is machine-checked on
the standard axioms, `AdaptiveMinEntropyPool` is a faithful and necessary restriction, and the `S=∅` witness is proved —
good, honest progress that isolates all remaining P3 lucky-guess difficulty into `CreditResolved`, and within it into the
stage-4 rank/pivot-injection claim. I attacked stage 4 and the substitution rule and found no counterexample, but the
injection's global correctness is unproved and (per cases 2–3) subtle, so `CreditResolved` remains genuinely open and
should not be treated as done until the rank claim is a theorem.** Nothing is false. P3's `n10prime` is still not
closed; the secure-first build remains the dense scheme, whose one open concrete-`H` obligation is `ChainExPostFacto`
(§25). Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

**Addendum (pool necessity, `LuckyPoolNeeded.lean`).** The prover has now machine-checked that the pool condition is
necessary **for the counting step**: on `Fin 3` with `M = 3` the chain sum is `9 > |Ω| = 6`, while with the true pool
`M − 1` it is tight at `6`. It explicitly does **not** claim `AdaptiveMinEntropy`'s *inequality* fails without the pool,
and suspects it does not. This refines §33 task 1: the pool is **needed for the proof** (the chain-sum bound
`Σ Π w ≤ |Ω|` breaks without it), and its necessity **for the statement** is **open** (plausibly the bound still holds,
just unprovable by this chain). So the pool hypothesis stays, correctly, as a proof requirement — not a demonstrated gap
in the target.

## 34. PR #183 §31 follow-ups (segDAG/segScheme trusted; tagged transfer a theorem): both done correctly — MERGE (27 Sep 2026)

Re-review of PR #183 at head `6b503b00`, which closes both §31 follow-ups: (1) `segDAG`/`segScheme` moved into the trusted
`Pous/Model/Dense.lean` with `TRUSTED.sha256` regenerated; (2) the tagged-keying transfer is now a theorem
(`PousProofs/Dense/SegTagged.lean`: `segTagScheme`, `segTag_meets_14`, `segTag_auditSecure`). **Verdict: both are done
correctly, everything is machine-checked on the three standard axioms, and the deployed tagged 14 GB scheme is now
certified (in the random-oracle model) rather than argued. MERGE. Nothing is false.**

**Independent build (my VM).** I built the actual PR package in a worktree at `6b503b00` (`protocols/pous/lean`, reusing
my cached Mathlib — manifest identical). `TRUSTED.sha256` **verifies**, and it now covers `Pous/Model/Dense.lean` with a
regenerated hash (`d63ce37f…`, vs the pre-move `baef91ca…`), so the moved `segDAG`/`segScheme` are inside the audited
trusted layer. `lake build` of the trusted `Pous` and `PousProofs.Dense.SegTagged` succeeds (only deprecation warnings),
and `#print axioms` on `segTag_meets_14`, `segTag_auditSecure`, `segTagScheme_correct`, `tagEmbed_injective`,
`label_tag_eq`, `pr_comp_injective`, `tagEmbed_14_injective` all give `[propext, Classical.choice, Quot.sound]`; no
`sorry`/`native_decide` in `SegTagged.lean` or `Dense.lean`.

**Follow-up 1 — `segDAG`/`segScheme` are trusted, and unchanged.** I diffed the moved definitions against what §30
reviewed: **byte-identical** (`segDAG.par k = {j : j/B = k/B ∧ j < k}`, `segScheme` with the same `n, B, ℓ, enc, dec`).
So the move preserved the exact meaning §30 verified as faithful, and the 14 GB deployment scheme now lives, pinned, in
the trusted layer beside `denseScheme`. Correctly done; §31 call 1 closed.

**Follow-up 2 — the tagged transfer is a real, correct theorem.** `segTagScheme N B ℓ salt` is the *deployed* scheme
over `tagModel = randomOracle (Bits 256 × LabelQry B ℓ) (Bits ℓ)`: segment `s` is the dense scheme on `B` blocks with
oracle `H(tag_s, ·)`, `tag_s = salt ‖ u64 s` (256 bits, exactly `chainDense`'s salt slot), **local** block indices and
**local** parents, with block `(s,i)` placed at global position `segIndexEquiv N B (s,i)`. That is faithful to the
implementation's keying as described. `segTag_auditSecure` is the scheme-level reduction I said §31 needed (not a bare
key relabel): it transports the whole sequential-audit game from `segTagScheme` to `segScheme` through an injective query
map `tagEmbed`, with (a) codewords agreeing (`label_tag_eq`, via `mem_segDAG_par` linking the global DAG's within-segment
parents to the local complete DAG), (b) adversaries transferring with identical rounds and work (`liftProg` +
`run/depth/work/bounded_liftProg`), and (c) the oracle transferring (`pr_comp_injective`: `H ∘ f` is uniform when `H`
is, for injective `f`). Crucially it handles the **full oracle domain**: queries under a tag that is no segment's map
injectively to global queries no segment asks (`tagEmbed` writes the bogus tag via `padTag` into a foreign parent slot,
injective for `ℓ ≥ 256`) — exactly the subtlety I flagged in §31 (the tagged vs global `LabelQry` with parents differ, so
it is more than "a relabeled RO is an RO"). `segTag_meets_14` then gives `Meets (segTagScheme 448 (2^9) 524288 salt)` at
`k = 106`, `ε = 2^-128`, **for every salt**, reduced to the trusted `seg_meets_14`. It carries the satisfiability
witnesses (`tagEmbed_hyps_14`, `tagEmbed_14_injective`, `segTag_code_eq_14`). §31 call 2 is fully closed: the deployed
tagged scheme is machine-certified.

**Judgment call — should `segTagScheme` (and `tag`, `u64`) move to the trusted layer? Recommend yes, for consistency,
but it is not a soundness requirement.** `segTag_meets_14` is *the* deployment guarantee and `segTagScheme` is the actual
deployed model — indeed it is the *more* deployment-faithful object than `segScheme` (which is now trusted as the
hardness-carrier proxy). By the same governance logic that moved `segScheme` (§31 call 1), pinning `segTagScheme` and its
trivial keying helpers `tag`/`u64` in `Pous/Model/Dense.lean` keeps the deployment model from drifting and puts the thing
the code implements in the audited layer. The caveat that makes this a *preference*, not a blocker: `segTagScheme`'s
security is a **proven reduction** to the trusted `segScheme` (`segTag_auditSecure`), so it cannot be silently weakened
without breaking the proof wherever it lives; and the Lean↔code correspondence (that `segTagScheme` matches the
implementation) is a human check outside Lean regardless of placement. So moving it is the clean, consistent end-state
and I recommend it, but the PR is sound either way.

**Merge recommendation: MERGE PR #183.** Both §31 follow-ups are correctly done; every statement (`segTag_meets_14`,
`segTag_auditSecure`, the moved trusted defs) is machine-checked on the standard axioms with no `sorry`; `TRUSTED.sha256`
is regenerated and verifies. The one optional follow-up is the judgment call above (move `segTagScheme`/`tag`/`u64` into
the trusted layer), which is small and non-blocking. The standing condition is unchanged and unrelated to this PR:
`segTag_meets_14`, like all dense results, is a **random-oracle** guarantee; concrete-`H` security remains the open
`ChainExPostFacto` (§25). **Verdict (§34): MERGE; nothing false; the tagged 14 GB deployment is now machine-certified in
the RO model, with the two §31 gaps closed.** Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 35. Erratum to §25: `ChainExPostFacto`'s collision term was too small by 2^ℓ (`padBlk` is fixed) — I confirm it, own the miss, and clear the other collision terms (27 Sep 2026)

The `ChainExPostFacto` prover reports that §25's collision term `nPos²/2^{ℓ+(ℓ+c)} = nPos²/2^{2ℓ+c}` is too small by `2^ℓ`,
and the amended term is `nPos²/2^{ℓ+c}`. **I verified the argument: it is correct, the old statement was false as stated,
and I own the §25 error — I validated the `2ℓ+c` width without noticing the pad block is a fixed constant.** I also
checked every other permutation-model collision term for the same width error: `labelBirthdayT` and the RO dense
certificate are clean; the one forward risk is P3-over-chain (`keyP3c`), which reuses the same `padBlk` pad call.

**1. The argument is correct, and the old statement was false.** I confirmed in `SpongeModel.lean`: `padBlk : Bits r :=
fun j => decide (j = 0 ∨ j+1 = r)` — the fixed `10…01` pad, a constant. `labelOv`/`ovKey` end each row with a **pad
call** whose input is `Fin.append padBlk h` (`padBlk : Bits ℓ` fixed, `h : Bits (ℓ+c)` the chaining value), and the key
is that call's dropped `r`. So two rows' pad-call *real points* coincide **iff** their `(ℓ+c)`-bit chaining values
coincide — a birthday over `ℓ+c` bits, not the full `2ℓ+c`-bit call width I asserted in §25. This collision is
*exploitable*, not benign: a shared chaining value gives a shared pad-call input, hence a shared key, hence
`c_i ⊕ c_{i'} = W_i ⊕ W_{i'}` (public), so storing one row's label yields the other's for free — an extra answered
challenge. Since the collision term is an additive bad-event term and the true collision probability is
`Θ(#rows²/2^{ℓ+c})`, the old bound `main + nPos²/2^{2ℓ+c}` is *violated* by a collision-exploiting adversary (the
additive term understates the exploitable event by `2^ℓ`). `ChainExPostFacto` was a **stated target, never proved**, so no
proved theorem was wrong — but the target was false as stated, and the amendment to `nPos²/2^{ℓ+c}` restores truth. (The
sibling `SpongeExPostFacto` at line 306 already used `ℓ+c`; only the chain statement carried `2ℓ+c`.)

**2. I own the §25 miss.** In §25 I wrote "a `Π₂`-collision term at the full `2ℓ+c` width. ✓" and reasoned "a `Π₂` output
is `2ℓ+c` bits; two coincide with prob `1/2^{2ℓ+c}`." That framed the collision as over full-width call outputs; the real
collision that breaks resampling is over the *inputs* (real points), whose block half is the fixed `padBlk`, so the
effective width is `ℓ+c`. This is the same class of error as my §28 miss: I checked the obvious reading and missed a
structural constant. I have added a correction pointer at the §25 collision line.

**3. Deployment is unaffected.** At 64 KB, `ℓ+c = 524800` and `nPos² ≤ 2^{59}`, so the corrected term is `≤ 2^{59-524800}
= 2^{-524741}`, utterly negligible; `k = 111` (as-stated) stands. So this is a statement-correctness fix, not a security
regression.

**4. Other collision terms — the width sweep.** I checked whether the same fixed-constant width error appears elsewhere:
- **`labelBirthdayT` (P3, `p3ModelT`): clean.** `pr_pair_perm` bounds a pair at `1/2^{n·wc}`, a collision between two
  honest *label outputs* (full `n·wc`-bit `P_t` outputs), obtained by marginalizing the fresh lex-later tweak's
  permutation. There is no fixed-constant input half (the `P_t` inputs `x_t = transpose(c¹)⊕k²` etc. vary fully), so the
  width `n·wc` is correct. Unaffected.
- **The RO dense certificate (§30, `dense_meets`/`seg_meets_14`): clean.** Its collision `((B(Q+1)+B)²/2^ℓ)^{s+1}` is over
  `ℓ`-bit random-oracle outputs, keyed by the full `(node, parents)`; no fixed-constant input half. Unaffected. (Same for
  the tagged `segTag_meets_14`, which reduces to it.)
- **Forward risk — P3-over-chain (`keyP3c`, `p3ChainModel`): the same error would recur.** `keyP3c` is
  `ovKey f (domP3 …) (ps ++ [padBlk])` — it reuses the identical `padBlk` pad call. So *when* P3 moves to the overwrite
  chain `H`, its key/label-collision term must be stated over the reduced width `n·wc + 512` (the chaining value), not
  the full `2·n·wc + 512`, or it repeats exactly this mistake. Current P3 (`n10prime` over `p3ModelT` with a random-oracle
  `H`) is not affected — its `labelBirthdayT` is the clean `n·wc` case above — but this is flagged for whoever states the
  chain version. I will apply the same width check there.

**Verdict (§35): the erratum is correct — `ChainExPostFacto`'s collision term must be `nPos²/2^{ℓ+c}` (the pad block is a
fixed constant, so real-point collisions are over the `(ℓ+c)`-bit chaining value); the old `2ℓ+c` term was too small by
`2^ℓ` and false as stated, and §25's validation of it was my error, now corrected with a pointer. The deployment is
unaffected (`k = 111` stands). No other current collision term (`labelBirthdayT`, the RO/tagged dense certificate) has the
same width error; the one to watch is P3-over-chain's `keyP3c`.** I will review the amended `SpongeModel.lean` §10
statement when it lands (task 3, deferred). Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

**Addendum (amendment landed, 27 Sep 2026 late).** Task 3 done: the fix is in and I re-verified it on my VM (three
standard axioms, no `sorry`). (a) **Amended statement:** `ChainExPostFacto` (`SpongeModel.lean` §10, sha `0da48eec`, and
`SpongeDense.lean`) now has collision term `nPos²/2^{ℓ+c}` (line 624), main term unchanged; it is still an open `Prop`
(nothing proves it). Matches the §35 prescription exactly. (b) **Witness:** `ChainEPFErratum.lean`'s `ovH_fiber_card`
proves a chaining value (an `ovH`-image, `ℓ+c` bits) has *exactly* `2^ℓ` preimages among the `2ℓ+c`-bit outputs (the
`r`-part is free) — the clean combinatorial root of the erratum: the `ovH` map is `2^ℓ`-to-1, so its image is `2^{ℓ+c}`
and two outputs collide on their chaining value at rate `(2^ℓ−1)/(2^{2ℓ+c}−1) ≈ 1/2^{ℓ+c}`, strictly above the retracted
`1/2^{2ℓ+c}`. `collision_width_lt` (`ℓ+c < 2ℓ+c`) confirms the amendment only weakens the statement. This is the same
fact as my `padBlk`-fixed framing, stated more cleanly via the fiber. (c) **Re-verified deployment:** `chain_meets_64`
(conditional on `ChainExPostFacto`) gives `Meets (chainDense (2^9) 524288 512 (dom salt)) .sequential 5 (2^20) 111
2^-128` for every salt, via `chain_timedINC` (the port of `dense_timedINC` to the permutation model, resting on the
proved `chainDense_hard`) and `theorem1_ii_seq`. Its `chainPi` carries the corrected `nPos²/2^{ℓ+c}` term, which at
64 KB is `≤ 2^-524741` (utterly negligible; the union term still closes at `2^-128` from the freshness part), and the
sampling term is tight (`p₀^111 ≤ 1%`, `p₀^110 > 1%`). Note `k = 111` (vs the random-oracle `106`) is the chain's
*inherent* one-label loss (`/2^{ℓ·s}` with `s = B−D−1`, one `2^ℓ` weaker than B5's `/2^{ℓ·(s+1)}`), **not** a consequence
of the collision erratum — the collision term is negligible at either width — so the erratum leaves `k = 111` unchanged,
as claimed. `dom_inj` gives distinct per-block domains (`salt ‖ u256 i`), the §20-style distinctness for the chain.
**Amendment verdict: correct and fully landed — the statement is fixed, the witness machine-confirms the erratum's
combinatorial root, and the k = 111 deployment re-verifies (conditional on the still-open `ChainExPostFacto`) with the
corrected term. My §25 error is now both documented and machine-witnessed.**

## 36. `PinFamily` was false on `chainX p` (the hit pair's unconstrained toucher); the `splitProg` fix closes the gap — foundation proved, threading still pending (27 Sep 2026)

Review of the `PinFamily` bug and the `splitProg` fix (`credit-resolved.md` §10), for the P3 lucky-guess track.
**Verdict: the bug is real and the fix is correct — I verified `splitProg` (inverse-queries-last within each round) makes
the constrained forward `qHit` precede the unconstrained inverse `qInvIn`, and the hit pair is the *unique* pair with an
unconstrained toucher, so the §4 assumption is restored globally (rank-cover and pivot-totality together), with §5 case 2
removed as a bonus. The fix's mechanical foundation (`splitProg` + its run/depth/work/bounded preservation) is proved on
the standard axioms. But the fix is not yet threaded: `PinFamily`/`creditResolvedTyped_of_pinFamily` still use `chainX p`
— the chain §10 proves false — so the current `n10prime_of_pinFamily` route is vacuous (a false hypothesis) until
`PinFamily` is restated on the split chain. This vindicates my §33 caution and is another latent §28-class vacuity, caught
pre-landing.**

**The bug is real and correctly diagnosed.** §4's rank argument assumed every pair a class constraint mentions is *first
sampled by a query the class constrains* (an honest slotted query). The hit pair `(z₀_t, x_t)` breaks it: besides the
constrained forward `qHit = P_t(z₀_t)` (`Sum.inr (Sum.inl …)`, verified), it is touched by `qInvIn = P_t⁻¹(x_t)`
(`Sum.inr (Sum.inr …)`), which is **not** an honest query — it has no slot, no transfer. `hitAt` only forbids `qInvIn` in
rounds `< r` (`¬ Asked … (r−1)`, verified), so a same-round-earlier `qInvIn` first-samples the pair, and class members
need not agree on `P⁻¹(v)` (those with `x_t ≠ v` are in the class) — so the hit's `n` units get fewer than `n` pins and
`2^{bits} ≤ 2·Π w` fails, exactly the `n = 2` example. Importantly this is a defect of the *chain order*, not a
counterexample to `AdaptiveMinEntropy`/`CreditResolvedTyped` (which ask only for *some* chain).

**Does the fix close the gap? Yes, in principle — and its foundation is proved.** `splitProg` turns each `round qs k`
into `round (qs.filter ¬inv)` then `round (qs.filter inv)`. So within a round every forward answer precedes every inverse
answer; `qHit` (forward) always precedes `qInvIn` (inverse). Across rounds `qInvIn` cannot be earlier than the hit round
(`hitAt`), so the hit pair is now first-sampled by the constrained `qHit` in every case. I verified the preservation
lemmas on the standard axioms: `run_splitProg` (same answers — reordering within a round is sound because a round's
queries are fixed by earlier rounds), `depth_splitProg` (`= 2·depth`, the `2D` half-rounds), `work_splitProg`,
`bounded_splitProg` (`Bounded D Q → Bounded (2D) Q`). So the transform and its accounting are landed and correct.

**Other §4 reliance on the same assumption — covered by the one fix.** The assumption underlies *two* §4 steps: the
rank-cover (every credited unit gets a pin, `PinFamily`'s `cover` clause) and the pivot-injection totality (`ι` maps every
credit to a fresh pivot). Both are broken *only* by the hit pair — §10's "other pairs" check is correct: honest pairs are
touched only by constrained honest queries (`qP`/`qI`, both slotted, so whichever is first is constrained), and arbitrary
`P_t` queries only *exclude* values (the pool factor), never first-sample a constrained pair's value. Since `splitProg`
fixes the ordering at the chain level, it restores the assumption everywhere §4 uses it simultaneously; there is no
separate unfixed reliance. As a bonus §5 case 2 (`qI1 w`+`qP1 w` same round, inverse first) disappears — the forward now
comes first (type `F`). I found no additional broken case.

**But the fix is not yet threaded — the current route is vacuous.** I built the current store snapshot (it *does* build
cleanly — my first attempts failed only on my own build-ordering/stale-oleans, not a store bug): `PinFamily` (a `Prop`
hypothesis) is stated on `chainX p`, and `creditResolvedTyped_of_pinFamily`/`n10prime_of_pinFamily` (proved, standard
axioms) consume it on `chainX p`. Since §10 proves `PinFamily` on `chainX p` is **false**, this route proves `n10prime`
from a false hypothesis — vacuous, the §28/`DecodeHyp3` pattern again. `splitProg` is defined and its lemmas proved, but
it is **not** used in `PinFamily` or the glue yet. So, per my §29 rule, `PinFamily`-on-`chainX p` must not be called
non-vacuous — it is provably false — and the fix is incomplete until `PinFamily` is restated on `chainX (splitFam ∘ p)`
and the glue re-proven. The prover knows this (§10 is the plan; `LuckySplit` is the first landed piece).

**Checks for when the split restatement lands.** (1) The restated `PinFamily` on the split chain must be *true /
dischargeable* — a satisfiability witness per §29 (the `n = 2` example now yielding `Π w ≈ 2^{2wc}`), since the old one is
provably false. (2) The credits/class/`hitsBy` must be preserved from `p` (`D` rounds) to `splitFam ∘ p` (`2D` rounds) —
the "same classes and credits" claim; the round re-indexing `D → 2D` is the subtle part to verify (`cred3`, `luckySet`,
`hitsBy` correspondence). (3) Coverage (`luckyBits_ge` via `knowledgeSimHits` + `columnHard_timedK`) must still hold on
the split chain with `p`'s credits, and the `2D` depth must not leak into the bound. `run_splitProg`/`bounded_splitProg`
(proved) already cover the run/depth half of this.

**Verdict (§36): the bug is real, correctly diagnosed, and does not refute `AdaptiveMinEntropy`/`CreditResolvedTyped`
(chain-order defect only); the `splitProg` fix closes the gap in principle — inverse-last makes the constrained `qHit`
precede the unconstrained `qInvIn`, the hit pair is the unique offender, and the fix restores every §4 use of the
assumption at once (plus removes §5 case 2). Its foundation (`splitProg` preservation lemmas) is proved. The fix is *not
yet threaded*: `PinFamily`/glue still sit on the false `chainX p`, so the current `n10prime_of_pinFamily` is vacuous until
`PinFamily` is restated on the split chain and re-proven with a satisfiability witness. Nothing is falsely claimed — the
prover flagged it — but the pin route establishes nothing until the threading lands.** This is exactly the §33
pivot-injection-totality risk materializing, caught before it was treated as done. P3's `n10prime` remains open; the
secure-first path is unaffected (dense, `ChainExPostFacto`, §25). Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 37. `PinFamily` restated on the split chain (§36 fix landed, verified); the ι case table not yet landed — preliminary review of the two questions (28 Sep 2026)

Two things this turn. **(A) The §36 fix is fully landed and I verified it.** `PinFamily` (`LuckyPinHyp.lean`) is now
`… → PinsAt D Q … p S H ω`, and `PinsAt` is stated on `chainX (splitFam p) tag G W (2·D) Q` — the *split* chain, not the
false `chainX p`. `creditResolvedTyped_of_pinFamily` (`LuckyPinGlue.lean`) is **re-proven** on that split chain
(`chainX (splitFam p) … (2D) Q`, `bounded_splitFam`, `fibre_chain (bounded_splitFam …)`), so `n10prime_of_pinFamily`
routes through the split chain. And `LuckySplitWitness.lean`'s `pinsAt_example` proves `PinsAt` holds at `ω₀` on the
**exact `n = 2` instance that broke the unsplit chain** (§36/§10): the hit answer pins component 0 at index 36 and `Y1_1`
pins component 0 at index 51, covering `ω₀`'s 2 lucky units — where the unsplit chain left the hit's randomness unpinned.
I rebuilt all of it against my `pous`: `pinsAt_example`, `example_hyps`, `creditResolvedTyped_of_pinFamily`,
`n10prime_of_pinFamily` all on `[propext, Classical.choice, Quot.sound]`, no `sorry`. **This closes my §36 caveat:** the
route is no longer on the provably-false `chainX p`, and `pinsAt_example` is exactly the satisfiability witness §36 asked
for (the fix works where the old one failed). `PinFamily`/`PinsAt` remain open `Prop`s (the full lemma is still the ι
construction), but they are now the *right, dischargeable* statements.

**(B) The ι case table (the main §37 ask) has not landed yet.** `credit-resolved.md` still ends at §10; the detailed
case table indexed by `(top node, lower node)` — with the "≈ 6 components, 5 tokens" accounting and the hard case (a
lower pair first sampled by an inverse query) — is not in the doc. Only the §8 ι-*plan* is there (domain = credited-unit
tokens; codomain = `(ℓ, component j)`; totality from stage 2 "`Φ`-forced ⟹ in game"; injectivity from *distinct nodes →
disjoint variables*, *within-node three groups → three sources*, *within-group distinct components*). So I cannot yet
check the two questions against the actual table; I will when it appears. Preliminary read against the plan:
- **"tokens ≤ fixed components" per group.** The plan's injective `ι` (token → `(ℓ, j)`) with `Σ r_ℓ ≥ #tokens` is the
  right shape, and "≈ 5 tokens ≤ ≈ 6 components" has a slack of 1 — but that margin is exactly what a per-group table
  must verify, group by group. The hard case (a lower pair first sampled by an *inverse* query) is genuine and is where
  I will focus: under `splitProg`, inverse answers come last, so a lower pair first sampled by `qI1` means `qP1` was not
  asked — `qI1` is still a *constrained* honest slot, but the realization is **type I** (it pins the input `x_w`, not the
  output `y_w`), so the component bookkeeping differs from types F/Y. Getting the type-I component count right (so its
  tokens still fit the group's fixed components) is the crux the table must nail; I can't sign off on it from the plan
  alone.
- **Exhaustive group split.** The five token kinds (column `(w,u)`, top `u`, lower key `w`, top key `u`, hit `t`) must
  each map to a unique `(top, lower)` group with no token missed or double-counted (else injectivity or cover breaks).
  The `(top, lower)` coordinates plausibly cover all five, but exhaustiveness-and-disjointness is a bookkeeping check
  that needs the table.

**Verdict (§37): the §36 fix is landed and verified — `PinFamily` now lives on the split chain, the glue is re-proven
there, and `pinsAt_example` witnesses it on the counterexample that broke the old chain (all standard axioms, no `sorry`);
my §36 caveat is closed. The ι case table is not yet written, so its two load-bearing checks ("tokens ≤ fixed components"
per `(top,lower)` group, and exhaustiveness of the group split) remain to be done — I flag the type-I lower-pair case as
the one to scrutinize — and I will review the table before its Lean lands, per the request.** Nothing is false; P3's
`n10prime` stays open on the ι construction; the secure-first path (dense, `ChainExPostFacto`, §25) is unaffected. Overall
verdict unchanged: **GRANTED WITH CONDITIONS**.

**Completion (case table landed, §11; go/no-go): GO for the Lean.** The ι case table is in `credit-resolved.md` §11. I
reviewed the type-I row, the count lemma, the token→group mapping, and the exclusions, and I found no gap; the design is
sound. First, the framing correction the prover made is right and I own it: type I is "`qI1 w` first asked *strictly
before* every round asking `qP1 w`," not "`qP1` never asked" — a later `qP1 w` adds the *uncredited* relation `Rx1` (`κ¹_w`
fixed), which credits no `lkey` because `w` is already whole after `qI1 w` (E2). That extra relation is a harmless spare
(it can only *add* a pin), so it does not disturb the count.
- **The count lemma (§11.5) is a sound GF(2)-rank argument.** Per group, `#pinned = #(effectively-independent relations)
  − #(virtual atoms)`: `dim V` rises by 1 at each eff-indep relation and each newly-sampled atom, `V` ends spanning all
  atoms, so `#sampled − #unpinned = #eff-indep − #virtual`. With (a) each token's relation eff-indep, (b) distinct tokens
  → distinct relation components, (c) each virtual atom cancelled by its attached `RI`, this gives `#pinned ≥ #tokens`. I
  checked the identity; it holds. The content is entirely in (a)/(b), i.e. in the exclusions.
- **Exhaustive and disjoint (§11.4).** The six atom kinds partition into the four group families `C/L/X/M` by the pair
  types; the five token kinds each have one row with a complete case split (relying on E10 to tie credit rule to type);
  groups share no atoms, so `cover = Σ_groups #tokens ≤ Σ #pinned`. Sound modulo E10.
- **The type-I row `M(u,w)` (the case I flagged) is handled correctly.** The column's relation fixes the *virtual* output
  `Y = c¹_w(u)`, and the pin comes from `RI(w)` (`a ⊕ κ`, on the *input* side) — and crucially `RI(w)` never touches `Y`,
  so the input-side pin and the `Y`-relations (`Rx2`/`Rc2` for top/tkey) are on disjoint atoms and don't compete. The two
  instances (C1 column then later `qI1 w`; `qI1 w` with the column already available) both count out (1 pin ≥ 1 token, or
  a spare). This is the type-I bookkeeping I said needed care, and it is right.
- **E7–E10 are plausibly true and consistent with §27/§28** (I sanity-checked each against the `timedReachK`/`cred3`
  model): E7 is the key-gated reverse move (`rev_mem`); E8 is the top-credit mutual exclusion (T3/KT/C3) plus
  top-in-game-after — and it is consistent with my §28 same-round `qI2`+`qP2` double, which here appears as a `top` token
  (via `Rc2`) *plus* a `tkey` token (via `Rx2`) on **distinct** relations, not a collision; E9 is column-credit
  persistence; E10 ties credit rule to pair type (derivable from E2/E5). None contradicts the game model.

**Conditions on the Lean (the load-bearing pieces, all "to do"):** E7–E10 are stated but not formalized — they are the
game facts that guarantee effective independence, so they are the crux, and E7 (reverse move) and E8 (top-credit
exclusion) carry the most weight. The count lemma needs its abstract GF(2)-span + class-fixedness formalization (§11.8
step 4), and the per-group effective-independence enumeration (§11.6) is the completeness-critical step — Lean will *force*
that enumeration to be exhaustive, which is the right place to catch a missed "relation-in-`V`" case (my recurring §7.3
concern, now at finest grain). One specific check I want in the Lean: that the §28 same-round `top`+`tkey` double really
lands on distinct atoms/relations (`Rc2` vs `Rx2`), with no hidden shared component.

**Verdict (§37, completed): GO.** The §11 case table is sound in design — the count lemma is a correct rank argument, the
token→group mapping is exhaustive and disjoint, the type-I `M(u,w)` row correctly pins the input side while cancelling the
virtual output, and E7–E10 are true-as-stated game facts consistent with §27/§28. Nothing is false and I found no gap, so
the prover should proceed to the Lean; the conditions are that E7–E10 be formalized as stated and the per-group
effective-independence enumeration be discharged exhaustively (where Lean will enforce completeness). I will review the
resulting `PinFamily` proof — especially E7/E8 and the `M`-row — when it lands. Overall verdict unchanged: **GRANTED WITH
CONDITIONS**.

## 38. Public-encoder milestone-1 game (`PubEncoderModel`/`PubEncoderDraft`): the definitions are faithful — GO for proving on top (28 Sep 2026)

Statement review as named reviewer of the public-encoder milestone-1 game (untrusted server encodes `(pp*, C*)`, a setup
check verifies `dec pp* C* = W`). I read the brief (`NOTES.md`), the proposed trusted definitions (`PubEncoderModel.lean`,
sha `b918cd29`), the statements (`PubEncoderDraft.lean`, all `sorry`), built the lane against my `pous`, and confirmed the
proved game-independent lemmas (`denseScheme_encDec`, `segScheme_encDec`, `chainDense_encDec`, `auditSecure_seq_add`,
`meets_seq_add`) are on `[propext, Classical.choice, Quot.sound]`, no `sorry`. **Verdict: the model is faithful and
well-designed on all seven points; GO for proving on top of it. Nothing is false.** The seven checks:

1. **Order of randomness — right.** `E : Bits n → Ω → Coins → (pp*,C*)` sees `W`, the whole primitive `ω`, and the setup
   coins `r`, but **not** the check coins `ξ` (a separate `PubOutcome` coordinate drawn after `(pp*,C*)` is fixed). So the
   server *commits before the challenge* — the essential soundness ordering — and can't adapt `(pp*,C*)` to `ξ`.
   Preprocessing sees everything `(W,pp*,C*,r,ξ,ω)`, correctly (it is always post-setup). `E` seeing the whole `ω` is the
   standard unbounded-primitive idealization (as the decoder); the check reaches the primitive via `M.answer ω`. Correct.
2. **Transfer needs `[Subsingleton sch.Coins]` — correct and not too restrictive.** The public preprocessor sees `r`
   (a public encoder has no secret coins); today's does not. So the games coincide only when `r` is trivial — otherwise
   the public game is *strictly stronger for the adversary*, and a trapdoor/coin-bearing scheme rightly does **not**
   transfer. The deployed dense schemes all have `Coins := Unit`, so it applies to every milestone-1 instance. It is the
   *correct* condition, and intended, not an over-restriction.
3. **Idealized commitments — acceptable, same level as today.** The check reads the committed `W` and `(pp*,C*)`
   directly, and the audit reads the same `C*`. This idealizes `com_W` (SHA-256) and the Merkle root binding `C*` exactly
   as the per-block tags are already idealized in `Model/Scheme.lean` — no *new* idealization beyond the existing trusted
   layer. The standing caveat (com_W collision-resistance and Merkle binding are cited assumptions outside the model) is
   the same class as the current tag idealization. Acceptable.
4. **Completeness is in `PubMeets`, and the sanity lemmas are right.** `PubMeets` conjoins `V.Complete`, so a reject-all
   check *fails* `PubMeets` (it can't vacuously "meet" by rejecting everything). The three sanity lemmas correctly
   bracket it: `exactCheck_complete` (completeness from `Correct`), `honest_pub_seq_accepted` (the honest server+prover
   win with pr 1), and `acceptAll_not_pubAuditSecure` (an accept-all check *loses* when `δ+ε < 1`, so the check is
   load-bearing). This is exactly the anti-vacuity discipline I have been asking for — the check cannot be trivial at
   either end. (All three are `sorry`; the design is right.)
5. **`pubAuditSecure_exact_iff` captures "no weaker, no stronger."** Under `Correct`, `EncDec`, `Subsingleton Coins`:
   *no stronger* — acceptance of `exactCheck` forces `dec pp* C* = W`, and `EncDec` (`enc(dec …) = (pp,C)`) then forces
   `(pp*,C*) = enc W ω r`, i.e. the server's codeword *must* be the honest one, collapsing the public game to today's;
   *no weaker* — today's game is the `E = enc` instance of the public game, so public security (∀ `E`) implies it. The
   iff is the right formalization of "milestone 1 claims exactly today's security," and `EncDec`/`Correct`/`Subsingleton`
   are precisely the hypotheses each direction needs.
6. **k = 111 via monotonicity — sound.** `meets_seq_add` (proved) gives `Meets` at `k ⇒ Meets` at `k+j`: more sequential
   challenges only make the adversary's job harder (answering a superset), so `pr(win)` is monotone decreasing in `k`.
   The RO certificates (`dense_meets_64`, `seg_meets_14`, tight at `k=106`) therefore yield the `k=111` deployment
   requirement; the chain (`chain_meets_64`) is at `k=111` directly (its one-label loss makes 111 its tight point). All
   three instances land at a uniform `k=111`. Correct — and note the direction is right: 111 challenges is *more*
   security than 106, not less.
7. **Chain instance conditional on `ChainExPostFacto` — correctly flagged.** `chain_pub_meets_64` takes
   `(hepf : PousSponge.ChainExPostFacto)`, so `ChainPubMeets64` is conditional on the chain lane's open (and §35-amended)
   lemma, with no satisfiability witness here. That is the honest citation; the dense and seg instances are unconditional
   (RO model).

**Anti-vacuity of the game itself:** `PubAuditSecure(exactCheck)` is equivalent (point 5) to the real `AuditSecure`,
which is non-vacuous, so the target is neither trivially true nor empty; `E` is genuinely quantified over all servers,
and `exactCheck` reduces malicious servers to the honest codeword rather than ignoring them.

**Verdict (§38): GO for proving on top.** The trusted definitions (`Scheme.EncDec`, `SetupCheck`/`Complete`,
`exactCheck`, `PubEncoder`, `PubPreprocessor`, `PubOutcome`, `pubSimAccepts`/`pubSeqAccepts`, `PubAuditSecure`,
`PubMeets`) are faithful and correctly ordered; the transfer/iff/monotonicity/instance/sanity statements are the right
ones; the game-independent lemmas are proved on the standard axioms. Conditions to carry forward, none blocking: the
transfer/iff/instances/sanity lemmas are still `sorry` (this is a design review — the proofs are the next step); the
idealized-commitment bindings (`com_W`, Merkle root) are cited assumptions at the existing trusted-layer level; the chain
instance is conditional on the open `ChainExPostFacto` (§35); and, as with §31/§34's `segScheme`, moving these into the
trusted layer (`Pous/Model/PubEncoder.lean`, `Pous/Accounting/PubMeets.lean`) makes them pinned/audited — appropriate,
with the `pubAuditSecure_exact_iff` equivalence to `AuditSecure` as the faithfulness anchor. Overall verdict unchanged:
**GRANTED WITH CONDITIONS**.

## 39. Band-graph chain statement (`BandChainModel`, sha `ba654b0f`): faithful, and it answers my note's attacks — GO, with the D ≤ d cliff as a deployment condition (28 Sep 2026)

Statement review of the band-graph-over-overwrite-chain scheme (the idea from my note
`internal/chain-band-graph-plausibility.md`): one layer on `bandDAG B d` (node `v`'s parents `v−d…v−1`), decode
`min(v,d)+1` calls instead of dense's `v+1`. Statements-only file (all targets `def … : Prop`, no theorems; I built it,
0 `sorry`/`axiom`/`native_decide`). **Verdict: the statement is faithful and non-vacuous, and it directly and correctly
answers the three attacks I raised in the note; GO for proving on top. The one genuine caveat is the security cliff at
`D = d` (below), which the worker's `d ≈ 12` margin recommendation correctly addresses.** The four checks:

1. **`ChainClock` covers held partial chain states, including my held-intermediate-chaining-value shortcut — yes.**
   `ChainClock` quantifies over the *whole* `ChainKnow` holding `P₀` (labels `labs`, chaining values `hs` at any
   position, dropped `r`s), and states: a label known after `t` rounds is a **seed** of `P₀` or its own row has `≤ t`
   calls. A held chaining value `h_{v,j}` is a seed for row `v` (via `ChainKnow.seeds`, whose `card_seeds_le_size`
   already prices it `1 + c/ℓ ≥ 1`, §25), yielding at most label `v` — so it never beats storing `C_v`. This is exactly
   the shortcut I flagged as the main attack, and the statement neutralizes it by construction. `ChainClock` is the
   right generalization of the proved `chain_invariant` (it tracks the *clock* `ovCalls v ≤ t`, not just reach), and it
   is plausible for the reason my note gave: each row starts from its **own** `IV(dom v)`, so no holding for another row
   shortens row `v` (non-pipelinable). `band_game.py`'s `clock`/`partial` runs corroborate it.
2. **The gap attack is the only failure mode, and `d ≥ D` suffices for adversarial gap placement — yes.**
   `WeightedChainCert` (`s + |shortRows G VC D| < k → ChainHard`) makes the *only* non-priced way to know `≥ k` labels
   be "short rows" (`ovCalls ≤ D`). For `d ≥ D`, every row `v ≥ D` has `min(v,d)+1 ≥ D+1 > D` calls, so `shortRows =
   {0…D−1}` — exactly `D`, giving `chainDense`'s `(B−D−1, D, B)`-hardness (`BandChainHard`), **for every holding**: the
   per-row row-length bound is gap-placement-independent (distinct IVs), so adversarial spacing cannot help. This settles
   the "adversarial gap placement" worry from my note. Conversely `BandGapAttack`/`BandGapAttack512` prove `d ≥ D` is
   *necessary*: with `d+1 ≤ D`, holding all but the multiples of `d+1` frees `⌊(B−1)/(d+1)⌋` blocks (102 of 512 at
   `d=4, D=5`), refuting `(506,5,512)`-hardness. So the gap attack is precisely the failure mode, bounded by `d ≥ D`.
3. **`ChainExPostFactoG` is a faithful generalization, same RHS, §35 width — yes.** It is `ChainExPostFacto` with
   `Dense.completeDAG B`/`labelOv` replaced by any `G : TopoDAG B`/`labelG G`; the right-hand side is *identical*
   (`2^m·2·(nPos²·B·2)^{s+1}/2^{ℓ·s} + nPos²/2^{ℓ+c}`), with the collision term at the amended **`ℓ+c`** width (§35),
   not `2ℓ+c`. `ChainExPostFactoGSpec` (`ChainExPostFactoG → ChainExPostFacto`) confirms it specializes to the dense
   lemma (`labelG` on the complete DAG *is* `labelOv`). The shared `nPos B Q` is a sound (conservative) bound for any
   DAG, since `Σ_v ovCalls G v ≤ B(B+1)/2` (the complete-DAG count); the band's true position count is smaller, so `k =
   111` is inherited but possibly loose — fine for a statement. B5 is DAG-generic, so proving the ex-post-facto at this
   generality is the right move.
4. **No vacuity at degenerate parameters — checked.** `BandChainHard`/`BandGapAttack512` use `k = B = |univ|` (tight, no
   `k > B` vacuity), and require `D+1 ≤ B`; `BandNeedsRoom` (`¬ChainHard (bandDAG 1 1) univ … 0 1 1`) witnesses that
   `D+1 ≤ B` is necessary, mirroring §30's necessity discipline. The gap-attack prices are valid (a price-410 win also
   refutes the `s=506` hardness). No degenerate corner slips through.

**The cliff (the real caveat).** Unlike dense (complete-DAG, `≤D`-free for *any* `d`), the band is `(B−D−1, D, B)`-hard
**only while `D ≤ d`**; at `D = d+1` the gap attack frees a constant fraction (`BandGapAttack`). So band security carries
a *new deployment condition*: the effective round budget `D` must not exceed the in-degree `d`. The worker's
recommendation `d ≈ 12` (against `D = 5`) is the right response — a `7`-round margin against `D` growing (faster
hardware, more audit rounds) — and the decode is still `d+1 = 13` calls, ~20× below dense's ~256. I endorse the margin,
and flag that this `D ≤ d` fragility is the price of the band's cheaper decode and must be stated as a deployment
assumption (it is not a soundness gap in the statement — `BandGapAttack` makes the boundary explicit).

**Verdict (§39): GO for proving on top.** The band statement is faithful, non-vacuous, and answers all three attacks
from my note (held partial states via `ChainClock`+seeds; adversarial gap placement via the per-row bound; collision
width via §35). The open targets are the right ones: `ChainClock` (the weighted certificate's load-bearing core, a
plausible generalization of `chain_invariant`) and `ChainExPostFactoG` (the DAG-generic ex-post-facto, on which
`BandMeets64` is correctly conditional, inheriting the open `ChainExPostFacto`/§35). Conditions: prove `ChainClock` and
`WeightedChainCert`; `BandMeets64` stays conditional on `ChainExPostFactoG`; and the `D ≤ d` cliff is a deployment
assumption to document, with `d ≈ 12` as the recommended margin. Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 40. Band-graph proofs (`BandChain.lean`, sha `d7945f77`, 45 theorems): verified on my build — the proofs are correct; the decision rests on the cliff, not on any soundness gap (28 Sep 2026)

Verification of the landed band-graph proofs, for Daniel's decision on switching the secure-first scheme to the band
graph at `d = 12`. The statement file is unchanged since §39 (`BandChainModel.lean` still `ba654b0f`), so this is a proof
check against the statements I already reviewed. **Verdict: the proofs are correct and complete — I rebuilt them myself
and every named theorem uses only the three standard axioms with no `sorry`. The scheme decision turns entirely on the
cliff (a deployment-robustness trade-off), not on any soundness gap; the proofs faithfully establish exactly what §39
reviewed.**

**1. Independent build + axioms.** I compiled `BandChain.lean` against my `pous` (it imports the unchanged
`BandChainModel`), 0 `sorry`/`axiom`/`native_decide`, and `#print axioms` on all the load-bearing theorems —
`chain_clock`, `weighted_chain_cert`, `band_chain_hard`, `band_gap_attack`, `chainDense_hard_of_clock`,
`chainExPostFactoG_spec`, `band_meets_64`, and the witness/cliff theorems below — gives `[propext, Classical.choice,
Quot.sound]`, no `sorryAx`. Each is `theorem X : <Target>` for the §39-reviewed `Target` (`chain_clock : ChainClock`,
`band_meets_64 : BandMeets64`, etc.), so the proofs match the reviewed statements. I also read the core proofs:
`weighted_chain_cert` is `chain_clock` + `card_seeds_le_size` (known challenge labels ⊆ seeds ∪ short rows, `|seeds| ≤
s`), and `band_chain_hard` is it + `card_shortRows_band` (a band with `d ≥ D` has *exactly* `D` short rows, by
`le_antisymm`). Real, non-degenerate proofs.

**2. Deployment witnesses — correct and tight.** `band_hard_512` (`ChainHard (bandDAG 512 5) univ … 506 5 512`, `d=D=5`,
`k = B = |univ|` tight) and `band_hard_512_d12` (`d=12 ≥ D=5`) instantiate `band_chain_hard` at the deployment point;
`weighted_cert_hyp_512` shows `506 + 5 < 512` (`shortRows_512 = 5` exactly), so the certificate is used one below its
bound (full strength, non-vacuous). These confirm the hardness holds at `B = 512` for both `d = 5` and the recommended
`d = 12`.

**3. Cliff theorems — correct, and they bracket the decision.** `band_cliff_d5` (`¬ChainHard (bandDAG 512 5) … 505 6
512`) proves `d = 5` breaks one round past its in-degree (`D′ = 6`); `band_cliff_d12` (`¬ChainHard … 498 13 512`) proves
`d = 12` breaks at `D′ = 13`; and `band_d12_margin` proves `d = 12` is `(512−D−1, D, 512)`-hard for *every* `D ≤ 12`. I
checked the mechanism: each cliff is `band_gap_attack` + `ChainHard.mono` (a price-`B−⌊(B−1)/(d+1)⌋` gap-attack holding
refutes the higher-priced hardness), and the freed fraction (16.6% at `d=5`, 7.6% at `d=12`) exceeds the `1−ρ = 5.3%`
state-bound slack, so the gap-attack holding fits under the storage bound and wins — a genuine break, not a probability
degradation. So the theorems precisely establish: dense-level security for `D′ ≤ d`, catastrophic failure at `D′ = d+1`.

**4. Cross-check `chainDense_hard_of_clock` — sound and reassuring.** It proves the *same* weighted certificate, applied
to the complete DAG, reproduces dense's `(B−D−1, D, B)`-hardness (the complete DAG also has exactly `D` short rows). So
the new clock/weight machinery agrees with the existing `chainDense_hard`/`complete_hard` on the dense case — a real
consistency check that the generalization didn't drift.

**5. `chainExPostFactoG_spec` — right.** It proves `ChainExPostFactoG → ChainExPostFacto` by instantiating the generic
hypothesis at `G = Dense.completeDAG B` and rewriting `labelG_complete = labelOv`. So `ChainExPostFactoG` (the DAG-generic
form the band needs) is *strictly stronger* than the dense `ChainExPostFacto`: proving it discharges both. The prover's
claim that B5 is DAG-generic (so the generic proof is no harder) is plausible, but note this means the band's `Meets`
rests on the *stronger* open lemma — the same open obligation as dense, at greater generality.

**6. `docs/band-vs-dense.md` — accurate.** I verified the numbers: decode averages `5.97` (`d=5`) and `12.85` (`d=12`)
vs dense's `256.5`; work per segment `3057`/`6578` vs `131328` (43×/20× less); depth `6`/`13` vs `512` (85×/39× less);
`k = 111` over the chain (given `ChainExPostFactoG`), and **no** `k` in the random-oracle model (`b1_free_fraction`
rebuilds a constant fraction in one round — the band is chain-only, correctly stated); the cliff table (`d=5` breaks at
`D′=6`, `d=12` at `D′=13`, dense degrades gracefully with higher `k`); and the "larger `d` only moves the cliff; escaping
it fully means `d` near `B`, i.e. dense" caveat. The memo is honest and correct.

**Verdict (§40): the band-graph proofs are verified — correct, complete, on the three standard axioms, matching the
§39-reviewed statements, with sound deployment witnesses, cliff theorems, cross-check, generalization spec, and an
accurate comparison memo.** For Daniel's decision, the factual picture: switching to the band at `d = 12` buys ~20×
cheaper decode and ~39× less decode depth at the *same* `k = 111` and the *same* storage bound, resting on the *same*
open ex-post-facto obligation (in its DAG-generic form `ChainExPostFactoG`, which also yields dense's). The cost is a
**cliff**: unlike dense (which degrades gracefully), the band breaks *catastrophically* one round past `d` — a genuine,
machine-proved break within the storage budget — so it adds a hard deployment condition (effective `D ≤ d`), and the
`d = 12` margin gives ~2.2× headroom on the per-call timing floor before that condition fails. That robustness trade-off
(graceful dense vs cheap-but-cliffed band) is the decision, and it is a security-engineering judgment for Daniel; from
the red-team side there is nothing false and no hidden soundness gap — the band is exactly as sound as dense over the
chain, conditional on the same lemma, for as long as the `D ≤ d` timing assumption holds. Overall verdict unchanged:
**GRANTED WITH CONDITIONS**.

### §40 addendum — the band public encoder (`BandEncDec.lean` `f58d6945`, `BandPubEncoder.lean` `a51aca2c`)

Two files landed for `DISCREPANCIES.md` row B4 (carrying the band codec into the public-encoder game), queued for §40 in
`band-chain/NOTES.md`. **Verdict: both are correct — I rebuilt them against my `pous` and all their theorems use only the
three standard axioms with no `sorry`. Item 1 is a clean one-lemma, DAG-generic `EncDec` that covers band and dense
alike and adds no hypothesis; item 2 is a clean composition that meets the public-encoder requirement at deployment,
conditional on the same open `ChainExPostFactoG` as `band_meets_64` and nothing more. GO for both.**

**Item 1 — `BandEncDec.lean` (encode-after-decode, any DAG).** The load-bearing lemma is `labelG_dec`: for any
`TopoDAG N`, permutation `f` and codeword `C`, labelling the decoding of `C` returns `C`. The proof is strong induction
over the nodes (`WellFoundedLT.induction`) resting on `absorbedG_congr` — a row absorbs *only* its parents, which are
`G.par_lt`-earlier — so it is the honest port of dense's `labelOv_dec` to an arbitrary DAG, with no shortcut. From it,
`chainScheme_encDec` gives `EncDec` for the overwrite-chain scheme on *every* DAG (peeling `codeEquiv` with
`Equiv.symm_apply_apply`, then `labelG_dec`); `chainBand_encDec` is its band instance (row B4), and
`chainDense_encDec_generic` re-derives dense's own `EncDec` from the *same* lemma via `labelG_complete` /
`absorbedG_complete` (the complete DAG's row absorbs exactly what dense's `absorbed` does). That the one lemma reproduces
the existing `chainDense_encDec` is a genuine consistency check that the generalization didn't drift. **No new
hypothesis** appears beyond the `[NeZero B]` every scheme already takes (`neZero_512` discharges it at `B = 2^9`), so
there is no room for vacuity. The satisfiability witness `band_codec_bijective_512` proves the band codec is both
`Correct` and `EncDec` at the deployment point for `d = 5` *and* the recommended `d = 12`, i.e. `dec`/`enc` are inverse
bijections there — a real, checked instance, not an empty guard.

**Item 2 — `BandPubEncoder.lean` (the one new statement, `ChainBandPubMeets64`).** `ChainBandPubMeets64 d` is faithfully
`public-encoder`'s `ChainPubMeets64` with `chainBand (2^9) d 524288 512 (dom salt)` in place of `chainDense` and every
other parameter identical (`exactCheck`, `.sequential`, `D = 5`, `Q = 2^20`, `k = 111`, `ε = 2^-128`) — I diffed the two
`def`s. The theorem `band_pub_meets_64 (hepf : ChainExPostFactoG) (d) (hd : 5 ≤ d)` is the clean composition
`pubMeets_exact _ (chainBand_encDec …) (band_meets_64 hepf d hd salt)`: it takes §40's already-verified band `Meets`,
supplies item 1's `EncDec`, and transfers through the §38-reviewed public-encoder machinery. It introduces **no new
assumption** — its only hypothesis is `ChainExPostFactoG`, inherited verbatim from `band_meets_64`, so the band's public
encoder rests on exactly the same open obligation as the band's `Meets` and no more. `band_pub_meets_64_d5` and
`band_pub_meets_64_d12` are the deployment witnesses; the `Subsingleton (chainBand …).Coins` instance (coins `= Unit`)
is what lets the exact check apply.

**Trusted-model dependency and a §38 strengthening.** The transfer relies on `pubMeets_exact` /
`pubAuditSecure_exact` / `pubAuditSecure_exact_iff` from `public-encoder/PubEncoder.lean` (now `5946ed41`) over the
proposed trusted definitions in `PubEncoderModel.lean` (`b918cd29`, unchanged since I reviewed it in §38). Worth
recording: in §38 those three transfer theorems were `sorry`; in `5946ed41` they are **proved**, and my build confirms
`PousPub.pubMeets_exact`, `pubAuditSecure_exact` and `pubAuditSecure_exact_iff` all depend only on
`[propext, Classical.choice, Quot.sound]`. So the §38 "next step for the prover" is now discharged on the standard
axioms, which retroactively strengthens the §38 GO: the public-encoder game's `Meets`-transfer is no longer an
assumption but a theorem.

**Independent build + axioms.** I copied both files (sha-matched to the store: `f58d6945`, `a51aca2c`) into
`~/chainepfverify`, compiled them against my `scratch6-pous` on top of the reviewed `DenseReCert` / `PubEncoderModel` /
`PubEncoderDraft` / `PubEncoder` / `BandChain` chain (0 `sorry`/`axiom`/`native_decide` in either file), and ran
`#print axioms` on `labelG_dec`, `chainScheme_encDec`, `chainBand_encDec`, `chainDense_encDec_generic`,
`band_codec_bijective_512`, `band_pub_meets_64`, `band_pub_meets_64_d5`, `band_pub_meets_64_d12` and the three
`PubEncoder` transfer theorems — every one gives `[propext, Classical.choice, Quot.sound]`, no `sorryAx`. This matches
`NOTES.md`'s claim (12 new theorems on the standard axioms, `leanchecker --fresh BandPubEncoder` exits 0) and confirms no
existing file was changed (`BandChain.lean` still `d7945f77`, statement file still `ba654b0f`).

**Verdict (§40 addendum): GO for both items.** The band codec's encode-after-decode is a faithful DAG-generic lemma
that adds nothing beyond `[NeZero B]`, and `ChainBandPubMeets64` is a faithful restatement of `ChainPubMeets64` for the
band, proved by a clean composition that inherits *only* the open `ChainExPostFactoG` — the same concrete-H obligation
the whole chain lane already carries (the proof by `bc-35b053cc` is pending and will be reviewed when it closes). So if
Daniel adopts the band at `d = 12`, its public-encoder deployment is on exactly the same soundness footing as its
`Meets`: correct today, conditional only on `ChainExPostFactoG`. Overall verdict unchanged: **GRANTED WITH
CONDITIONS**.

## 41. `PinFamily` is closed: `CreditResolvedTyped`, `ZeroAdviceLucky` and `N10′` at the lucky instances are proved with no remaining hypothesis — the §36/§37 conditions are genuinely discharged, on the three standard axioms (28 Sep 2026)

The P3 decode prover (`bc-4b3abaed`) reports `PinFamily` on the split chain is proved, closing the last gap of the
lucky-guess line I have tracked since §29/§32/§33/§36/§37. **Verdict: confirmed — GO. I rebuilt the whole `freshness`
package myself (53 modules, 0 failures) and `#print axioms` on all four final theorems, every load-bearing intermediate,
the glue chain and the non-vacuity witnesses gives `[propext, Classical.choice, Quot.sound]` with no `sorryAx`; there is
no `sorry`/`admit`/`axiom`/`native_decide` anywhere in the directory. The three §36/§37 conditions — split order, the ι
case table, the Rc2/Rx2 distinct-atom check — are each discharged by a real proof, not restated as a hypothesis, and
nothing is vacuous. `PinFamily` is a theorem (`PousKnowledge.pinFamily`), so `CreditResolvedTyped`, `ZeroAdviceLucky` and
`N10primeAtIf okLucky posLucky` follow unconditionally.**

**Independent build + axioms.** I refreshed all 53 `Freshness/*.lean` from the store into `~/freshverify2` (the
`Pebbling`/`HintCard` inputs are byte-identical to the store, so I reused their oleans) and did a clean topological
rebuild against my `scratch6-pous` — `built=53 failed=0`. `#print axioms` on `PousKnowledge.pinFamily`,
`PousAssembly.creditResolvedTyped`, `PousAssembly.zeroAdviceLucky`, `PousAssembly.n10prime_lucky`, on the intermediates
`realize_eq`, `pool_Rsrc`, `c_pin`, `pin_of_cf`, `group_pins`, `group_hrel`, `tokens_eq`, `φ_injOn`, `pinsAt`,
`self_mem_Cls`, on the glue `creditResolvedTyped_of_pinFamily` / `zeroAdviceLucky_of_creditResolvedTyped` /
`n10prime_of_pinFamily`, and on the witnesses `okLucky_one` / `adaptiveMinEntropy_empty` / `pinsAt_example` /
`example_hyps` — all 21 report the three standard axioms and nothing else. This matches the prover's fresh audit #22
(2295 declarations, 237 pins).

**1. The type-I row (my §37 focus) — discharged.** `realize_eq` (`LuckySem`) computes each source's chain variable at
its realization as its honest value. In the `P1`/`P2` type-I case it realizes via the *inverse* honest query (`k = 4`/`5`
= `qI1`/`qI2`), so the variable is the inverse answer `(ω''.2 …).symm (c1 …)` = `P⁻¹(c¹_w)`, which it rewrites to the
honest `in1`/`in2` by `c1_eq`/`c2_eq` and `Equiv.symm_apply_apply`. The `valG` side (`valG_c1a`, `LuckyGroupSem`) then
shows the relations read `c¹` from the right atom in *both* the type-I and non-type-I branches (`c1a_cases`). This is a
real computation from the query answer, not a restatement — exactly the framing the prover corrected me on in §37 (type
I = `qI1 w` asked strictly before any `qP1` round), now carried through honestly.

**2. Freshness uses the split order and nothing else (§36 / §10) — discharged.** `pool_Rsrc` (`LuckyGroupC`) proves every
present source's realization has `Pool ≥ 2^{nwc} − n·Q`, by cases on the source, and each case's "partner query is absent
before the realization" obligation is met by the split ordering: type-F forward slots by `fwd_before_inv`, type-I inverse
slots by `inv_before_fwd`, and a hit's `qInvIn` by `fwd_before_inv` against the `hitsBy` filter's "`qInvIn` not asked by
`r_h − 1`" clause. Those two ordering lemmas come from `fA_split_fwd`/`fA_split_inv` — a forward first-ask lands in the
first half-round, an inverse in the second — which *is* the `splitProg` order of §36. Nothing here re-assumes the gap; it
consumes the split-chain construction that landed in §36.

**3. The `C(u,i)` timing / the ι case table (§37) — discharged.** `c_pin` (`LuckyGroupC`) pins every component of `P2[u]`
at its realization when `tokC u` holds, and it discharges the two exclusions I asked about in §37: for a T1/T2-credited
top it shows the credit round is no later than the realization by contradiction through `not_credit_of_inGame` (had
`qP2 u` been asked by round `r`, `u` would already be in the game and not credited at `r+1` — this is E8); for an output
it uses `typY2_of_output` to force type Y (E10), hence Part B (`2·D·n·Q ≤ RP2`), where `c2_eq_of_output` applies. The ι
case table itself is realised concretely: `tok_part` and `comp_part` (`LuckyGroupCount`) map the token conditions onto
the 13 relation kinds exhaustively and disjointly, and `tokens_eq` (`LuckyCover`) turns that into the *equality*
`luckyUnits = Σ tokG + Σ tokC` (using `cred3_lowerWhole = ∅` and the complementary `tTop`/`tokC` split of `topWhole`).

**4. The token identity is an equality — confirmed.** `tokens_eq` is a genuine equality, not an inequality slack: it
proves `cred3` credits no whole lower label (`cred3_lowerWhole = ∅`) and that `tTop u` and `tokC u` are complementary on
`topWhole`, so each credited top contributes its `n` tokens to exactly one of `G(u,·)` or `C(u,·)` — none dropped, none
double-counted.

**5. Injectivity across group kinds and the Rc2/Rx2 distinct-atom check — discharged.** `φ_injOn` (`LuckyCover`) is
injective because realizations of distinct present sources differ (`Rsrc_injOn`), and the one cross-kind clash `P2[u]` is
excluded structurally: `G(u,·)` samples `P2[u]` only for type I (`fI2`), `C(u,·)` only for type F/Y (`¬fI2`)
(`p2_not_sampled`). The Rc2/Rx2 distinctness lives in `LuckyGroupCount`: `rx2_exclusive` (E8) shows at most one of the
three `qP2` rules fires, `ka_injOn` shows a group's atoms have distinct realizations, `group_count` bounds `tokG` by the
sampled atoms in the GF(2) span via `pinned_count` (an honest finrank argument in `LuckyRank`: `|A| = 8` dimensions cap
the raising relations), and `double_top_tkey` — named "Rc2 against Rx2" — proves a same-round credited top and key land
on distinct atoms (the top's `c²` tokens go to `C(u,·)` via Rc2 on `P2[u]`; no `G(u,w)` samples `P2[u][w]`, so the key's
Rx2 tokens sit elsewhere). This is the §28 double-count risk closed by a proof.

**6. Few is `≤ 6n`, comfortably under the `32n` asked.** `Jf_few` routes the nonempty indices through
`srcAll`'s realizations, and `card_srcAll` bounds that by `6·n` (4n non-hit sources + ≤ 2n hits); the `PinsAt` slot only
needs `≤ 32n`, so there is 5×+ headroom.

**7. Non-vacuity — witnessed.** `self_mem_Cls` proves every class contains `ω` (class-fixedness is never over an empty
set); `okLucky_one : okLucky 1 32 (2^15)` shows the target's restriction is satisfiable; `pinsAt_example` /
`example_hyps` (`LuckySplitWitness`) exhibit an instance meeting `PinFamily`'s hypotheses on the split chain; and
`adaptiveMinEntropy_empty` gives the `S = ∅` base. The per-group semantic facts (`group_hat`, `group_hrel`,
`group_pins`, `realize_eq`, `pool_Rsrc`, `c_pin`, `pin_of_cf`) are *theorems*, so — unlike the DecodeHyp3 episode of
§28/§29 — none is an assumed hypothesis that could be vacuously false. `CreditResolvedTyped` is unchanged from my
§33/§36/§37 review (the per-typed-class M8d form: `0 < n`, the `64·n·Q_tot ≤ 2^{nwc}` pool bound, `∀ c, Bounded`, and for
every `(S,H)` a `PrefixDet`/`Fibre` counting chain with `2^{bits} ≤ 2·∏ w`), and `N10primeAtIf okLucky posLucky` is a
genuine probability bound over all `A₁,A₂` — non-vacuous because `okLucky` is satisfiable. This is the correctly-resolved
form of the N10 lesson: the target is now *proved*, at `pos = 10n`, with the `(2n)²/2^{nwc}` collision term, rather than
posited as a named hypothesis.

**Verdict (§41): GO.** `PinFamily` is a real, non-vacuous, standard-axiom theorem on the split chain, and it discharges
each of the three §36/§37 conditions by proof rather than restatement. The lucky-guess line
(`PinFamily → CreditResolvedTyped → ZeroAdviceLucky → N10′` at the lucky instances) is closed with no remaining
hypothesis — the last named assumption I had been guarding (`AdaptiveMinEntropy`, §32) is now bypassed by a proved chain.
This closes the P3 obligation I flagged at §29; what remains for the wider P3 scheme is downstream assembly, not this
lemma. Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

### §41 note — `ChainExPostFactoG` bad-fit analysis (`bc-35b053cc`): the `Pr[Bad]` fit holds, no statement change, and it does *not* repeat the §35 collision-width error

Alongside §41 I sanity-checked the dense/band prover's argument (`internal/p3-instantiation/chain-epf-badfit-analysis.md`)
that `ChainExPostFactoG` needs no statement change: the `Q·nPos/2^ℓ` label-guessing term is absorbed into the
compression term as label freshness, and `Pr[Bad] ≤ nPos²/2^(ℓ+c)` fits the existing collision term. **Verdict: it
holds — no gap, so no message to `bc-35b053cc` is warranted.** The reasoning, checked against the store code
(`sponge-dense/SpongeModel.lean`, `ChainEPFTranscript.lean`):

- The RHS already carries `2^m · (nPos³·2/2^ℓ)^(s+1) + nPos²/2^(ℓ+c)`; the collision term is the §35-amended `2^(ℓ+c)`
  width (the file even comments it as "erratum to red-team §25"), and `nPos B Q` is the complete-DAG position count, a
  valid upper bound for any DAG (band included), so the DAG-generic reuse changes no term.
- The decomposition is the right one and is *conservative in exactly the direction §35 was not*: the ℓ-bit
  parent-label coordinate is handled by freshness/compression (a fresh correct label is an ex-post-facto prediction the
  `(…/2^ℓ)^(s+1)` term already pays for, counted per *distinct* label ≤ the storage bound, so the naive `Q·nPos` factor
  collapses — robust to a band node having up to `d` parent slots), while only the `(ℓ+c)`-bit chain-state coordinate is
  charged as a collision. **[Superseded — see the §41-note erratum below: the chain-state coordinate must *also* be a
  compression item, not a collision term.]** It never widens the collision space to `2^(2ℓ+c)` to buy improbability from
  the block, which was the precise §35 miss; a per-coordinate union bound only over-counts.
- The one genuine correction the prover self-flagged is real and I confirmed it in the code: `obsKey`/`bcond` are
  currently key-based (`bcond` checks `keyAt = v`, but a query slot shows the label `ovR x = C_p`), so query-slot
  freshness cannot fire and item 1 would leak as a real `Q·nPos/2^ℓ` term unless made label-based. The proposed fix
  (show/compare the label, i.e. `keyAt ⊕ Wb`) is bound-preserving because `Wb` is a known fixed shift — XOR by it is a
  bijection on the shown value, and `realPt`/`pr[Coll]` are about the points, not the shift.

So the fit is sound *contingent on* the label-based correction landing and the compression continuing to count distinct
fresh labels against the storage bound (not per query/parent-slot). Those are the load-bearing points; the final word is
the machine-checked `ChainExPostFactoG` (that the collision term stays `2^(ℓ+c)`, `bcond` is label-based, and the axioms
are standard), which is already queued to join §40 when it closes.

### §41-note erratum — the chain-state coordinate is a compression item, not a birthday collision (from `bc-35b053cc`'s `chain-epf-chaining-fresh-gap.md`, 28 Sep 2026)

While building `mem_reach_of_asked`, `bc-35b053cc` found that my §41-note (and their own `chain-epf-badfit-analysis.md`)
mis-classified the chaining coordinate. **I confirm the correction: I was wrong to charge the `(ℓ+c)`-bit chain-state
`h` as a birthday collision term. It must be a width-`(ℓ+c)` *compression* item. The RHS is unaffected — it already
carries the mixed-width compression term — so the statement still needs no change, but the reasoning in the §41-note
bullet above is corrected here.** I re-derived both points against the store code:

- **Why `h` is not a birthday for the real adversary.** The full adversary is `A₂ (A₁ π)`; `A₁` reads `π` and can encode
  a real chaining value into its `m`-bit advice, so "a query's `h` equals an as-yet-underived real chain state" is
  *engineered*, not a coincidence. It is `2^{-(ℓ+c)}` only per *fixed* advice `σ`; over the `2^m` advice strings it sums
  to `2^m·nPos²/2^(ℓ+c)`, which the RHS does **not** carry and should not. So `h` cannot sit in a small π-only `Bad`; it
  is a compressed fresh item exactly as a held label is — the same move my §41-note applied to the label coordinate, now
  also required for the chaining coordinate. This is driven by **deep blocks**: `ovCalls G v = |parents| + 1`
  (`SpongeModel.lean:549`), so at `D = 5` every block `c ≥ 5` is deep (`ovCalls > D`) on both the complete DAG and band
  `d = 12`, and ≥ 106 of the `k = 111` challenges are deep. A deep block is unreachable in `D` `ChainKnow` rounds from
  labels alone (`canCall` needs `(v,j−1) ∈ hs`, one call/round), so an adversary wins it by *holding an intermediate
  chaining value* — a valid strategy that `ChainKnow.size` prices at `1 + c/ℓ` and `ChainHard` quantifies over. A
  labels-only reduction holding cannot invoke `ChainHard` on deep blocks; this is a genuine implementation gap.
- **The RHS absorbs the width-`(ℓ+c)` items.** `NOTES.md:283–289` already types fresh items as `key`/`r` (width ℓ) or
  `h` (width `ℓ+c`), ≤ `s+1` items, total `> ℓ·s` bits, each holding with prob `2·2^{−width}`, under
  `2^m·2·(nPos²·B·2)^(s+1)/2^(ℓs)`. Crediting a chaining item only `ℓ` in the `2^(ℓs)` denominator is a safe
  under-count, and it is in fact *exact per unit of size*: a chaining item costs `(ℓ+c)/ℓ` in `ChainKnow.size` and saves
  `ℓ+c`, i.e. `ℓ` saved per unit size — the same rate as a label — so total saving `≥ ℓ·s` for any mix, and the surplus
  ">`ℓ·s` bits costs at most one label" is the `+1` in `s+1`. The `1 + c/ℓ` chaining price was calibrated precisely for
  this. Naming (`nPos²·B` / `nPos³`) is generous enough to enumerate `(block × call × position)`, and the only π-only
  collision term stays `¬NoColl` (`nPos²/2^(ℓ+c)`, no `2^m`).

**Verdict on the gap: `bc-35b053cc`'s accounting is right, the RHS genuinely absorbs width-`(ℓ+c)` items, and the
statement (`ChainExPostFacto`/`ChainExPostFactoG`) needs no change.** The gap is in the (label-only) implementation; the
fix is the parallel chaining-fresh layer (`bcond_h`/`bEv_h`/`pr_Ev_h` pinning `ovH(π x) = h` at width `ℓ+c`, `P₀`
carrying `hs` seeds, a mixed `card_Ev`/minimal-`(s+1)` argument), and their option 1 (incremental, reusing the landed
label layer) is the right call. This does not disturb the §40 verdict, whose `band_meets_64` was already conditional on
the still-open `ChainExPostFactoG`; I will review the chaining-fresh layer when that proof lands. Delivered directly to
`bc-35b053cc` as `internal/p3-instantiation/chain-epf-chaining-fresh-redteam-verdict.md`.

## 42. P3 `Meets` at 64 KB (`p3_meets_64_D10_final`, `D = 10`, `k = 117`): unconditional and verified — plus the `JointClassWeight` erratum (the 14 GB lemma is false, but the 14 GB `Meets` is not refuted) (28 Sep 2026)

Two parts, per the review brief: the one-segment 64 KB headline (unconditional, built on §41's `pinFamily`), and the
14 GB joint core. **Verdict: the one-segment finals are a GO — I rebuilt them and both `p3_meets_64_D10_final` and
`p3_meets_64_D12_band16_final` are `Pous.Meets` with no hypothesis on the three standard axioms. The 14 GB path is
*conditional* and its proposed sufficient lemma `JointClassWeight` is FALSE (I verified `bc-4b3abaed`'s counterexample);
but `JointClassWeight` is an open `def`, not a proved theorem, so no false statement exists in the Lean, and the 14 GB
`Meets` / `ZeroAdviceLuckyMulti` target is not refuted. The single-segment layer (§41, `class_weight_of_typed`, and the
64 KB headline) is untouched by the cross-segment defect.**

### Part A — the one-segment 64 KB headline: GO

**Independent build + axioms.** I built `Thm1`, `PebblingCol` and `PebblingMeets` on top of my §41 `Freshness`/`Pebbling`
build against `scratch6-pous`, and `#print axioms` on `p3_meets_64_D10_final`, `p3_meets_64_D12_band16_final`,
`okLucky_deploy`, `okLuckyMulti_deploy`, and the conditional 14 GB theorems all give `[propext, Classical.choice,
Quot.sound]` — no `sorryAx`. This is a *load-bearing* check here: `pous/PousTargets.lean` declares
`theorem1_ii_seq := sorry` as a placeholder, so a sorry-free `Meets` confirms the build resolves
`@PousTargets.theorem1_ii_seq` to the thm1-family **proof** (`Thm1.Theorem1iiSeq`), not the pous placeholder.

**The glue is a genuine assembly, not a restatement.** `p3_meets_64_D10_final = p3_meets_64_lucky_at _ n10prime_lucky
theorem1iiSeq 10 10 le_rfl band_twoWay_220_12`. Inside `p3_meets_64_lucky_at` (`P3MeetsLucky.lean:165`): it discharges
`Meets`'s five conjuncts (`ε ≤ εMax` by `le_rfl`, `Correct`, `CodeHoldsW`, `SpaceBound expansion`, and `AuditSecure`),
building the `AuditSecure` bound by feeding a `TimedINC` instance — `p3_timedINC_R` from `segBoundR_of_lucky`, which
consumes `n10prime_lucky` (§41) + `okLucky_deploy` + the `ColumnHard` certificate — into the **trusted**
`Pous.Pinned.Theorem1iiSeq` (`theorem1iiSeq := @PousTargets.theorem1_ii_seq`), then closes with `stateBound_64`,
`sampling_64lucky` and `union_termW`. So the chain `pinFamily (§41) → n10prime_lucky → segBoundR_of_lucky → TimedINC →
Theorem1iiSeq (trusted) → Meets` is real, and the band certificate `band_twoWay_220_12 : ColumnHard (bandGraph 220 12) 10
220 3` (proved by `band_columnHard_twoWay` + `decide`, not vacuous) supplies the hardness.

**`okLucky 220 2384 (2^20)` is what it says, and holds.** `okLucky n wc Q = 0 < n ∧ 2^15 ≤ Q ∧
64·n·(n·(Q+1)+2n) ≤ 2^(n·wc)`; at `n = 220, wc = 2384, Q = 2^20` the pool term is `≈ 2^42 ≤ 2^(220·2384) = 2^524480`,
discharged by `okLucky_deploy` (sorry-free). Its `n = 220, wc = 2384, Q = 2^20` match the deployed scheme
`p3SchemeR 2384 (bandGraph 220 12)` (band on `n = 220`, `wc = 2384`).

**The `Meets` parameters match the trusted statement.** `Meets` is `Pous.Meets` (`pous/Pous/Accounting/Params.lean:42`):
`ε ≤ εMax ∧ Correct ∧ CodeHoldsW ∧ SpaceBound expansion ∧ AuditSecure sch reveal (stateBound ρ) D Q k (ofReal δ) ε`. The
final gives `reveal = .sequential`, `D = 10`, `Q = 2^20`, `k = 117`, `ε = 2⁻¹²⁸ = εMax`, at `stateBound ρ`, `δ`. Since
`gameDepth D = D` (`TweakedDraft.lean:76`, the §22 fix), `gameDepth 10 = 10` matches the certificate's depth. The `D = 12`
fallback `p3_meets_64_D12_band16_final` is the same with `band_twoWay_220_16 : ColumnHard (bandGraph 220 16) 12 220 3`.

**Part A verdict: GO.** The 64 KB one-segment `Meets` is unconditional relative to the ideal model `p3ModelT` and the
trusted `Pous.Meets`, sorry-free on the standard axioms, faithfully parameterised, resting only on the §41 chain that I
already certified. (Aside: the auxiliary `P3MeetsT` is off the finals' import closure and does not build in my setup —
it still uses a `(D+1)/2` game-depth that the current `gameDepth = D` lemmas reject; it is not in `All.lean`'s targets
and does not affect the finals.)

### Part B — `JointClassWeight` is false (erratum to my in-progress §42), but the 14 GB `Meets` survives

`bc-4b3abaed` found (`internal/p3-decode/joint-class-weight-counterexample.md`) that `JointClassWeight`
(`P3MeetsFinal.lean:174`) is false. **I verified it against the code and concur.**

**The counterexample is correct.** At `N = 2, n = 1, wc = 24, D = 3, Q = 2^15` (which satisfies `okLuckyMulti` —
`64·(2·1)·(2·(2^15+1)+4) = 8 389 376 ≤ 2^24`), each segment `s`'s single program asks `H` then `P⁻¹` at the *other*
segment `s'`'s honest input (revealing `z0_{s'} = P_{t_{s'}}⁻¹(x_{s'})`), then `P` forward at its own tweak on that
answer. On the event `E = {z0_0 = z0_1, z0_s ≠ hin_s, c2_s ≠ L₀}`, each segment gets a hit at `t = (0,0)`: `hitAt (p s)`
(`Lucky.lean:53`) requires only `¬ Asked (p s) (qInvIn_s t)` — its *own* family — and `p s` never asks the inverse at its
*own* tweak (it asked the other's), so the hit counts, even though `p s'` did ask it. Each hit adds `n·wc` to
`luckyBits`, so `jointLuckyBits = 2·n·wc = 48` while `|S| = 2`, and the single coincidence `z0_0 = z0_1` (probability
`2^{-n·wc}`) buys `2·n·wc` credited bits. The class weight is then
`Σ_{jointLuckySet = S} 2^{jointLuckyBits} ≥ |E|·2^{48} ≈ |Ω|·2^{24} ≫ 8·|Ω| = 2^{|S|+1}·|Ω|` — an overshoot of
`≈ 2^{n·wc − 3}`, and the same attack scales to the deployment. The defect is precisely per-family `hitAt`: `Asked` is
per program family, so a cross-segment inverse query is invisible and two segments credit the same event. Confirmed
against `hitAt`/`hitsBy`/`z0`/`qHit`/`qInvIn` and `okLuckyMulti`.

**No false theorem exists in the Lean.** `JointClassWeight` is a `def : Prop` (an open hypothesis); every use is
`(hj : JointClassWeight) → …`. The audit shows those conditional theorems (`p3_meets_multi_64_D10_of_jointClassWeight`,
`zeroAdviceLuckyMulti_of_jointClassWeight`) are sorry-free *implications* — valid, but now with an unsatisfiable
hypothesis, so that route is dead. `jointClassWeight_one` (the `N = 1` case) stays true and sound: at one segment the
inverse and the hit are in the same family and `hitAt` excludes it, so it is not the general statement and does not
become a false witness. **The prover correctly left `JointClassWeight` unproved** — this is the satisfiability discipline
from §29 working as intended: an open named hypothesis was falsified before anyone proved it.

**The 14 GB `Meets` survives, conditionally.** It was never unconditional: `p3_meets_multi_64_D10_of_joint` is conditional
on `ZeroAdviceLuckyMulti`, and `JointClassWeight` was only one *proposed* sufficient route to it. That route is dead; the
target `ZeroAdviceLuckyMulti` is **not** refuted, for a real reason I checked: the over-credited hits are on shallow
tweaks whose honest input `x_t` is cheap, they reveal only `x_t` (not a top label), and the counterexample programs
return a constant and *do not win* (`WinZMulti` fails). `ZeroAdviceLuckyMulti` bounds *winning* families, so useless
correlated hits do not touch it; a hit that helped win would be on a deep tweak, which needs the other segment to compute
a deep `x_t` — exactly what hardness forbids without paid luck. So the 14 GB headline remains a conditional result that
now awaits a *correct* joint-accounting lemma rather than the false `JointClassWeight`. And the single-segment layer
(§41 `pinFamily`/`creditResolvedTyped`, `class_weight_of_typed`, and Part A's 64 KB `Meets`) is entirely unaffected: the
defect needs `N ≥ 2` cross-segment queries.

**The proposed fix (pending review).** `bc-4b3abaed`'s §5 proposes crediting each segment against *all* segments'
programs run in parallel (`ps_s c` runs every `p s' c` concatenated, with `p s c`'s output), under union typing in a
common slot space `n·(NQ+N+1) ≤ N·Q_tot`. This makes a hit count only if *no* program asked the inverse first, which
kills the counterexample, while keeping coverage (`ps_s`'s knowledge ⊇ `p s`'s) and the existing union-bound counting.
The direction is right and matches how §20 handled cross-block distinctness structurally. `internal/p3-decode/joint-accounting-proposal.md`
has **not landed yet**; I will review the redefinition (the parallel-composition combinator and its `Asked`/rounds/slot
lemmas, union-typed transfers, the re-assembled joint `J`, and non-vacuity) when it appears, applying the §29
satisfiability-witness rule to the new named lemma before calling it non-vacuous.

**Verdict (§42): the 64 KB one-segment `Meets` is GO (unconditional, standard axioms); the 14 GB `Meets` is intact as a
conditional result; the `JointClassWeight` lemma is withdrawn as false (verified), with no soundness cost to the Lean
because it was never proved.** Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 43. The joint-accounting redefinition (`JointAccountingDefs.lean`: `parFam`/`psJ`/`jointLuckySetJ`/`JointClassWeightJ`) and the pinned refutation (`JointClassWeightFalse.lean`): GO, with the §4 proof and §6 witnesses as conditions (28 Sep 2026)

`bc-4b3abaed`'s reply to §42: a Lean refutation of the old `JointClassWeight`, and a replacement built on joint
accounting (`internal/p3-decode/joint-accounting-proposal.md` §1–§3). **Verdict: GO. On my own build I confirmed the
refutation applies to the *real* p3-meets statement (by `rfl`) and is a complete proof on the three standard axioms; the
replacement definitions are faithful, kill the counterexample while keeping coverage, and union typing is sound for the
`N = 971` union bound; `JointClassWeightJ` is plausibly true and its §6 witness plan meets the §29 rule. The conditions
are the still-unwritten §4 proof and §6 witnesses — the defs are the right thing to land now.**

**The refutation hits the real statement, and is sorry-free.** `JointClassWeightFalse.lean` restates `okLuckyMulti`,
`jointSlot`, `jointLuckySet`, `jointLuckyBits` and `JointClassWeight` verbatim (it cannot import p3-meets, which imports
it). I verified the bridge myself: `PousP3Meets.JointClassWeight = PousJointRefute.JointClassWeight := rfl` and
`PousP3Meets.okLuckyMulti = PousJointRefute.okLuckyMulti := rfl` both typecheck, so
`¬ PousP3Meets.JointClassWeight` follows from `not_jointClassWeight` in one line, and both depend only on
`[propext, Classical.choice, Quot.sound]` — no `sorryAx`. The proof is genuine: `shift_count` (post-composing `P_t` by an
XOR shift is a permutation of `Ω` fixing everything not reading `P_t`, so `P_t(x)=b` is a `1/M` share) gives
`card_good : M²·|E| ≥ (M−2)·|Ω|`, hence class weight `≥ 2^{48}·|E| ≥ (2^{24}−2)·|Ω| > 8·|Ω| = 2^{|S|+1}·|Ω|`. So the §42
counterexample is now machine-checked against the exact statement.

**§1 definitions are faithful.** `par2`/`parList`/`parFam` are honest lock-step composition (per round `qs ++ qs'`,
answers split `take`/`drop`; `parFam` extracts program `i`'s output). Because the ideal oracle is stateless,
`run (psJ p s c) = run (p s c)` — lock-step changes no program's view — so `psJ p s` is faithfully "segment `s`'s output
with everyone's knowledge." `honestSlots` is `luckySet`'s honest part (`luckySet_eq_parts` is `rfl`); `jointLuckySetJ`
unions the segments' honest+hit slots in the *common* composed slot space and places outputs at `(c, N·Q+1+s)`;
`jointLuckyBitsJ = Σ_s luckyBits (psJ p s)`. All compile and match the proposal.

**§2 kills the counterexample and keeps coverage.** `hitAt (psJ p s)` now requires `¬ Asked (psJ p s) (qInvIn_s)` —
*no* program asked `P_s⁻¹(x_s)` — so the counterexample's cross-segment inverse makes `hitsBy (psJ p s) = ∅` and the
shared event is credited to neither segment (and a hit at tag `s` lands only in segment `s`'s bits). Coverage survives:
`run (psJ p s c) = run (p s c)` carries `WinZ` for `p s` to `psJ p s`, so `luckyBits_ge` still gives
`WinZMulti → Σ_s luckyBits (psJ p s) ≥ N(k−X)·n·wc`; joint knowledge only removes shared spurious hits, never a genuine
winning credit (reconstructing a deep top label in `D` rounds is lucky relative to everyone — the `ColumnHard`/game-depth
bound does not improve with more queries on other tags).

**§2/§3 union typing is sound for the `N = 971` union bound.** `jointLuckySetJ ⊆ range n ×ˢ range (N·Q+N+1)` of size
`n·(NQ+N+1) = nNQ+nN+n ≤ N·(n(Q+1)+2n) = N·Q_tot` (since `nN+n ≤ 3nN` for `N ≥ 1`), and `|jointLuckySetJ| ≤ 9nN`, so
`sum_choose_le_two`/`choose_ten_ge` at `nN` apply as in the current glue. Union (not tuple) typing is sound because every
query carries a tag (a `P_t` tweak, or an `H` key domain `domP3 tag …`) and tags are injective, so a slot names at most
one segment, recoverable from the prefix — all the transfers need; the tuple would cost `≈ N^{9nN}`, far beyond the
`pos = 10nN` slack.

**`JointClassWeightJ` is plausibly true, and §6 meets the §29 rule.** §4 is the §41 `pinFamily` argument on one joint
chain (common Part A, per-segment Part B), with the no-cycle fix that every credit is luck relative to all programs — the
exact defeat of the counterexample — and pool `≥ M − n·NQ ≥ M − N·Q_tot` (`okLuckyMulti`). §6 commits to Lean witnesses:
hypotheses satisfiable (deploy + the refuting instance), `jointClassWeightJ_one` (`N=1` from `class_weight_of_typed`), the
counterexample neutralized (`hitsBy (psJ) = ∅`), a *positive* non-triviality witness (`N=2`, one idle segment, one real
credited hit at probability `1/M`, `jointLuckyBitsJ = n·wc`), and non-vacuous coverage — the satisfiability discipline
applied correctly.

**Conditions (gate calling `JointClassWeightJ` proved/non-vacuous; do not block adopting the defs):**
1. The §4 proof and §6 witnesses must land before p3-meets swaps in `_of_jointClassWeightJ`; today only the defs compile
   and no theorem is claimed, which is correct. I will review both when they land, applying §29 before calling the lemma
   non-vacuous.
2. Watch three load-bearing new pieces: the composition lemmas (`run (psJ) = run (p)`, `Asked (psJ) ↔ ∃ s', Asked (p s')`,
   `(D, N·Q)` boundedness); the joint chain's non-interference ("a Part B move of segment `s` changes only tag-`s`
   points" — needs injective tags to isolate each `P_t` domain, proved not assumed); and the union-typed transfers via
   tag decoding *up to the prefix* (the §37-style framing point).
3. Adopt by import (not copy) so `okLuckyMulti`/`JointClassWeightJ` have one source, and mark the old `JointClassWeight`
   refuted (as `DecodeHyp3` is), since the dead `_of_jointClassWeight` theorems still reference it.

**Verdict (§43): GO** — the refutation is confirmed against the real statement on standard axioms, and the joint-accounting
replacement is faithful, closes the defect, preserves coverage, and is sound for the union bound, with a §29-compliant
witness plan. Delivered directly to `bc-4b3abaed` and `bc-58ec406e` as
`internal/p3-decode/joint-accounting-redteam-verdict.md`. Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 44. `ChainExPostFactoG` assembly (`ChainEPFV3`/`Final`/`Assembly`/`Birthday`/`Reach`, `bc-a359729a`): the assembly is GO, conditional only on the two v3 compression deliverables — interim verdict, with one required fix to `ExistsBEvU` and one stale file (28 Sep 2026)

`bc-a359729a` has assembled `ChainExPostFactoG` (the last gate for the MVP headline), conditional only on `bc-35b053cc`'s
two v3 compression deliverables `ExistsBEvU` and `PrEvMixed` (still being built). **Interim verdict: the assembly is
correct and kernel-clean — I rebuilt the whole stack and `chainExPostFactoG_of_v3` (and the band/dense `Meets`
corollaries) use only the three standard axioms, resting only on those two hypotheses. The RHS is `ChainExPostFactoG`'s
exactly, the degenerate cases are handled, and the obs-round freshness redefinition is faithful to B5 and fixes the v1
holes. TWO items must be fixed before the two v3 theorems land: (a) `ExistsBEvU` is unprovable as stated and needs a
`validItem` hypothesis; (b) `ChainEPFReachCounterexample.lean` is stale against the updated `ChainEPFFresh`.**

**Build + axioms.** I refreshed all `sponge-dense` + `band-chain` sources into `~/chainepfverify` and rebuilt. The six
assembly files (`ChainEPFItem`, `ChainEPFReach`, `ChainEPFBirthday`, `ChainEPFAssembly`, `ChainEPFFinal`, `ChainEPFV3`)
compile, and `#print axioms` on `chainExPostFactoG_of_v3`, `band_meets_64_of_v3`, `chain_meets_64_of_v3`,
`compressionHyp_of_v3`, `chainExPostFactoG_of_compression` and `pr_Bad_le` all give `[propext, Classical.choice,
Quot.sound]` — so the assembly is conditional only on `ExistsBEvU`/`PrEvMixed` (which are hypotheses, not axioms).
`ChainEPFMixed`/`ResampleT`/`StableT`/`StableT2` (bc-35b053cc's in-progress `exists_bEvU`/`pr_Ev`) do not build yet —
expected.

**1. Faithful defs; `PrEvMixed` satisfiable; `ExistsBEvU` needs a fix (§29).** `V3.kindRound`/`icond`/`brelU`/`bEvU`
restate the v3 contract verbatim, and `ExistsBEvU`/`PrEvMixed` match the contract's `exists_bEvU`/`pr_Ev`. `PrEvMixed` (a
probability bound over a sorted pattern) is satisfiable. **`ExistsBEvU` is not, as stated:** it quantifies over arbitrary
`F : Finset (ItemKind B)`, but `bEvU` needs `φ.Pairwise (brelU R)` (a strict `kindRound` order), which requires
`kindRound` injective on `F` — and it is not. I verified in Lean that `.label v` and `.chaining v (ovCalls G v)` are
distinct items (widths `ℓ` vs `ℓ+c`) with **equal** `kindRound` (both `itemRound v (ovCalls v)`, because `xin_pad` makes
the pad chaining share the label's point), and `icond` does not exclude the pad chaining item. So an `F` with both can
meet the hypothesis yet admit no sorted `φ`. **Fix:** add `(∀ k ∈ F, R.validItem k)` to `ExistsBEvU` and the contract's
`exists_bEvU`; on valid items `kindRound` is injective, and `compressionHyp_of_v3` already builds `F` from `freshHolding`
(valid) and already proves `hvalid` — it just needs to pass it. This keeps the `rfl`-match with `ChainEPFMixed`. Delivered
to `bc-a359729a`/`bc-35b053cc`.

**2. RHS matches `ChainExPostFactoG` exactly, with factor-2 slack.** `chainExPostFactoG_of_compression` proves
`ChainExPostFactoG` directly (so the RHS matches by construction — confirmed by typecheck), splitting
`pr[win] ≤ pr[win ∧ NoCollU] + pr[Bad]`, with `pr[Bad] ≤ nPos²/2^(ℓ+c)` (`pr_Bad_le`, no `2^m`, a genuine first-collision
`swapTo` bound) and the compression term. The proved compression bound is `2^m·(nPos²·B·2)^(s+1)·2^(−ℓs)`, exactly half
the stated first term `2^m·2·(nPos²·B·2)^(s+1)/2^(ℓs)` (`hfinal`'s `le_mul_of_one_le_left`), so the reported factor-2
slack is real and conservative.

**3. Degenerate cases handled.** `B = 0` (nothing answered, `win` impossible since `0 < k`), `2·nPos > 2^ℓ`
(`rhs_ge_one`: `2^ℓ ≤ nPos²·B·2`, so RHS `≥ 1`), and `0 < k` forced by `hard` at the empty holding. All present in
`chainExPostFactoG_of_compression`.

**4. Freshness redefinition (obs-round, B5-style) — correct; v1 counterexample genuine.** The v1 `bfreshLabel`/
`bfreshChaining` ("unasked before `itemRound ≥ D`" = never asked by an adversary) were refuted by `bc-a359729a`'s decoy
attack (`ChainEPFReachCounterexample`: `B=2`, `D=1`, ask `realPt 1` and decoy `xin 1 1`; `¬Bad` holds, yet block 1 leaves
the reach by `chain_clock` — my §39/§40-verified lemma). The fix is B5's shape: `icond` shows a value "no later than the
first round that asks it" (`∀ ρ < τ`, `τ` the showing round), and a label may be shown as itself **or** its key
(`v' = labelG v ∨ v' = keyAt v`), which also closes the second hole (inverse queries reveal `keyAt`, not `labelG`).
`ChainEPFFresh` now carries this (sha `6eef98c0`). **Stale file:** `ChainEPFReachCounterexample.lean` still destructures
the *v1* `bfreshLabel` and no longer compiles against the updated `ChainEPFFresh` (`error: Function expected at hno`); its
logic is sound but it should restate v1 locally (as `JointClassWeightFalse` does) or be dropped, else it breaks a folder
`leanchecker`.

**Verdict (§44, interim): the assembly is GO** — correct, kernel-clean, RHS-exact, with sound degenerate handling and a
faithful B5-style freshness fix, conditional only on `ExistsBEvU`/`PrEvMixed`. Before those two land: fix `ExistsBEvU`
(add `validItem`) and the stale counterexample file. When `ChainEPFMixed` lands with `V3.x = x` by `rfl` (and
`exists_bEvU` proved with the `validItem` hypothesis), I finish §44 and §40 together — that closes the concrete-H
obligation for the band and dense deployments. Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

### §44 addendum — `PrEvMixed` needs the carried-reveal pattern (`bc-35b053cc`'s peel gap): the gap is real, the fix is sound — GO for v4 (28 Sep 2026)

`bc-35b053cc` reports that `PrEvMixed` cannot be proved with the v3 `Pos × ItemKind` pattern (pin the recomputed
`itemPoint`, chain-order peel), and proposes the carried-reveal pattern (`internal/p3-instantiation/chain-epf-prev-gap.md`).
**Verdict: I agree on both questions — the gap is real, and the carried-reveal fix (their option A) is sound with the
naming inside `nPos²·B`. Proceed to v4; my §44/§40 close will apply to the v4 definitions.**

- **The gap is real.** `card_Ev_snoc` peels the chain-latest item `t` by resampling its recomputed point
  `z_t = xin v_t p_t`; obligation (b) then needs `z_t` unasked before *every shorter* item's observation round `τ_s`, but
  `icond` only gives it unasked before `t`'s own `τ_t`. `NoCollU` doesn't close the gap: the adversary can learn
  `chainH v_t (p_t−1)` from an **output** h-coincidence (`ovH(π x) = ovH(π(xin v_t (p_t−1)))` for some asked `x`) and ask
  `z_t` early. `NoCollU` forbids only distinct chain **inputs** coinciding (a pure-π property), whereas this is an output,
  **adversary-dependent** coincidence — outside both `NoCollU` and the pure-π birthday `pr_Bad_le` bounds. So a π sits in
  `bEvU(φ++[t]) ∧ NoCollU` while the resample moves `o_s`'s transcript, and the `card_Ev_snoc` injection is not total. The
  *bound* `PrEvMixed` is true; the itemPoint / chain-order peel is the wrong vehicle. (This is precisely the obstruction
  the v3 contract pre-flagged and bc-a359729a's "point 2".)
- **The carried-reveal fix is sound.** Peeling by **reveal round** `κ_r` and pinning the **raw** revealed point makes the
  max-`κ` item unasked before every shorter item's `τ_s ≤ κ_s ≤ κ_t` by construction — so the output-h shortcut that
  broke chain order is irrelevant, closing (b) with only `NoCollU`. Asked items pin a fixed transcript point (preserved by
  `realAt_inl_resampT`, no cascade); never-asked items (`κ_r = kindRound ≥ D`) pin `itemPoint` and peel chain-latest among
  themselves via `xin_stable`; `κ` orders the mixed case away. The RHS stays exact (single `nPos²/2^(ℓ+c)`, `pr_Bad_le`
  untouched). **Naming fits:** the element is `(o, r, row)` with the item **read off `r`** (not separately enumerated), so
  the two positions give `≤ nPos²` and the `Fin B` row makes it `nPos²·B` — matching the RHS's per-item `nPos²·B`, exactly
  B5's "read the node off `realAt`", and avoiding the `|Pos|²·M` (`M ≤ B(B+1)/2`) blowup that would exceed `nPos²·B` for
  `B > 1`. Their alternative (B) (enlarge `NoCollU`/`Bad`) is correctly rejected: the shortcut is adversary-dependent, not
  a pure-π birthday, and risks a `2·nPos²/2^(ℓ+c)` collision term.
- **Status.** The existence half is done and wired: `ChainEPFMixed` (`081cde66`) proves `exists_bEvU` with the §44
  `validItem` signature, and `example : ExistsBEvU := …` type-checks (bc-35b053cc), on the standard axioms. The remaining
  work is bc-35b053cc's carried-reveal `RevPos`/`realAtR`/`bEvU`/`icond` and the mixed `pr_Ev`, plus bc-a359729a's `rfl`
  update of `ChainEPFV3`'s pattern-element type and re-glue of `compressionHyp_of_v3`/`card_names_le`. When those land I
  close §44 and §40 against the **v4** definitions, checking that the carried-reveal `bEvU`/`PrEvMixed` are faithful and
  that `chainExPostFactoG_of_v3` becomes unconditional on the standard axioms.

### §44 erratum — the carried-reveal `PrEvR` (v4) is FALSE; three holes and a peel-order dilemma; the fix is a new technique (28 Sep 2026)

**I retract the §44-addendum GO on the carried-reveal `PrEvR`.** The realized v4 `PrEvR` (`ChainEPFCarry` + `ChainEPFV3`
`7d82caec`) is false as stated — I confirmed three independent refutations/obstructions and then a change of proof
technique. The peel *principle* I approved (round-order, raw reveal) was right in direction, but the realized `icondR`
violated "raw only, and a prediction not a derivation" in ways I did not catch, so my GO was premature.

- **`not_prEvR`** (`bc-58ec406e`, `PrEvRCounterexample.lean`, machine-checked): the v4 chaining `icondR` branch requires
  only `obsKeyH` show `ovH(π z)` for `z` the query's *raw revealed point*, with no tie to an honest position. An inverse
  query `Π₂⁻¹(y)` has `z = π⁻¹ y` and shows `ovH y = ovH(π z)` trivially, so the item holds for every `π` (prob 1 vs the
  claimed 1/5). Confirmed at the `icondR` definition. **Derived, not predicted.**
- **The label cascade** (`bc-35b053cc`, §05:45Z): the adv-*label* branch clause `z = realPt π v` recomputes `realPt`
  (`= xin v (ovCalls v)`), which a labeller-chaining peel (`resampH` at `xin v p_t`) changes — so the label item fails
  preservation. `NoCollU` can't exclude it (output-`h` shortcut; option B rejected). **Raw-only violated.**
- **The two-form hole** (`bc-a359729a`, `ChainEPFCarryAdvCounterexample.lean`, machine-checked): a label item accepts
  `v' = ovR(π z) ⊕ Wb v ∨ v' = ovR(π z)` without the name recording which, so one item pins to two values at `≈ 2/2^ℓ`
  (> `1/(2^ℓ − nPos)`). **Naming/width double-count.**
- **The peel-order dilemma** (`p3-concrete-peel-order.md`): observation stability needs reveal-order peeling; pin
  stability needs chain-order; inverse queries make the two incompatible (B5 avoided this only with forward queries). And
  tying items to honest inputs (to fix `not_prEvR`) reintroduces the cascade — the two constraints pull opposite ways. No
  single peel order survives inverse reveals.

I delivered the first two verdicts as `internal/p3-instantiation/prevr-false-redteam-verdict.md` (retracting the v4 GO;
the two v5 constraints; the three "derived-not-predicted" P3-side routes — `Π₂⁻¹` answers, `P⁻¹` keys, reversed-top
columns).

**The resolution (coordinator decision, `proof-technique-decision.md`): drop peel-and-count for a shared lazy-sampling
technique — I GO it on all four points.** (1) Union over the `2^m` advice strings `σ` (at fixed `σ`, `A₂(σ)` is
deterministic and `π` uniform — the sound home for advice-driven predictions); (2) lazy-sample `Π₂`/`P` (forward *and
inverse*), each first-decided answer uniform over unused values so a fresh item is bounded by `1/(2^w − used)`,
`used ≤ nPos` — inverse queries become genuine fresh samples, dissolving `not_prEvR`; (3) freshness defined *online* as
non-derivability in the game's own round-by-round closure (`ChainKnow`/`P3ChainKnow.reach`), which covers all three holes
at the root (freshness = derivability, not observation form) — including knowledge-dependent derivations (the 06:25Z
`pin2 u`/`key²` case); (4) the RHS is unchanged — `2^m` on the compression term, pure-`π` honest-input coincidences only
in `nPos²/2^(ℓ+c)` (no `2^m` on the collision), exactly my §41-note resolution. Verdict delivered as
`internal/p3-instantiation/lazy-sampling-technique-redteam-verdict.md`.

**Two load-bearing obligations I will not sign off without, at each proof:** (a) *closure completeness* — the game closure
must capture every derivation (`sim`: values shown are fresh or in `reach … τ`, answers become knowledge one round later),
else a "fresh" item is actually derivable and two items share a deciding sample → the product bound over-counts → the tail
is false; (b) *RHS-fit* — every match charged either under `2^m` (prediction) or in pure-`π` `nPos²/2^(ℓ+c)`, with no
residual `2^m·(collision)` term (that would be a statement change, which I would flag). On the current design I see no
statement change. Next: review the `lazy-perm/` API when `bc-a359729a` posts it, then each `pr_EvR`/`P3ChainEPF` proof.
The ChainEPF close (§40/§44) and everything conditional on it (`band_meets_64`/`band_meets_14`, the P3 `_of_v3`/`_of_prEvR`
wrappers) stay conditional on an *open, currently-false-as-stated* obligation until the lazy-sampling `pr_EvR` lands.

**Band `pr_EvR` v5 case table (06:15Z) — GO to build.** `bc-35b053cc`'s case table + online-freshness + fixed-σ reduction
is complete and sound for the one-permutation band game: every `{forward, inverse, labeller, guess} × {labKey, labLabel,
chain}` cell is covered (the absence of `P`/reversed-top rows is correct — those are P3-side), the three holes are
dissolved at the root, and both my conditions hold. **Independence** is the load-bearing claim and it is sound: each fresh
item's deciding sample is the single Π₂ sample at its honest point `xin v p`, so `NoCollU` (distinct chain inputs, π-only)
makes distinct items' deciding samples distinct — no sample decides two. This works because the band is *whole-value*
(every fresh quantity is a whole Π₂ answer part, no component/transpose structure). **RHS fit:** every row is a per-σ
prediction (under `2^m`) or the π-only `NoCollU` collision (`nPos²/2^(ℓ+c)`); no `2^m·collision` term. One open naming
detail (`kind ·3` vs the `·2` fold-by-observation fallback) — not a soundness issue. Verdict delivered as
`internal/p3-instantiation/band-prevr-casetable-redteam-verdict.md`. Build-time obligations I'll hold it to: closure
completeness formalized (`mem_reach_of_asked_obs`), independence proved via `NoCollU`, naming `≤ nPos²·B`, standard axioms.

**§46 closure gap (heads-up, re-review queued).** `bc-58ec406e` found `P3ChainKnow` (my §46 GO) misses a derivation:
`pin2 u = transpose(c¹)_u ⊕ key²_u` holds *component by component*, so `P⁻¹(c²_u)` yields components of `key²_u` that the
whole-key game's closure does not see — a component-wise derivation that, left uncredited, would let the EPF proof count a
*derived* key² component as a *fresh* prediction (over-count → false tail). This is exactly my closure-completeness
obligation instantiated; my §46 GO checked the game's faithfulness/hardness/`k=106` but not closure completeness against
component-wise derivations, so I did not catch it. It does **not** touch the band (whole-value, no columns). The
coordinator chose fix (A): add top-key components to the game, restating `P3ChainHard`/`P3ChainCert`/both targets, with the
final `Meets` and `k = 106` unchanged. **Queued: §46 re-review against the restated model** when it compiles, requiring the
P3 case table to show independence per *component* sample under the enlarged closure. Overall verdict unchanged: **GRANTED
WITH CONDITIONS**.

**`lazy-perm` library (`LazyPerm` `201d2162`, `LazyPermRounds` `42fd8822`) — GO.** The shared probability backend for the
lazy-sampling technique is proved; I rebuilt it (Mathlib-only) and audited 15 load-bearing declarations, all on the three
standard axioms (or a subset), no `sorry`, with a non-vacuous witness (`Example.prob_le_half`). All five points are sound:
(1) faithful oracle — `Oracle = ∏_i Perm(α i)` uniform (independent uniform per component), `ans` forward `π i x`/inverse
`(π i).symm y`, correct `Fresh`/`dom`/`rng` for both directions; (2) `card_step_le` correct — per history-fixed fiber the
fresh answer is uniform over `N − used ≥ N − n`, giving `≤ |T|/(N−n) ≤ a/b` via `(N−k)!` counting, forward and inverse
alike, with `pin_mul_le` yielding the `(2^w − nPos)⁻¹` per item; (3) `card_hits_le`/`prob_hits_le` telescope
`card_step_le` over a *fixed* finset `J` of distinct steps → `∏ (a_j/b_j)`; (4) global-step-index naming closes the
adaptivity gap (the deciding step is deterministic, `J` fixed) within `nPos·#kinds ≤ nPos²·B`; (5) the `ofRounds` locating
lemmas (`ofRounds_hist`/`_next`/`_next_tail`, `roundsSeq_eq`, `roundQs_eq_trace = trace`) hold. The library correctly
*exposes* — as client hypotheses I will verify per proof — the two red-team conditions: distinct named steps (independence
/ "no sample decides two items", per component on the P3 side) and `Fresh` ⇐ online game-closed freshness (closure
completeness), plus steps `< nPos`. Verdict delivered as `internal/p3-instantiation/lazy-perm-library-redteam-verdict.md`.
Next: §46 (A′) re-review when it compiles, then each `pr_EvR`/`P3ChainEPF` proof against this API.

**Fresh-prediction bridge (`LazyPermFresh` `6082e346`, `bc-58ec406e`): GO, with a P3 parameter flag.** I rebuilt it
and audited `prob_pattern_le`, `prob_fresh_le`, `sum_patterns_le`, `prob_fresh_width_le`, `inv_sub_le` and
`prob_exists_le`: all are on the three standard axioms, with no `sorry`. A scratch witness (a `Fin 8` permutation, one
forward query, target `{7}`) discharges every hypothesis of `prob_fresh_width_le` together. Its winning event is
satisfiable and the conclusion is a non-trivial `≤ 1/2`, which meets §29.

1. **The union is sound.** The realized pattern `X.image (name π)` lies in the fixed, `π`-independent set
   `patterns nPos Adm`, and each fixed pattern's event mentions only `(step, kind)`. Dependence of names on `π` or on
   the other items is absorbed by the union. Because `T` is typed `K → History → Qry → Finset`, a target cannot depend
   on the answer or on anything later, except through the paid-for kind. That rules out the `not_prEvR` "derived, not
   predicted" hole class by construction.
2. **Distinct steps are preserved.** `DistinctSteps` is exactly injectivity of `Prod.fst`, so `kd` is well defined.
   `prob_hits_le` runs over the fixed `P.image Prod.fst`, `prod_image` uses `hP`, and `InjOn (name π) X` keeps the width
   sum intact.
3. **Constant fit.** The band fits easily (`|K| ≤ nPos·B`, whole items, `h2` immediate). P3 at `(220, 2384)` fits: the
   budget is `14n·log₂ nPosC + n·wc ≈ 610K` bits, and even with subset kinds (`|K| ≈ 4·2^n`) the fit holds for
   `s + 1 ≤ 2 432`. The natural count is `s + 1 ≤ 3n + (k−X) ≤ 880`, costing about 221K bits; multi fits likewise.
   One item per column (`≈ 23 100` items) would not fit, even with width-only kinds. So the item-count bound (one item
   per honest sampled point, thin items only from `c¹`/`key²`/`pin2`) is a load-bearing P3 obligation. **As stated
   (`∀ wc > 0`), the P3 targets cannot be discharged by the bridge.** `h2` needs `2·nPosC ≤ 2^wc`, which `0 < wc` does
   not give, and subset kinds need roughly `4n ≲ wc`. I flag a possible statement change: add a parameter hypothesis in
   the style of `n ≤ 2^255`. It is harmless for the finals, since it is discharged at `(220, 2384)` and leaves `Meets`
   and `k = 106` unchanged.
4. **Explicit inputs: yes.** `h_distinct`, `h_fresh`, `h_target` and `h_lt` (and `hT`, `h2`, `hX`, `hwin`) are all
   explicit arguments. They map onto my independence, closure-completeness and positions conditions.

Verdict delivered as `internal/p3-instantiation/lazy-perm-fresh-bridge-redteam-verdict.md`. The overall verdict is
unchanged: **GRANTED WITH CONDITIONS**.

**`bEvV5'` product bound is FALSE (bc-35b053cc, 07:14Z): confirmed. Erratum to my 06:15Z band case-table GO. The key
rule is proved equivalent. The P3 check is done; v6 is pending.**

- **The counterexample.** I reran `bevv5-product-bound-mc.py` and all four rows reproduce exactly (2.6×–139×). My own
  lazy-sampling simulator, which reads the events off `icondV5'`/`bEvV5'`/`NoCollU`, gives 2.6×, 23×, 27× and 118×.
  - The event `π(xin 2 2) = y₁` alone implies the pattern, at about `2^{−(2ℓ+c)}`, while the product claims
    `2^{−2(ℓ+c)}`.
  - `ChainExPostFactoG` is not threatened: the attack wins worse than guessing.
- **My miss.** In the 06:15Z table I endorsed independence through `NoCollU` ("each item is decided at its honest
  point's own sample"). That is false for inverse-first samples, whose match is decided at upstream samples that other
  items can share. I also passed the I-yield row on a closure that `icondV5'` never built.
- **The `ChainKnow` key rule (label ⇒ pad `r`).** The gap bc-a359729a found is real for the freshness closure.
  - I rebuilt `BandChainKeyRule` (`7afbf22b`) on standard axioms. `toChainHard` is sound, so the switch is a
    weakening.
  - I proved the converse in scratch, `chainHard'_of_chainHard`, for every DAG and all parameters. It works by a seed
    swap: each seeded `h` at or above the pad is replaced by `h_{v,pad−1}`, at no extra price, and the domination is
    round by round. So `ChainExPostFactoG' ↔ ChainExPostFactoG`.
  - Through `chainExPostFactoG_of_chainExPostFactoG'`, the existing `band_meets_64`, `band_pub_meets_64`, dense
    `chain_meets_64` and band-multi `band_meets_14`/`band_meets_14_k106` transfer verbatim at unchanged numbers, all
    kernel-checked on standard axioms. No statement changes in content, and nothing needs restating.
- **P3.** The inverse-rule closure is genuinely implemented: `onlineH`/`Kon` over the full (A′) `P3ChainKnow`,
  `simOn` by construction, and both halves of each `Π₂⁻¹` payload shown. `P3ChainKnow` has the label-to-key rules
  (`P⁻¹`, and per component through `kc`/`pc`), so there is no key-rule gap.
  - The P3 case table does have the band's *charging* hole. Rows `H`/`R`/`K1`/`K2`/`L-lab` charge an inverse-first
    item at its honest point's own sample; only the top rows charge upstream.
  - The bridge's explicit `h_fresh` would make that a stuck proof, not a false bound. The unlanded `P3Client` item
    design must add upstream charging.
- **v6 is not yet posted.** My checklist: (a) freshness closed under `ChainKnow'`; (b) charge at the later of the
  inverse step and the upstream fixing sample; (c) chains of inverse hits, and merged names per step; (d) the
  counterexample as a regression test; (e) RHS fit; (f) axioms and §29.

Verdict delivered as `internal/p3-instantiation/bevv5-and-key-rule-redteam-verdict.md`, with
`key-rule-seed-swap-redteam.lean` and `bevv5-independent-lazy-check-redteam.py` beside it. The overall verdict is
unchanged: **GRANTED WITH CONDITIONS**. The ChainEPF close (§40/§44) waits on v6.

**Band v6 design (`band-v6-design.md` `65143c09`, bc-fd23893e): NOT GO yet. Three blocking fixes and four
corrections, all local; no statement change.**

- **What passes.** The history-backed determined set (item (g)); the label/key fold, so no same-round double credit;
  "later of" charging; full-value targets with exact cardinalities; the width accounting.
- **The regression.** My simulator at bridge-valid parameters (`ℓ ≥ 6`): v6's charges meet their product (ratios
  0.52–0.73), while v5's still fail (2.1×–15.9×).
- **F1 (blocking).** The design targets `PrEvR`, which is refuted twice in the store (`not_prEvR`). `CompressionHyp2`
  hardwires v3's `freshHolding`, which contains the I-yield item. v6 needs its own per-advice statement over its seed
  holding, with new glue to `ChainExPostFactoG'`, in the shape of P3's `FreshTail`/`p3ChainEPF_of_tail`.
- **F2 (blocking).** The step-order scan lets a round-τ answer suppress a round-τ guess's credit. Then
  `VCround(τ) ⊆ reach'(τ+1)` is false: a same-round parallel guess of `h(v,p)` runs two calls in one round,
  uncharged. Round-τ commitments must be classified against pairs of rounds `< τ` before any round-τ answer. This
  also removes a same-coordinate collision in §4's merge.
- **F3 (blocking).** Names omit the pointer: the show position at producer steps, the chain position at inverse
  steps. The fit is `3(|Pos| + |posSet|) ≤ nPos·B`, which holds for `B ≥ 4`, so small `B` needs a direct argument.
  `σ` is used for both the advice and a slot table.
- **F4–F7 (corrections).**
  - F4: list every seed in the online prefix up to the cutoff (at most `s + 1`), and compute targets from the listed
    seeds only.
  - F5: "producer" means the step where the coordinate becomes determined.
  - F6: the §7 instance is two slots (ℓ at the inverse step, ℓ+c at `S2(2,1)`), not one `rh` slot.
  - F7: `2·nPos ≤ 2^ℓ` is a trivial case split, not a hypothesis.

Verdict: `internal/p3-instantiation/band-v6-design-redteam-verdict.md`. The overall verdict is unchanged:
**GRANTED WITH CONDITIONS**. The ChainEPF close still waits on a revised v6.

**Band v6 design, revised (`1f3a2ca4`): GO, with two design edits.**
- **F1–F7 are fixed.** The design has its own `BandFreshTail`, with glue to `ChainExPostFactoG'`; round-causal
  `VCcredit`; pointers in the names; the prefix listing; producer = determining step; the two-slot regression; and
  the trivial branches.
- **G2 (§3.2).** The inclusion must be `VCcredit(τ) ⊆ reach'(Seeds≤τ) τ`, with no slack. It holds, since round-τ
  pairs are excluded, and a win at depth `D` needs `reach' D`.
- **G1 (§6).** An `rh` slot can need two show pointers: a non-hit inverse query's r-part plus a separate forward
  query's h-part, both charged at the sample of `xin(v,p)`. So the uniform-`|K|` closed form fails. Count per seed
  instead: `prob_fresh_le` with a per-kind weighted sum, where an `rh` slot's budget is `(nPos²·B·2)²`. The same form
  applies to the `B ≤ 3` lemma.

Verdict: `internal/p3-instantiation/band-v6-design-rereview-redteam-verdict.md`.

**G3 added (~10:45Z): truncate at the cut. Erratum to F4.** bc-58ec406e's P3 instance transfers to the band. A
listed seed can be charged at a post-listing program inverse step whose pair identification needs an unlisted seed,
so listing alone is not enough. The fix fits the band's tight right-hand side:
- per-pattern truncation `S_P`, cut at the latest show step among `P`'s items, which adds no extra factor (an explicit
  cut union would cost about `nPos`);
- charge *every* seed of the truncated run, since each extra seed pays for its name when `2^ℓ > nPos²·B·2`;
- widen the trivial branch to `2^ℓ ≤ nPos²·B·2`.

The verdict is now GO with G1–G3 written into the design. Addendum in the same verdict file.

**Confirmed (`2f67d15d`): G1–G3 are folded in correctly** (per-seed `M^d` names, the no-slack `reach'(τ)`,
per-pattern truncation with all-seed charging, and the widened trivial branch). GO for charging and naming. One
wording clarification: the realized pattern is taken at the first crossing step, so `cut(P(π)) = c(π)`.

## 45. `JointClassWeightJ` is proved (`JointGlue.jointClassWeightJ`, `bc-4b3abaed`): my three §43 conditions are discharged by real proofs, the §6 witnesses hold — the 14 GB P3 lemma is closed (28 Sep 2026)

`bc-4b3abaed` has proved `JointClassWeightJ`, the corrected joint class-weight lemma I reviewed as an open `def` in §43
(with conditions) after refuting the original `JointClassWeight` in §42. **Verdict: GO. On my own build,
`PousJointAccounting.jointClassWeightJ : JointClassWeightJ` is a theorem on the three standard axioms, proving the exact
§43-reviewed statement (`JointAccountingDefs.lean` unchanged, `example : JointClassWeightJ := jointClassWeightJ`
typechecks). All three §43 conditions are discharged by genuine proofs — none restated or assumed — and the §6 witnesses
are proved. This closes P3 at 14 GB at the lemma level; the remaining step is `bc-58ec406e`'s mechanical wiring of the
headline (`_of_jointClassWeightJ`), not a soundness gap.**

**Build + axioms.** I built the seven new files (`JointCompose`, `LuckyK`, `JointTransfer`, `JointChain`, `JointPins`,
`JointGlue`, `JointWitness`) on my §43 freshness build. `#print axioms` on `jointClassWeightJ`, on the condition lemmas
(`run_psJ`/`asked_psJ`/`bounded_psJ`, `c1T_congr_tag`/`c2T_congr_tag`/`partB_congr_tag`/`fibreJ`,
`ktransfer_typed`/`ktransfer_joint`) and on the witnesses (`jointClassWeightJ_one`, `hitsBy_psJ_pJ_empty`,
`card_hitEvent`) all give `[propext, Classical.choice, Quot.sound]` — no `sorryAx`, no new axiom.

**§43 condition 1 — composition lemmas (`JointCompose`).** `run_psJ : run (psJ p s c) = run (p s c)` (by induction on
`par2`/`parList`), `asked_psJ : Asked (psJ p s) ω q r ↔ ∃ s', Asked (p s') ω q r`, and `bounded_psJ` (`(D, N·Q)`-bounded,
depth `≤ D` via `zipAll`, work the sum). Real lemmas that subsume the p3-meets side; this is the "same output, joint
knowledge" foundation the whole reduction rests on.

**§43 condition 2 — non-interference by injective tags, proved not assumed (`JointChain`).** This was the load-bearing
point I flagged. It is genuinely proved: `c1T_congr_tag` and `c2T_congr_tag` are **well-founded recursions on the node**
(`termination_by v.val`, `decreasing_by G.par_lt`) establishing that `c¹`/`c²` at tag `τ` read `H` only at keys with
`k.1 = τ` and `P` only at tweaks with `t.1 = τ`. `partB_congr_tag` lifts this to "a segment's Part B is fixed by its
tag's points" (`AgreeTag`), and `agreeTag_updH`/`agreeTag_movF` show a resample of a different segment's variable changes
no tag-`τ` point. `fibreJ : Fibre XJ PoolJ` consumes `Function.Injective tags` (`tags_ne_of_lt`) to keep every earlier
segment's Part B across a segment's moves. So non-interference is derived from the label definitions by recursion, not
posited.

**§43 condition 3 — union-typed transfers decoded up to the prefix (`LuckyK`/`JointTransfer`).** `KTransfer` bundles the
three facts the single-segment pins need (honest/hit/out), each stated from the prefix at the transferred query's first
round; `LuckyK` re-proves the pins (`realize_eqK`/`group_hatK`/`group_hrelK`/`c_pinK`/`Jf_*K`) for any `KTransfer`.
`ktransfer_joint` shows the union-typed class `{jointLuckySetJ = S, jointHitSlotSetJ = H}` is a `KTransfer` for every
`psJ p s`: `joint_honest`/`joint_hit`/`joint_out` apply `slot_transfer` to the composed family `pQ p` — fed by
`roundsQ_of_prefix` (rounds agree *before the first-ask round*, from the split-chain prefix, not the full `ω`) — and
decode the segment from the query's tag (`qTag`), pinned by injective tags, with output slots excluded by index
(`N·Q + 1 + s > slot`). This is exactly the §37-style "decode over the prefix" I asked for.

**§6 witnesses (`JointWitness`).** All three hold, and satisfy the §29 discipline: (1) `jointClassWeightJ_one` derives the
`N = 1` base **independently** from the proved `class_weight_of_typed` (via `luckySet_eq_unshift`), not from
`jointClassWeightJ` — no circularity; (2) `hitsBy_psJ_pJ_empty` proves the §42 refuting family credits **no** joint hit
(the other segment's round-2 `qInvIn_s` is now visible in `psJ` via `asked_psJ`, so `hitAt` fails) — the counterexample
is provably neutralized; (3) `card_hitEvent` exhibits a **positive** credited joint hit (segment 0 guesses, segment 1
idle) on `E` with `Pr[E] = (M−1)/M²` and `jointLuckyBitsJ ≥ wc` — the lemma is non-vacuous, crediting real luck.

**Consequence for §42.** The 14 GB `Meets`, which §42 left conditional after `JointClassWeight` was withdrawn as false, is
now discharged at the lemma level: `jointClassWeightJ → zeroAdviceLuckyMulti_of_jointClassWeightJ → ZeroAdviceLuckyMulti
→ p3_meets_multi_64_D10_of_joint`. What remains is `bc-58ec406e` swapping the p3-meets glue to the `_of_jointClassWeightJ`
route (§5 of the proposal) — a mechanical rewire I will confirm (and mark the old `JointClassWeight` refuted) when it
lands, but it introduces no new statement.

**Verdict (§45): GO — `JointClassWeightJ` is a sound, non-vacuous, standard-axiom theorem proving the §43 statement, with
all three conditions discharged by proof.** Overall verdict unchanged: **GRANTED WITH CONDITIONS** (the standing
conditions are now just the ChainEPF v3 close for §44/§40 and the p3-meets headline rewire).

### §45 addendum — the 14 GB headline rewire (`P3MeetsFinal`, sha `01bf6e4e`): confirmed, no new statement, `Meets` params unchanged (28 Sep 2026)

`bc-58ec406e` wired the 14 GB headline to the now-proved `jointClassWeightJ`. **Verdict: confirmed. The rewire adds no
new statement, keeps the `Meets` parameters identical to §42, and makes the 14 GB finals unconditional on the three
standard axioms.** Checked on my own rebuild of p3-meets (`P3MeetsFinal` sha `01bf6e4e`):

- **Unconditional + standard axioms.** `p3_meets_multi_64_D10_final := p3_meets_multi_64_D10_of_jointClassWeightJ
  jointClassWeightJ` and the `D = 12` fallback `p3_meets_multi_64_D12_band16_final` now take **no hypothesis**;
  `#print axioms` on both gives `[propext, Classical.choice, Quot.sound]`. The single-segment finals
  (`p3_meets_64_D10_final`, `_D12_band16_final`) are unchanged and still unconditional.
- **No new statement; `Meets` params unchanged from §42.** I confirmed by explicit type-match that the finals prove
  exactly `Meets (p3SchemeNR 2384 (bandGraph 220 12) 971) .sequential 10 (2^20) 117 ((2⁻¹)^128)` (and the `D=12`,
  `bandGraph 220 16` fallback) — the same `Meets` Prop as §42's conditional `check_p3_meets_multi_64_D10`. Only the proof
  route changed: the old `_of_jointClassWeight` (false hypothesis) is replaced by `_of_jointClassWeightJ` fed the proved
  `jointClassWeightJ`, via the unchanged `zeroAdviceLuckyMulti_of_jointClassWeightJ → p3_meets_multi_64_D10_of_joint`.
- **Composition lemmas de-duplicated.** `P3MeetsFinal` imports `Freshness.JointCompose`/`JointGlue`; `psJ` is no longer
  defined in p3-meets (the `run`/`bounded` lemmas come from `JointCompose`). The old `JointClassWeight` remains only as the
  refuted marker (superseded, referenced by `not_jointClassWeight`), like `DecodeHyp3`.

So the P3 14 GB headline is **closed** (unconditional), matching the 14.4 MB single-segment headline. **Standing note:** the
ChainEPF v3 close (§44/§40) is still pending and stays first in my queue — `ChainEPFMixed`'s `exists_bEvU` has landed with
my §44 `validItem` fix (verified, no `sorry`), but the mixed `pr_Ev` (the `PrEvMixed` deliverable) and the
`ExistsBEvU`/`PrEvMixed` discharge into an unconditional `ChainExPostFactoG` are not yet in the store, so `band_meets_64`
/`chain_meets_64` remain conditional for now. Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 46. P3 with a concrete chain `H` (`p3-concrete/P3ConcreteModel`, sha `51c09265`, `bc-58ec406e`): the model and both targets are faithful, plausible, sound and non-vacuous — GO, with `P3ChainEPF`/`P3ChainEPFMulti` the open obligations (28 Sep 2026)

`bc-58ec406e` scoped P3 with `H` = the overwrite chain on Π₂ (reused from `sponge-dense`), aiming at `k = 106` (down from
the ROM's 117). **Verdict: GO. The chain-column game and both ex-post-facto targets are faithful to P3-with-chain-H,
plausibly true, the one-label weakening and power position count are sound and non-vacuous, the `k = 106` derivation
holds, and the witnesses/necessity lemmas meet §29.** On my own combined build (`SpongeDense` `c17e13ca` +
`PebblingMeets`/`Thm1`/`Freshness`), `#print axioms` on the outright-proved side (`p3ChainCert`, `p3ChainCert_band16`,
`p3ChainHard_of_clock`, `inv_reach`, `not_p3ChainHard_X0`, `not_p3ChainHard_zero`, `p3ChainEPF_hyps_sat`,
`p3ChainEPFMulti_hyps_64`) and the two conditional Meets finals all give `[propext, Classical.choice, Quot.sound]`; the
finals `#check` as `P3ChainEPF(Multi) → Meets (p3SchemeC/NC 2384 (bandGraph 220 12)(971)) .sequential 10 2^20 106 2^-128`.

1. **Faithful.** `p3ChainModel` (Π₂/Π₂⁻¹/P_T/P_T⁻¹) imported unchanged; `p3SchemeC`/`NC` decode via `decodeC` over the
   chain (counterparts of `p3SchemeR`/`NR`). `P3ChainKnow`/`round` cross the column game with the chain game: `canCall`
   needs the parent label and the previous chaining value (one Π₂ call/round); `Π₂⁻¹` recovers a block + earlier `h`; `P`
   forward gives lower-from-key and top-from-key+column; `P⁻¹` gives lower key (W public) and top column↔key. Pricing:
   top/`r`/label `n`, column `1`, chaining value `n + c/wc` = `(m+c)/wc` columns. The targets are `n10prime`/`Multi` in
   shape with `P3ChainHard` for `ColumnHard`, over `topLabelC` (matching the scheme).
2. **Plausible; multi uses joint accounting.** `P3ChainEPF` is the §41 lucky-guess line redone in the two-permutation
   model (both merged halves exist); `P3ChainEPFMulti` bounds `JointEventC` and is correctly scoped to lock-step joint
   accounting (per-segment `JointClassWeight` is false, §42; the joint `JointClassWeightJ` is proved, §45), with a
   conservative `((N·nPosC)²+(2Nn)²)/2^{n·wc}` collision term.
3. **One-label weakening + power positions — sound, not vacuous.** `(k − X − 1)` is conservative (weaker bound), the
   `ChainExPostFactoG`-vs-B5 one-label slack, the boundary for merging component-`wc` credits with whole-Π₂-answer chain
   items. `nPosC^{14n}` is a **power** (`≥ 1`), not a binomial — the right non-vacuity choice, since `C(nPosC, 14n) = 0`
   at tiny `Q` would falsely force the bound to 0. `nPosC = n(Q+1)+n(n+1)+2n`. Degenerate cases hold (`k>n` empty, `k=X+1`
   → `≥ 2^m ≥ 1`, `wc>0`, tiny `Q` covered).
4. **`k = 106` holds.** `X_eff = 1 (certificate) + 1 (weakening) = 2`; `p3ChainCert` proves `X = 1` and
   `not_p3ChainHard_X0` proves `X = 0` fails (exact). The conditional finals type-check at `k = 106` on the standard
   axioms, so the `β`/`p₀^106 < 1%`/collision numerics carry it. The move from ROM `k = 117` to `106` follows from the
   sharper chain game (`X = 1` vs `3`).
5. **§29 met.** `p3ChainEPF_hyps_sat` (inner `P3ChainHard` satisfiable), `p3ChainEPFMulti_hyps_64` (deployment side
   conditions incl. `tagR_injective`), the proved certificates, and the necessity lemmas `not_p3ChainHard_X0`/`_zero`
   (X = 0 fails, so X = 1 is exact and the game non-vacuous) — all on the standard axioms.

**Verdict (§46): GO.** The scoping is sound; `P3ChainEPF`/`P3ChainEPFMulti` remain the open obligations (the concrete-H
ex-post-facto bound, the P3 analogue of `ChainExPostFactoG`), the merge of P3 credit rules with the chain's whole-Π₂
fresh items, for which the one-label slack is the deliberate margin. Delivered to `bc-58ec406e` as
`internal/p3-instantiation/p3-concrete-redteam-verdict.md`. Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

### §46 re-review — closure gap fixed by (A′); `P3ChainKnow` gains `kc`/`pc`; the closure is sound, but the targets still need `n ≤ 2^255` (28 Sep 2026)

My §46 GO on `P3ChainKnow` missed a closure incompleteness (`bc-58ec406e`): `pin2 u = transpose(c¹)_u ⊕ key²_u` holds
*component by component*, so `P⁻¹(c²_u)` yields `key²_u` components the whole-key game could not see — which the EPF proof
would miscount as fresh predictions. Fix (A) added top-key components (`kc`); (A) alone still failed my per-component
condition (the 3-way relation has three sides, (A) itemized two), so **(A′)** also adds `pin2` components (`pc`) with the
any-two-of-three rule. **On the (A′) model (`P3ConcreteModel` `2a188e88`, 16 modules rebuilt) the closure restatement is
sound on all four points I set:** (1) the `assemble` any-two-of-three closes in one pass because each `(u,w)` is an
independent triple (deriving the third never unlocks a blocked derivation); (2) independence holds per component (items on
one sample use disjoint coordinates; target `2^{uncovered·wc}`); (3) no derivation is missed — the relations are exactly
Π₂/`P` (whole), `pin1 = W ⊕ key¹` (whole), `pin2 = col ⊕ key²` (per coordinate), and cross-round derivations are captured
by `round = step ∘ assemble` iterated (`D`-round reach = `D`-step power); (4) invariants preserved — I audited
`p3ChainCert` (X = 1), `not_p3ChainHard_X0` (X = 0 false) and both finals (`Meets` at **k = 106**, 14.4 MB and 14 GB) on
the three standard axioms.

**But §46 does not fully close yet:** `bc-4b3abaed` found the targets need `n ≤ 2^255`. `domP3 tag L v` encodes `2v + L`
into the IV's 256-bit half, so for `v ≥ 2^255` it wraps (`2·2^255 + L ≡ L`) and rows `0`, `2^255` collide — the target is
then false at large `n` (a §47-style shared-domain break). It is not in `2a188e88` (both targets have only `0 < n`). This is
a required statement fix (same class as the §42/§47 domain-separation conditions), and my §46 GO didn't catch it because it
lives in the `∀ n` quantifier. When `bc-58ec406e` lands it I verify: `n ≤ 2^255` a hypothesis of both targets, discharged
at `n = 220`, with an injectivity lemma (`domP3` IV injective for `n ≤ 2^255`) and a necessity/failure lemma (the concrete
`v`/`v+2^255` collision, so it is exact and non-vacuous per §29), and the final `Meets`/`k = 106` unchanged. Verdict
delivered as `internal/p3-instantiation/p3-concrete-aprime-rereview-verdict.md`. `bc-4b3abaed`'s `JointBirthday`
(`p3-concrete-multi/Birthday.lean`) is queued for the P3-14 GB review. Overall verdict unchanged: **GRANTED WITH
CONDITIONS**.

**§46 finalized (06:46Z fix verified) — GO.** The `n ≤ 2^255` fix landed; I rebuilt all 11 modules (`P3ConcreteModel`
`f3d37ef6`, `P3Concrete` `411cfd24`, `P3ChainAssembly` `e2d7e4d9`) and audited on the three standard axioms. It is stated in
both targets right after `0 < wc`; discharged at `n = 220` (`p3ChainEPF_hyps_64`, the multi hyps, `p3ChainEPF_hyps_sat`,
and threaded through `segBoundC_of_epf`/`jointSegBoundC_of_epfMulti`); and **exact** — `injective_domP3`
(`n ≤ 2^255 → injective` over all `(layer,row)` pairs) is the sufficiency, `not_injective_domP3` (`2^255 < n → ¬injective`,
via `domP3_shift`'s rows `0`/`2^255` collision) the necessity. Invariants intact: `p3ChainCert` (X = 1),
`not_p3ChainHard_X0` (X = 0 false), both finals at **k = 106**. So the P3 concrete-H scoping — model, (A′) game, certificate,
both targets, conditional `Meets` at k = 106 — is sound and correctly stated; `P3ChainEPF`/`P3ChainEPFMulti` remain the
open obligations, to be proved via the lazy-sampling technique.

### §46 addendum — the `P3Client` blocker (bc-58ec406e): the same-round double credit is real, the fixes are sound, and C1 is GO (28 Sep 2026)

**Status.** `CollBound` is wired (`P3ChainColl.lean` `09da74d4`), so `P3ChainEPF` rests on `P3Client p3Bad` alone.
Two unproved intermediate statements, `FreshTail` and `P3Client`, are false as stated. Nothing false is in Lean.

**1. Same-round double credit (confirmed).** `onlineH` compares a round's shows only with earlier rounds, and
`assemble`'s `pin2 = col ⊕ key²` is deterministic.
- There is a cheaper form than the report's: with the lower layer known, guessing only `key²_u` (ℓ bits) credits both
  `kc (u,·)` and `pc (u,·)`, `2n` columns.
- On two rows this beats `FreshTail`'s claim at `s = 4` once `ℓ > 14n·log₂ nPosC` (524 480 against 85 568).
- `P3ChainEPF` is not threatened.

**Fix 1 (a per-round basis modulo `assemble`): GO.** `assemble` is the game's only instantaneous rule, and the other
credited kinds have single representations.
- Brute force (`p3-assemble-basis-check-redteam.py`): `assemble` is idempotent (exhaustive at `n = 2`, sampled at
  3 and 4).
- The greedy basis size does not depend on the order and equals the GF(2) rank modulo `Kon` (4,000 rounds per `n`),
  so the price is exact.
- The attack row's credit drops from `2n` to `n`.
- Obligations: `assemble_idem` and `shown_le` in Lean; the extra `mem_onlineH` clause; and the per-rank-2-triple
  charging at the two distinct samples. A naive "later of" rule for `pc` can collide with a `col` credit.

**Fix 2 (`s ≤ n`): GO.** The fit caps the item count independently of `s`, and `k > n` makes the win event empty.

**C1 (`2·nPosC ≤ 2^wc`; multi `2·N·nPosC ≤ 2^wc`): GO.** It is a weakening, the bridge's `h2` for one-column kinds.
It is discharged at `(220, 2^20)` (`≈ 2^28.8`) and at `N = 971` (`≈ 2^38.7`); `Meets` and `k = 106` are unchanged. The
necessity lemma shows necessity for the technique, not for the target. C2 (`n₀ ≤ n`) will be reviewed with the
item-count lemma.

**Band v6.** The same gap appears only if one instantaneous class (label and key via `read'`) is represented by two
seed elements. 07:22Z §2's fold (seeds `r`/`h`, `labs = ∅`) avoids it. This is a condition on v6, which is still
unposted.

Verdict: `internal/p3-instantiation/p3-client-double-credit-redteam-verdict.md`. The overall verdict is unchanged:
**GRANTED WITH CONDITIONS**.

### §46 addendum 2 — P3 attribution design v2 (slot tables, charge table, C2): GO with conditions (28 Sep 2026)

**The slot tables.** `LazyPermDecide` (`8444d445`) builds and has no `sorry`. `prob_fresh_slots_le`, `first_fix`,
`exists_first_fix`, `readAt_eq`, `ofRounds_roundQs_det`, `roundQs_congr` and `length_hist_of_next` are all on
standard axioms or a subset.
- The slot-table bridge is sound: a union over a `π`-independent finite `Sig`, one level above the name union. It
  fixes the transpose obstruction honestly, since one `pin2_u` guess is paid once.
- **The condition.** The credits that `σ` lists must be *prefix-closed* in the online order. Otherwise the charge
  rules (rows 2, 4, 6 and 9 depend on which other credits exist) aren't determined by `(σ, history)`. My example: a
  triple whose `kc` credit is decided after `c¹_w`.
- With prefix-closure, and since every credit is a whole-value match (so targets pin whole shows), width-only kinds
  suffice. That costs about `4n` slots.
- Small Lean items: a labeller-phase corollary of `ofRounds_roundQs_det`, and the deciding-step slots are optional
  given `readAt`.

**The charge table.**
- Rows 1, 3, 5, 7 and 8, and distinct steps: GO.
- Row 2: GO; "as `pc`" must follow rows 8/9.
- Row 6: GO; "shown" means credited in `σ` at a round ≤ the inverse round.
- Row 9: GO; its justification is false when the second credit is `col` (`c¹_w` early), but the rule holds.
- **Row 4: fix.** A same-round credited `key¹_w` collides at the `Π₂` sample, so charge at the inverse step with
  target `W ⊕ kshow`.

**C2.** The shape `(2·nPosC)^c ≤ 2^wc` is right; no linear-in-`n` term is needed. But over all `Q` the doc's
constants need `c ≈ 14` for large `n`, 16 at `n ≥ 16`, and 39 at `n = 1`, not 5–6. Deployment allows `c ≤ 82` for one
segment and `≤ 61` for the multi target. My recommendation is one condition replacing C1: `c = 40`, or `c = 20` with
`16 ≤ n`, fixed from the proved count.

Verdict: `internal/p3-instantiation/p3-attribution-design-redteam-verdict.md`. The overall verdict is unchanged:
**GRANTED WITH CONDITIONS**.

### §46 addendum 3 — "decided" is not "determined" (bc-58ec406e): history-backed freshness (`VC`) is sound — GO; erratum to addendum 2 (28 Sep 2026)

**The gap is real.** `Kon` holds values the adversary *could* compute. So a correct guess of an unasked,
game-derivable `h_{v,1}` earns no credit, yet it decides the pair at `block_2 ‖ g`. A later inverse hit then needs
`h_{v,2}`, which the history does not determine.
- Neither the inverse step nor the already-sampled `S2(v,2)` can take the charge.
- It is a bookkeeping gap, not a false bound.
- **Erratum to addendum 2.** I claimed `readAt` reads any *decided* value and worded row 6 as "decided or credited".
  It reads only *determined* values.

**The fix is sound.** Credits become "shown and not in `VC`". `VC` is the closure over constants, program-revealed
pairs, the identities and the triples, which is exactly "determined by history + `σ`'s credits". So every credit is a
genuine prediction.
- **The simulation.** `VC_τ ⊆ Ks' τ` holds by induction on rounds, pair by pair: each revealed honest pair's shown
  side was credited or in `VC` at its own round, so the game has the other side one round later. This is independent
  of `VC`'s derivation route, so chains aren't a problem.
- `win_price_on` is unchanged. There is no statement change, and at most `3n + s + 1` credits.
- **Conditions.** State the full rule list (including label = columns and key = components). Use a round-level `VC`
  for crediting and a step-level `VC` for targets. Replace "decided" with "in `VC`" in every row, with a lemma that a
  non-`VC` cell is determined at its own pair's fresh sample, as a coordinate projection, given a prefix-closed `σ`.
  Keep `σ` prefix-closed.
- `LazyPermDecide` `3d2d6412` builds cleanly.

**Band v6 needs the same.** `ChainKnow'.reach` also over-approximates. So seeds must be decided against a
history-backed `VC` (with the key rule as an identity), with `VC_τ ⊆ reach'` one round later. This is v6 checklist
item (g).

Verdict: `internal/p3-instantiation/p3-decided-vs-determined-redteam-verdict.md`. The overall verdict is unchanged:
**GRANTED WITH CONDITIONS**.

### §46 addendum 4 — truncation at the cut and uniform targets (bc-58ec406e): both GO; erratum to my condition 4 (28 Sep 2026)

**The build.** I rebuilt 16 modules from the store: `P3ChainOnline` `e22ef63c`, `P3ChainCut` `898a095e`,
`P3ChainTrunc` `dd1a5b99`, `P3ChainStepVC` `dad66424` and `LazyPermDecide` `ac297bbc`, among others. There is no
`sorry`. `vc_le`, `shown_le`, `simOn`, `win_price_on`, `onlineHC_full`, `stratC_hist_le`, `honest_decide_C`,
`agree_svc` and `readAtP_eq` are all on standard axioms.

**Truncation: sound, and it replaces my condition 4.** Prefix-closure alone fails while post-cut program steps remain.
Their instance shows a pre-cut credit whose transfer needs a pair identified only by a post-cut credit.
- The event doesn't depend on the strategy.
- `stratC_hist_le` and `honest_decide_C` hold.
- With σ = all credits of the truncated run, every honest pair decided before `j` has both sides in `svc`.
- The union over `c` costs `log₂(nQ+1)` bits, which P3 affords.
- C2 should be re-run with `3n + s + n + O(1)` credits plus the cut slot. My `c = 40` has headroom.

**Uniform targets: sound.** Pin every answer cell in `svc`.
- `h_target` follows from `agree_svc` and `readAtP_eq`, with honesty. `h_fresh` is `honest_decide_C`.
  `h_distinct` is trivial. `hT` is `card_agreeSet`.
- **Conditions:**
  - `T = ∅` unless the pinned width equals `w κ`;
  - the key lemma is over honest pairs only;
  - ι's injectivity: transfer chains strictly increase the step, the positional bijection is injective, and in a
    rank-2 triple both samples are pinned, since σ-credits determine the third cell.
- Their observation that a per-step potential fails is correct.

**The band needs the same truncation** (G3 in the band v6 re-review), in a per-pattern, free form.

Verdict: `internal/p3-instantiation/p3-truncation-uniform-targets-redteam-verdict.md`. The overall verdict is
unchanged: **GRANTED WITH CONDITIONS**.

## 47. The band scheme at 14 GB (`band-multi/BandMultiModel`, sha `9081a902`, `bc-4b3abaed`): the 448-segment store is one `ChainExPostFactoG` instance — faithful, and `k = 106`/`111` certified — GO (28 Sep 2026)

`bc-4b3abaed` proved the band scheme at 14 GB by treating all 448 segments as **one** `ChainExPostFactoG` instance over
the disjoint-union DAG (no joint lemma needed). **Verdict: GO. `ChainBandMeets14`/`ChainBandMeets14Global` are faithful,
`segFaithfulCode` correctly decomposes the store into 448 one-segment codes, `shared_domain_breaks` is a genuine
refutation showing injective domains are necessary, the k-table is right (`111` and `106` certified, `105` fails), and the
witnesses/necessity lemmas meet §29.** On my own build (band-multi over `BandChain`/`DenseReCert`/`ChainEPFV3` in
`chainepfverify`), all 70 audited theorems report `[propext, Classical.choice, Quot.sound]` — no `sorryAx`.

1. **Faithful.** `ChainBandMeets14 d = ∀ salt, Meets (chainBandSeg 448 (2^9) d 524288 512 (segDom salt (2^9)))
   .sequential 5 (2^20) 111 2^-128`. `chainBandSeg` is `chainScheme` on `bandSegDAG 448 512 d` (the disjoint union of 448
   band DAGs on global indices, `par v` = same-segment `v−d…v−1`) over **one** `idealPerm` (one shared permutation), with
   `segDom salt v = dom (tag salt (v/B)) (v%B)` and `tag = salt ‖ u64 s` — the implementation's per-segment tags. So it
   is 448×512 = 229376 blocks, 64 KiB labels, one permutation, per-segment tags; `Global` is the same with one 256-bit
   salt and global indices. Faithful. The key structural point: `ChainExPostFactoG` is generic in `B`/`TopoDAG B` and
   counts the win jointly over all blocks of one game, so the 14 GB store is literally one instance — cross-segment
   queries are inside the one union, so unlike P3's per-segment accounting (§42), **no joint lemma is required**.
2. **`segFaithfulCode` correct.** `segFaithfulCode` proves block `(s,i)` of the 14 GB code equals block `i` of the
   one-segment `chainBand B d` code of segment `s`'s data under `tag salt s` — so the store is exactly 448 independent
   one-segment band codes (via `labelG_seg` strong induction + `blocks_gIdx`). ✓
3. **`shared_domain_breaks` genuine.** `shared_domain_breaks : SharedDomainBreaks` refutes `Meets` for the shared-domain
   variant (`sharedDom` = one salt, local index) for every `d, D, Q, k, ε`: identical segments get identical labels, so a
   preprocessor storing segment 0's `2^28` bits answers every challenge with zero online queries (`sharedDom_label`,
   `seqAnswers_ret`), the audit accepts with probability 1, and `δ + ε < 1` (`delta_add_lt_one`). `sharedDom_not_inj`
   confirms it violates exactly the injective-domain hypothesis. This is the necessity proof for cross-segment domain
   separation — the concrete analogue of the §42/§44 cross-segment-collision lesson.
4. **k-table right.** `band_meets_14 : BandMeets14` (`ChainExPostFactoG → ∀ d ≥ 5, ChainBandMeets14 d ∧ …Global d`) and
   `band_meets_14_k106 : BandMeets14K106` are proved; `seg_k105_fails` proves `¬ (p₀(β₁₀₅ …)^105 ≤ δ)` — a genuine
   refutation that `k = 105` fails the `p₀^k ≤ 1%` requirement. So `k = 111` and `k = 106` are certified, `k = 105` is
   not; the union amortizes one segment's `s = B − D − 1` loss over 448 segments, bringing `k` below one segment's 111.
5. **§29 met, no vacuity.** Witnesses `band_seg_hard_14`/`_d12`, `shortRows_seg_14` (2240 short rows),
   `weighted_cert_hyp_14` (`227135 + 2240 < 229376`), `segDom_inj_14`/`dom_inj_14`, `band_meets_14_d5`/`_d12`, `neZero_14`
   — all proved. Necessity: `band_seg_needs_N` (`0 < N`), `band_seg_needs_room` (`D+1 ≤ B`),
   `band_seg_gap_attack`/`band_seg_cliff_d12`/`band_seg_d12_margin` (`D ≤ d`, cliff at `D = 13`), and
   `shared_domain_breaks`/`sharedDom_not_inj` (injective domains). No vacuity: `band_seg_hard` uses `k = N·B = |univ|`
   (tight), `audit_k_lt_B` (`111 < 512`), and the bound has no binomial position term.

**Verdict (§47): GO.** The 14 GB band rests only on `ChainExPostFactoG` — the same open obligation as the one-segment
`band_meets_64` — with no joint lemma, which is architecturally cleaner than P3's joint accounting for multi-segment.
**Note:** the `band_meets_14_of_v3`/`_d12_of_v3`/`_k106_of_v3` wrappers reference v3's `PrEvMixed` (confirmed:
`band_meets_14_of_v3 : ExistsBEvU → PrEvMixed → …`); per §44 that def is being replaced by the v4 carried-reveal form, so
these need the trivial re-point to v4 (already requested) — this does not affect `band_meets_14` itself. When the ChainEPF
v4 close lands, `band_meets_14` becomes unconditional alongside `band_meets_64`. Overall verdict unchanged: **GRANTED
WITH CONDITIONS**.

## 48. Public encoder for the band codec (`public-encoder/PubEncoderBand.lean`, sha `140e823e`): `PubMeets` with the exact check is `Meets` — sound and not trivialized, with four deployment conditions for the handoff (28 Sep 2026)

**Build.** I rebuilt it against the store's `PubEncoder` (`5946ed41`), `PubEncoderModel` (`b918cd29`),
`BandPubEncoder` (`a51aca2c`), `BandChainKeyRuleEquiv` (`a38fc5c3`) and `BandMulti`. It has no `sorry`, and these
are all on `[propext, Classical.choice, Quot.sound]`: `pubMeets_exact_iff`, `band_pub_iff_64`/`_14`/`_14_global`,
`band_pub_meets_64_of_keyRule`/`_14_of_keyRule`/`_d12_of_keyRule`, and `band_pub_hyps_witness`.

**1. `pubMeets_exact_iff` is correct.** Given `Subsingleton Coins` and `EncDec`,
`PubMeets sch (exactCheck sch) … ↔ Meets sch …`.
- **Meets ⇒ PubMeets** (`pubAuditSecure_exact`). The exact check accepts only `(pp*, C*)` with
  `dec pp* C* = W`, and `EncDec` then forces `(pp*, C*) = enc W ω r` (`enc_eq_of_dec`). So the server's output is the
  honest encoding. The public preprocessor's extra view is the coins `r` (a subsingleton) and `ξ : Unit`, so it
  carries nothing, and the reduction to today's preprocessor loses nothing. Completeness of the check is exactly
  `Correct`.
- **PubMeets ⇒ Meets** (`pubAuditSecure_exact_iff`). The public adversary can play the honest encoder and ignore the
  extras. So the public game is also no *easier* to meet.
- **The equivalence is not vacuous.** `PubMeets` carries `V.Complete`, which rules out reject-all.
  `acceptAll_not_pubAuditSecure` shows that an accept-all check fails at the problem statement's parameters. The
  equivalence therefore reflects the check's content.

**2. The band instances are sound.**
- **The iffs.** `band_pub_iff_64`/`_14`/`_14_global` are `forall_congr'` over the salt with `pubMeets_exact_iff`.
  They typecheck only because `ChainBandPubMeets64` and `ChainBandMeets64` (and the 14 GB pairs) name the same
  scheme, salt domain, `.sequential`, `D = 5`, `Q = 2^20`, `k = 111` and `ε = 2^-128`.
- **The hypotheses are true of the deployed codec, not assumed.** `chainScheme` has `t = 0` and `Coins = Unit`, and
  `chainBand_encDec`/`chainBandSeg_encDec` hold because the band code is a bijection for each primitive: label = key ⊕
  W, with keys from parent labels in `C`.
- **The inputs are exactly `ChainExPostFactoG'`.** `band_pub_meets_64_of_keyRule : ChainExPostFactoG' → ∀ d, 5 ≤ d →
  ChainBandPubMeets64 d`, and `_14_of_keyRule` gives both 14 GB layouts. These go through `chainExPostFactoG'_iff`,
  which by §44's seed swap is equivalent to `ChainExPostFactoG`. There is no other hypothesis.

**3. Does it model a real public-encoder deployment? Yes, under four conditions for the handoff.**
1. **The check is the exact, full-decode check.** The verifier decodes all of `C*` with the primitive and compares it
   with the committed `W`. For the band that is about the encoding's total work (`B·(d+1)` calls), fully parallel
   (each block from its parents in `C*`, so low depth). Its cost is not in any statement, and a cheaper sampled or
   spot-check is *not* covered. "No extra weakness" holds for the exact check only.
2. **The salt is fixed by the verifier or the protocol, not the server.** The salt is a scheme parameter (`dom salt`,
   `t = 0`), and the statements quantify over every salt, which subsumes a random one. The server has no `pp` channel
   to choose it. A deployment in which the server picks the salt, possibly grinding it against the public primitive,
   is outside the model.
   - "No coins" hides nothing for the band: the codec genuinely has no setup randomness.
   - The theorem does **not** apply to P3 (`t = 192`, salt as coins, where `EncDec` fails). There `pp*` would carry a
     server-chosen salt, and the check would also have to verify it.
3. **`W` is fixed before setup, and the primitive is independent of `W` and the salt.** This is the same as `Meets`,
   so it is no public-encoder-specific weakness. Choosing `W` or the salt adaptively after inspecting the primitive is
   outside both games.
4. **The commitment to `W` and the binding of `C*` (the Merkle root) are idealized**, as in `PubEncoderModel` (§38).

**The handoff claim, as it can be stated.** For the band codec at 64 KiB and at 14 GB (both domain layouts), an
untrusted server encoding the data is exactly as secure as verifier-side encoding: `PubMeets ↔ Meets`, proved. This
assumes a setup check that fully decodes the server's codeword and compares it with the committed data, with the salt
fixed by the verifier. Everything is conditional on the open `ChainExPostFactoG'` (the v6 tail). The verifier's decode
cost is not modeled, and cheaper checks are not covered.

Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

**§46 addendum 5 (28 Sep 2026, ~12:35Z) — the single-segment C2 is confirmed.** `P3ChainEPF` (`P3ConcreteModel`
`dd3acc42`) now carries `(2·nPosC n Q)^40 ≤ 2^wc`, alongside C1, which it implies and which is harmless.
`P3ChainEPFMulti` carries `(2·(N·nPosC))^40 ≤ 2^wc`. So `P3ChainEPF` is the `N = 1` case, as the reduction
`p3ChainEPF_of_multi` needs.
- **The discharge.** `c2_64` (`2·nPosC ≤ 2^29`, so `2^1160 ≤ 2^2384`) and `c2_64_multi` (`N ≤ 2^10`: `2^1560`), within
  the ceilings of `c ≤ 82` for one segment and `c ≤ 61` for the multi target.
- **Rebuilt.** `P3ConcreteModel`, `P3Concrete`, `P3ChainCert` and `P3ConcreteFinal`. The finals
  `p3_meets_concrete_64_D10_final`/`_multi_` still take only `P3ChainEPF`/`P3ChainEPFMulti`, with `Meets` unchanged
  (`k = 106`, `D = 10`, `Q = 2^20`, `2^-128`, `N = 971`), on standard axioms.
- **The `pin2` rule.** My second-credit rule was not injective: a block transfer can land on the same `c¹_w(u)`.
  bc-58ec406e's R1–R3 fix, which takes whichever sample is not entered otherwise, is proved in `P3ChainCharge` and
  `P3ChainTriple`.
- **The band.** There is no analogue, since the band has no XOR-routed credits (confirmed in the band v6 re-review
  file).

## 49. Public encoder, milestone 2: the sampled check (`PubEncoderSampledModel` `d7ee15a2`, `PubEncoderSampled` `2777daaa`, write-up `docs/public-encoder/sampled-check.md`): definitions GO; the gap statement needs one sharpening (28 Sep 2026)

**Build.** I rebuilt both files against the store's `PubEncoderModel`, `PubEncoder` and `PubEncoderBand`. There is no
`sorry`, and all of these are on `[propext, Classical.choice, Quot.sound]`: `pubSampled_seq_le`, `seq_ball_le`,
`pr_sample_pass_eq`, `skip_attack`, `union_route_vacuous`, `timedINCBall_of_timedINC`, `seg_pub_sampled_14`,
`dense_pub_sampled_64` and `band_pub_sampled_14_of_ball`.

**The definitions are faithful.**
- **`blockDist`**: the number of blocks where `W'` differs from `W` under the block map. It is injective for
  `Dense.blocks`, which `card_ball_le` needs.
- **`sampleCheck`**: its coins are `Fin t → Fin B`, uniform with replacement.
  - **It is a real spot-check.** The server's encoder `E W ω r` has no `ξ` argument, so the indices are drawn
    independently *after* the server's output is fixed.
  - **Comparing blocks of the full `dec` output is the same as a local check.** For the chain codec, a sampled block's
    decode reads only its parents in the fixed `C*`, and `dec_i = C*_i ⊕ key_i(C*)`.
  - The preprocessor sees `ξ`, which is realistic: the server learns which blocks were checked. The bound conditions
    on `ξ`, so this knowledge gains nothing against fresh audit challenges.
  - Completeness is `Correct` (`sampleCheck_complete`).
- **`TimedINCBall`**: `TimedINC` with data `w(ω)` chosen after the primitive, within `m` blocks of a fixed `W`. This is
  exactly the freedom that passing a sampled check gives. One generality point: `w` sees `ω` but not the coins. That
  is harmless for the coin-free dense and band codecs, but make `w : Ω × Coins → Bits n` before reusing it for a
  scheme with coins (P3).

**The headline theorems are correct.**
- **The three-term bound** (`pubSampled_seq_le`) splits on the server's decoding.
  - If it is more than `m` blocks off, passing is bounded by `((B−m−1)/B)^t`, conditioning on `(ω, r)`.
  - Otherwise encode-after-decode makes `C* = Enc(W')` with `W'` in the ball, and `seq_ball_le` (`Theorem1iiSeq` with
    adaptive data, conditioning on `ξ`) gives `|Hist|·π + p₀^k`.
- **The ball and the union.** `card_ball_le` bounds the ball by `2^B·2^(mℓ)` through patches.
  `timedINCBall_of_timedINC` is a sound union.
- **The attack.** `pr_sample_pass_eq` is exact. `skip_attack` is a genuine construction: its codeword is zero on `J`,
  it decodes to `W` off `J`, and it passes with probability at least `((B−|J|)/B)^t`.
- **The random-oracle points.** 14 GB (`seg_pub_sampled_14`, `t = 42 957`, `m = 476`) and 64 KiB
  (`dense_pub_sampled_64`, `t = 22 962 > B`, so the full decode is cheaper) are proved outright. The union over the
  ball is rigorous there, because the random oracle's `π` scales entirely with `2^β`.

**Is the band "gap" honest? Yes as stated, with one sharpening.**
- **`band_pub_sampled_14_of_ball` is conditional on `hball` and `hπ`**, explicit hypotheses with no witness, labelled
  "the gap" in both the file and the write-up. It must not be cited as a result.
- **`union_route_vacuous` is robust.** Even an exact ball count (about `B·2^ℓ` at `m = 1`) leaves
  `|Hist|·|ball|·K ≈ 2^(1959 + 524306 − 524724) > 1`, since the `|Hist| ≈ B^110 ≈ 2^1959` factor alone swamps the
  margin. So "the union route bounds nothing for every `m ≥ 1`" is right. And `m = 0` needs `t ≈ 89·B`, worse than the
  full decode.
- **The sharpening.** The write-up calls the adaptive-data fix "plausible if the obligation's collision event depends
  only on π and the positions (nPos is data-free)". For the band that condition **fails**. The collision *bound*
  `nPos²/2^(ℓ+c)` is data-free, but the collision *event* `NoCollU` is not: honest chain inputs absorb parent labels,
  which are `key ⊕ W`.
  - With `W'` chosen after `π` from a ball of size at least `2^(2ℓ)` (for `m ≥ 2`), a setup-time server has
    `|ball|·nPos²` chances at an `(ℓ+c)`-bit chain-input coincidence. The model lets setup be unbounded; only storage
    and the online responder are bounded.
  - So the collision term cannot simply be "paid once".
  - Whether an engineered collision actually helps the adversary is unanalysed.
  - **Suggested wording:** "the adaptive-data band obligation is open. Its natural collision event is data-dependent,
    so it may fail against an unbounded setup-time server. Closing it needs a collision argument that does not union
    over the ball." That is a question about the *truth* of the statement, not just a change to it.
- **The recommendation is sound:** keep milestone 1's full decode as the deployed check.

Overall verdict unchanged: **GRANTED WITH CONDITIONS**.

## 50. P3 with a concrete chain `H` is closed: `P3ChainEPF` and `P3ChainEPFMulti` are proved, and `Meets` holds unconditionally at `k = 106` for 14.4 MB and for 14 GB (`N = 971`) — closure audit (28 Sep 2026)

**Scope.** The endpoints are `p3SegCharges`, `p3ChainEPF_holds` and `p3ChainEPFMulti_holds`, in
`p3-concrete/P3ChainSegCharges.lean` (`433b30ea`). Their new supporting files are `P3ChainRoundDet` (`3be482cc`),
`P3ChainTable` (`0274f34a`) and `P3ChainTarget` (`9d6f6894`). The finals are in `P3ConcreteFinal` (`26a85f99`). The
bc-58ec406e / bc-4b3abaed chain is audited end to end.

**1. The endpoints are exactly the approved statements, and nothing was weakened.**
- **Definitions.** `P3ChainEPF`, `P3ChainEPFMulti`, `P3ChainHard`, `P3ChainCert`, `nPosC`, `p3SchemeC` and
  `p3SchemeNC` all live in `P3ConcreteModel.lean` `dd3acc42`, byte-identical to the version I confirmed in §46
  addendum 5.
- **The printed bodies match.** Both carry `0 < n`, `0 < wc`, `n ≤ 2^255`, C1 (`2·nPosC ≤ 2^wc`, and the `N·nPosC`
  form for multi), C2 (`(2·nPosC)^40 ≤ 2^wc`, and the `N`-scaled form), `X + 1 ≤ k` and
  `P3ChainHard G 512 wc D k X`. Multi adds `1 ≤ N` and injective tags. The right-hand sides are the §46 ones:
  `2^m·nPosC^(14n)/2^((k−X−1)·n·wc) + (nPosC² + (2n)²)/2^(n·wc)`, and for multi
  `N·2^m·(N·nPosC)^(14nN)/2^(N(k−X−1)·n·wc) + ((N·nPosC)² + (2Nn)²)/2^(n·wc)`.
- **Everything they depend on is unchanged.**
  - `SpongeDense.lean` (`p3ChainModel`, `P3COmega`, `keyP3c`, `topLabelC`) is `c17e13ca`, as verified before.
  - `bandGraph` (`p3-column/BandComb.lean`) is `a961e605`, unchanged since 27 Sep.
  - In the trusted layer, `Meets` (`Accounting/Params.lean`), `Audit` and `Scheme` are unchanged. Since my earlier
    copy, the only changes are P2 additions: `Model/M1p.lean` and the pinned `P2MeetsM1…` statements.
- **No escape hatches.** Across the 113-module closure there is no second definition or shadowing of any endpoint
  name, and no `axiom`, `opaque`, `extern`, `implemented_by`, `unsafe` or kernel-check skip.
- **The internal objects are non-trivial, and they match the reviewed design.**
  - **`Kind n`** is `(honest pair, #components − 1, capacity flag)`, with width `(k+1)·wc + 512·cap` and
    `|K| ≤ 16n³ + 16`.
  - **`Sig n M`** is a table of `3n + k` slots, each an optional value name with a code `≤ M`.
  - **`KatT`** is the listed values whose code is round-available at the step. This is round determinism, the form I
    asked for in place of anchoring.
  - **`Tgt`** is `readAtP` over the oracles that realize the table and are consistent with the history. It pins the
    decided pair's answer cells that are known in `svc`, and is `∅` unless the kind's width matches (my condition 1).
  - **`OnFresh`** requires that `σ` be π's realized table at the full-schedule cut, that `¬JBad` hold, and that the
    item be a charged step. `name = (dstep, kindOf)`, with distinct steps from `dstep_inj`, and `dstep_ne_seg` across
    segments. The cut is the full schedule (`Real`: schedule length `= c`), so there are no post-cut program steps.
    That meets the truncation requirement.

**2. It rebuilds fresh from the store, on standard axioms, and `leanchecker` passes.**
- **The build.** In a new tree I resolved the transitive import closure of `P3Concrete.All` from the store's current
  sources: 113 modules, namely 52 `Freshness`, 29 `P3Concrete`, 11 `P3ConcreteMulti`, 8 `Pebbling`, 4 `PebblingCol`,
  2 `PebblingMeets`, 1 `Thm1`, 1 `HintCard`, plus `SpongeDense` and four lazy-perm files. I rebuilt `Pous` from the
  store's `lean/pous` (2089 jobs) with the fetched Mathlib. Every module compiles.
- **The drafts.** Three `Pebbling.*Draft` modules in the closure emit `sorry` warnings. None is reachable from the
  endpoints, as the axiom audit shows.
- **The axioms.** `p3ChainEPF_holds`, `p3ChainEPFMulti_holds`, `p3SegCharges` and `p3ChainCert`, and both
  unconditional finals below, are all on `[propext, Classical.choice, Quot.sound]`.
- **`leanchecker --fresh P3Concrete.All` exits 0** (4 min 35 s).

**3. The finals are the reviewed `Meets`.**
- **One segment (14.4 MB).** `p3_meets_concrete_64_D10_final p3ChainEPF_holds` gives
  `Meets (p3SchemeC 2384 (bandGraph 220 12)) .sequential 10 (2^20) 106 (2^-128)`.
- **14 GB.** `p3_meets_concrete_multi_64_D10_final p3ChainEPFMulti_holds` gives
  `Meets (p3SchemeNC 2384 (bandGraph 220 12) 971) .sequential 10 (2^20) 106 (2^-128)`.
- These are exactly the §42/§46 parameters. The `D = 12` fallback on `B(220, 16)` (`…_D12_band16`) is also
  unconditional at `k = 106`.
- bc-4b3abaed's wiring has not landed yet. My one-line scratch instantiations of both finals typecheck on standard
  axioms, so the wiring is a formality. I'll recheck it when it lands.

**What the headline says, for Daniel.** In the ideal-permutation model (`Π₂` and the tweakable `P` ideal, with `H` the
overwrite chain over `Π₂`), P3 on `B(220, 12)` with 64 KB labels meets the trusted requirement:
- sequential audit with 106 challenges;
- `D = 10` rounds of `2^20` queries per answer;
- `ε = 2^-128`, with the requirement's `ρ` and `δ`;
- for one 14.4 MB segment and for 971 segments (14 GB).

It rests on no open hypothesis. The standing model conditions from §38, §42 and §46 still apply: `W` is fixed before
setup, the primitives are idealized, and the verifier encodes, since the public-encoder results are separate (§48–§49).

**Verdict: the P3 concrete-H closure is GO.** The overall verdict stays **GRANTED WITH CONDITIONS**, because the band
scheme's `ChainExPostFactoG'` (v6) is still being built.

## 51. The P3 concrete-H pins (`Pous.Pinned.P3ConcreteMeets64`, `P3ConcreteMeets14GB`, `P3ConcreteMeets64D12`) and the trusted model `Pous/Model/P3Chain.lean` (`60843b90`): the pins are the §50 finals, the copies are exact at the elaborated level, and no existing pin moved — GO (28 Sep 2026)

**Scope.** This reviews bc-4b3abaed's proposal in the store's `lean/pous`:
- the new `Pous/Model/P3Chain.lean` (264 lines);
- in `Pous/Pinned.lean` (`2a5c3e22`), one import and three definitions;
- one import in `Pous.lean`;
- three `sorry` targets in `PousTargets.lean`;
- three names in `Grader/Registry.lean`;
- a paragraph in `ASSUMPTIONS.md`;
- the recomputed `TRUSTED.sha256` (`44eda307`).

It also covers the wiring in `lean/submissions/p3-concrete-multi/finals/P3ConcreteFinals.lean` (`19b3c1b1`) and the
grading in `grading/`.

**Method.** Everything below ran on my own VM, against scratch copies; the store was not modified.
- I copied the store's `lean/pous` (`sha256sum -c TRUSTED.sha256` passes), built `Pous` (2090 jobs), and built the
  13-module source closure of `P3Concrete.P3ConcreteModel` from the store's current sources against it.
- A metaprogram then compared the elaborated constants of each source (`PousX`) with its trusted copy (`Pous.X`).
- I dumped every constant of the trusted modules in the old build (my 14:20 copy, the pre-proposal state) and in the
  new build, and diffed the dumps.
- I regenerated the three solutions with the store's `flatten.py`, graded them with `grade.sh`, and ran `check.sh`.

**1. The pins are exactly the §50 finals, and `P3Chain.lean` is a faithful copy.**
- **The statements.** Each pinned body is token for token the type of the matching theorem in `P3ConcreteFinals.lean`,
  after the renaming:
  - `P3ConcreteMeets64` is `p3SchemeC 2384 (bandGraph 220 12)`, `D = 10`;
  - `P3ConcreteMeets14GB` is `p3SchemeNC 2384 (bandGraph 220 12) 971`, `D = 10`;
  - `P3ConcreteMeets64D12` is `p3SchemeC 2384 (bandGraph 220 16)`, `D = 12`.

  All three are `.sequential` with `Q = 2^20`, `k = 106` and `ε = (2⁻¹)^128`, the §50 parameters. `#print` shows the
  elaborated pins in that form. `P3ConcreteMeets64` is `rfl` to the explicit
  `Meets (M := p3ChainModel 220 2384) (p3SchemeC 2384 (bandGraph 220 12)) …`, and `#print axioms` on each pin shows
  only the standard three.
- **The source text.** `P3Chain.lean` has 31 declarations: 29 definitions and abbrevs, the lemma `bandExtra_lt`, and
  the two instance declarations. The proposal's count of "27 definitions and one lemma" is a slight undercount, which is
  cosmetic.
  - After `PousX → Pous.X`, every declaration's code is identical to its source: `SpongeDense.lean` `c17e13ca`
    (§§2, 7, 9), `pebbling/ColumnAwareDraft.lean`, `p3-column/BandComb.lean` `a961e605`, `p3-meets/P3Meets64.lean`
    and `p3-concrete/P3ConcreteModel.lean` `dd3acc42`.
  - Only docstrings differ:
    - `bandGraph` says `B(n, k)`;
    - `WbitsW` gains a docstring;
    - `p3SchemeC`/`p3SchemeNC` drop the "counterpart of `p3SchemeR`/`NR`" references, and `NC` adds "segment-major".
  - The two instances differ by design (item 3).
- **Why text equality is not enough.** The same text can elaborate differently. For example, `P3ConcreteModel` opens
  `PousP3Base` and `P3Chain` does not, and the lanes have their own instances in scope. So I compared the elaborated
  terms.
- **The elaborated terms.** The dependency cone has 54 constants: the 31 declarations plus their `match_1`, `_proof_n`
  and `_simp_n` auxiliaries. For 48 of them, the type, value, universe parameters and reducibility are the same `Expr`
  after renaming. The other six:
  - **`instFintypeP3COmega`.** Same type and value (`Fintype.ofFinite _`). Only its reducibility and its instance
    attribute differ, as intended.
  - **`bandExtra_lt`.** A theorem with the same statement and a different proof term. Three of its auxiliaries are named
    differently, which makes four of the six. This is irrelevant.
  - **`decodeC`.** Its value differs in one constant: the `NeZero (1 + 1)` proof behind the `Fin 2` literal `1` in
    `(tag, 1, v)`. In `P3Chain`, Lean reuses the identical auxiliary it had already made for `c2c` in the same module
    (`Pous.Sponge.c2c._proof_4`). The source module makes its own (`PousP3Concrete.decodeC._proof_1`). Both prove the
    same `Prop`, so they are definitionally equal by proof irrelevance, and the kernel accepts
    `@PousP3Concrete.decodeC = @Pous.P3Concrete.decodeC := rfl`.
  - **The reverse check.** The trusted layer has 60 constants under the five new prefixes, and all but one have a source
    counterpart. The exception is a `bandExtra_lt` proof auxiliary. So `P3Chain` holds the copies and nothing else, and
    the constants the pins mention are the ones §46 and §50 reviewed.
- **The sources since §50.** §50 used my 14:20 copy. Of the finals' 115 source modules, 7 have changed since:
  `Pebbling.ColumnAwareDraft`, `ForwardCoreDraft` and `TweakedDraft`, `PebblingMeets.P3Meets64`, and
  `Freshness.Assembly`, `Decode` and `Decode2`.
  - All seven changes are bc-58ec406e's 15:20Z `sorry` hygiene. The `sorry`'d `n10prime`, `n10prime_core` and
    `n10primeMulti` became `Prop` abbrevs (`N10primeT`, `N10primeMultiT`, `N10primeStmt`, `N10primeCoreStmt`), and each
    `type_of% @PousTweaked.n10prime…` became the abbrev, which is the same `Prop`.
  - No copied definition changed, and nothing on the finals' path changed.
  - Two modules are new: `P3ConcreteMulti` (an import list) and `P3ConcreteFinals`.
- **The wiring.** Each of `P3ConcreteFinals.lean`'s three theorems is a one-line application:
  `p3_meets_concrete_64_D10_final p3ChainEPF_holds`, `…_multi_…_final p3ChainEPFMulti_holds` and
  `p3_meets_concrete_64_D12_band16 p3ChainEPF_holds`. These are the instantiations I typechecked in scratch for §50, so
  §50's open note on the wiring is closed. Item 5 checks it.

**2. The renaming `PousX → Pous.X` is sound.**
- **The prefixes were unused.** Before the proposal, the trusted layer had no constant under `Pous.Sponge`,
  `Pous.ColumnAware`, `Pous.P3Column`, `Pous.P3Meets` or `Pous.P3Concrete`. The renaming is a bijection on five fresh
  prefixes, following the `Pous.Dense` precedent.
- **The lanes are unaffected.** Their `PousX` constants coexist with the copies: the 13-module source closure builds
  unchanged against the new layer.
- **The pattern is exact.** `flatten.py` renames with `\bPousX\b`. That leaves `PousP3ConcreteMulti` alone, since there
  is no word boundary inside it, and it cannot hit a longer identifier. Hits in comments and strings are harmless.
- **The deletion is exact.** `flatten.py` deletes each moved declaration by a header regex that must match exactly once
  (`remove_decl`), along with its docstring and attributes. A copy left in place would be a duplicate declaration
  against `Pous`, and the build would fail.
- **The solutions regenerate exactly.** Running the store's `flatten.py` (`f7a245df`) on the store's 115 sources, in
  `P3ConcreteFinals`' import order, reproduces all three `Solution-*.lean` byte for byte (`982a6045`, `ca1531ac`,
  `bd875b08`, as in `GRADE.txt`).
- **A doc nit.** `P3Chain.lean`'s header cites `freshness/Pebbling/ColumnAwareDraft.lean`. The file is
  `lean/submissions/pebbling/ColumnAwareDraft.lean`, module `Pebbling.ColumnAwareDraft`.

**3. Making `P3COmega`'s `Fintype` and `Nonempty` local changes only elaboration, never a pinned `Prop`.**
- **Why the meaning is fixed.**
  - `IdealModel` carries `[fintypeΩ : Fintype Ω]` and `[nonemptyΩ : Nonempty Ω]` as structure fields
    (`Pous/Game/Oracle.lean`). They are filled once, when `p3ChainModel` is defined.
  - `Meets`, `AuditSecure` and `pr` then read `M.fintypeΩ`, through `attribute [instance] IdealModel.fintypeΩ`.
  - `(p3ChainModel n wc).fintypeΩ = instFintypeP3COmega n wc` is `rfl`, in both the source and the trusted layer, and
    the two values are the same `Expr` (item 1).
  - Any other instance is equal to it anyway (`Subsingleton.elim`), so `pr` cannot depend on the choice.
  - The local scope ends at `end Pous.Sponge` and covers `p3ChainModel` and `topLabelC`. Nothing later in the file needs
    `Fintype (P3COmega …)`. The `Fintype (Bits 192)` of `Coins` is elaborated inside `p3SchemeC`/`NC` and is part of
    the `Expr` comparison.
- **What a submission sees.** With only `import Pous`, `Fintype (Pous.Sponge.P3COmega 220 2384)` no longer synthesizes,
  and `Nonempty` resolves to `instNonemptyProd`. A proof that needs the instance on the bare type must register it
  itself. `flatten.py` does exactly that, replacing each source `instance` line with
  `attribute [instance] instFintypeP3COmega` or `instNonemptyP3COmega`, so the proof sees the source's instance order.
  This affects elaboration only. The pinned `Prop` is fixed in the trusted environment, and the grader matches it by
  kernel `isDefEq`.
- **The stated reason holds.** I made the trusted instances global next to `SpongeDense`. Then
  `Fintype (PousSponge.P3SOmega n wc)` fails for symbolic `n wc` with "maximum recursion depth has been reached":
  unifying `n*wc + (n*wc + 512)` with `n*wc + 512` blows up. Local instances are the right call.
- **Optional.** When a submission turns the trusted `instFintypeP3COmega` into an instance, Lean warns that it is a
  semireducible definition of class type. The source's `instance` was `instanceReducible`. `@[instance_reducible]`
  would restore that. It affects no pin and not the kernel.

**4. Nothing in the existing trusted layer moved.**
- **The files.** Compared with my 14:20 copy of the store's `lean/pous`, only the files listed under Scope differ,
  besides the new `P3Chain.lean`.
  - `Pinned.lean` gains an import and three definitions after the last existing pin.
  - In `Registry.lean`, `pinnedTargets` gains three names, and `allowedAxioms` is unchanged.
  - These files are byte-identical: `lakefile.toml`, `lean-toolchain`, `lake-manifest.json`, `check.sh`, `grade.sh`,
    `CheckAxioms.lean`, `Grader/Main.lean`, `lean-audit.json`, and every other file under `Pous/`.
- **The elaborated constants.** I dumped every constant from a trusted module in both builds, with its full type and
  value (`dbgToString`, proofs included).
  - All 445 old constants are byte-identical: after removing the additions, the new dump hashes to the old one's
    `7ece665f`.
  - The new build adds exactly 64 constants: the 60 in `P3Chain`, and 4 in `Pous.Pinned`. Those are the three pins and
    `P3ConcreteMeets14GB._proof_1`, the proof of `NeZero 971`.
  - Nothing was removed or changed. `P3Chain` declares no global instance, simp lemma, notation, coercion or macro, so
    importing it cannot alter how later trusted files elaborate, and the dump confirms that.
- **The registry.** `pinnedTargets` now has 46 names, which are all 47 `Prop` definitions in `Pinned.lean` except the
  refuted `InvExPostFactoTwoLayer`.

**5. I reran the grading and the acceptance check.**
- **`grade.sh`.** It ran on my scratch trusted layer with the regenerated solutions. All three pass on
  `[propext, Classical.choice, Quot.sound]`:
  - `P3ConcreteMeets64`: PASS in 177 s;
  - `P3ConcreteMeets14GB`: PASS in 153 s;
  - `P3ConcreteMeets64D12`: PASS in 142 s.

  Each run compiles the 115-module flattened closure in the sandbox, and then the grader replays it through the
  kernel. That re-checks bc-4b3abaed's wiring and bc-58ec406e's proofs against the trusted constants.
- **`check.sh`.** It ran on the same tree with a scratch copy of the store's `lean/tools/lean`, and printed
  **ALL CHECKS PASSED**:
  - the audit's controls;
  - `AUDIT: PASS` over 509 declarations in 21 modules, which includes `P3Chain`'s 60, with `leanchecker --fresh`;
  - `PousTargets` elaborating;
  - the positive control and all negative controls.

**Doc nits.** None of these is blocking.
- `ASSUMPTIONS.md`'s counts are stale after this proposal:
  - "43 statements" should be 46;
  - "Ten were added on 28 Sep" should be 13;
  - "the ten pins above" should be 13.
- `ASSUMPTIONS.md`'s "Trusted" line names `Model/M1p.lean` but not `Model/P3Chain.lean`. Both fall under `Pous/Model`,
  but for parity it should name both.
- The `Pinned` docstrings are accurate:
  - `m = 220·2384 = 524480`;
  - a label is 65,560 B (64 KB), and a segment is 14.42 MB;
  - `971` segments make 14.005 GB;
  - `D` and `Q` count `P^{±1}` and `Π₂^{±1}` calls;
  - the scope states that `W` is fixed before the primitives and that the model is idealized.

**Verdict: GO to pin `P3ConcreteMeets64`, `P3ConcreteMeets14GB` and `P3ConcreteMeets64D12` with
`Pous/Model/P3Chain.lean`.** The pins state the §50 finals, over constants identical to the reviewed ones, and the
existing layer is unchanged. The standing model conditions (§50) apply. The overall verdict stays **GRANTED WITH
CONDITIONS**, because the band v6 is still being built.

## 52. The band scheme is closed: `ChainExPostFactoG` is proved unconditionally (band v6, design (c′)), and the band and dense-chain `Meets` finals hold with no hypothesis — GO (28 Sep 2026)

The full verdict is the ~20:05Z entry of `internal/p3-instantiation/band-v6-design-rereview-redteam-verdict.md`.

**What is proved.** bc-87c3b40e's v6 chain (`lean/submissions/sponge-dense/ChainEPFV6*.lean`) proves:
- `bandFreshTail_v6`;
- `chainExPostFactoG'_v6 : ChainExPostFactoG'`;
- `chainExPostFactoG_v6 : ChainExPostFactoG`.

These are exactly the §39 target (`BandChainModel` `ba654b0f`, with the §35 collision term) and its key-rule form. The
chain follows my (c′) design:
- the charges are unchanged;
- each name's pointer is the slot holding the target value;
- the step field is partitioned, with labeller items placed at a stopping time.

**Two departures, both sound.**
- **Widths depend on the history** (`prob_hitsAt_hist_le`). Each run pays its own widths, and those sum to its
  realized seed width.
- **Known-partner pointers** try a child pair, then the partner's own pair, then the held partner's show. All three are
  readable before the step.

`M`, `BandFreshTail`, the wrappers and `k` are unchanged.

**Verification** (my VM; the store was not modified):
- The 71-module closure of `All` builds on the fresh trusted layer.
- No `sorry` and no escape hatches.
- Everything is on `[propext, Classical.choice, Quot.sound]`.
- Each final's type is, by `rfl`, the conclusion of the reviewed conditional theorem, with no hypothesis weakened.
- `leanchecker --fresh` exits 0 over `All` and my audit modules.

**Now unconditional:**
- `ChainBandMeets64 d` for all `d ≥ 5`: 64 KiB, `B = 2^9`, `D = 5`, `k = 111`;
- `ChainBandMeets14 d` and `ChainBandMeets14Global d`: 448 segments at `k = 111`;
- the 14 GB `k = 106` variant;
- the public-encoder forms `ChainBandPubMeets64/14/14Global d`;
- `ChainExPostFacto`, and with it the overwrite-chain dense `chain_meets_64`: `chainDense (2^9) 524288 512`, `k = 111`.

**Pins.**
- **GO:** the eight band `Meets`/`PubMeets` finals and `chain_meets_64_final`. The three `PubMeets` pins need a trusted
  `PubMeets`/`exactCheck` with §48's conditions in the docstring.
- **Each needs a trusted model file** after the §51 precedent. Its definitions and hashes are listed in the verdict file.
- **Don't pin** `chainExPostFacto_v6` or the four root theorems. They are correct, but pinning them would freeze
  proof-internal definitions.

**Overall verdict: GRANTED WITH CONDITIONS.** No proof obligation remains open on the band, dense-chain or P3 chains.
The conditions are now only these:
- the standing model and deployment conditions: ideal primitives, `W` fixed before setup, `d ≥ D`, and §48 for public
  encoders;
- pinning and grading the new finals in the trusted layer.

## 53. The band trusted model (`trusted-draft/Pous/Model/BandChain.lean` `fc149e43`) and its six pins: GO, with one install condition; the public-encoder block is GO once its lane changes; and `ChainDenseMeets 64 (2^20) 111` is GO as a new statement (28 Sep 2026)

**Scope.** This reviews bc-87c3b40e's staged files in `lean/submissions/sponge-dense/trusted-draft/`, not yet in
`lean/pous`. The request is in `internal/p3-instantiation/band-trusted-model-review-request.md`. I am the reviewer of
record, and bc-fb71544d has left no document.
- **The model file.** `Pous/Model/BandChain.lean` `fc149e43` holds 16 definitions and one instance.
- **The pins.** `Pous/PinnedBand.lean` `3b26ee27` has the six pins.
- **The public-encoder block.**
  - `Pous/Model/PubEncoder.lean` `583d2bd9`;
  - `Pous/Accounting/PubMeets.lean` `8aad8c44`;
  - `Pous/PinnedBandPub.lean` `841d518c`.
- **The bridge.** `ChainEPFV6TrustedBridge.lean` `8817b2b3`.

I checked everything on my own VM, against a scratch copy of the store's `lean/pous` with the drafts added. The store was
not modified.

**1. The copies are exact at the elaborated level.**
- **The comparison.** This is my own metaprogram, not `elab_compare.py`. It walks the dependency cone from the 16 lane
  roots, renames `PousX → Pous.X` for `Sponge`, `DenseReCert`, `BandChain` and `BandMulti`, and compares type, value,
  universe parameters and reducibility.
- **The result.** 35 of 39 constants are identical `Expr`s, including the eleven reused from `P3Chain` (the overwrite
  chain and `parentsDesc`, which §51 verified).
- **The four differences are proof auxiliaries.**
  - `chainDense` and `chainScheme` differ only in the auxiliary proof of `0 < B` from `NeZero B`, the `B_pos` field.
    The lane uses `spongeDense._proof_1` and `chainScheme._proof_1`; the copies share `chainDense._proof_1`. The values
    are equal once proof-auxiliary names are normalized.
  - The other two differences are those auxiliaries' names.
- **The reverse check.** The model file has 34 constants, and all but two have a lane counterpart. The two are that
  shared proof and the `NeZero (448 * 2 ^ 9)` instance, whose auto-generated name differs from the lane's. It is a
  `Prop` instance with the same type.
- **The bridge.** It compiles in the scratch layer. All six `pinned_*` depend only on
  `[propext, Classical.choice, Quot.sound]`, and `leanchecker --fresh ChainEPFV6TrustedBridge` exits 0 in 212 s.

**2. `Pous.Sponge.idealPerm` (the new trusted content) is GO.**
- **The definition.** `Ω = Equiv.Perm (Bits b)`, drawn uniformly through its Mathlib `Fintype`. `Qry = Bits b ⊕ Bits b`,
  and `.inl x ↦ Π x`, `.inr y ↦ Π⁻¹ y`.
- **It matches the proofs.** It is structurally identical to the lane's `PousSponge.idealPerm`, which the proofs used,
  including the `Fintype` and `Nonempty` fields.
- **It is the standard model.** It is the ideal permutation with inverse queries. That is more conservative than M1's
  forward-only `perms`, and it uses the same `.inl`/`.inr` convention as `P3Chain.p3ChainModel`.
- **Access is as in every model.** The honest encoder and decoder use forward queries only. `Q` counts both directions.
  Only the preprocessor sees `Π` whole (`Preprocessor … → M.Ω → Bits S`), as in every trusted model.
- **Nothing is trivialized.** `Ω` is nonempty and finite, with `(2^b)!` elements.

**3. The six pin statements are GO.** Each inlines exactly the `*Meets*` body I approved in §52, with `∀ d, 5 ≤ d` and
`∀ salt` kept:
- `BandChainMeets64`, `…D5` and `…D12` are `ChainBandMeets64`;
- `BandMultiMeets14` is `ChainBandMeets14 d ∧ ChainBandMeets14Global d`;
- `BandMultiMeets14K106` and `ChainDenseMeets64` are the §52 statements.

The docstrings are accurate, including "not `DenseMeets`" and the `d ≥ D` cliff.

**4. The public-encoder block: GO once the lane changes.**
- **The copies.** All 29 constants of `PubEncoder.lean` and `PubMeets.lean` equal `PubEncoderModel.lean` `b918cd29`
  (§38) across two environments. The only difference is in hygienic binder names, which embed the module name.
  `Scheme.EncDec` stays in the lane, as planned.
- **The pins.** The three `BandPub*` statements are the §52 `PubMeets` forms. Their docstrings list exactly §48's four
  conditions.

**Rulings on the four choices.**
1. **Staging: GO.** Keep the files out of `lean/pous` until Daniel approves. The install steps listed are right.
   - **The install condition.** The P3 graded solutions (`p3-concrete-multi/grading/Solution-*.lean`) flatten all of
     `SpongeDense` into `Pous.Sponge`, so they declare `idealPerm`, `dom`, `parentsNF`, `absorbed`, `labelOv` and
     `chainDense`. Once `BandChain.lean` is imported, those collide with the trusted names, and the three P3 pins would
     fail to re-grade.
   - **What to do about it.** Extend that `flatten.py`'s `MOVED` list with these six names, regenerate, and re-grade P3
     in the same install. The band solutions' flatten must remove both files' copies.
   - **Also:** re-run `check.sh`, and repeat §51's before/after constant dump (additions only).
2. **Inline bodies, literal `ε`, and the conjunction: GO.** This follows the `P3Concrete*` precedent. `Meets` itself
   checks `ε ≤ εMax`.
3. **Public-encoder names: GO**, on one condition. `PubEncoderModel.lean` must stop declaring the 29 names and import the
   trusted files before `Pous.lean` imports them. The three `BandPub*` pins enter only with that lane change. The terms
   are identical, so the lane's proofs should rebuild unchanged.
4. **The finals' docstrings: GO.** `ChainEPFV6FinalPub.lean` `e5cdb2a8 → f401d4db` is docstring-only; the code is
   identical outside comments.

**Second item: `ChainDenseMeets 64 (2^20) 111`, statement review. GO, as a new named statement.**
- **The statement.** It is `SpongeDense`'s `ChainDenseMeets` (`c17e13ca`) at `k = 111`:
  - `∀ salt : Bits 256`;
  - `Meets (chainDense (2^16) 8192 512 (dom salt)) .sequential 64 (2^20) 111 (2^-128)`;
  - the same scheme, model, `D`, `Q` and `ε` as the `k = 107` target. Only `k` changes.
- **It is weaker, and honestly so.** The sequential `Meets` is monotone in `k`, since acceptance on `k' ≥ k` challenges
  implies acceptance on the first `k`, so `k = 111` is strictly weaker than `k = 107`. Nothing about the adversary, the
  model or `ε` is weakened. The cost is 4 more challenges (+3.7% audit transfer, 111 KiB) at the trusted `DenseMeets`
  point (`2^16 × 1 KB`, `D = 64`, `k = 107`), for the concrete overwrite-chain `H` in place of the random oracle.
- **The numbers reproduce** (my script, exact integer logarithms):
  - `S = ⌊(18/19)·2^29⌋ = 508614548`;
  - `log2 M = 89.0888`;
  - the union bound `Σ_{j<k} 2^{16j}·chainPi ≤ 2^-128` allows `β ≤ 530503721` at `k = 111`;
  - `p₀ = 0.959350`;
  - `p₀^107 = 1.179% > 1%`, `p₀^110 = 1.041%`, `p₀^111 = 0.9988% ≤ 1%`.

  So 111 is the least certifiable `k` by this route.
  - **The `β` window at `k = 111`** is `[530498073, 530503721]`, about 5,650 bits.
  - **The same computation at 64 KiB** gives `k = 111`, with `chain_meets_64`'s `β = 265253616` inside its window
    `[265216780, 265254132]`.
  - **Proof advice.** Bounding `M ≤ 2^89.1` (for example `M^10 ≤ 2^891`) loses about 734 bits over `s + 1 = 65472`
    factors. So pick `β` near `530500000` rather than at either end.
- **`k = 107` is open, not refuted.** It needs a per-seed name count of about `≤ 2^77`, which is a stronger ex post facto
  bound.

What to change around it:
- **Keep the old target.** Don't redefine `ChainDenseMeetsPinned`. Keep it as the open `k = 107` target, add a new
  definition, say `ChainDenseMeets111 := ChainDenseMeets 64 (2^20) 111`, and label it as the weaker deployment in its
  docstring and in any pin.
- **If it is pinned,** it reads the same trusted `chainDense`/`dom` as `ChainDenseMeets64`, so it needs no new trusted
  definition.

**Verdict: GO for `BandChain.lean` and the six band pins, subject to the P3 re-grade in the same install.** The
public-encoder block and its three pins are GO once `PubEncoderModel.lean` is retired as described. `ChainDenseMeets 64
(2^20) 111` is GO as a new, explicitly weaker statement. The overall verdict is unchanged from §52.

## 54. `ChainDenseMeets111` is proved as approved, and the staged band install meets the §53 condition — GO (28 Sep 2026)

This reviews two items from bc-87c3b40e in `lean/submissions/sponge-dense/`. I checked them on my own VM, against scratch
copies; the store was not modified.

**1. `ChainEPFV6FinalDense111.lean` (`c723e7b7`): GO.**
- **The statement.** `ChainDenseMeets111 := ChainDenseMeets 64 (2^20) 111` is the statement §53 approved. By `rfl` it is
  `SpongeDense`'s `ChainDenseMeets` (`c17e13ca`, unchanged) at `k = 111`:
  - `∀ salt`;
  - `chainDense (2^16) 8192 512 (dom salt)`;
  - `.sequential 64 (2^20) 111 (2^-128)`.

  `ChainDenseMeetsPinned` is untouched and is still the open `k = 107` target. The docstring calls the new statement
  strictly weaker and states the cost.
- **The proof.** `chainDenseMeets111_final` is the `chain_meets_64` argument at `β = 530500000`, from
  `chainExPostFacto_v6`. It depends only on `[propext, Classical.choice, Quot.sound]`. `leanchecker --fresh
  ChainEPFV6FinalDense111` exits 0 in 207 s. The only compiler message is an unevaluated-exponent lint in
  `pow_split_le`.
- **The numbers, checked with exact integers.**
  - **`β` is inside the §53 window.** `530500000 ∈ [530498073, 530503721]`, and `S = 508614548` is the exact floor.
  - **The `M` bounds hold.** `M^100 ≤ 2^8909` and `M^72 ≤ 2^6415`, so `M^65472 ≤ 2^5832901`. The exact value is
    `2^5832821.x`, so the split loses only 80 bits.
  - **The union exponent is −3754.** It is `1776 + β + 1 + 5832901 − 536338432`, well below the needed −129.
  - **The sampling term fits.** As a rational, `p₀^111 = 0.99958% ≤ 1%`, while `p₀^110 > 1%`.

**2. The staged install (`trusted-draft/install/`): GO.**
- **The patch.** `lean-pous.patch` (`acd29f99`) applies cleanly (`patch -p1`) to a fresh copy of the store's `lean/pous`.
  - **Files changed:** exactly `Pous/Model/BandChain.lean` (added, byte-identical to the §53 `fc149e43`), `Pous.lean`,
    `Pous/Pinned.lean` (`edc2a2c8`), `PousTargets.lean`, `Grader/Registry.lean`, `ASSUMPTIONS.md` and `TRUSTED.sha256`
    (`347a2d85`). The recomputed `TRUSTED.sha256` passes `sha256sum -c`.
- **The six pins are the ones I approved.** `Pinned.lean` spells the model names out, for example
  `Pous.BandChain.chainBand` in place of an `open`. Elaborated, each of the six equals the staged `PinnedBand`
  constant that `ChainEPFV6TrustedBridge` proves. The one difference is a shared auxiliary proof: both
  `Theorem1iiiTimed._proof_1` and `BandChainMeets64._proof_2` prove `Nat.AtLeastTwo (1 + 1)`.
- **Counts and records.**
  - **`Pinned.lean` and the targets.** There are now 53 `Prop` pins, and the registry has 52 names: every pin except
    the refuted `InvExPostFactoTwoLayer`. `PousTargets` gains six `sorry` targets.
  - **`ASSUMPTIONS.md`.** It goes from 46 to 52 statements and from thirteen to nineteen added that day. It gets a
    paragraph on the six pins, and `BandChain.lean` joins its trusted-model line.
- **Nothing moved.** Before and after the patch I dumped every constant in the trusted modules, with its full type and
  value.
  - The 509 existing constants are unchanged.
  - The patch adds 41: 34 in `Pous.Model.BandChain` and 7 in `Pous.Pinned`, which are the six pins plus one auxiliary.
  - `check.sh` prints ALL CHECKS PASSED: the audit (550 declarations in 22 modules, with `leanchecker --fresh`),
    `PousTargets`, and the grader controls.
- **The §53 install condition is met.**
  - **The flatten change.** `flatten.py` (`6bf0d91c`) adds exactly the six headers to `MOVED["SpongeDense"]`: `idealPerm`,
    `dom (salt`, `parentsNF`, `absorbed`, `labelOv` and `chainDense`. `remove_decl` aborts on anything but one match,
    so each is unique.
  - **Regeneration.** Rerunning it on the store's current 115 sources reproduces the three staged solutions byte for
    byte (`7e17ea99`, `31894558`, `69bb07ed`). The six declarations are gone, at 34039 → 34004 lines. The old
    `flatten.py` still reproduces the recorded solutions, so the sources haven't changed.
  - **Grading on the patched layer.** All three pass on the three axioms:
    - `P3ConcreteMeets64`: PASS in 181 s;
    - `P3ConcreteMeets14GB`: PASS in 139 s;
    - `P3ConcreteMeets64D12`: PASS in 122 s.
  - **The negative control.** The recorded D12 solution fails with "does not compile":
    `Pous.Sponge.idealPerm has already been declared`, and likewise for `dom` and `parentsNF`.

**Fixes: docs only, none blocking.**
- **`ASSUMPTIONS.md` should say the grading is pending.** It says the six band pins "are unconditional" with the red
  team's GO, but it doesn't say they are not yet graded. Unlike the P3 pins, they have no graded solution until a flatten
  of the v6 chain exists: they are proved in the lane (`ChainEPFV6TrustedBridge`) and grade only as open targets. The
  paragraph should say so, and so should the reviewer guide's status column.
- **`INSTALL.txt` omits one hash.** `flatten.py.patch` is `58f2f49c`.
- **`ChainDenseMeets111` isn't in this install.** If it is pinned later, it reads only trusted `chainDense`/`dom`, and its
  docstring must keep the "strictly weaker than `k = 107`" note.

**Verdict: GO on both items.** The install is ready to apply as staged once Daniel approves the pins, with the P3
solutions replaced by the three regenerated ones in the same change. The overall verdict is unchanged from §52.

## 55. The band trusted model, second review (bc-fb71544d): I agree with §53, and I also ran the install and the public-encoder migration — model GO, six pins GO, public-encoder block GO with its lane change (28 Sep 2026 ~20:57Z)

**Scope.** The same request and files as §53, with the shas re-checked at 20:55Z:
- `BandChain.lean` `fc149e43`;
- `PinnedBand.lean` `3b26ee27`;
- `PubEncoder.lean` `583d2bd9`;
- `PubMeets.lean` `8aad8c44`;
- `PinnedBandPub.lean` `841d518c`;
- the bridge `8817b2b3`;
- `ChainEPFV6FinalPub.lean` `f401d4db`.

The copies' sources are `SpongeDense.lean` `c17e13ca`, `BandChainModel` `ba654b0f`, `BandMultiModel` `9081a902`,
`DenseReCert` `99709a42` and `PubEncoderModel` `b918cd29`. I worked in scratch copies on the builder's VM and did not
write in `~/build` or the store's `lean/`. This section adds only the checks §53 did not make. On everything else it
reached the same results independently: `idealPerm`, the copies, the pins and the four rulings.

**1. The definitions are equal in the kernel, not just as `Expr`s.**
- **The source text.** The 17 declarations of `BandChain.lean` match their sources' code and docstrings after the rename.
- **The cone.** A separate metaprogram of mine, run on the model file's side, found 39 copied constants:
  - 20 are identical;
  - 18 are identical once proof auxiliaries (`_proof_N`, `match_N`, `_unary`) are normalized;
  - one is the shared `B_pos` proof, `chainDense._proof_1`, whose lane counterpart is `spongeDense._proof_1`.
- **Kernel equality.** In one environment holding both the lane and the trusted copies:
  - each of the 24 copied or reused definitions is equal to its source by `Eq.refl`. The well-founded ones, `labelG` and
    `labelOv`, need `with_unfolding_all`;
  - each of the six pins is `Iff.rfl` to its lane wrapper.
- **The checker.** My own run of `leanchecker --fresh ChainEPFV6TrustedBridge` exits 0 in 233 s.

**2. The install, simulated: no existing constant moved, and `check.sh` passes.**
- **The setup.** A copy of `lean/pous`:
  - `Pous.lean` and `Pinned.lean` import `BandChain`;
  - the six pins are pasted as written, with `PinnedBand`'s file-level `open` placed before Track B, the worst place
    for it;
  - `Registry` has the six names, `PousTargets` has six `sorry` targets, and `TRUSTED.sha256` is recomputed.
- **The before/after dump, as in §51.**
  - Before: 509 constants. After: 550.
  - None was removed, and none changed its type, value or reducibility.
  - The 41 added constants are all in `Pous.Sponge`, `Pous.BandChain`, `Pous.BandMulti`, `Pous.DenseReCert` and
    `Pous.Pinned`.
- **`check.sh`: ALL CHECKS PASSED** (exit 0, 584 s).
  - The audit passes on 550 declarations in 22 modules, on the three standard axioms, with the 13 pinned theorems
    unchanged.
  - The open targets elaborate, all grader controls behave as expected, and the trusted tree is unchanged.
- **The P3 collision.** §53's install condition is real. `Solution-P3ConcreteMeets64.lean` declares all six names in
  `namespace Pous.Sponge`: `idealPerm` (l.104), `dom` (211), `parentsNF` (214), `absorbed` (218), `labelOv` (474) and
  `chainDense` (483). Re-flatten with those six in `MOVED` and re-grade P3 in the same install.

**3. The public-encoder migration builds, and the three pins are proved over the trusted copies.**
- **The migration.** I changed a copy of `PubEncoderModel.lean` to import `Pous.Model.PubEncoder` and
  `Pous.Accounting.PubMeets`. It keeps only `Scheme.EncDec` (45 lines).
- **It builds.** Every downstream lane pub module compiles against it unchanged:
  - `BandEncDec`, `PubEncoder`, `BandPubEncoder` and `PubEncoderBand`;
  - `ChainEPFV6FinalPub`, `PubEncoderDraft`, `PubEncoderSampledModel` and `PubEncoderSampled`.
- **The pins are proved.** A bridge proves `Pous.Pinned.BandPubMeets64`, `…14` and `…14Global` from
  `PousPub.band_pub_*_final`, each on `[propext, Classical.choice, Quot.sound]`. Each pin is also `Iff.rfl` to its lane
  wrapper.

  So §53's "the lane's proofs should rebuild unchanged" is now verified.
- **What I did not run.** `check.sh` with the pub files installed. Run it after the real install.

**Nits, none blocking.**
- **The `open`.** `PinnedBand`'s file-level `open Pous.Sponge Pous.BandChain Pous.BandMulti` is harmless even in the
  worst placement (§2 above). Still, keep the qualified names or a `section` in the installed `Pinned.lean`, as the
  builder's install already does.
- **The docstrings.** Following the P2/P3 precedent in `Pinned.lean`, add to each pin's docstring:
  - a "Statement reviewer: bc-22298e90 (§52/§53); second review bc-fb71544d (§55)" line;
  - the grading path of its final.
- **`BandGapAttack`.** Cite its lane file path.
- **`PinnedBandPub`.** Its "(`PubMeets ↔ Meets`)" should cite `band_pub_iff_*` by name.

**Verdict.**
- **`BandChain.lean`: GO.**
- **The six band pins: GO.**
- **The public-encoder block: GO**, installed together with the `PubEncoderModel` change in §3.
- **Required before merge:** §53's P3 re-flatten and re-grade in the same install, and `check.sh` on the real install.

## 56. The six band pins are graded (`trusted-draft/install/band-grading/`, patch `f7379b0d`): GO; and a four-line grader hardening, recommended for the install batch (28 Sep 2026)

I checked everything on my own VM, against scratch copies; the store was not modified.

**The patch.** `f7379b0d` differs from `acd29f99` (§54) only in `ASSUMPTIONS.md`. It now says all six grade PASS, and it
fixes "the nineteen pins above". `TRUSTED.sha256` still passes. The cited `sponge-dense/grading/GRADE.txt` is where
`INSTALL.txt` §3 puts `band-grading/`.

**1. The flatten: GO.**
- **The two edits change proofs only.** A flatten with `EDITS` disabled differs from the real one in exactly the two
  documented lines:
  - the trailing `rfl` in `obsFold_of_mem_tr`, inside its `:= by` block (`ChainEPFExistsV5`);
  - `labelG_eq` becoming `Pous.BandChain.labelG_eq` in a `rw` inside `labelG_seg`'s proof (`BandMulti`). Separately
    compiled, `BandMulti` resolves it to `PousBandChain.labelG_eq`.

  No statement changes. In any case, the grader checks every final proof against the trusted pin.
- **It reproduces.** `flatten_band.py` (`0c5bada8`) and `negative_controls.py` (`06bccf47`), run on the store's current
  63 sources (`MODULES.txt` `a8f40c13`), reproduce the six solutions byte for byte (`dee5fd30`, `a70bec48`, `e7f9726f`,
  `dc8b5d48`, `b485d9ba`, `470a9797`). They share one body and differ only in the `solution` line. The control file
  reproduces too (`b71a3988`).
- **The grades reproduce.** `run_grades.sh` on my copy of `lean/pous` with `f7379b0d` applied:
  - all six band pins PASS in 59–95 s, on `[propext, Classical.choice, Quot.sound]`;
  - `Neg-KeepBandCopies` fails, because it does not compile;
  - the `k = 106` solution graded as `BandMultiMeets14` fails with "does not have the pinned type".

**2. Grader robustness: not a soundness issue. Recommended, not blocking.**
- **The cause.** `Grader/Main.lean` step 3 is an unbounded `Kernel.isDefEq sinfo.type (mkConst target)`. For the
  d = 12 theorem against the d = 5 pin, the literals differ, so the kernel keeps unfolding `Meets`, `chainBand`,
  `bandDAG` and the well-founded `labelG`. The builder saw 8.1 GB at 162 s.
- **No false PASS is possible.** `isDefEq` answers `true` only for real definitional equality, and a timed-out or
  OOM-killed grader exits non-zero.
- **The real risk.** A mistaken near-miss can hang or exhaust a grading machine. The band pins make that likelier,
  because they come as d = 5/d = 12 twins. The exposure is the same for every existing pin.
- **The recommended fix: compare syntactically first.**
  - **The change.** Replace the `isDefEq` in step 3 with `unless sinfo.type == mkConst targetName do report … "solution
    does not have the pinned type …"`. This matches `grade.sh`'s contract, `theorem solution : Pous.Pinned.NAME`, which
    elaborates to exactly that constant.
  - **Tested on a scratch copy** (`~/v6c/pous-hard`: `f7379b0d` plus this change, `TRUSTED.sha256` updated):
    - the d = 12 solution graded as `BandChainMeets64D5` fails at the comparison instantly, at 60 s total, which is the
      compile and replay;
    - the honest d = 5 solution PASSes;
    - `check.sh` prints ALL CHECKS PASSED. The positive control passes, and `wrong_statement` and `rt_grader_swap` fail
      as before.
  - **Add a control.** Make the d = 12-as-d = 5 case a new `check.sh` negative control.
- **Also recommended: a memory cap on both the sandboxed compile and the grader.** The compile and the kernel replay
  stay unbounded, so any submission can still exhaust memory there. For example, `lean -M` in the sandbox and a
  `prlimit`/cgroup limit on `pous-grader`. An honest band grade peaks at 3.9 GB (compile) and 4.8 GB (grader). Measure
  the larger P3 solutions before choosing the limit, around 16 GB.
- **When.** Both changes touch trusted files (`Grader/Main.lean`, `grade.sh`), so they need their own review. Bundle
  them with the install's held sha-changing batch if convenient. They are not a precondition for installing the band
  pins.

**Verdict: GO for the band grading and patch `f7379b0d`.** The recommended grader fix is the syntactic comparison plus
a memory cap. The overall verdict is unchanged from §52.

## 57. The staged grader hardening (`install/grader-hardening.patch` `93b63ea1`): GO (29 Sep 2026)

This reviews the request in `internal/p3-instantiation/grader-hardening-review-request.md`. I checked it on my own VM:
`f7379b0d` then `93b63ea1`, applied to a scratch copy of `lean/pous`; the store was not modified. After the patch,
`TRUSTED.sha256` (`d83f62e9`) passes, with `Grader/Main.lean` `388b35c0` and `grade.sh` `8965c788`.

- **The type check: GO.** Step 3 becomes `sinfo.type == mkConst targetName`, on the kernel-replayed type.
  - **It is safe.** The target is universe-monomorphic, as step 1 checks, and syntactic equality implies definitional
    equality. So nothing can pass that the old check rejected.
  - **What it drops.** It rejects only solutions that state the target unfolded, or as some definitionally equal type.
    That is outside `grade.sh`'s contract, `theorem solution : Pous.Pinned.NAME`, and all 49 recorded solutions state
    the constant.
  - **Where definitional equality still happens.** An honest proof's check now runs only in the step-2 replay, which is
    under the new limits.
- **The near-miss control: GO.** `near_miss.lean` is `theorem solution : Pous.Pinned.BandChainMeets64D12 := sorry`,
  graded as `BandChainMeets64D5`. It fails in 25 s with "does not have the pinned type", before the axiom audit. On the
  unhardened tree it times out, so `check.sh` catches a regression.
- **The limits: GO.**
  - **The values.** 16 GiB resident (`lean -M` for the compile; `setMaxMemory` for the grader, checked by the kernel
    replay), and twice that in address space (`ulimit -v`, `prlimit --as`). That is about 3× the largest honest
    resident peak (P3, 5.3 GB) and 1.8× the largest mapping (17.9 GB).
  - **They hold on honest work.** The honest d = 5 solution PASSes under the defaults in 103 s.
  - **They fail safely.** At `POUS_GRADE_MEMORY_MB=2000` the same solution FAILs as "does not compile". That label is
    acceptable, because a limit only ever turns a verdict into FAIL, never into PASS.
  - **The environment variable.** It comes from the operator's environment, not the submission. Unset, the grader has
    no in-process limit when run by hand, and `grade.sh` always sets it.
- **Nits, optional.**
  - A distinct "resource limit exceeded" reason would be clearer than "does not compile".
  - `grade.sh` could check for `prlimit` up front, as it does for `unshare`.

**Verdict: GO.** It is ready for the held install batch.

## 58. `BandMultiMeetsFamily` (draft PR #431 at `a762a82a`, stacked on #428): the statement is GO (29 Sep 2026)

This is the named POUS-pin reviewer's statement review, on top of the subagent red-team read
(`internal/p3-instantiation/band-family-pin-redteam-verdict.md`, GO), which I checked rather than repeated.

- **The statement.** In `protocols/pous/lean/Pous/Pinned.lean` it is `BandMultiMeets14` with `448` replaced by every
  `N` in `1 ≤ N ≤ 2^64`, as `∀ (N : ℕ) [NeZero N], N ≤ 2 ^ 64 → …`. Everything else is textually unchanged:
  - `chainBandSeg N (2^9) d 524288 512`;
  - both layouts (`segDom salt (2^9)` with a 192-bit salt, and `dom salt` with a 256-bit salt);
  - `∀ d ≥ 5`, `.sequential`, `D = 5`, `Q = 2^20`, `k = 111`, `ε = (2⁻¹)^128`.

  There is no hypothesis beyond the range.
- **It reads only approved definitions.** The repo's `Pous/Model/BandChain.lean` at `a762a82a` is byte-identical to the
  §53 `fc149e43`, and no `Pous/Model`, `Game` or `Accounting` file changes. The PR's trusted edits are this definition,
  one `Registry` name, the `CheckAxioms` line and the two `TRUSTED.sha256` entries.
- **The range is right.** `segDom` keys segment `s` by `tag salt s = salt ‖ u64(s)`, which is injective across
  segments exactly for `s < 2^64`, that is `N ≤ 2^64`. The subagent machine-checked a collision at `2^64 + 1` segments.
  The global layout's indices, below `2^73`, are far inside `dom`'s 256 bits. `[NeZero N]` excludes `N = 0`.
- **My own check.** On a scratch copy of the trusted layer, three axioms:
  - the statement elaborates;
  - it instantiates at `N = 1` and `N = 2^64` with `d = 5`, and `NeZero (N * 2^9)` synthesizes (core's Nat instance);
  - `Fam → BandMultiMeets14` holds, as `fun h d hd => h 448 (by norm_num) d hd`, so the differing `NeZero` proof is
    irrelevant.
- **Nothing is weakened.** It strictly generalizes `BandMultiMeets14`, and, through the global layout at `N = 1`,
  `BandChainMeets64` (the subagent's check). `BandMultiMeets14K106` (`k = 106` at 448) is not subsumed, so it stays
  pinned.
- **It is non-vacuous.** `shared_domain_breaks_fam` is now in the lane (`BandMultiFamily.lean`): `Meets` fails for
  every `N ≥ 2` with a shared domain. So the statement's domain injectivity is load-bearing, not trivial.
- **The grading record exists** (`band-multi/family-pin/GRADE.txt`, the subagent's nit b). The family solution PASSes
  on the three axioms, and both cross-grades FAIL with "does not have the pinned type".

**Nit.** Add "Statement reviewer: bc-22298e90 (§58)" to the docstring beside the subagent's line.

**Verdict: GO on the statement.**

## 59. Flock keyed-draw tier 3 (draft PR #425 at `c4499c8c`): statements GO, with one small witness condition (29 Sep 2026)

This is a statement-only read, as POUS statement reviewer, next to root's red team (bc-f0bc7e75, which granted). The
source is the branch (`backends/flock/verifier/lean/soundness/`) and `…/landing/keyed-draw-statement.md`.

**Scope.** `lean-audit.json` at `c4499c8c` has 128 pins. Its difference from the union of #416 (`8aed7908`, 101) and #427
(`5550fd7c`, 107) is exactly the ten pins requested:
- `subsetOn_escape_le`, `drawOn_escape_le`, `execOS_work_escape_le`;
- `keyedWindow_escape_le` and `keyedWindow_escape_le_of_names`: the two records changed within #425, which now take A5
  as `hsec`;
- `keyedWindow_audit_of_record`, `keyedWindow_extraction_audit_of_record`;
- `prob_auditReg`;
- `keyedWindowReg_audit_of_record`, `keyedWindowReg_extraction_audit_of_record`.

The delta `7fd7e0b9 → c4499c8c` changes no record, only A5's docstring and a restack onto #427's `Window.lean`.

- **The spec pins are the right comparisons.** `subsetOn_escape_le` bounds the per-swap `Key.subset` over uniform
  streams by `Law.subset`'s escape. `drawOn_escape_le` bounds the window's per-stratum draws by `Law.stratified`'s, under
  `PlanStrata`, which ties the layout's strata to `σ` and `k`. `execOS_work_escape_le` bounds the work draw under A3 in
  the same way. Escape is "the draw misses `B`", and a bound on it is what the audit consumes.
- **`keyedWindow` is the live draw.** It is `PlanDraw.window` on `derive(secret, domain, context)`, which is
  `verity.randomness` v1, pinned to the Python by vectors. A refused window (a repeated call index) or a short draw is
  modelled as drawing every unit. That can only help the verifier: a real refusal accepts nothing, and auditing every
  unit means no escape. The docstring says so; keep it that way.
  - **The claim.** `(keyedWindow sec …).escape B ≤ (stratified σ k hk).escape B + η`, with A5 on `sec` and A4 for
    `windowTest B` at every `B`, with one `η`.
  - **`_of_names`.** It replaces the distinct-framings hypothesis with admission, distinct stratum names within each
    call, and frames under `2^64` bytes. These are checks the draw itself makes.
- **Step 4 and the claims of record.**
  - **The bound.** Both forms bound "accept, and at least 0.1% of the work (or verification work) unsound" by
    `2^-40 + η + ε_ks + δ_link`, through #421's slack record form and #427's split lemma. The numeric hypotheses
    (`27713`, `hW`, `hone`, `hN`, `hfy`) are the record form's.
  - **The receipt-keyed game.** `auditReg` is: the prover registers `R`, then `L R`'s coin, then the session.
    `prob_auditReg` is `rfl` onto `audit (L (reg σ))`.
  - **So the per-strategy route is sound.** The registration is fixed before the coin, and the secret is drawn after it
    (A5, C2). A4 and the analysis are taken for every `R`, with one `η`, so grinding the receipt buys nothing.
- **A4 (`KeyedStreamsUniform`, `prf/sha-256`): GO.**
  - **It is scoped, not refutable.** It is a predicate on one test, following A2's precedent, so it is not refutable by
    a key-encoding test. It is used only for the natural `windowTest B`, under distinct framings.
  - **The docstring is right.** The dual-PRF and BCK96 wording is correct, and the secret's uniformity is correctly
    moved out to A5. `η ≤ 2^-128` at `S = 32` is in `ASSUMPTIONS.md`.
- **A5 (`UniformSecret`, `uniform/python-secrets`): GO.**
  - **The Prop.** The secret's pushforward is exactly uniform, a clean statement.
  - **The docstring.** Its platform wording carries the red team's conditions: Linux `getrandom(2)`, fork safety,
    vmgenid or a hardware RNG for restored snapshots, and an idealized CSPRNG. It also says a reused secret is outside
    it.

**Condition** (the standing §29 rule; it doesn't block the statements). Add a satisfiability witness for A5: the
identity source, `UniformSecret (fun ω : Fin S → Fin 256 => ω)`, which holds by `rfl`. A4's substantive content is
cryptographic; its only Lean witness, `η = 1`, is trivial, and saying so in `ASSUMPTIONS.md` is enough.

**Verdict: GO** on the ten pins, the two changed records, A4's docstring and A5.
