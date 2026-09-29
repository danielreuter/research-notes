---
cursor:
  subagentId: "bc-51aad0a4-29e4-5b89-a799-383acbe93d5f"
---

lane: coordinator · kind: handoff · from: generated-outputs (bc-51aad0a4, vllm project worker) · created: 2026-09-29T03:50Z ·
to: research coordinator (bc-8ece7cde) · cc verity-root

# Fleet guard request: prefix `vy-check-genout`, and a go for a notes push

Two asks. Please reply in `internal/lanes/generated-outputs/` (Project store).

## 1. A guard for one check pod

Daniel's rule is that generated output isn't kept in git. This check is for the Verity PR that applies it, branch
`cursor/remove-generated-outputs-3d5f`, head `428b254d`. I'll record `check` on it:
`uv run python tools/check/check.py --record --on vy-check-genout`.

- **Prefix:** `vy-check-genout`.
- **Cap:** $1.50. **Deadline:** 06:30Z. **Balance floor:** $25.
- **The pod:** one CPU pod, 8 vCPU (`--cpu cpu5m --vcpu 8`, 64 GB, 120 GB disk), the default image, with the pod-side idle guard
  (`--guard true`). I expect a cold Lean audit, about 1.5 to 2 h.
- **Nothing under `backends/flock/` changes,** so the run skips `lean-agreement` by name and needs no `--send`.
- **Order:** I create the pod only after you confirm the guard is armed. I terminate it as soon as the run's custody is on the
  remote.
- **One more problem:** the GitHub token on my VM is invalid, so the branch isn't on origin yet. `research run --on` ships the
  commit to the pod over ssh, so the check doesn't need origin. The merge does, and I'll push as soon as the token works.

## 2. The notes cleanup: when may I push to `main`?

It's ready, and it's on the notes remote as branch `evidence-to-store-3d5f` (not `main`). It is two commits on `942e0118`:

1. **`0171208f`:** `steward.toml` sets the render's `out` to `/workspace/steward/renders/daily`, outside the notes. The kb gets
   the rule "evidence goes to the store": LANE-CONTRACT 2.5 (§6, §8, §C), plus cloud-lane-setup, ops-tools, TABLES and
   kb/README.
2. **`888e160e`:** removes 4,401 files, 70 MB, from `renders/`, `campaigns/*/assets/` and `lanes/*/evidence/`.
   - I checked every one against the store by hash: its sha256 names a remote object with the same size and an MD5 ETag
     equal to the local bytes.
   - The index is `art:4bedc7b053caaa80c0105fa9346ee799b00cbdb09a2492879b459e85092e35d9` (PRESERVED). It maps each path to an
     `art:` id and member. The README says how to resolve a `notes-asset:` path.
   - History isn't rewritten.
   - The 631 files the store doesn't hold stay (211 MB, mostly 90 renders).

**The push needs this order, or the mirror puts files back.** The mirror's forward filter sends each cloud lane's whole folder
(`/lanes/$l/***`) from the store to the pod clone. The pod's `notes sync` then commits whatever the clone lacks. That covers 537
of the removed files, in 62 cloud lanes.

Before I push, one of these must hold:

- **(a)** The control pod's research checkout (`/workspace/steward/verity`) has this PR. Its `notes sync` and snapshot then
  leave `renders/`, `campaigns/*/assets/` and `lanes/*/evidence/` out.
- **(b)** The mirror's `fwd` gets `--exclude='/lanes/*/evidence/'`, in `cloud-mirror-filters.sh`, before its
  `/lanes/$l/***` includes.

Two more mirror changes, whichever you pick:

- In your local `pass.sh`, the render source moves from `$N/renders/daily/*-tables.json` to
  `/workspace/steward/renders/daily/*-tables.json`.
- The steward writes its renders there from the next 13:00Z render. The old code already does, because `out` is absolute.

Tell me which one holds, and I'll rebase onto `main` and push with `research notes sync`. Or wake me with
`WAKE: generated-outputs bc-51aad0a4 notes push`.

A merge request for the Verity PR follows once `check` is recorded.
