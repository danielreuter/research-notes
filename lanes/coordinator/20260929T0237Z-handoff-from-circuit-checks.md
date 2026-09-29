lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-29T02:37Z · to: research coordinator (bc-8ece7cde)

# Merge request: #334 at 4e81bb36 (verdict reuse + warm Lean dependencies), measured on one US 8-vCPU, 32 GB pod

- **Head:** `4e81bb36` (`cursor/check-verdict-cache-4d78`). It contains main `5810574d` (train K2, with #134) and merges cleanly
  onto main `b4fd93e9`. Please record `check` on the train candidate.
- **Measured** on US-CA-2, cpu3g 8 vCPU and 32 GB, with the steps in parallel and the agreement skipped by name (#334 doesn't touch
  backends/flock/):
  - **cold, `r20260929-012455-b576` on a13124d7:** 41.1 min. The Lean audit took 39.9 min with every dependency cloned and built;
    pytest 21.4, circuit-check 11.2.
  - **warm on the next commit, `r20260929-021245-4f82` on 4e81bb36, passed:** 15.4 min.
    - The Lean audit took 0.2 s, with all 4 packages reused.
    - circuit-check took 47 s, with 834 of 834 targets reused.
    - pytest took 15.4 min, re-running every suite because #320 keys each suite on every pyproject.toml and that commit changed
      one.
    - A commit that leaves the workspace metadata alone reuses the suites too, so check is about 1 min. That figure is derived
      from these steps, not measured as one run.
- **Guards:** a pod-side dead-man fails closed through the pod key's GraphQL `podTerminate`. On this image `runpodctl` is
  unauthorized with that key, so arming failed closed twice first, and those two pods were terminated before setup. The VM
  guard was capped at $1.50: spent $0.39, and it's stopped. The pod is terminated.
- **The 401 risk for the Lean train, and the proposed durable fix:**
  - **The risk:** a cold audit clones about 30 dependency repositories anonymously. GitHub throttles that from RunPod's shared
    NAT addresses, and the coordinator's check pods share them.
  - **The fix:** store each package's fetched `.lake/packages` once as an artifact in the evidence store, keyed and pinned by
    `lake-manifest.json` + `lean-toolchain`, like `upstream.json`. A pod that completes a cold fetch produces it and publishes
    it through the run's custody.
  - **How pods get it:** the launcher gives each check run a short-lived presigned R2 URL for it. That is read access to one
    object, not an account credential, and nothing goes through the control pod's disk. The pod verifies it by hash and
    restores it before the audit.
  - **The result:** no GitHub clone ever happens. The audit's `dependencies` digests and kernel replay still check everything.
    #334's per-pod warm cache then makes repeats free.
  - **Needs:** Daniel's OK if a presigned URL counts as a credential. Mathlib's own oleans can keep coming from Mathlib's cache
    CDN, which isn't GitHub, keeping the artifact to sources plus the ArkLib build.
