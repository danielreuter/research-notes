---
id: 20260930T2135Z-reply-from-coordinator-check-and-lean-data-movement
campaign: verity
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: old research coordinator (bc-8ece7cde), answering @proofs 2:24 PM PDT (Daniel: is data movement a real constraint?)
---

# Data movement for merge-train `check` and Lean builds/audits: small, except the Lean dependency caches, which pin Lean work to a warm node

These numbers come from today's node-1 runs and caches, with no new runs. They are TCQ (`r20260930-204047-2f00`, no Lean change, no `send`) and TLU (`r20260930-205002-a3c8`, a three-PR Lean chain).

## 1. `check` (one merge-train commit)

- **Read:**
  - The train branch by `git fetch` (seconds).
  - The uv environment, from a warm cache of about 1 GB (`~/.cache/uv`).
  - The Lean toolchain via elan (3.0 GB on disk, installed once).
  - A 4 MB verdict tarball that the launcher sends.
  - The Lean dependencies, from local disk (see §2).
  - With `send`, also the upstream Rust verifier build: 448 MB, cached per pinned build (`~/.cache/verity/flock-b684b12`).
- **Written:**
  - The run directory: 48 MB for TCQ, 2.2 GB for TLU (Lean rebuilt).
  - `lean-agreement` under `send`: about 3.9 GB of undeclared scratch (TCP #250). Custody uploads only declared outputs, so R2 gets tens of MB.
  - Disk, not bandwidth, is what bit before: `lean-agreement` and `lean-audit` hit ENOSPC on 30–36 GB RunPod disks.
- **Between steps:** nothing is held in RAM. Steps share only local-disk caches keyed by input:
  - per-slot test verdict caches, 32–40 MB each;
  - the Lean audit's pass cache, 5.9 MB;
  - the Lean dependencies.
- **Wall time on a 32-vCPU slot** (the steps run in parallel):

  | Step | TCQ (no Lean change) | TLU (Lean changed) |
  |---|---|---|
  | Whole check | 909 s (about 15 min) | still running |
  | pytest | 894 s | 946 s |
  | circuit-check | 321 s | 247 s |
  | lean-suites | 426 s | 251 s |
  | lean-audit | 0.3 s (cached pass) | 1,641 s (27 min) |
  | preflight + lean-build | under 1 min | under 1 min |
  | lean-agreement | skipped | — |

- **Startup overhead:** under 1 minute warm (preflight, uv sync and lean-build together).

## 2. Lean builds and audits

- **Dependencies:** one bundle per package, keyed by `lake-manifest.json` and `lean-toolchain`, and fetched from R2 by sha256 (`tools/check/lean-deps.json`).

  | Package | Bundle | Unpacked on node 1 |
  |---|---|---|
  | level3 | 0.70 GB | 8 GB |
  | pous | 0.70 GB | 8 GB |
  | network_warden | 0.71 GB | 8 GB |
  | soundness (ArkLib) | 1.31 GB | 10 GB |
  | **Total** | **3.4 GB** | **34 GB** |

  Mathlib's own build comes from Mathlib's CDN (`lake exe cache get`, 448 MB cache), not GitHub.
- **Audit I/O:** an audit reads those dependencies from local disk and writes a small pass record. A cold export audit (`--export`) also writes new bundles (0.7–1.3 GB each) that custody puts on R2. The Lean re-hash step (`tools/lean/merge.py`) is CPU-only and uses the same dependencies.
- **What pins a job to a node:**
  - **Warm Lean dependencies:** 34 GB, per toolchain and manifest. This is the only real pin.
  - **Per-slot test caches:** under 40 MB. Anywhere works; a cold slot just reruns tests it could have skipped.
  - **The agreement build:** 448 MB, per pinned upstream build.
  - `/root/agreement-inputs` was the RunPod layout; on node 1 it is the cache above.
- **Cold-node staging:** fetch 3.4 GB of bundles from R2 plus Mathlib's CDN cache, then unpack about 34 GB. I have no clean timing for a cold staging; `r20260930-141912-f78f` (network_warden's cold export) is the record to read. Staging is one-time per node per toolchain or manifest bump, and all packages share one toolchain.

## 3. Could `check` split into 15–60 min jobs?

It already nearly is:

- **pytest** (about 15 min), **circuit-check** (4–5 min) and **lean-suites** (4–7 min) are independent. Each needs only the tree and the uv environment, so it can run anywhere.
- **lean-audit** (0–27 min) and **lean-agreement** need the warm Lean dependencies (and the agreement build), so they should go to a node that has them.
- **Splitting cost:**
  - Each job repeats a fetch and a warm uv sync, about 1 minute.
  - Something must collect the per-step verdicts for one commit before `research merge`, which today reads one `check` Attempt.
  - Splitting would shorten a train's wall time only when the Lean audit is the long pole.

## Bottom line

For checks and Lean work, data movement is not a bandwidth constraint. The per-job I/O is about 1 GB warm or less, and results are tens of MB to R2. The constraint is placement: Lean jobs need a node with the 34 GB warm dependency cache, and `send` needs about 4 GB of free scratch. Everything else can go anywhere.
