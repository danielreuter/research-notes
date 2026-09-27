"""Red team for the certified bounds of ``accumulation/`` (SPEC §2 lower bound, §3 upper bound) against the
exact ``I*(P; F, G, X)`` of SPEC §4.

* :mod:`accumulation.redteam.circuits` -- a small declarative spec for micro Verity programs built from the
  block vocabulary (:mod:`accumulation.ir.blocks`) with ``CH=1``, so the exact solver can enumerate them.
* :mod:`accumulation.redteam.harness` -- one instance = ``(program, F, G, X)``; runs ``extract`` ->
  ``lower_bound`` / ``upper_bound`` (+ ``check_plan``) / ``exact_min_input``, materialises literal plans into
  gate partitions and re-checks them with ``is_legal`` / ``partition_cost``; records the optimal partition.
* :mod:`accumulation.redteam.torture` -- hand-derived cases (each docstring derives ``I*``), including dense
  inference / training micro circuits and the ``G`` forced-split case; automatic binding-``G`` points.
* :mod:`accumulation.redteam.fuzz` -- seeded random micro-circuits on random ``(F, X, G)`` grids, shrinking,
  JSONL logs.
* :mod:`accumulation.redteam.validation` -- the SPEC §6 validation table (``results/validation.md`` /
  ``.json``) from the torture suite and fuzz logs, with the fuzz aggregate and the "attacks" (optimal
  partitions) on instances where ``L/I* < 0.5``.

Nothing here edits ``bounds/``, ``graph/``, ``ir/``: defects there are *reported*, not fixed.  ``exact/`` is the
reference the red team maintains (``G`` support in the solvers lives there).
"""
