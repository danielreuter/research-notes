#!/usr/bin/env bash
# commit-gpu: the GPU committer's byte-identity tests (hash_gpu.frame_v3 vs verity.commitments / core vectors / hashlib /
# blake3; frame_gpu vs the host tree builders; commit_cost --impl gpu vs the references), then the neighbouring suites
# the change touches (hashchain, leaf, core commitments), on the synced tree /workspace/src.
source /workspace/hash-commit/scripts/lib.sh
tests /workspace/src backends/shared/hash_gpu/tests/test_frame_v3.py backends/direct/ligero/frame_gpu_test.py tests/test_commit_cost_benchmark.py
cp $HC/tests.log $HC/tests-cg.log
tests /workspace/src backends/shared/hash_gpu/tests backends/direct/ligero/hashchain_test.py backends/direct/ligero/leaf_test.py \
  backends/direct/ligero/leaf packages/verity/tests/commitments
cp $HC/tests.log $HC/tests-neighbours.log
