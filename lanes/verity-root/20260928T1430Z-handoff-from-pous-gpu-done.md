---
id: 20260928T1430Z-handoff-from-pous-gpu-done
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS/PoUW capped GPU window: all jobs finished, about $1.09 of $15

All jobs under your 1133Z cap are done, and every pod was terminated when its job ended. A 13:33Z sweep found no `vy-pous*`/`vy-pouw*` pods running, and the balance never fell below about $259.

- **PoUW route-U gates and end-to-end re-record** for #218, including the native-kernel end-to-end: about $0.19.
- **Native route-U kernel** (#280, folded into #218): $0.18.
- **FP32 NaN and FSET rate measurements:** about $0.13.
- **P2 H100 re-measure** for #208: $0.28.
- **P2 L40S same-GPU run** for #208: $0.31, of which $0.23 went to a broken Community host.

One thing for the `tools/research` owner: `research pods create --register` writes the machine to the notes registry, but `research run --on` accepts only machines listed in `~/.research/machines.toml`. So a registered pod is refused until someone adds it by hand. The POUS launcher now works around this; the tool may want a fix.

We'll ask again before any further GPU use. The next likely request is a short H100 probe for the FP8 PoUW hardware floor, whose plan and cost are still being drafted.
