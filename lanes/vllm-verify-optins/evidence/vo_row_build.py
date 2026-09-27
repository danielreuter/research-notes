"""vo_row_build.py TARGET_JSON ROW ROLE REPO REV [row flags...]: `verity-vllm row run ... --stages build` on a host without a GPU, with the
row's declared target replaced by TARGET_JSON (the record's device target, plus an opt-in knob or none).  Everything else is the row's
own Build stage (`row_stages.SingleRow.build`: the step and every request shape under their launch contexts, the build summary, GP-01's
workload Program, the build-target family check, the required-value manifest).  Two things are patched: `row_records.declared_target`
(the row's `--target`) and `SingleRow.precheck_target` (it reads the device, which this host does not have; the Build-side family check
`target-family --no-device --build-summary` still runs).  The workload file is not edited."""
import os
import sys

from verity_vllm.pipeline import cli, row as ROW, row_records as R, row_stages as RS

target, args = sys.argv[1], sys.argv[2:]
R.declared_target = lambda wl: target
RS.SingleRow.precheck_target = lambda self: self.log(f"precheck-target skipped (no GPU on this host); declared target {target}")
sys.exit(ROW.main(cli.parse("row", ["run", *args, "--stages", "build"], os.environ)))
