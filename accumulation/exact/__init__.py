"""Exact ``I*(P; F, G, X)`` for micro circuits (SPEC §4): the reference the bounds are tested against.

* :mod:`accumulation.exact.solve` -- :func:`flatten`, the literal SPEC §1 checker (:func:`is_legal`,
  :func:`partition_cost`) and the brute-force / MILP solvers behind :func:`exact_min_input`.
* :mod:`accumulation.exact.micro` -- tiny Verity programs built from the real vocabulary.
"""

from accumulation.exact.solve import (  # noqa: F401
                                      BRUTE_MAX_GATES,
                                      ExactResult,
                                      FlatCircuit,
                                      Infeasible,
                                      exact_min_input,
                                      f_violations,
                                      flatten,
                                      is_legal,
                                      make_flat,
                                      partition_cost,
                                      ru_imports,
                                      ru_work,
                                      up_set,
                                      up_work,
)
