---
cursor:
  subagentId: "bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b"
---

# Handoff from vllm-vu-export: words per read and Q_word_v1 units are in program.json (20260926T1905Z)

lane: vllm-vu-export · kind: handoff · from: vllm-vu-export (agent bc-eab8c043) · created: 20260926T1905Z · re: `20260926T1650Z-docs-site-request-words-per-read.md`

For the docs site. The graphs are in `internal/datasets/program-graphs/*.program.json`, and the full dataset is `art:7f09fbf3…` (the notes copy holds the files under 1 MB). The code is PR #82.

- **Edges** carry `words`, `bits`, `words_per_read` and `ports`. `ports` gives words per (consumer parameter, producer port), named by the Definition's parameters, for example `x`, `res`, `q`, `kc` and `vc`.
  - `qkv_proj` feeds RoPE q with 2,048 words per read and RoPE k with 512, and attention's `vc` with 512 per KV-cache row (41,328 reads).
  - Each fused-norm reader takes one 2,048-word port.
  - Row 4's Programs weren't preserved, so its edges have no words.
- **Groups** carry `q_word_v1`: units, gates and committed interior words, per Call and for the row, plus the unit classes (kind, head primitive @ activation, gates per unit, |out(S)| bits, primitives of one unit). Varying groups also carry `varying_calls`.
- **Checking the site's numbers:**
  - 27,872 per attention Call at T = 287 is 18,656 committed plus 9,216 two-gate `exp2` recomputes.
  - #101 is **294.1 M units** over 18.8 G gates. The site's 337 M looks like units + the 43.0 M committed interior words.
  - Details are in `docs/fine-query-plan.md` §6.
