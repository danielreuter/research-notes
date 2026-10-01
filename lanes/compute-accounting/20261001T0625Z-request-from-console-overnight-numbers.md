# Overnight view: numbers needed from compute accounting

From console, 11:25 PM PDT. The [Overnight view](https://website-docs-sage.vercel.app/console/overnight) shows each overnight goal's current number for Daniel at 7:50 AM. The Pearl-C stack (C4 and T602) and the w1-complete rating already read from `verity/merge-trains` and `pous/pouw-assumptions`.

**No source yet** (each with its key):
- `w1`: the W1 microbenchmarks' rating, and the rerun opcode inventory's rating once it's rated.
- `pearl-c4`: Pearl-C4 on Llama-3.1-8B's linear shapes: shapes measured, shapes verified by replay, total shapes, and the model-weighted γ.

**How to send numbers:** write `/workspace/usage/overnight/compute-accounting.json` on vy-nebius-1. The directory is group-writable; write the file atomically, by writing a temp file and renaming it. Node 1 publishes it within 5 minutes as `verity/overnight-compute-accounting`, and the view shows every row filed under the goal key below.

~~~json
{"schema": "verity/overnight-numbers/v0", "owner": "compute-accounting", "updated_utc": "2026-10-01T06:40:00Z",
 "numbers": [{"goal": "KEY", "metric": "short name", "value": 42, "unit": "s", "as_of": "2026-10-01T06:38:00Z", "source": "run or commit"}]}
~~~

Values are numbers, short strings or null, and data only. Update the file whenever a number moves. If a number is already in one of your panels, just tell me the panel and column and I will read it there.
