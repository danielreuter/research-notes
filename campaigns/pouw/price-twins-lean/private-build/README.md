---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# The price-twins lane's private build, for a successor (1 Oct, 02:05Z)

This folder holds what lived only on bc-876ca543's VM: the policy and aggregator of the private copy that every audit in
`../README.md`, `../v2-hot/`, `../v1-hot/` and `../fp4-delta/` ran on. The source tree isn't copied here, since the lane
contract keeps source trees out of `internal/`. `manifest.sha256` pins every `.lean` file instead.

| File | What it is |
| --- | --- |
| `lean-audit.json` | the copy's policy after the last audit: 853 pins (store base + every staged set of this lane), with its `layers`, `assumptions` and `reads` |
| `PearlC-aggregator.lean` | `Pouw/PearlC.lean` as built, with the staged modules imported after the store's |
| `manifest.sha256` | sha256 of all 234 `.lean` files in the copy (`Pouw/**`) |
| `lean-toolchain` | `leanprover/lean4:v4.34.0`; Mathlib `5ed2965256` |
| `compose-check-v2hot.lean` | a scratch check, not a module: bc-b58c6093's TT_OUT and accounting lemma with this lane's twin and value lemma give 0.36217% as one theorem, using only the standard axioms. It needs bc-b58c6093's `ttout-lean-staging/v2-hot/` files overlaid |
| `sync.sh` | `sync.sh SRC DST`: copy into the store with retries and a sha256 check, since the store's FUSE mount returns EAGAIN under load |

**How the copy was built** (the build section of `../README.md`):
1. Start from the store's `lean/submissions/pouw/` (09:20Z).
2. Apply `rev1-tile-device-bundle/bundle.diff`, add `device/`'s chain-cap files, and overlay `ttout-fp4-staging/` (11:33Z).
3. Apply rev2's two `Device.lean` items and `DeviceSm120Gamma.lean`.
4. Overlay this lane's `Pouw/`, `fp4-delta/Pouw/`, `v2-hot/Pouw/` and `v1-hot/Pouw/`.

The store has moved on since (M1 and later merges). So a successor should rebuild on the current store and run
`audit.py --update`. The type hashes should match the staged records.

**Audit tool.** These records were written by the workspace's `tools/lean/audit.py`, which prints raw notation. The store's
vendored tool (`lean/tools/lean`) prints `d.G = 0` and `↑(…)`. The two tools agree on every type hash and assumption, and
the `*-store-print.json` files hold the store-tool printing.
