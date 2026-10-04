---
id: lean/20261004T2112Z-draft-formal-verification
campaign: lean
lane: lean
kind: draft
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# Formal verification

Draft of a documentation page, 3 Oct 2026. The first half describes the design in the abstract and the second half how it
is built today. It replaces `docs/lean-workflow.md`. The architecture it sits in, the protocol and the harness, is in
`note:lean/20261004T2112Z-draft-architecture`.

## What it is

Formal verification turns Verity's security claims into **validated specs**.

- A **spec** is everything a reader has to trust about a protocol's security, written in Lean: the **protocol** (its
  definitions), the **assumptions** (each a named `Prop`), and the **guarantees** (each a `Prop` saying that assumptions
  imply a conclusion about the protocol), with every definition they mention.
- The **math** is the proofs: every theorem and lemma that derives the guarantees from the assumptions. Nobody reviews
  it; a machine checks it.
- A spec is **validated** at a commit when a person has approved it and a machine has checked that the commit's math
  proves every guarantee from Lean's allowed axioms only.

The record lives in the database: commit C validates spec S, whose digest is D, and reviewer R approved D.

The work splits by who can do it:
- **People read the spec.** That is the **spec review**, and it ends in an **approval**.
- **A machine checks the math.** The **validator** confirms that a commit's proofs prove exactly the approved spec, with
  every declaration replayed through Lean's kernel. That is **validation**.

A proof is never read by a person, and a spec is never trusted until a person has read it. What has to be trusted is
the spec, the validator with Lean's kernel, and the integration machine. Proofs, authors, development machines and the
build cache are not.

## Architecture

~~~mermaid
flowchart LR
  subgraph dev["Development: the author's VM, untrusted, decides nothing"]
    A["Author<br/>(person or agent)"] --> W["Edit spec or proofs,<br/>check what changed"]
  end
  subgraph int["Integration: hardened server, decides merges"]
    B["Build from source,<br/>sandboxed"] --> V["Validate the proofs<br/>against the approved spec"]
    G["Merge gate"]
  end
  SR["Spec review<br/>(a person)"] -- "approves the spec's digest" --> DB[("Database")]
  W -- "pushed commit" --> B
  V -- "result for this commit" --> DB
  DB -- "pass + approval" --> G
  G --> M[("main:<br/>validated specs")]
  G -- "on merge: publish<br/>the commit's build" --> C[("Build cache")]
  C -- "read, hash-checked" --> W
~~~

Development has to be fast; integration has to be fast and secure. The database records every integration run and
every approval, and the merge gate reads only that. The cache carries integration's work to development, one way only.
Integration is not specific to Lean: it is the repository's one merge check, and validation is one of its steps.

## Parts

**Lean package.** Every package that states guarantees uses four modules:

| Module | Holds | Trusted |
|---|---|---|
| `Protocol` | the protocol's definitions, the shape an implementation must match | yes: it's part of the spec |
| `Assumptions` | each assumption as a named `Prop`, with its rationale | yes: it's part of the spec |
| `Guarantees` | each guarantee as `def G : Prop` | yes: it's part of the spec |
| `SecurityProofs` | `theorem G : Guarantees.G`, and every lemma behind it | no: the validator checks it |

**Shared definitions.** The definitions every spec is stated in live once, in core's Lean package
(`packages/verity/lean`, `Verity.Protocol`), and each protocol's spec imports them: the probability of an outcome over
the verifier's uniform coins (`prob`, and `value` for an optimal prover), and the one form of a guarantee
(`Sound g accept E δ`: whatever the developer does, the verifier accepts while the claim `E` is false with probability
at most `δ`). The game is not a category of its own (Daniel, 3 Oct 23:39Z): what it models (who moves, what the
developer may do, that the verifier's coins are uniform and live) is part of the assumptions, beside claims about the
world such as uniform OS randomness or SHA-512's collision resistance. Core's code still names it `Verity.Game`.

**Spec lock.** A file in the package that records the digest of its spec: the three trusted modules and every definition
they read. A changed digest means a changed spec, and it needs a spec review.

**Spec review.** A reviewer other than the author reads the printed spec and approves its digest for a commit. The
approval carries to later commits while the digest stays the same.

**Validator.** `validate(spec lock, commit)` returns a verdict per guarantee:
- It builds a trusted challenge, `theorem Check.G : Guarantees.G := sorry`, from the approved spec, and treats the
  commit's `SecurityProofs.G` as the answer.
- Lean's comparator checks that the two statements match constant for constant, and that the only axioms used are
  `propext`, `Classical.choice` and `Quot.sound`.
- Every declaration is replayed through the kernel.
- It runs sandboxed, failing closed, and builds from source without reading the cache.

**Integration.** The repository's merge check runs on a pushed commit, on a hardened machine. Validation is one of its
steps, beside every package's tests. A merge needs a pass on that exact commit, plus a spec review for any spec it
changes.

**Build cache.** It holds compiled modules for merged commits, keyed by toolchain, platform, dependency manifest and each
module's input hash. Integration writes it, and only on merge. Development machines read it with a read-only credential
and check every file's sha256. A kill switch empties it for every client at once.
- The bucket is `verity-lean-cache`. Everything lives under `main/`, which a 7-day lock keeps from being overwritten or
  deleted. There are two kinds of object:
  - one record per merged commit and package, `main/<toolchain>/<platform>/<package>/<manifest>/<rev>.sha256.json`, with
    the sha256 and size of every file the build staged: Lake's `outputs.jsonl` mapping, and an archive per module;
  - blobs `main/blobs/<sha256>`, each named by its own hash and shared across commits.
- The client (`tools/lean/cache.py get`) downloads every file itself and checks its sha256 against the record before Lake
  sees it. Then it hands the files to Lake (`lake cache unstage`), and `lake build` restores those modules instead of
  compiling them. Lake never reads the bucket, because its own hashes aren't cryptographic. A miss or a mismatch means the
  module is built from source.
- The publisher builds in the integration sandbox and runs as root outside it. It hashes the staged files itself and signs
  its uploads directly with the bucket-scoped parent key (`/etc/verity/lean-cache.env` on the integration machine, root
  only). No Cloudflare API token sits beside the key to mint short-lived credentials, because such a token would be a
  broader credential than the key itself.
  - Every write is conditional (`If-None-Match: *`). A 412 or a 409 means the object already exists; the publisher then
    checks that the stored blob's ETag is its MD5, and refuses to publish if not.
  - Blobs go up in a single part, so the ETag is the MD5.
  - The record goes last, so every blob a record names exists.

## What it uses from the rest of Verity

| Interface | Owner | How formal verification uses it |
|---|---|---|
| Tool declarations (`research.store.tool.Tool`) | research | the validator and the merge check are Tools: a name, a command, and the result kinds they produce |
| `research run` | research | every validation and merge check is a recorded run of an exact commit |
| The database (today "the evidence store"): artifacts, runs, results by kind, labels | research | results (`check/v1`, a new `lean-validation/v1`), spec-review approvals as labels, the pinned dependency bundles |
| Merge gate (`research merge`, trains) | research coordinator; Control runs trains | it reads the merge check's result and the spec-review labels |
| Machines and the scheduler | infra (`tools/cluster`) | integration's machines and job slots |
| Control (the site) | console | the cache's kill switch, the trains' gate, and the docs |
| Object storage (R2) | console deploys | the build cache, in a bucket of its own |
| Lean toolchain, Lake, comparator, Mathlib, ArkLib | upstream, pinned in the repository | building and checking |

## What depends on it

| Consumer | Reads |
|---|---|
| The merge gate | whether validation passed on the exact commit, and whether each changed spec was approved |
| Documentation (Table 1, protocol pages) | which guarantees are validated, under which assumptions; claim ids from `verity.claims` |
| Each protocol's `PROTOCOL.md` | its guarantees by name |
| Protocol implementations in Python | `Protocol`'s definitions, which differential tests compare them against (e.g. the warden's `schedule.py` against `NetTiming.Protocol.Schedule`) |
| The upstream watch | each assumption, to report when a pinned dependency proves it |

Lean also appears in Verity as **code**: C-Flock's verifier of record is a Lean program, which benchmarks run and the
merge check compares with upstream's Rust verifier. That code uses the build and the cache, but validation concerns
proofs only.

## As implemented today

| Part | Today | Gap |
|---|---|---|
| Lean package | `protocols/{pous,pouw,network_warden}/lean`, `packages/verity/lean`, `backends/flock/verifier/lean/{soundness,level3}` | C-Flock's packages and parts of PoUW predate the four modules |
| Spec lock | `lean-audit.json`: a record per guarantee (its statement and every definition it reads), written by `tools/lean/audit.py --update` | one digest of the spec instead of per-theorem records |
| Spec review | the `statement-reviewer` grant: a store label on `pr:N@head`, required by `tools/check/queue.toml` when a record's statements or reads change | the trigger becomes the spec lock's digest |
| Validator | `tools/lean/audit.py`: lint (no `sorry`, `axiom` or `native_decide`), pinned statements, kernel replay (`Replay.lean`), the upstream watch; declared as Tool `lean_audit`, run nightly on main | the comparator check against the approved spec, a sandbox that fails closed, and its own result kind |
| Integration | `check` (`tools/check/check.py`, Tool `check`, result `check/v1`): every test suite, `circuit-check`, and the Lean steps (`lean-audit`, `lean-changed`, `lean-unit-cut`, `lean-agreement`), on node 1 or 2; then `research merge` or a Control train | builds aren't sandboxed; every job on node 1 runs as `research`, which has passwordless sudo, so any job can read the machine's credentials and write check's cached passes; the trains gate on main reads no `merge_requires` rules since `preflight=` moved after them (infra's fix in #966) |
| Build cache | the bucket `verity-lean-cache` with its lock and lifecycle rules (console, 3 Oct 20:56Z); the read token in the Personal environment's secrets; the parent key on node 1; pinned dependency bundles come from the store (`tools/check/lean-deps.json`) | the publisher and the client (`tools/lean/cache.py`, @lean, in progress), infra's sandbox and timer, the kill switch |
| Development | Cursor VMs, building from source; `tools/lean/setup.sh` installs the toolchain and Mathlib's cache; the fast path (`lean_changed.py --records`, #966) checks records on node 1 | restoring pinned dependencies and main's cached build on setup |

**Is `check` a tool?** Yes. In research's terms a Tool is a declared program: its name, its command, the result kinds it
produces and what a merge requires of it. `research run` records each run of it in the database. `check` is the repository's
integration Tool, and `research merge` accepts a commit only with a passing `check` of that exact commit. Lean
validation is one of its steps. Daniel's ruling (3 Oct 23:39Z): `check` becomes `validate`, and the workflow this page
calls integration is validation. The name is wired into the merge gate, the trains, the push guard and the `check/v1`
result kind, so the rename lands as one change with them.

## What to build, in order

1. **The validator** (`tools/lean/`): comparator against the approved spec, plus replay and lint. It runs sandboxed and
   fails closed. Declared as a Tool producing `lean-validation/v1`; `check` runs it as its Lean step, and an author can
   run it alone on any pushed commit.
2. **The spec lock and spec review:** a `lock` command that prints the spec with its digest, and the approval keyed
   on that digest (`queue.toml`, `research merge`). It replaces the per-theorem records and `--update`'s review.
3. **Integration hardening** (infra and the validator's owner): jobs stop running as a user with sudo; then Lean
   builds run in infra's sandbox, and check's caches live under a user no job runs as. Every merge gate reads its rules
   from the `check` declaration itself and fails closed when it can't.
4. **The build cache:** the bucket and controls (console), the publisher on merge, and the client in `tools/lean/`
   with the sha256 check and the kill switch.
5. **Development setup:** `tools/lean/setup.sh` restores the pinned dependencies and main's cached build.
6. **Names:** update the Glossary and `AGENTS.md` (the table below), and move the remaining packages to the four modules.
7. **One shared model:** PoUS, PoUW and C-Flock's soundness each define their own probability (`Pous.pr`, `Pouw.pr`,
   `FlockSoundness.Game.prob`), which predate core's. Each moves onto `Verity.Game`/`prob`/`Sound`, or first proves
   that its own definition equals core's, so that existing statements keep their meaning while they move.
8. **This page,** on the docs site.

Retired once those land: per-theorem records in `lean-audit.json`, `--update`'s review printout, and the fast path's
record check (#966), whose job the cache and the validator take over.

## Names

| Today | Becomes | Why |
|---|---|---|
| Lean audit, `audit.py` | validation, the validator | in the Glossary an audit is the developer–auditor protocol |
| `lean-audit.json`, pins | spec lock | it records the digest of the spec |
| pinned theorem, pinned statement | guarantee | already the Glossary's word |
| statement reviewer | spec reviewer | in the Glossary a statement is what a backend proves |
| the `lean-audit` step | the `lean-validate` step | follows the validator |
| `check`, the workflow called "integration" | `validate`, validation | Daniel, 3 Oct 23:39Z; it frees "integration" for the vLLM kind of component. One change with the gate, trains, push guard and `check/v1`, which are wired to the name |
| game (`Verity.Game`) | part of the assumptions | Daniel, 3 Oct 23:39Z: what the game models is assumed, not a category of its own |
| proof lane | an author | a lane is one agent on one task |
| validated guarantee | validated spec | the spec is what gets reviewed and validated, as a whole |
| evidence store | the database | a general store of artifacts and labels, of which runs are one kind of record; research's rename, repository-wide |
| grant (`grant=statement-reviewer`, `grant=red-team`) | approval, by a role | every sign-off by a person that the merge gate reads |
