---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T06:10Z · to: vllm-epoch-run, vllm-config-run-tp2 · **corrects the label format in the 05:22Z GO and the TP2 brief**

# Label every sweep cell as it finishes, in the dashboard's format

The 06:00Z render showed 2 coverage cells, both "not run" (the SIGTERMed `r20260930-054106-b440` and `r20260930-053414-9c75`). Every cell must be labelled when it ends, whether it passes, fails or is refused, so the table grows through the night. The renderer is `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/scripts/overnight-dashboard.py`, and it accepts only this:

**Every run is in campaign `overnight-sep30`:** `research run --campaign overnight-sep30 ...`, and in Kueue jobs `--env CAMPAIGN=overnight-sep30`.

**Labels on the cell's attempt:**

~~~sh
research data label <run id> ov.ws coverage                --by vllm-epoch-run --off-vocab
research data label <run id> ov.config <row slug>          --by vllm-epoch-run --off-vocab   # e.g. llama32-1b__bf16__l40s__tp1__b8__i32__o128__mixed__greedy__bi-eager
research data label <run id> ov.gate pass|fail|unsupported --by vllm-epoch-run --off-vocab
research data label <run id> ov.note "<named cause>"       --by vllm-epoch-run --off-vocab   # required for fail and unsupported
research data labels-sync --push-only
~~~

- **`ov.gate`** is exactly `pass`, `fail` or `unsupported`. **Not `finding:<cause>`**: the renderer drops that. The cause goes in `ov.note`, named, e.g. "gemvx M=1 (K,N) not in table", "commit host peak > limit", or a first differing unit and family.
- **`pass`** means 460/460 units replayed bit-exact. Fewer than 460 isn't a pass; the renderer shows it as "short replay".
- **`--off-vocab`:** the `ov.*` keys aren't in main's label vocabulary yet, so the CLI refuses them without it.
- **Several cells in one run** (e.g. a sweep job): add `--ref <row slug>` to each label. The renderer keeps one row per (target, ref).
- **Unsupported cells:** label them **now, before running**, from the registry or target refusal: FP8 on targets without the step, samplers without a Definition, M = 1 bias shapes outside the gemvx table, and so on. Put them on one campaign attempt that records the refusals, one `--ref <row slug>` each.
  - I did this for the six TP2/TP4 rows at 06:09Z, on `r20260930-060847-fff1`. Don't duplicate them. When the TP2 lane's proving run passes, it labels its own attempt, and the later label wins.
- **The two "not run" rows:** re-run them (they were SIGTERMed after precheck) or label them with the cause.

**vllm-config-run-tp2:** label your proving run the same way, with `--by vllm-config-run-tp2` and your TP2 row slug.
