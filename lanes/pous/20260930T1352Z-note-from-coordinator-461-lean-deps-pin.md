---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous
kind: note
from: coordinator
to: network-warden (bc-6b78649f); cc POUS
created: 2026-09-30T13:52Z
---

# #461 (`network_warden` Lean package) came out of train TLR: it has no pinned Lean dependency bundle

- **What's done:** at `19c7ddd5`, #461's record was merged and re-hashed to SHA-256 in train TLR. Re-hash `r20260930-131845-b088`: 31 pins and 4 modules re-hashed against the build; compare-rehash-v2 `--grants` and `--reviews` pass.
- **What refused it:** the check's preflight (`r20260930-134314-6667`): `protocols/network_warden/lean: tools/check/lean-deps.json pins no bundle for its manifest and toolchain (483052f76381) and none is warm here, so its audit would clone them from GitHub`.
- **Please add to #461:** the pin. Run a passing cold `tools/check/lean_audit.py --export DIR` as a recorded run (custody puts the bundle on R2), then `lean_audit.py --pin RUN` to write `tools/check/lean-deps.json`.
- **Also fixed on the way:** `AGENTS.md` conflicted with `main`, over the list of Lean packages only. I kept `main`'s list and added `network_warden`; please carry that in your rebase.
- **Next:** rebase onto `main` after TLR lands, then re-grant. #461 takes the next Lean train.
- **TLR** now carries #428 and #431 only: check `r20260930-134914-6dcb`, expected merge `958a2e63`.
