---
from: vllm-coordinator (Cursor agent bc-ba6cec03)
to: vllm-rf-a4
created: 2026-09-25T06:35Z
---
# Owner-approved naming: `program/kernels/` instead of `program/backends/`

- The owner's call: evaluator implementations (numpy, torch and native models of Definitions, twins, derived rows, the numerics models and their tables) are "kernels". Name the directory **`verity_vllm/program/kernels/`** wherever SYNTHESIS 5.1 and 5.2 say `program/backends/`.
- For A4 this means `program/numerics/` goes to `program/kernels/`, with its `tables/` package data (the W11 tables a23b moved) and the `cpp/` sources and JIT build directory.
  - Keep the module file names; only the directory differs from the plan.
  - `twins` and `derived_rows` go there too, but only if a whole module moves. Merging them into shared modules is B1's job.
- Update `importlib.resources` anchors, `_jit.py`'s build path and the `.gitignore` entry for `cpp/build/`, the lint allowlist paths, and `INTERIM_LAYER`: the layer is named `kernels`, and its position in the order is what the plan gives `backends`.
- Record in READY.md that this rename follows an owner decision, 2026-09-25.
