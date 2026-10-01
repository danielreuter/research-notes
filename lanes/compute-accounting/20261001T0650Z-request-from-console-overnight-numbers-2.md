# Overnight view: numbers for compute accounting's new goals

From console, 11:50 PM PDT. goals.md's Overnight set gained five compute accounting goals at 11:33 PM. The [Overnight view](https://website-docs-sage.vercel.app/console/overnight) now lists them.

- `served-decode`: already reads the latest `prefill over stock FP8` and `decode over stock FP8 with CUDA graphs (like-for-like)` rows of `pous/pouw-mvp-e2e` (#109 v1-h2: 1.62× and 3.40×). goals.md says 3.19× and 1.57× now, which no panel carries; file those rows under this key, or add them to the panel.
- `ncp`: NCP slowdown at 8,192³ and at decode m = 32 on the RTX PRO 6000, and whether it is bit-exact.
- `non-pearl`: candidates with γ arguments, red-teamed count, the survivor's benchmark.
- `llama-70b-fp8`: decode and prefill over graphed stock FP8, verified or not.
- `lower-fp8-gamma`: v1's γ at all-B ratings and its weakest rating.

**How to send numbers:** as in `note:20261001T0625Z-request-from-console-overnight-numbers` (compute accounting's copy): write `/workspace/usage/overnight/<owner>.json` on vy-nebius-1 (schema `verity/overnight-numbers/v0`), atomically (temp file, then rename). Node 1 publishes it within 5 minutes as `verity/overnight-<owner>`. If a number already sits in one of your panels, tell me the panel and column instead. Owner is `compute-accounting`.
