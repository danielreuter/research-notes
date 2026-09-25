import sys
from pathlib import Path

base = Path(sys.argv[1]) / "integrations/vllm/verity_vllm/pipeline/telemetry"
p = base / "admission.py"
s = p.read_text()
i = s.index("@dataclass(frozen=True, kw_only=True)\nclass PlanOptions:")
block = s[i:]
s = s[:i].rstrip("\n") + "\n"
s = s.replace("from verity_vllm.config import option\n\n", "")
p.write_text(s)
head = '''"""`verity-vllm telemetry-admission` -- the empirical admission planner's subcommands (`pipeline.telemetry.admission`).

    verity-vllm telemetry-admission plan --workload wl.json [--row ROW] [--out admission.json]     the row's advisory plan line
    verity-vllm telemetry-admission compare <attempt_dir>... [--md]                                predicted vs observed peaks
    verity-vllm telemetry-admission predict --model M --requests N ...                             reservation per stage
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from verity_vllm.config import option
from verity_vllm.pipeline.telemetry.admission import (GiB, RowConfig, cgroup_memory_max, compare, plan_row, predict,
                                                      render_compare_md, render_points_md, retain_exclude_families,
                                                      row_config_from_attempt, row_config_from_workload)


'''
(base / "admission_commands.py").write_text(head + block)
print("ok")
