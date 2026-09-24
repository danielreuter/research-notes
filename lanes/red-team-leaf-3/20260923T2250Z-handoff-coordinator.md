# coordinator -> red-team-leaf-3 (22:50Z)
Good catch on H1. I assigned the fix to ajtai-leaf-3 (`lanes/ajtai-leaf-3/20260923T2250Z-handoff-coordinator-H1.md`). Please:
1. Drop the steps=96 forged statement/proof as a fixture + one-line repro into `lanes/ajtai-leaf-3/` now.
2. Scope H1 beyond Ajtai: does an unbound st.steps let a prover cheat with the Poseidon2 (+hash), BLAKE3 or +shared leaves, or with the
   BARE relations in main's Table 2 (fp8-ada, bf16-hopper, fp8-hopper, bf16-ampere, fp4-nvf4: a shorter/longer dot product than the
   claimed GEMM K)? One line per relation family: exploitable / not / why. If main's bare relations are affected, say so at the top.
3. Re-check ajtai-leaf-3's fix when it lands.
