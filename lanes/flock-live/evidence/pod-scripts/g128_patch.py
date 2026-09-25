#!/usr/bin/env python3
"""flock-128: patch flock-cuda-ffi/tests/gpu_roundtrip.rs for the 2^-128 profile runs.

- GPU_PROFILE=fast|fast100 selects the LigeritoProfile (was Default = Fast); every schedule the FFI gets
  (queries, query PoW bits, claim/consistency grinding, PIOP grinding sites) is derived from it as before.
- the transcript domain is per repetition: flock-128/<profile>x<reps>/rep<i> (prover FFI and Rust verifier).
- roundtrip<N, TAMPER>: warm-up, then GPU_RUNS timed runs of GPU_REPS sequential proofs; verify every rep;
  prints G128RESULT json. With GPU_NEG=1: replay rep0 as rep1, flip yr[0], flip a zerocheck round, verify rep0
  under the other Ligerito profile -- each must be rejected (G128NEG lines). EXPECT_REJECT=1 (witness tamper):
  the rep0 proof must be rejected.
Leaves the strings flock-bench's 22-gpu-unit.sh asserts on intact, so run this BEFORE 22 generates gpu_unit.rs.
"""
import pathlib

p = pathlib.Path("crates/flock-cuda-ffi/tests/gpu_roundtrip.rs")
s = p.read_text()
if "G128RESULT" in s:
    print("gpu_roundtrip.rs already patched"); raise SystemExit(0)

old = "        profile: Default::default(),\n        num_lanes: None,\n        merkle_hash: CUDA_HASH,"
assert s.count(old) == 1
s = s.replace(old, "        profile: g128_profile(),\n        num_lanes: None,\n        merkle_hash: CUDA_HASH,")

old = "    let dump_c = dump_z.map(|p| CString::new(p).unwrap());\n"
assert s.count(old) == 1
s = s.replace(old, old + "    let dom = g128_domain();\n")
old = "        domain: DOMAIN.as_ptr(),\n        domain_len: DOMAIN.len() as u32,"
assert s.count(old) == 1
s = s.replace(old, "        domain: dom.as_ptr(),\n        domain_len: dom.len() as u32,")

old = "static GPU_TEST_LOCK: Mutex<()> = Mutex::new(());\n"
assert s.count(old) == 1
s = s.replace(old, old + '''static G128_DOMAIN: Mutex<Vec<u8>> = Mutex::new(Vec::new());
fn g128_env(k: &str, d: &str) -> String {
    std::env::var(k).unwrap_or_else(|_| d.to_string())
}
fn g128_profile() -> flock_core::pcs::ligerito::LigeritoProfile {
    use flock_core::pcs::ligerito::LigeritoProfile as L;
    match g128_env("GPU_PROFILE", "fast").as_str() {
        "fast" => L::Fast,
        "fast100" => L::Fast100,
        o => panic!("GPU_PROFILE {o}"),
    }
}
fn g128_other(l: flock_core::pcs::ligerito::LigeritoProfile) -> flock_core::pcs::ligerito::LigeritoProfile {
    use flock_core::pcs::ligerito::LigeritoProfile as L;
    if l == L::Fast { L::Fast100 } else { L::Fast }
}
fn g128_reps() -> usize {
    g128_env("GPU_REPS", "1").parse().unwrap()
}
fn g128_rep_domain(rep: usize) -> Vec<u8> {
    format!("flock-128/{}x{}/rep{rep}", g128_env("GPU_PROFILE", "fast"), g128_reps()).into_bytes()
}
fn g128_set_rep(rep: usize) {
    *G128_DOMAIN.lock().unwrap() = g128_rep_domain(rep);
}
fn g128_domain() -> Vec<u8> {
    let d = G128_DOMAIN.lock().unwrap().clone();
    if d.is_empty() { DOMAIN.to_vec() } else { d }
}
''')

a = s.index("/// Full roundtrip: GPU prove, Rust verify;")
b = s.index("#[test]\n#[ignore] // needs an sm_120 GPU; run explicitly with --ignored\nfn gpu_roundtrip_m22")
s = s[:a] + '''/// flock-128 roundtrip: GPU_REPS sequential proofs (one transcript domain each), GPU_RUNS timed runs.
fn roundtrip<const N_BLOCKS_LOG: usize, const TAMPER: bool>() {
    let _test_guard = GPU_TEST_LOCK.lock().expect("GPU test lock poisoned");
    let reps = g128_reps();
    let runs: usize = g128_env("GPU_RUNS", "3").parse().unwrap();
    let expect_reject = g128_env("EXPECT_REJECT", "0") == "1";
    g128_set_rep(0);
    let warmup_secs = gpu_prove(N_BLOCKS_LOG, None).prove_secs;
    let mut run_secs: Vec<f64> = Vec::new();
    let mut last: Vec<GpuArtifacts> = Vec::new();
    for _ in 0..runs {
        last.clear();
        for rep in 0..reps {
            g128_set_rep(rep);
            last.push(gpu_prove(N_BLOCKS_LOG, None));
        }
        run_secs.push(last.iter().map(|g| g.prove_secs).sum());
    }
    let r1cs = &last[0].r1cs;
    let m = r1cs.m;
    let lc_circuit = SparseMatrixCircuit::new(&r1cs.a_0, &r1cs.b_0).with_const_pin(r1cs.const_pin);
    let check = |g: &GpuArtifacts, proof: &R1csProofLigerito, dom: &[u8], pp: &PcsParams, cm: &Commitment| {
        let mut ch = FsChallenger::with_hash(dom, CUDA_HASH);
        verify_ligerito(&g.r1cs, cm, proof, &lc_circuit, pp, &mut ch)
    };
    let t1 = Instant::now();
    let mut ok = true;
    for (rep, g) in last.iter().enumerate() {
        let r = check(g, &g.proof, &g128_rep_domain(rep), &g.pcs_params, &g.commitment);
        if expect_reject {
            assert!(r.is_err(), "witness-tampered GPU proof accepted at m={m}");
            println!("G128NEG {{\\"m\\":{m},\\"negative\\":\\"witness_tampered_rep{rep}\\",\\"rejected\\":true,\\"why\\":\\"{:?}\\"}}", r.err().unwrap());
            ok = false;
        } else {
            r.unwrap_or_else(|e| panic!("Rust verifier rejected GPU rep{rep} proof at m={m}: {e:?}"));
        }
    }
    let verify_secs = t1.elapsed().as_secs_f64();
    let mut sorted = run_secs.clone();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let bytes: Vec<usize> = last.iter().map(|g| bincode::serialize(&g.proof).unwrap().len() + bincode::serialize(&g.commitment).unwrap().len()).collect();
    println!(
        "G128RESULT {{\\"m\\":{m},\\"nbl\\":{},\\"profile\\":\\"{}\\",\\"reps\\":{reps},\\"netlist\\":\\"{}\\",\\"warmup_s\\":{warmup_secs:.4},\\"prove_median_s\\":{:.4},\\"prove_min_s\\":{:.4},\\"prove_runs_s\\":{:?},\\"verify_s\\":{verify_secs:.4},\\"proof_bytes\\":{},\\"proof_bytes_per_rep\\":{:?},\\"all_verified\\":{ok}}}",
        N_BLOCKS_LOG, g128_env("GPU_PROFILE", "fast"), g128_env("VU_NAME", "blake3"),
        sorted[sorted.len() / 2], sorted[0], run_secs, bytes.iter().sum::<usize>(), bytes
    );
    if expect_reject || g128_env("GPU_NEG", "0") != "1" {
        return;
    }
    let neg = |name: &str, r: Result<_, _>| {
        let e = match r { Ok(_) => panic!("negative {name} ACCEPTED at m={m}"), Err(e) => e };
        println!("G128NEG {{\\"m\\":{m},\\"profile\\":\\"{}\\",\\"negative\\":\\"{name}\\",\\"rejected\\":true,\\"why\\":\\"{e:?}\\"}}", g128_env("GPU_PROFILE", "fast"));
    };
    let g0 = &last[0];
    if reps >= 2 {
        neg("rep0_proof_replayed_as_rep1", check(g0, &g0.proof, &g128_rep_domain(1), &g0.pcs_params, &g0.commitment));
    }
    let mut bad = g0.proof.clone();
    bad.pcs_open.ligerito.final_proof.yr[0].lo ^= 1;
    neg("yr0_bit_flipped", check(g0, &bad, &g128_rep_domain(0), &g0.pcs_params, &g0.commitment));
    let mut bad = g0.proof.clone();
    bad.zerocheck.multilinear_rounds[0].0.hi ^= 1;
    neg("zerocheck_round_flipped", check(g0, &bad, &g128_rep_domain(0), &g0.pcs_params, &g0.commitment));
    let mut pp = g0.pcs_params.clone();
    pp.profile = g128_other(pp.profile);
    let cm = Commitment { cap: g0.commitment.cap.clone(), params: pp.clone() };
    neg("rep0_verified_under_other_ligerito_profile", check(g0, &g0.proof, &g128_rep_domain(0), &pp, &cm));
}

''' + s[b:]
for nbl in (16, 17, 18, 19):
    s += f"\n#[test]\n#[ignore]\nfn gpu_roundtrip_vs{nbl}() {{\n    roundtrip::<{nbl}, false>();\n}}\n"
p.write_text(s)

c = pathlib.Path("crates/flock-cuda-ffi/Cargo.toml")
t = c.read_text()
if "bincode" not in t:
    t = t.replace("[dev-dependencies]\n", "[dev-dependencies]\nbincode = { workspace = true }\n", 1)
    c.write_text(t)
print("patched gpu_roundtrip.rs for flock-128")
