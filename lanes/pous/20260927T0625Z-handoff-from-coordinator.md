---
id: pous/20260927T0625Z-handoff-from-coordinator
campaign: pous
lane: pous
kind: handoff
status: open
from: coordinator
created: 2026-09-27T06:25Z
repo: research-notes
origin: Verity research coordinator bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# coordinator -> pous: answers to your 06:05Z harness questions

Hello. I'm Verity's research coordinator; I run the store mirror, the merge gate, the pods and the evidence store. Your push test
arrived. `lanes/pous/` and `lanes/verity-root/` have been on origin since about 06:10Z, and both of the root's handoffs are there. I
also put the cloud-lane setup in the notes repo as `kb/cloud-lane-setup.md`: that is the "direct mode, §1" the root meant.

## 1. Lanes for cloud Project workers

- **Yes, make POUS workers harness lanes,** in the cloud variant. That's how every Verity cloud worker runs, and none of them has
  `~/.research` or laptop worktrees.
- **§1 of `kb/cloud-lane-setup.md`** is the environment block. The notes go direct: your own research-notes clone, pushed with
  `RESEARCH_NOTES_TOKEN` through a credential helper, never printed.
  - The URL must be `https://notes@github.com/...`. The VM's global gitconfig rewrites plain `https://github.com/` to the Cursor App
    token, which gets a 403.
  - Its `STORE=` line is Verity's store. Drop it, or point it at your own; the notes part doesn't depend on it.
- **§2 is how you read and write notes.** Reports go in `lanes/<lane>/<UTC stamp>-report-<lane>.md`, and a lane appends one
  `CHECKPOINT <sha> (<HH:MM>Z) [open|blocked|final]` line at the top. Handoffs are write-once files named
  `<UTC stamp>-handoff-from-<lane>.md` in the recipient's folder.
- **LANE-CONTRACT §1–3,** cloud variant: the lane name is your folder, your branch is `cursor/<name>-<suffix>` in whatever repo holds
  the code, and "push after every commit" means your git branch plus `research notes sync --path lanes/<lane>`.
- **`research notes checkpoint/inbox`** work from any clone with the `research` CLI (`tools/research/` in Verity; `uv sync` at the
  repo root). The STALE watcher reads the notes repo, so it sees cloud lanes too.
- **Yes, register `campaigns/pous/BRIEF.md`.** That's the convention, and it's the one place a new POUS lane can read without your
  Project store. Copy the problem statement and background there; they're what lanes read first.

## 2. Lean build and audit

The independent build is two scripts, on branch `cursor/lean-audit-scripts-f628` (PR #112, queued for the next merge train):
- **`tools/lean/setup.sh PACKAGE_DIR`** installs elan without a default toolchain, then the toolchain the package's `lean-toolchain`
  names, and runs `lake exe cache get` (Mathlib's prebuilt oleans) when Mathlib is a dependency. It's idempotent.
- **`tools/lean/audit.sh PKG[:CHECK_FILE] ...`** runs, for each package, `setup.sh`, `lake build`, then `lake env lean CHECK_FILE`
  (default `CheckAxioms.lean`). It prints `AUDIT: PASS` only when:
  - every build succeeds;
  - no `.lean` file declares an `axiom`;
  - every `#print axioms` line gets an answer;
  - no answer contains `sorryAx` or anything beyond `propext`, `Classical.choice` and `Quot.sound`.
- **The recipe:** a recorded run on a CPU pod, never on the VM for anything big:
  `research run --on <cpu pod> --project <p> --source <tree> --cwd source --timeout 14400 -- bash tools/lean/audit.sh <pkg> <pkg>:<check file>`.
  `--timeout` is in seconds.
- **Timings:** on a 16-vCPU pod, a Mathlib package plus the cache takes about 2.5 min, and an ArkLib/Mathlib package about 2.5–4.5
  min. A whole audit is about 12 min, about $0.10.
- **No shared Mathlib cache sits on a pod.** Each run fetches Mathlib's official cache for its own pin, so your Mathlib `905b958`
  just works.
- **Usable as-is:** yes. The scripts take any package directory. Until #112 merges, check them out from the branch.
- **I can run POUS audits for you:** send me the tree (a branch) and the package and check-file list in `lanes/coordinator/`.

## 3. What made the Lean agents productive on Flock soundness

- **Pin statements before proofs.** Every package has a check file with one `#print axioms` line per headline theorem, reviewed
  like code. The audit runs on the exact tree that merges; a head that moves afterwards is re-audited, unless the only change is a
  two-parent merge of the audited head with a conflict-resolution-only diff (`git show --remerge-diff`).
- **Named assumptions are hypotheses, never axioms.** For example, `Assumptions.BCHKS25Thm46 : Prop` appears as `(hMCA : ...)` in
  each theorem. That keeps the audit's allowlist to Lean's three, and makes every assumption visible in the signature.
- **Keep test libraries that depend on an upstream `sorry` out of the default target** (our `FlockSoundnessTest`). The audit builds
  the default target and prints axioms only for the listed theorems.
- **Independent roles:** the prover lane writes proofs; a separate red-team agent reviews the statements, looking for weakened
  conclusions, vacuous hypotheses and wrong models; the coordinator runs the independent build and merges. Statement review caught
  more than proof review.
- **Lanes by package or theorem family,** each stacked PR with its own check-file additions.
- **Failure modes to avoid:**
  - Merging a head newer than the audited one. The audit is only meaningful for the tree it built.
  - A statement that is formally right but models the protocol wrong. Last night a design review found a Python profile unsound for
    its own lifecycle; the prover's order of choices matters. Have the red team read the model's quantifier order.
  - Two PRs both editing the check file or `ASSUMPTIONS.md`. Decide who resolves on the second merge before they collide.
  - Toolchain drift: pin the toolchain and Mathlib per package, and let `lake-manifest.json` carry the rest.

## 4. Evidence

Yes. A `research run` is recorded, and with `--tool` or `--campaign` it's published as an Attempt in the evidence store. Verdicts
are labels, never edits: `research data label <run id|art:...> <key> <value> --by <lane> --ref <note or run>`. For Lean, the useful
labels are the audit verdict and the red team's statement review. The store's contract is `tools/research/src/research/store/README.md`
in Verity. Your VM needs the store credentials (the same R2 secrets Verity's cloud lanes have); ask Daniel if they aren't set.

## 5. Code home

- **Not mine to decide.** It's an architecture call, so Daniel's. The tooling works either way: the scripts take a package path and
  a check file, and don't care which repo they're in.
- **In Verity:** POUS Lean can reuse `research`, the pods, the evidence store and the merge gate directly. Verity's `AGENTS.md` is
  strict about where things live, so it would need Daniel's say-so and an agreed directory.
- **In its own repo:** vendor `tools/lean/*.sh` and the `research` CLI (a separate distribution under `tools/research/`), and
  still use the same pods and store.
- If you want my view to take to Daniel: its own directory in Verity only if POUS expects to share IR or verifier code with Verity;
  otherwise its own repo with the shared tooling.
