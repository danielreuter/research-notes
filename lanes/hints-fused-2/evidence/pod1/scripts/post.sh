#!/bin/bash
# after the A/B: profiles of the fused floor, gates (reference comparison on every honest sub-batch), pytest subset
cd /workspace
while [ ! -f /workspace/logs/ab_done ]; do sleep 10; done
X=/workspace/src
B="/workspace/venv312/bin/python -m backends.direct.ligero.run"
P="/workspace/venv312/bin/python prof_rep.py"
C="--zk --mode interactive --reps 2 --device cuda --instances-cache /workspace/instances-cache --total-vus 4096"
G="--vus 2048 --batch 16384 --device cuda --instances-cache /workspace/instances-cache"
mkdir -p /workspace/prof
LIGERO_REFERENCE_HINTS=0 /workspace/run.sh $X prof_fu_v3x4_p2_16k $P /workspace/prof/fu_v3x4_p2_16k --relation fp8-ada-v3x4 bench-vu --out /workspace/results/prof_fu_v3x4_p2_16k.json $C --batch 16384 --pipeline 2
LIGERO_REFERENCE_HINTS=0 /workspace/run.sh $X prof_fu_v3x4_p4_16k $P /workspace/prof/fu_v3x4_p4_16k --relation fp8-ada-v3x4 bench-vu --out /workspace/results/prof_fu_v3x4_p4_16k.json $C --batch 16384 --pipeline 4
LIGERO_REFERENCE_HINTS=0 LIGERO_FUSED_HINTS=0 /workspace/run.sh $X prof_to_v3_p4_16k $P /workspace/prof/to_v3_p4_16k --relation fp8-ada-v3 bench-vu --out /workspace/results/prof_to_v3_p4_16k.json $C --batch 16384 --pipeline 4
echo "prof done $(date -u +%H:%M:%S)" >> /workspace/logs/chain.log
/workspace/run.sh $X gatezk_v3x4 $B --relation fp8-ada-v3x4 gate-vu $G --zk --out /workspace/results/gatezk_v3x4.json &
/workspace/run.sh $X gatezk_v3 $B --relation fp8-ada-v3 gate-vu $G --zk --out /workspace/results/gatezk_v3.json &
wait
echo "gates 1 done $(date -u +%H:%M:%S)" >> /workspace/logs/chain.log
/workspace/run.sh $X gate_v3x4 $B --relation fp8-ada-v3x4 gate-vu $G --out /workspace/results/gate_v3x4.json &
/workspace/run.sh $X gatezk_v2x4 $B --relation fp8-ada-v2x4 gate-vu $G --zk --out /workspace/results/gatezk_v2x4.json &
OMP_NUM_THREADS=4 /workspace/run.sh $X pytest_subset /workspace/venv312/bin/python -m pytest -q -rfE -p no:cacheprovider \
  backends/direct/ligero/pipeline_race_test.py backends/direct/ligero/pubsel/relation_test.py backends/direct/ligero/privsel/relation_test.py \
  backends/direct/ligero/relations_test.py backends/direct/ligero/chain_test.py backends/direct/ligero/bench_vu_test.py \
  backends/direct/ligero/fold_test.py -k "not test_folded_unit_is_exactly_four_chained_base_steps and not test_folded_chain_is_the_base_claim_cpu" &
wait
echo "gates 2 + pytest done $(date -u +%H:%M:%S)" >> /workspace/logs/chain.log
echo POST_DONE > /workspace/logs/post_done
