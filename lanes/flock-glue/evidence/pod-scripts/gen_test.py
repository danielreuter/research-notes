"""flock-glue: generate crates/flock-cuda-ffi/tests/gpu_glue.rs from upstream tests/gpu_roundtrip.rs (cwd = repo root).
The upstream parse/verify plumbing is kept; gpu_prove gains a circuit + mode argument (0 BLAKE3 kernel, 1 host witness
upload, 2 device unit witness), and gpu_glue_tail.rs (tests glue_check / glue_bench) is appended."""
import pathlib
import sys

HERE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")


def sub(s, old, new):
    assert s.count(old) == 1, (old[:70], s.count(old))
    return s.replace(old, new)


t = pathlib.Path("crates/flock-cuda-ffi/tests/gpu_roundtrip.rs").read_text()
# Statements are built once per (circuit, n_blocks_log) and leaked (a prover builds its circuit shape once, not per
# batch); LAST_HOST records the host seconds before the FFI call and after it (stream parse into typed proof).
t = sub(t, "struct GpuArtifacts {\n    r1cs: BlockR1cs,", "struct GpuArtifacts {\n    r1cs: &'static BlockR1cs,")
t = sub(t, "fn gpu_prove(n_blocks_log: usize, dump_z: Option<&str>) -> GpuArtifacts {\n    let r1cs = build_block_r1cs(n_blocks_log);",
        "static STMTS: Mutex<Vec<((u32, usize), &'static BlockR1cs)>> = Mutex::new(Vec::new());\n"
        "static LAST_HOST: Mutex<(f64, f64)> = Mutex::new((0.0, 0.0));\n\n"
        "fn stmt(key: (u32, usize), build: impl FnOnce() -> BlockR1cs) -> &'static BlockR1cs {\n"
        "    let mut g = STMTS.lock().unwrap();\n"
        "    if let Some(&(_, s)) = g.iter().find(|(k, _)| *k == key) {\n        return s;\n    }\n"
        "    let s: &'static BlockR1cs = Box::leak(Box::new(build()));\n"
        "    let _ = s.statement_digest();\n"
        "    g.push((key, s));\n    s\n}\n\n"
        "fn gpu_prove(n_blocks_log: usize, dump_z: Option<&str>) -> GpuArtifacts {\n"
        "    gpu_prove_with(stmt((0, n_blocks_log), || build_block_r1cs(n_blocks_log)), &BLAKE3_CSC_MATRICES, 0, dump_z)\n}\n\n"
        "fn gpu_prove_with(r1cs: &'static BlockR1cs, mats: &'static OnceLock<CscMatrices>, mode: u32, dump_z: Option<&str>) -> GpuArtifacts {\n"
        "    let t_entry = Instant::now();")
t = sub(t, "    let t0 = Instant::now();\n    let mut out: *mut u8 = null_mut();",
        "    let pre_secs = t_entry.elapsed().as_secs_f64();\n    let t0 = Instant::now();\n    let mut out: *mut u8 = null_mut();")
t = sub(t, "        prove_secs: t_prove.as_secs_f64(),\n    }\n}",
        "        prove_secs: {\n"
        "            *LAST_HOST.lock().unwrap() = (pre_secs, t_entry.elapsed().as_secs_f64() - pre_secs - t_prove.as_secs_f64());\n"
        "            t_prove.as_secs_f64()\n        },\n    }\n}")
t = sub(t, "let matrices = BLAKE3_CSC_MATRICES.get_or_init(", "let matrices = mats.get_or_init(")
t = sub(t, "        profile: Default::default(),\n        num_lanes: None,", "        profile: glue_profile(),\n        num_lanes: None,")
t = sub(t, "    let rc = unsafe { flock_cuda_prove_blake3(&params, &mut out, &mut out_len) };",
        "    let rc = unsafe {\n        match mode {\n"
        "            0 => flock_cuda_prove_blake3(&params, &mut out, &mut out_len),\n"
        "            2 => flock_glue_prove_unit(&params, &mut out, &mut out_len),\n"
        "            3 => flock_glue_prove_unit_pre(&params, &mut out, &mut out_len),\n"
        "            _ => {\n                let h = HOST_WIT.get().expect(\"host witness\");\n"
        "                flock_cuda_prove_host(&params, h.0.as_ptr(), h.1.as_ptr(), h.2.as_ptr(), h.3.as_ptr(), &mut out, &mut out_len)\n"
        "            }\n        }\n    };")
i = t.index("#[test]\n#[ignore] // needs an sm_120 GPU; run explicitly with --ignored\nfn gpu_roundtrip_m22")
t = t[:i] + (HERE / "gpu_glue_tail.rs").read_text()
pathlib.Path("crates/flock-cuda-ffi/tests/gpu_glue.rs").write_text(t)
print("wrote tests/gpu_glue.rs")
