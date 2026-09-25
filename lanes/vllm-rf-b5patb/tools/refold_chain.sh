#!/bin/bash
# Re-fold row 101 at head and at base, then compare both with the fixture and with each other.
# The record was folded under `gen_llama_llama32_1b`; since P6 the same role's profile is `derived_LLAMA32_1B`
# (`profile_module_for_case("LLAMA32_1B")`, as run_config and stoch_negatives.sh pick it).
#   usage: refold_chain.sh HEAD_TREE BASE_TREE
H=$1; B=$2
R=/workspace/b5pat/rows/101-records
P=derived_LLAMA32_1B
bash /workspace/b5patb/refold.sh "$H" r101_head "$R" "$P"
bash /workspace/b5patb/refold.sh "$B" r101_base "$R" "$P"
/workspace/venv312/bin/python /workspace/b5patb/refold_compare.py "$R" /workspace/b5patb/refold/r101_head /workspace/b5patb/refold/r101_base \
  | tee /workspace/b5patb/refold/compare.txt
