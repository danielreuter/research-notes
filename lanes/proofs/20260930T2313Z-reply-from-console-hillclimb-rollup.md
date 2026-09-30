---
id: 20260930T2313Z-reply-from-console-hillclimb-rollup
campaign: verity
lane: proofs
kind: reply
status: open
repo: danielreuter/website
origin: console (bc-ddee017b, Slack @console)
---

# Re hill-climb plots: yes to a roll-up, one file per subcircuit at `/workspace/usage/hillclimb/` on vy-nebius-1; the console side is built

Re `note:20260930T2259Z-handoff-from-proofs-hillclimb-plots-spec`.

**Yes, please publish a roll-up.** On node 1 the store's outputs are named generically (`result`, `run_files`), so a single
file per subcircuit is simpler and sturdier than scanning attempts. I'll read it directly.

- **Where:** `/workspace/usage/hillclimb/<anything>.json` on vy-nebius-1. The directory exists (research:research, setgid 2775).
  Write the file whole and rename it into place, as with `infra-pool.json`.
- **Shape:** your point records unchanged, wrapped like this:

~~~json
{
  "schema": "verity/hillclimb-rollup/v0",
  "updated_utc": "2026-10-01T05:00:00Z",
  "subcircuit": {"id": "bf16/GemmCoordinate_v2/K=2048", "dtype": "bf16", "definition": "GemmCoordinate_v2",
                 "K": 2048, "dot": "HopperBF16WgmmaDot16_v1"},
  "points": [ {"schema": "verity/hillclimb-point/v0", "step": 0, "...": "..."} ]
}
~~~

  `subcircuit.id` must match `<dtype>/<Definition>/K=<K>`. Include every step, gate failures too; the console draws those hollow
  and keeps them out of best-so-far.
- **Write the file as soon as a subcircuit is set up, with `"points": []`.** Its page appears in the sidebar at once, showing
  "No runs recorded yet". The page list comes only from these files, so NVFP4, MXFP4 and FP8 need no console change.
- **Path to the site:** node 1's `verity-console.timer` (every 5 minutes) publishes each file as the table panel
  `verity/hillclimb-<slug>`. Deployed at 4:12 PM PDT, dry run clean.
- **Limits:** one panel holds about 130 steps (64 KiB). Strings are cut at 200 characters, commits at 12.

**Site:** `/console/proofs/<slug>`, one page per subcircuit, grouped in the sidebar as "BF16 GemmCoordinate_v2 → K = 2,048". The
page stacks three hover-synced panels against step:
- overhead on a log axis in powers of ten, with the best-so-far line;
- VU/s;
- GPU util % with GPU-held s/VU on a right axis.

The tooltip shows label, commit, run, PT time, byte-identity and flag badges. The latest best is shown top right, with its
flags. The old Progress (prover-overhead) page is gone from the console. It's on website `cursor/console-v2-a491` @ 2f6ced2 and
not deployed; Daniel's go-ahead is pending.

**Not yet removed:** the control pod's store group still publishes `verity/prover-overhead-*` and `verity/prover-gains` to
`/admin/live`. I can't reach the control pod. Whoever holds it should drop those two from `verity_console.py`'s store group, and
the stale rows would then need deleting from the site DB, which needs Daniel's yes.
