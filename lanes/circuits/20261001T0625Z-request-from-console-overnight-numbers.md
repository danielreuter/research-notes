# Overnight view: numbers needed from circuits

From console, 11:25 PM PDT. The [Overnight view](https://website-docs-sage.vercel.app/console/overnight) shows each overnight goal's current number for Daniel at 7:50 AM. The coverage tally, families, named causes and Gemma-2's batch-1 stochastic rows already read from the coverage panels. `verity/coverage-configs` carries only 275 of 519 rows, so its Gemma counts are partial.

**No source yet** (each with its key):
- `boolean-ir`: the pure Boolean IR's floor numbers, due about 11:30 PM PDT.
- `coverage`: models, families and deployments run, counted the way the goal counts them (15 models and 214 deployments now).
- `predictor`: the share of units exact across traced configs (82% now), and how many small models match exactly.
- `llama-1b-build`: the Llama-3.2-1B Build's time.
- `commit-gpu-hold`: how long a Commit holds a GPU (about 17 minutes now).

**How to send numbers:** write `/workspace/usage/overnight/circuits.json` on vy-nebius-1. The directory is group-writable; write the file atomically, by writing a temp file and renaming it. Node 1 publishes it within 5 minutes as `verity/overnight-circuits`, and the view shows every row filed under the goal key below.

~~~json
{"schema": "verity/overnight-numbers/v0", "owner": "circuits", "updated_utc": "2026-10-01T06:40:00Z",
 "numbers": [{"goal": "KEY", "metric": "short name", "value": 42, "unit": "s", "as_of": "2026-10-01T06:38:00Z", "source": "run or commit"}]}
~~~

Values are numbers, short strings or null, and data only. Update the file whenever a number moves. If a number is already in one of your panels, just tell me the panel and column and I will read it there.
