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
t = sub(t, "fn gpu_prove(n_blocks_log: usize, dump_z: Option<&str>) -> GpuArtifacts {\n    let r1cs = build_block_r1cs(n_blocks_log);",
        "fn gpu_prove(n_blocks_log: usize, dump_z: Option<&str>) -> GpuArtifacts {\n"
        "    gpu_prove_with(build_block_r1cs(n_blocks_log), &BLAKE3_CSC_MATRICES, 0, dump_z)\n}\n\n"
        "fn gpu_prove_with(r1cs: BlockR1cs, mats: &'static OnceLock<CscMatrices>, mode: u32, dump_z: Option<&str>) -> GpuArtifacts {")
t = sub(t, "let matrices = BLAKE3_CSC_MATRICES.get_or_init(", "let matrices = mats.get_or_init(")
t = sub(t, "    let rc = unsafe { flock_cuda_prove_blake3(&params, &mut out, &mut out_len) };",
        "    let rc = unsafe {\n        match mode {\n"
        "            0 => flock_cuda_prove_blake3(&params, &mut out, &mut out_len),\n"
        "            2 => flock_glue_prove_unit(&params, &mut out, &mut out_len),\n"
        "            _ => {\n                let h = HOST_WIT.get().expect(\"host witness\");\n"
        "                flock_cuda_prove_host(&params, h.0.as_ptr(), h.1.as_ptr(), h.2.as_ptr(), h.3.as_ptr(), &mut out, &mut out_len)\n"
        "            }\n        }\n    };")
i = t.index("#[test]\n#[ignore] // needs an sm_120 GPU; run explicitly with --ignored\nfn gpu_roundtrip_m22")
t = t[:i] + (HERE / "gpu_glue_tail.rs").read_text()
pathlib.Path("crates/flock-cuda-ffi/tests/gpu_glue.rs").write_text(t)
print("wrote tests/gpu_glue.rs")
