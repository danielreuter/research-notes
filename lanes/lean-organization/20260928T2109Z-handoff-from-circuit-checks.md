---
id: 20260928T2109Z-handoff-from-circuit-checks
campaign: verity
lane: lean-organization
kind: handoff
status: open
repo: danielreuter/verity
origin: circuit-checks
---

# check will cache the Lean audit per package and keep Lean dependencies warm, without editing audit.py

**To:** lean-organization (bc-866e1acc). **From:** circuit-checks (bc-1122c760). **Needs from you:** a reply only if one of the
three assumptions below is wrong, or if your pin-hash change breaks one.

Daniel approved two things for `check`: warm Lean dependencies on each check pod, and reusing audit verdicts across commits with
identical inputs. I'm building both in `tools/check/` as a follow-up to #134, and I'm not touching `tools/lean/audit.py`.

**How check will run the audit step:**
- **The key per package:** for each package with a `lean-audit.json`, the key covers:
  - the tracked files of the package, less the Lake packages nested in it (as `lean_modules` skips them);
  - its path dependencies from `lake-manifest.json` (as `path_deps`);
  - `tools/lean/` in full;
  - `lean-toolchain`.

  A pass is stored under that key, and a hit skips the package.
- **On a miss, hermetically:** the audit runs on a scratch copy holding only those inputs, as `audit.py --all --build --root
  <scratch>/backends --out ...`, from the scratch copy's own `tools/lean`. A read of anything else finds nothing, so the audit
  fails instead of caching a pass.
- **Warm dependencies:** each package's `.lake/packages` is kept per pod, keyed by `lake-manifest.json` plus `lean-toolchain`. It
  is moved into the scratch package before the build and back afterwards. Your `dependencies` check still compares the
  `.olean` digests with the record, and kernel replay still covers our modules.
- **Threads:** `LEAN_NUM_THREADS` is set to the pod's real core count. A pod's hardware count is the host's (256).

**The three assumptions to check against your change:**
1. An audit reads nothing in the repository outside the package, its path dependencies, `tools/lean/`, the fetched dependencies
   and the toolchain.
2. `audit.json` keeps `packages[].package` and `packages[].failures`, and `failed` names the controls when they fail.
3. `--all --root DIR` from a copy of the tool directory stays supported.
