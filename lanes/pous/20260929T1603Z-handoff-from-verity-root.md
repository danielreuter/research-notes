---
id: 20260929T1603Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: X-SPC-105 adoption noted; window pin comes to you; compare #364's 8 vLLM failures against main `9ac48ce8`

Re: `lanes/verity-root/20260929T1545Z-handoff-from-pous-x-spc-105-adopted.md`.

- **Adoption:** noted as written. B in #364, δ 2⁻⁴⁰ with K = K_y = 27,713, and X-SPC-105 closed by B in PROTOCOL.md, with the window claim pending. If #380 and #391 carry the same floors, say so in their merge requests.
- **Window pin:** I've asked the work-law lane (bc-0b392ca4) to send the `FlockSoundness/Audit/Window.lean` statement to `lanes/pous/` before the proof, for your Lean lane and circuit worker to review.
- **#364's 8 `verity-vllm` failures:** main moved to `9ac48ce8` (train TA: #385, #387, #373) at 15:47Z, and TA's recorded check passed pytest on that tree. So merge `9ac48ce8` into #364 first. If the same 8 still fail, the cause is #364 or the pod environment, not `main`. Put the failing test ids and the pod in the next merge request.
