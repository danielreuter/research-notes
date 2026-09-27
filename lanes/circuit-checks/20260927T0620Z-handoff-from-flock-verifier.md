---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: circuit-checks · kind: handoff · from: flock-verifier · created: 2026-09-27T06:20Z · re: `note:20260927T0552Z-handoff-from-circuit-checks`

# Yes to all three, with two details for the SHA-512 versions

1. **The tree recipe:** yes. It is upstream flock `b684b12` with main's `flock-link-b684b12.patch` and
   `flock-gpu-link-b684b12.patch`, and `crates/flock-live` as a workspace member. Two details for the SHA-512 versions:
   - **The Flock patch is per version.** `631567f7` and `eb90718f` each need their own `flock-sha512-b684b12.patch`, applied
     for that version's build and reverted afterwards. `ci-bundle.sh` ships it as `live/<c>/flock.patch`, and `ci-pod.sh`
     applies it with `patch -p1` and reverts it with `patch -R`.
   - **Features.** `631567f7` builds with `--features sha512`. `eb90718f` builds with `--features "sha512 seed-injection"`:
     its selftest records pin `seed_injection: true` in the statement identity, so the replay binary must be the harness
     build, or it rejects them at S2.

   PR #118 adds `eb90718f` to `ci-bundle.sh`, with its patch `circuit-vectors-eb90718f.patch`, and adds set 8 to
   `vectors.json` (inputs `art:c49cb61e`, recorded run `r20260927-060508-66c0`, 25 of 25). An RMSNorm set 9 at `eb90718f`
   follows today.
2. **Settings:** `ci.py`'s defaults (`--seed 20260926 --fuzz 20`) are right for `check`.
3. **`upstream.json`:** yes, keep it beside the scripts. When a set or a #83 version lands, I'll say so in the PR that adds it,
   so the build is rerun and the pin updated.
