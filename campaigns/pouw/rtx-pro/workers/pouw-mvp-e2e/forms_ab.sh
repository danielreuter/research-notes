#!/usr/bin/env bash
# served_profile.sh under GPU 1's default forms and under PEARLC_A_FORMS=s,one, alternating (ABAB) in one run, each in a
# lease of its own, into $RESEARCH_RUN_DIR/<forms>-<round>.  served_ab.sh's K=V lists split on commas, which the forms carry.
set -uo pipefail
for r in $(seq 1 "${ROUNDS:-2}"); do
  for forms in default s-one; do
    ( if [ "$forms" = s-one ]; then export PEARLC_A_FORMS=s,one; else unset PEARLC_A_FORMS; fi
      OUT=$RESEARCH_RUN_DIR/$forms-$r bash benchmarks/pouw/pearl_c_vllm/served_profile.sh ) || echo "forms_ab: $forms-$r failed ($?)"
  done
done
