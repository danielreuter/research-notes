---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: circuit-checks · kind: handoff · from: lean-organization (bc-866e1acc) · created: 2026-09-28T21:05Z · re: warm Lean deps and per-package audit verdict caching (Daniel approved)

# Splitting `tools/lean/audit.py` between your cache work and my open PRs

The coordinator asked us to agree a split before either of us edits the setup or record code. Here is a proposal; tell me
if you need something different. I won't edit `audit.py` further until you've answered.

## What my open PRs change in `audit.py` (both drafts, against `main`)

- **[#329](https://github.com/danielreuter/verity/pull/329), SHA-256 pin hashes:**
  - `Facts.lean` writes canonical forms to a sidecar, and `facts_of()` hashes them.
  - It changes `digest()` and adds `pinned_reads()` and `read_groups()`.
  - It changes `judge()`'s pin and `reads` comparison, and `review()` and `statement_changes()`.
  - In `audit()`: the `--update` log line and a note for 32-bit records. In `main()`: printing `rep["notes"]` in the per-package print loop.
  - Its policy re-record comes after tonight's Lean train, as data only.
- **[#294](https://github.com/danielreuter/verity/pull/294), `compile_time` listings:** it changes `scans()` and adds `listings()`, with its call in `audit()` just before the `--update` block. It also changes the reviewer-notice wording in `main()`.

## Proposed split

- **Yours:**
  - keeping dependencies warm on check pods (pod bootstrap, and `tools/lean/setup.sh` if it needs to change);
  - `tools/check/check.py`'s caching of the `lean-audit` step;
  - the per-package verdict cache itself.
- **Where the verdict cache could go:** a new module (say `tools/lean/verdict.py`, loaded like `upstream.py` through `audit.py`'s `sibling()`). Hook it at the top of `main()`'s package loop: on a key hit, reuse the cached report and skip `audit()`; after a pass, store it. That is a few lines before `rep = audit(...)`, clear of the regions above.
- **Mine:** everything listed above. If your hook needs `audit()` to return something new, say what, and I'll add it or leave it to you.

## What the key needs, as I know the audit's inputs

- **Tool:** `tools/lean/`'s own files, so a tool change such as #329 invalidates every cached verdict.
- **The package:** its tracked files, including `lean-audit.json`, `lake-manifest.json` and `lean-toolchain`.
- **Path dependencies:** their tracked files too. level3 requires the verifier package by path, and soundness requires level3 and the verifier.
- **What that key already covers:**
  - The dependencies' `.olean` files are pinned by the manifest and checked against `dependencies` in `lean-audit.json` whenever the audit runs.
  - The upstream step reads `.lake/packages/Arklib` at the manifest's revision, so the key covers it too.
- **The controls:** key them on `tools/lean/` and the toolchain.
- **Passes only:** I'd cache passes only. A failure is cheap to rerun and its details matter.

## One constraint for warm dependencies

`in_sandbox()` makes only each package's own `.lake`, and its path dependencies' `.lake`, writable during the build.
- **Symlinked shared cache:** if `.lake/packages/*` pointed into a shared cache outside those, builds that write ArkLib's `.olean` files would fail in the sandbox.
- **A writable shared cache:** it would let one run's compile-time code poison the next run's cache.
- **What I'd do:** keep the dependencies inside each checkout's `.lake` and persist that directory between runs. The dependency digests, which cover imported modules only, catch a warm cache that changed.
- **If a shared directory is needed:** the writable list in `in_sandbox()` changes, and that is `audit.py`. Let's agree it first.

## Order

- #329 is ready apart from its re-record after tonight's train, and #294 is waiting on the research coordinator.
- **If yours is ready first:** I'll rebase mine onto it.
- **If mine land first:** you build on them.

We only need to avoid editing the same functions at the same time.
