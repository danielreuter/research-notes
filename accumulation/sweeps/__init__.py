"""Characterization, sweeps, plots and reports for the bounded-accumulation study.

* :mod:`accumulation.sweeps.characterize` -- Goal-1 table (state floor, ADW, ratios) and the MAC audit
* :mod:`accumulation.sweeps.run`          -- bound sweeps over ``(algorithm, model, workload) x F x X`` (JSONL)
* :mod:`accumulation.sweeps.plots`        -- matplotlib figures from the sweep JSONL
* :mod:`accumulation.sweeps.report`       -- JSONL/JSON -> markdown tables in ``results/RESULTS.md``

Everything is driven from the repo root with ``PYTHONPATH=.``::

    .venv/bin/python -m accumulation.sweeps.characterize --audit
    .venv/bin/python -m accumulation.sweeps.run --preset smoke
    .venv/bin/python -m accumulation.sweeps.plots
    .venv/bin/python -m accumulation.sweeps.report
"""
