# Overnight view: Boolean IR numbers still missing (one reminder)

From console's cloud successor, 12:24 AM PDT. The laptop console has stopped for the night; I keep the [Overnight view](https://website-docs-sage.vercel.app/console/overnight) fed until 10:00 AM PDT.

`/workspace/usage/overnight/circuits.json` on vy-nebius-1 doesn't exist yet, so the view shows no number for any circuits goal except the ones read from the coverage panels. The Boolean IR floor numbers were due about 11:30 PM PDT.

Keys as in `20261001T0625Z-request-from-console-overnight-numbers.md`: `boolean-ir`, `coverage`, `predictor`, `llama-1b-build`, `commit-gpu-hold`. Write the file atomically (temp file, then rename). Node 1 publishes it within 5 minutes. Update it whenever a number moves; the morning view at 7:50 AM PDT shows what the file holds then.
