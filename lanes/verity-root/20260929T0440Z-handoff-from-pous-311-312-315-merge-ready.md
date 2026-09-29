---
id: 20260929T0440Z-handoff-from-pous-311-312-315-merge-ready
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #311, then #312, then #315 are merge-ready, in that order

From bc-13eada34, posted by the POUS coordinator because the worker's push got a 403.

1. **#311**, head `1a4bd3f0`: recorded check `r20260929-012847-abf3`, passed (bc-23d60f13).
2. **#312**, head `6c7ffb6d`: recorded check `r20260929-032358-9010`, passed.
   - Every step passed, including `lean-agreement`, which ran in full.
3. **#315**, head `109e12f6`: recorded check `r20260929-041059-e3db`, passed.
   - `lean-agreement` passed, reused from #312's run on the same pod.
   - **The resident weight copy is removed**, per Daniel's 00:15Z ruling. Per-forward is PoUW's only weight-operand
     path. The `weight_operands` setting and `keeps_weight_copy` are gone.
   - bc-13eada34 pushed it while bc-dd22acf8's GitHub token fails. bc-dd22acf8 resets to this head when its
     credentials recover.

**Both #312 and #315 carry the same one-line fix:** `backends/flock/pyproject.toml` adds `"protocols/one_stage"` to
`verity-flock`'s test inputs. Being identical, the two merge cleanly. If `main` lands that line first, it's the same
line.

**Checks:**
- Both were recorded against `main` `b4fd93e9`.
- They ran on the CPU pod `vy-pous-checks` (`tgkbxypwhjdx22`), because `lean-agreement` needs 24 GB.
- The pod was terminated at 04:36:26Z, and its billed spend was about $1.13, inside the coordinator's $3 guard.
- No `vy-pous*` or `vy-pouw*` pod is live now, apart from Round 12, which is approved separately.
