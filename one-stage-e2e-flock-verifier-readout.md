---
cursor:
  subagentId: "bc-6234dc23-40dd-5095-8c63-3d3b083de074"
---

# One-stage e2e readout: Lean Flock verifier (#85 / #113)

Refs: `origin/cursor/flock-verifier-sha512-draw-7ab3` (PR #113 tip `9d0d53df`) unless noted; `IntegrityProfile` / protocols from `origin/main`. Lane notes: `20260927T0445Z-handoff` (M0 format), `20260927T0140Z-report` (412 sessions).

## 1. CLI (`flock-verify`, Main.lean:265–278)

| subcommand | args | stdout / exit |
|---|---|---|
| `verify` | `[--statement ID]` `[--archive DIR]` `--circuit F` `--comp F` `--public F` `[--coins seed\|os]` `--session DIR...` | one `VERDICT {"session","accepted","why"}` per DIR; exit **0** all accept, **1** any reject, **2** usage/input error (Main.lean:109–138) |
| `statement` | same statement flags (no `--session`) | one JSON line (digest, σ, hello, …); 0/1/2 |
| `draw` | `--population N` and exactly one of `--k K` or `--p NUM/DEN`; optional `--stream HEX` | `DRAW {…}` (UnitDraw JSON); 0; 1 stream exhausted; 2 usage |
| `draw-test` | `FILE` (JSON list of `{record,statement,instances}`) | `DRAWCHECK {"ok","why"}` per case; 0/2 |
| `archive-put` | `DIR FILE...` | `{sha512}  {path}` lines; stores `DIR/sha512/<hex>`; 0 |
| `unit-cut` | `FILE...` (cut JSON) | `CUT {"file","ok","codes"}`; 0/1 |
| `comp-check` / `field-test` / `hash-test` / `merkle-test` / `hm96-test [sha512]` | test vectors | summary + 0/1 |

**`verify --archive`:** `F` are **SHA-512 hex keys** into `DIR/sha512/<H>`; object must hash to key (`archiveGet`, Main.lean:66–74). Without `--archive`, `F` are filesystem paths. Session DIR supplies only `session.json` + `<table>.rep{0,1}.bin`.

**`draw`:** population `N`; subset `K` or bernoulli `p=num/den`. Randomness: `Draw.drawOS` → `IO.getRandomBytes` (OS CSPRNG; **not** hard-coded `/dev/urandom` in source). Tests pin bytes with `--stream`. Output (`UnitDraw.toJson`, Draw.lean:74–79):
```text
{"law":"subset","population":N,"k":K,"units":[…ascending…]}
{"law":"bernoulli","population":N,"p":"num/den","units":[…]}
```
**Canonical equality (U1):** `canon` compact sorted-key JSON (`Flock/Canon.lean`); both sides must match after `canon`.

## 2. INPUTS

**Archive (statement objects):** circuit file, verifier public file, compression rows (`comp`), plus pinned MUFU tables under their SHA-512 (`MUFU_TABLES`). Session dir: record + proof bins only (§16.8).

**Producers:** `archive-put`; `agree.py`’s `archived()` (links into `OUT/archive/sha512/`); store fetch via `ci.py` (`research data fetch art:…`). **`selftest --record-dir`:** not found as a Lean-side producer on this ref (forgeries come from PR #83 vectors/`selftest_records.py` in `ci.py`).

**Accepted statement heads** (`Tags.all`, Tags.lean:124–126):
- `verity/flock-netlist/v1` (9294e161)
- `verity/flock-circuit@19c7269a`
- `verity/flock-circuit@fd02e847` (BLAKE3 row leaf, SHA-256 merkle)
- default `verity/flock-circuit` (Merkle/coin SHA-512 unsalted leaf scheme; **still** `row_leaf_in_circuit: blake3-keyed/row/v2`; statement/σ digests still **SHA-256** in Stmt.setup)

**M0 `eb90718f` (`hm96-sha512/row/v1`, `circuit_sha512`, 128-byte `b‖c` publics, SHA-512 Σ/record `_sha512` keys):** **not accepted**. Public.load still expects 32-byte digests and SHA-256 pub.sha (Public.lean:38–42); Record checks `*_sha256` / `proof_sha256` (Record.lean); Main still wires `Blake3Row.leaf`.

## 3. WHAT IT CHECKS

**Session S1–S18** (PROTOCOL §5.3; Record + Verify): kind/aborted; Hello; link exchange; Σ; roots/publics hashes; publics vs statement; points/y; exactly two rep streams; rounds/msg; root_B binding; link_sha256; stream exhaustion; proof digests; equal caps. Plus **PIOP/PCS** in `verifyRep` (§9–§14).

**U1–U3** after S4 (`Draw.check`, Record.lean:99): both-or-neither + canon equal; well-formed draw; `instances == |units|`.

**Partition-cut:** `unit-cut` CLI only (`Partition.validate` ≡ `validate_unit_cut`). **Not** wired into `verify`. Unit indices vs `verity/partition/v1` / program digest: **not found** in verify path; PROTOCOL §16.7: “Still ahead, once the verifier holds the IR program”.

**By content today:** circuit/public/comp/tables via `--archive` SHA-512 keys. Program/partition by content: **not found** (spec aspirational §16.8).

**Verdict:** accept/reject + `why` string in `VERDICT` JSON. **No** IntegrityProfile / draw/δ fields.

## 4. DRAW vs STATEMENT BINDING (§7.3)

Placement: after root registration, before coin commitment; cleartext; no `derive`/hash. Carried as public header `unit_draw` (under `pub.sha` and Σ) and record `unit_draw`. Instance `i` **is** proof unit `u_i` (one Flock instance = one drawn unit).

**M0 must emit for U1–U3:** same draw object on public header and record (canonically equal); well-formed; `instances = len(units)`; proved instances ordered as `units`. Sessions without draw on both sides still pass U-checks (vacuous). PROTOCOL: “until then no recorded session carries one” (pre-live draw).

## 5. AGREEMENT RUNS / LOCAL REPLAY

**“412 sessions”:** recorded CI `research run --tool flock_agreement` `r20260927-012244-342d`: 8 sets incl. SHA-512, **412/412** (note `20260927T0140Z`; result `art:a59f3cb2`). Driven by `agree.py` + `ci.py` over `vectors.json` (honest, mutants, retained, fuzz, forgeries, selftest dumps).

**CPU-only on this VM:** yes (README: interactive coins, CPU only). Toolchain `leanprover/lean4:v4.34.0`, `lake build`, **no** Lake deps for the exe. Notes: setup ~20–30 s, honest RoPE ~32 s; `$0` when inputs fetched. Level3/Mathlib is separate (proofs package).

**Replay at $0:** store arts in README — e.g. RoPE `art:799dab88` / `art:ef080b64` (9294e161), `art:5715c8f9`/`art:b9e86ae1` (19c7269a), `art:d9837120`/`art:bd9f7efb` (fd02e847), RMSNorm `art:fb5157c5`…; `research data fetch art:… --to DIR`. Not primarily repo fixtures.

## 6. INTEGRITY PROFILE + sampled_proofs (`origin/main`)

**`IntegrityProfile`** (profile.py:61): `levels`, `sizes`, `draws` (`Bernoulli`/`Subset`), `delta`; kw: `programs`, `prescribed`, `linked`, `covered`, `drawn`. Methods: `accept`/`rho`/`worst_case`/`to_json`.

**Constructors today:** `TwoStageLaw.profile` (law.py:65–71); tests. **Nothing** builds one from Lean `VERDICT`. vLLM uses `vu_key`/`select_verification_units` (derive-keyed), not flock-verify.

**law.py:** two-stage RU Bernoulli then VU Subset; keys via `derive` (`ru_key`/`vu_key` domains `…/ru-sample/v1`, `…/vu-sample/v1`); `select_replay_units` / `select_verification_units`.

**plan.py:** `VerificationPlan` maps gate classes → `Stage(p,k)` + unconditional covered classes; `units()` → one RU per gate for bernoulli-style plans.

**Contrast:** flock `draw` uses raw OS bytes (exact samplers, no `derive`); sampled_proofs uses beacon-keyed `derive`.

## GAPS for one-stage e2e

- No orchestration: register roots → `flock-verify draw` → cleartext draw → M0 prove drawn units → Lean verify → `IntegrityProfile`.
- Lean verdict ≠ profile; no bridge from `VERDICT` / draw / δ.
- M0 tip format (`hm96-sha512/row/v1`, SHA-512 statement/Σ/record keys, 128-byte publics) **not** in Tags/Public/Record/RowLeaf.
- Program + `verity/partition/v1` not loaded by content; unit membership / leaf positions not checked in `verify` (only standalone `unit-cut`).
- Sampled_proofs still two-stage + `derive`; one-stage cleartext draw is flock-only.
- No recorded e2e session with live `unit_draw` called out as available for Lean replay on this ref (PROTOCOL: draw live on M0 side; agreement corpus predates/does not require U1–U3 non-vacuous).
- Default Tags still BLAKE3 in-circuit row leaf; compression remains Blake3 `comp.rows`.
