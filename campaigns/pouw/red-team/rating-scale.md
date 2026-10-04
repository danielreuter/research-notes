---
cursor:
  subagentId: "bc-8b6cc7d8-1509-561d-8902-d0dff0b643f5"
---

# Red-team rating scale for PoUW assumptions (red-team-pouw, v1)

30 Sep 2026. The independent PoUW red team (bc-8b6cc7d8). One scale, applied to every row of
[the assumptions table](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/assumptions.md). A rating is
about the row **at its stated parameters and device**; the same claim elsewhere is a different row.

| Rating | Meaning | What it takes |
|---|---|---|
| **A** | Standard. A property of a public primitive or model that the field has studied for years, at these parameters, with a known margin. | Public cryptanalysis; no credible attack near the parameters. |
| **B (effort)** | Survived a targeted attack. A concrete claim that withstood a red-team attack **at its stated parameters on its stated device**, with no break. | At least one attack that ran at the stated parameters and could have broken it. The effort is written in: GPU-hours on the deployment card, CPU-hours on a bit-exact model. |
| **C** | Conjecture with weak evidence. Consistent with everything tried, but the evidence is paper, a stand-in model, another device or parameters, or an under-explored attack surface. A real risk remains. | A named falsifier: the one measurement or attack that would move it to B or D. |
| **D** | Broken at the stated parameters. A concrete input family or program beats the claim. | A run id reproducing the break. |
| **—** | Not rateable. The row states no precise claim yet (reserved, no design), or is retired or historical. | The reason. |

**Modifiers.** In parentheses, where the evidence lives (for example "C (Hopper atom, sim)"). A trailing **↑** or **↓**
flags a concrete next attack or measurement that could move the rating up or down.

**Rules.**
- A rating never exceeds the weakest thing the row's own statement depends on.
- CPU simulation on a bit-exact model can support B only for a row whose claim is about that model's function (an open
  lemma, a census). A claim about a device's speed or semantics needs the device.
- The red team rates; it does not grade its own designs, and it doesn't rewrite a row's statement. A mis-stated row gets a
  rating plus a note on what the statement should say.
- Every rating links a note in `internal/pouw/red-team/` and, where it rests on a run, cites the run id. Verdicts are also
  recorded as store labels `--by red-team-pouw`.
