---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
lane: coordinator
kind: handoff
from: census-json (bc-d763c580)
created: 2026-09-25T23:15Z
---

# census-json: two PRs ready. Merge both after the 01:00Z switch, #39 first.

**To:** research coordinator (bc-8ece7cde). Neither PR is needed for tonight's switch. Don't move `/workspace/steward/verity` onto them until the switch recipe has finished.

1. [PR #39](https://github.com/danielreuter/verity/pull/39) (`cursor/census-registry-574a`) adds `verity.census`. It's a typed, stdlib-only registry with stable ids for:
   - hardware peaks: `a100-sxm4-80gb/bf16`, `h100-sxm5-80gb/{bf16,e4m3}`, `rtx-4090/e4m3`, `rtx-5090/e2m1`;
   - networks: the reference `dc-1ms-100gbps`, plus `rtt-20ms-100gbps`, `rtt-100ms-100gbps` and `dc-1ms-10gbps`;
   - the workload `vu-k1536`;
   - the five frozen instance sets.

   `Target.native_peak` is now a census line, and `NativePeak` is gone. `contract`, `tables`, `views` and `latency` read peaks, networks, K and B, and the instance digests from the census. `tools/native_peak` is cross-checked against it by a test.
2. [PR #40](https://github.com/danielreuter/verity/pull/40) (`cursor/tables-json-574a`, which contains #39) adds `views --format entities`. That's the docs site's JSON, with circuits, configurations, results, the printed tables, and the census and claims entries it cites. It also adds `verity.claims` (the claim ids, such as `cr/sha-512` and `logup`). The steward's `published = "views"` entry now also writes `<stamp>-tables.json`.

**Evidence:**
- The markdown renders are byte-identical to main's: `views` under spec, legacy and unfiltered, raw JSON, and the frozen `tables`. Checked on a synthetic store of 124 results; parity ok.
- Tests pass except five failures that main also has: `test_evaluation` kernel list, `test_repository` ×2, `test_pods_connect[rsync]`, `test_store_honing` evict.
- There's no evidence store on this VM, so run `views --parity` on the control pod after the merge to confirm.

**After the switch and both merges (control pod):**

~~~sh
python -m verity_numerical.bench.views --root $ST --published --format entities > $RESEARCH_NOTES/../<this folder>/<stamp>-tables.json
~~~

From then on, the steward writes `<stamp>-tables.json` beside `<stamp>-tables.md` every day.

**For the docs site (please forward):**
- Its request is answered by PR #40's `--format entities`.
- A synthetic sample of the shape is `20260925T2315Z-sample-tables-entities-synthetic.json` in this folder. It's synthetic results, not real numbers.
- Its `assumptions.ts` isn't reachable from here (the branch isn't pushed), so I couldn't match its 26 ids one by one. I followed its format instead: `property/instance` for primitive assumptions, bare kebab ids otherwise.
- `verity.claims` is the source. The site should import from the render's `claims` section (each id's kind, name, label and standing) and delete `security-profiles.ts`.
- Any site id missing from core should come back as a request to add it to `verity.claims`.
- Text the renderer can't map yet is kept and listed under `unmapped`: free-text assumptions such as "BabyBear with its extension", the transcript-binding hash roles, and SP1's "unknown" ZK.
