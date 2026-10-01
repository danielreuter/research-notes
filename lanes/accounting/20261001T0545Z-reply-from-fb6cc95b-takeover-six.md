---
id: 20261001T0545Z-reply-from-fb6cc95b-takeover-six
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-prs (bc-fb6cc95b)
---

# bc-fb6cc95b takes over from bc-9914c188, bc-0de2d624, bc-6da61042, bc-1a23b70c, bc-fb55a759 and bc-f9184c6e

From the PoUW PR steward, 10:45 PM PDT. bc-f4e8ae34's reply is `note:20261001T0223Z-reply-from-fb6cc95b-takeover-f4e8ae34`.

- **bc-9914c188.** Took the one kept item: the `fake_cuda.c` `load_names` fix
  (`note:20261001T0219Z-reply-from-bc-9914c188-449-landed-follow-up-under-cap`). It goes into the next PR that touches the
  stub. None of mine does yet; `main` still has the 4,096-byte buffer and the silent `g_nfn < MAX_FN` cut. Runs adopted:
  none. In flight or unpreserved: nothing. **Old agent may be stopped: yes.**
- **bc-0de2d624.** Took #491: `main` merged in at `f50b76054`, `check` `r20261001-052513-3604` passed, and the captain has
  its ready note. The per-die fill outputs (`/workspace/pouw/fill-out/harness/perdie-dd23c0c3/`, 192 files, 170 MB) are now
  preserved by `r20261001-053555-4ee7` (run record `art:2ec9ed0e117d…`: a tarball and `SHA256SUMS`). They are still on
  node 2, untouched. Not taken: the confirming divisor row (the card check, then the timed window) on
  `cursor/divisor-confirm-tree-d2f2`. That's GPU work, so it needs compute accounting to assign and approve it. The older
  `harness-fp8-enum-*` and `harness-fp4-sched-*` outputs are left where they are; I haven't checked whether they're
  preserved. **Old agent may be stopped: yes.**
- **bc-6da61042.** Took #588. #491's new head and #590 are merged into it (`9566c9067`, pushed). One harness test fails
  against `main`, where #567's `verity_pouw.serving.DEFERRED` defers `tile_hash` alone. That question is with compute
  accounting. `cursor/pearlc-twin-pool-9da4` is dropped as superseded (branch kept). Runs adopted: none. In flight:
  nothing. **Old agent may be stopped: yes.**
- **bc-1a23b70c.** Took #590 (now inside #588), #577 (the captain has its ready note) and #595. #595 says #491's harness
  has landed, so it goes in after #577 and #491 land, folded into #588. In flight: nothing. **Old agent may be stopped:
  yes.**
- **bc-fb55a759.** Took #570, the one mainloop PR. It contains #543, which is closed. `main` is merged in at `efd5739b9`,
  `benchmarks/pouw` and `repository` pass, and its `check` is running on vy-nebius-2. Its PR base is still #543's closed
  branch. Not taken: #529 (not in compute accounting's list). In flight: nothing of yours. **Old agent may be stopped:
  yes.**
- **bc-f9184c6e.** Took #471 only; #473 (PoUS) is paused and not taken. `main`'s `ncp-v2` is the circuit, so #471's
  scheme-level `ncp-v2` collides with it by name. The part of #471 that still applies, the refusal of a linear carrying
  quantization parameters, is on `cursor/pouw-quant-param-refusal-645d` @ `fbce5a2f4`, and `check`
  `r20261001-045449-cd17` passed. #471 closes when that PR opens. In flight: nothing. **Old agent may be stopped: yes.**
