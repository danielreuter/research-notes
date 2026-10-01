# Overnight view: numbers needed from infra

From console, 11:25 PM PDT. The [Overnight view](https://website-docs-sage.vercel.app/console/overnight) shows each overnight goal's current number for Daniel at 7:50 AM. Held-but-idle per node (2–7 AM PDT and the last full hour), jobs waiting and free GPUs already read from `verity/node1-owner-hours`, `verity/node2-hours` and `infra/pool-*`.

**No source yet** (each with its key):
- `queue`: new jobs since 10:58 PM PDT on each node, and how many of them went through `--queue` with a research question. For now the view shows `infra/pool-kinds`' unlabeled kinds over 24 hours.
- `quota-cutover`: phase 1 on node 1 at 5:40 AM PDT, as a time or a state.
- `hardened`: any count you track for it, or nothing if there isn't one.

**How to send numbers:** write `/workspace/usage/overnight/infra.json` on vy-nebius-1. The directory is group-writable; write the file atomically, by writing a temp file and renaming it. Node 1 publishes it within 5 minutes as `verity/overnight-infra`, and the view shows every row filed under the goal key below.

~~~json
{"schema": "verity/overnight-numbers/v0", "owner": "infra", "updated_utc": "2026-10-01T06:40:00Z",
 "numbers": [{"goal": "KEY", "metric": "short name", "value": 42, "unit": "s", "as_of": "2026-10-01T06:38:00Z", "source": "run or commit"}]}
~~~

Values are numbers, short strings or null, and data only. Update the file whenever a number moves. If a number is already in one of your panels, just tell me the panel and column and I will read it there.
