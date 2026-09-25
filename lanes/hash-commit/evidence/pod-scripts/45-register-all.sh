#!/usr/bin/env bash
# hash-commit (pod): register every 4090 fp8-ada l=8192 p4 run measured before the 05:46Z PAUSE.  One full run-files tree
# per committer (proof dump included), the other rounds slim (no .proof files; their sha256 in proofs.sha256).
S=/workspace/hash-commit/scripts
P="vy-hash-commit hzku0ng1zou8ql (RTX 4090, EU-RO-1, Ryzen 9 7950X)"
F=fp8ada-l8192-p4
POD_DESC="$P" bash $S/40-register.sh \
  "base-$F-r4=4090 fp8-ada BEFORE 6e1cc576 r4" "tip-$F-r1=4090 fp8-ada step1 5d14dafa r1" \
  "k515e-$F-r4=4090 fp8-ada step2 515ed32a r4" "k0b40-$F-r7=4090 fp8-ada step3 0b40ae8a r7" \
  "tip-$F-r7=4090 fp8-ada step4 b862be30 r7"
SLIM=1 POD_DESC="$P" bash $S/40-register.sh \
  "base-$F-r1=4090 fp8-ada BEFORE 6e1cc576 r1" "base-$F-r2=4090 fp8-ada BEFORE 6e1cc576 r2" "base-$F-r3=4090 fp8-ada BEFORE 6e1cc576 r3" \
  "k5d14-$F-r2=4090 fp8-ada step1 5d14dafa r2" "k5d14-$F-r3=4090 fp8-ada step1 5d14dafa r3" "k5d14-$F-r4=4090 fp8-ada step1 5d14dafa r4" \
  "k515e-$F-r2=4090 fp8-ada step2 515ed32a r2" "k515e-$F-r3=4090 fp8-ada step2 515ed32a r3" \
  "tip-$F-r2=4090 fp8-ada step3 0b40ae8a r2" "tip-$F-r3=4090 fp8-ada step3 0b40ae8a r3" "tip-$F-r4=4090 fp8-ada step3 0b40ae8a r4" \
  "k0b40-$F-r5=4090 fp8-ada step3 0b40ae8a r5" "k0b40-$F-r6=4090 fp8-ada step3 0b40ae8a r6" \
  "tip-$F-r5=4090 fp8-ada step4 b862be30 r5" "tip-$F-r6=4090 fp8-ada step4 b862be30 r6"
cp /workspace/hash-commit/runs.txt /workspace/hash-commit/registered.txt /workspace/hash-commit/tests.log $RESEARCH_RUN_DIR/ 2>/dev/null
