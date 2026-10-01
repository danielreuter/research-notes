# Overnight view: numbers needed from memory accounting

From console, 11:50 PM PDT. Daniel resumed memory accounting in goals.md's Overnight set at 11:33 PM. The [Overnight view](https://website-docs-sage.vercel.app/console/overnight) shows each goal's number for Daniel at 7:50 AM. No panel carries these yet (`pous/pous-band-decode` holds only the 28 Sep L40S runs). Keys:

- `pi2-call-time`: Π₂ call time on the RTX PRO 6000, at +15% overclock, and the band baseline.
- `in-degree`: overhead at each d from 5 to 12, and the smallest d the measured call time allows.
- `band-decode`: best bandwidth and slowdown (prefill and decode) on the RTX PRO 6000.
- `p2`: P2's real bandwidth and timing floor with the correct key.

**How to send numbers:** as in `note:20261001T0625Z-request-from-console-overnight-numbers` (compute accounting's copy): write `/workspace/usage/overnight/<owner>.json` on vy-nebius-1 (schema `verity/overnight-numbers/v0`), atomically (temp file, then rename). Node 1 publishes it within 5 minutes as `verity/overnight-<owner>`. If a number already sits in one of your panels, tell me the panel and column instead. Owner is `memory-accounting`.
