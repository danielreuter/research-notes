---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

# Review of PR #111 (`verity/partition/v1`, `Q_word` v1): REQUEST CHANGES

**Reviewer:** lane `audit-lean`, independent of the author (cross-call-check). **Head reviewed:** `034ca061`
(`cursor/partition-object-v1-666c`). **Date:** Sun Sep 27, 2026, about 1:10 AM PT. Reviewed as digest-bearing core.

**Verdict: REQUEST CHANGES.** There are four blocking findings, B1–B4 below. Each is local and fixable in this PR,
without redesign. The design itself holds:
- the object is only program digest plus query;
- the committed set is derived;
- the evaluator is deterministic (exact interned ids, sorted sources, first-seen numbering);
- `owners()` terminates and never returns an owner of −2.

**What I ran.**
- The PR's 15 tests pass at `034ca061`.
- Merged locally with today's `main` (`928790af`, 154 commits ahead): it merges cleanly.
  - Core `packages/verity/tests`: 1,102 passed, 2 skipped.
  - `integrations/vllm/tests/query`: all passed.
- Direct probes of `partition_object` / `cut` at the PR head.
- A line trace of `cut.py` while evaluating the pinned vector from its descriptor bytes (the verifier's path).

## Blocking

### B1. `verify` crashes on a program whose root has a primitive Call

`Partition` explicitly accepts root nodes of form `primitive`, and `evaluate` gives such a Call one unit. But `verify`
(and `Partition.committed`) builds `CallGraph(fn)`, which reads `fn.body.ret`, and a `PrimitiveDefinition` has no body:

```python
Top = composite(("a", Array(2, I32)), I32, lambda B, S, a: B.call(I32Add, a[0], a[1]))   # root node forms: ['batch', 'primitive']
PO.evaluate(Program(Top)).population     # 1
PO.verify(PO.build(P), P)                # AttributeError: 'PrimitiveDefinition' object has no attribute 'body'
```

So the evaluator and the verifier disagree on which programs are in scope, and the Lean port has no pinned behaviour
for this case.

**Required:** give `CallGraph`, or `verify` and `committed`, the primitive Call. That is one computing gate: it reads
its inputs, is returned, and is committed as the output. Add it to the pinned vector.

### B2. Programs the query does not apply to raise instead of being refused

A root node of form `batch` or `scan` raises `NotImplementedError` from `Partition.__init__`. So `verify` raises rather
than returning a `CutVerdict` with a code. For the verifier of record, "not applicable" is a refusal. The Lean port
must refuse exactly the same programs, and today that set is defined by where Python happens to raise.

**Required:**
- a structured refusal from `verify`, for example `query-inapplicable` with the root index and form;
- a written applicability condition in `cut.py`'s algorithm text;
- a negative vector.

### B3. `verify(..., served=...)` checks only the Calls `served` names

When `served` is given, a Call missing from it silently falls back to the derived set, and unknown keys are ignored:

```python
PO.verify(obj, P, served={}).ok                  # True: serving commits nothing, and verify accepts
PO.verify(obj, P, served={first_call: [...]}).ok # True: the other Calls are never checked
PO.verify(obj, P, served={999: [0]}).ok          # True: a key that is no Call
```

The docstring says that `served` is "held to the derived set". A verifier that relies on this check to confirm that
serving committed every crossing value would accept a serving layout that omits them.

**Required:** when `served` is given, its keys must be exactly the program's Calls (refusals such as `served-missing`
and `served-unknown`). If partial maps are intended, remove `served` from `verify` rather than accept silently.

**Also:** document the numbering `served` uses. It is compacted computing-gate indices in layout order (`CallGraph`'s
numbering), not the Call's raw gate indices.

### B4. The pinned vector does not determine the behaviour the Lean port relies on

`partition_vectors.json` is also the version-bump discipline's only enforcement: "any change to a query's behaviour
bumps its version". So what it doesn't exercise can change silently. Tracing `cut.py` while evaluating the vector from
its bytes shows these paths never run:

| Path | Why it matters to the port |
|---|---|
| Packing several outputs into one run (`targets`) | Every width in the vector is 32 bits and X = 16, so every output is a run by itself. Real programs pack 1-, 8- and 16-bit outputs, and no X-dependence is pinned at all. |
| Wide fan-in gates (`_wide_operands`, `member_refs`, the `("u", j)` token), `WIDE_FAN_IN = 4096` | Changes which gates are external and which count as recomputes. The threshold lives in `layout.py`, outside the query. |
| `returned_inputs` (a Call returning wiring of its input) | Changes the committed set and the invariant's input reads. |
| Deduplicating a source read twice (the `seen` skip) | Changes the edge list, and so every ownership decision. |
| `owners()` dropping dead units and repeating the pass (line 385) | A whole branch of the cut algorithm. |
| `separable` refusals (a scan node, partial returns), structure-primitive members (`None` parts in `owner` and `locate`) | Changes unit numbering and `locate`. |
| Primitive root Calls | See B1. |
| Two of the three `WIRING` primitives | Only `F32Fabs_v1` appears. `Bf16ToF32_v1` and `F32BitsShl23_v1` are unpinned, and the set is code, not data. |
| Every refusal: `validate` codes, `program` mismatch, `unit-too-wide`, `gate-recomputed`, inapplicable forms | The port's accept/refuse boundary. |

**Required:**
- vectors that exercise each row of the table: narrow outputs at two values of X, one wide gate, one returned wiring
  input, a dead-unit second pass, and the separable branches;
- the query's non-parameter constants pinned as data in the vector file (`WIRING`, `WIDE_FAN_IN`), with a test that
  they equal core's, so changing either trips the version check;
- refusal vectors: the object mutations with their codes, and `verify`'s failure codes.

The Lean port's agreement on 3,500 random cases is good evidence. Pinning that corpus (its generator seed and the owners
digests) as a vector would make it reproducible here too.

## Non-blocking

- **N1. `program_sha512` has no domain prefix**, unlike the object digest (`"verity/partition/v1\0"`) and the owners
  digest (`"verity/partition/v1/owners\0"`). It mirrors core's `codec.program_digest` (SHA-256, same unprefixed bytes),
  and the descriptor carries its own `schema` field inside the hashed bytes, so I don't block on it. No root binds it
  yet (E6), so this is the cheapest moment to add `"verity-ir/descriptor/v1\0"`.
- **N2. The descriptor schema.** Q_word v1 is specified over schema `verity-ir/descriptor/v1`, but `codec.decode_program`
  also accepts v0, and `program_sha512` hashes any dict. `verify` should refuse a non-v1 descriptor, or the text should
  say what v0 means.
- **N3. `validate` raises `TypeError` on a non-string key** (`sorted` over mixed key types) instead of refusing. It is
  reachable only from non-JSON input; sort with `key=repr`.
- **N4. Query parameters are unbounded** (`X = 10^40` validates). The agreement fixes X and W, so this isn't a soundness
  issue. A stated bound (say `≤ 2^16`) keeps the port's integer types honest.
- **N5. `digest` doesn't validate** its argument, and `query()` coerces with `int()` (`X=16.7` becomes 16). Either
  validate inside, or document "validate, then digest".
- **N6. Complexity.** `owners()` can take O(n·(n+E)) (a promotion round per new committed unit), and `verify` builds the
  flat `CallGraph` of every distinct Definition, including large separable bodies that `evaluate` shortcuts. That is
  correct, but worth stating for the port's budget. The PR's scale table times evaluation, not `verify`.
- **N7. Canonical JSON** (float formatting, key order beyond ASCII, `ensure_ascii` escapes), reference sequences and the
  layout are still defined only by code. The PR says so (`internal/lanes/flock-verifier/20260927T0520Z-amendment-partition-object-v1.md`).
  They aren't a blocker for this PR, but they are a blocker for calling the port specified.

## Checked and fine

- **Digest framing** of the object and the owners digest: distinct NUL-terminated domains, and the canonical encoding is
  `codec.canonical_json` (sorted keys, no whitespace, ASCII).
- **Primitive decoding.** It checks each registry primitive's signature against the descriptor (`params`, `ret`), so
  widths and constant-ness are bound to the digest.
- **Constants.** Constant values are in primitive ids (`Const32[0x00000001]_v1`), so different constants never tokenize
  as a recompute.
- **The separable shortcut** is re-checked by `verify` against the whole flat body, which is how the cross-member
  recompute case is caught.
- **Determinism.** Every set is either sorted before it's used or used only for membership. The memo key
  (`"Q_word", fn.id, X`) omits W correctly, since W doesn't affect the cut.
- **The merge with `main`** is clean, and no digest of record changes.
