#!/bin/bash
# Re-fold row 101 at head and at base, then compare both with the fixture and with each other.
#   usage: refold_chain.sh HEAD_TREE BASE_TREE
H=$1; B=$2
R=/workspace/b5pat/rows/101-records
P=gen_llama_llama32_1b
bash /workspace/b5pat/refold.sh "$H" r101_head "$R" "$P"
bash /workspace/b5pat/refold.sh "$B" r101_base "$R" "$P"
/workspace/venv312/bin/python /workspace/b5pat/refold_compare.py "$R" /workspace/b5pat/refold/r101_head /workspace/b5pat/refold/r101_base \
  | tee /workspace/b5pat/refold/compare.txt
